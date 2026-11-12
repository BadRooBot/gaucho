/* forge system: show the in-game Forge icon and handle Forge opcodes */
use super::*;
use crate::hero::Item;

/// Equipment level-up success rate (fraction).
///
/// From `ini/item_value_type.dat` (EquipUpLevInfo, `CItemData::ReadUpLevInfo`
/// @0xf8ce34): row = `id@@category@@level@@quality@@rate@@stone_type@@`, key =
/// `category*10000 + level*10 + quality`. Rates by level (category 7):
/// 0-10 → 5000, 11-12 → 2500, 13-16 → 1667, 17-18 → 1429, 19-20 → 1250,
/// 21+ → 1112 (units of 1/10000). All current gear sits in the ≤10 band, so a
/// flat 50% matches what the dialog displays; refine to the real curve once a
/// type→level map is decoded (level is per-type data in the client config).
const UPLEVEL_RATE: f64 = 0.5;

/// Stone types consumed by the Upgrade tab. The client hardcodes them in
/// `CFDlgForgingUpLevel::SendUpLevelMsg` @0x141d818 (literals 0x109a00/0x109a01).
const STONE_UNBOUND: u32 = 1088001;
const STONE_BOUND: u32 = 1088000;

/// Take `n` items of `typ` from bag stacks (may span several stacks).
/// Caller must pre-check availability; returns the per-stack results in
/// `Hero::take` form (count already decremented, stacks with 0 removed).
fn take_type(h: &mut crate::hero::Hero, typ: u32, mut n: u32) -> Vec<Item> {
    let mut out = Vec::new();
    while n > 0 {
        let Some(id) = h.items.iter().find(|it| it.typ == typ && it.pos == 0).map(|it| it.id) else { break };
        let take = h.items.iter().find(|it| it.id == id).map_or(0, |it| it.count).min(n);
        match h.take(id, take) {
            Some(it) => {
                n -= take;
                out.push(it);
            }
            None => break,
        }
    }
    out
}

/// Function-open flag sent to `CNewFunctionOpenMgr::SetFunctionFlag`.
///
/// The official capture sends **0** (frame 54: `08 fba54e 28 00 60 d703` =
/// IdUser, N64Data=0, action 471) BEFORE action 74. `SetFunctionFlagEx`
/// stores it because the reset value is -1 (first-call rule), so the client's
/// `m_nFunctionFlag` latches to 0 — exactly like official. A later official
/// frame sends flag=1 (action 96) which is NOT stored (1 > 0 signed), so the
/// stored flag stays 0. `ProcessFuncStatus` needs hi>=0: 0 passes.
const FORGE_FUNC_FLAG: u64 = 0;

impl World {
    /// Send the function-flag frame (CMsgMBAction 0x273e, action 0x1d7) so the
    /// client's CNewFunctionOpenMgr unlocks gated features (incl. Forge).
    ///
    /// Wire format: 4-byte header + `CMsgActionPB` protobuf.
    /// The 64-bit flag is protobuf **field 5 (N64Data)**; the client reads it
    /// with `ldrd r2,r3,[r1,#40]` where 40 = struct offset 0x28 = field 5.
    pub(super) fn forge_open(&mut self, cid: u64) {
        let flag = if self.players.get(&cid).is_some_and(|p| p.h.reborn >= 1 || p.h.level >= 130) {
            0x1ff
        } else {
            0x20
        };
        self.forge_open_flag(cid, flag);
    }

    /// Same frame with a caller-chosen flag (GM `fsetflag`): a later, larger
    /// flag makes the client's `SetFunctionFlag` store it and re-run
    /// `ProcessFuncStatus` — the server-driven status re-evaluation path.
    pub(super) fn forge_open_flag(&mut self, cid: u64, flag: u64) {
        let p = &self.players[&cid];
        let id = p.h.id as u64;
        let (x, y, map) = (p.h.x as u64, p.h.y as u64, p.h.map as u64);
        let now = ms();
        let body = Pb::new()
            .v(1, id).v(3, 0).v(7, x).v(8, y).v(9, now)
            .v(12, 0x1d7u64)                       // UsAction = 471
            .v(13, 0).v(14, x).v(15, y).v(17, map)
            .v(5, flag)                            // N64Data = function-open flag
            .out();
        if self.trace {
            println!("[FORGE {cid}] send 0x273e action=0x1d7 flag=0x{flag:x}");
        }
        self.send(cid, 0x273e, &body);
    }

    /// Send `CMsgMBAction` **action 251 (0xFB)** — the "login server over" ping.
    ///
    /// Client-side dispatch (`CMsgMBAction::Process` @ `0xf6f2bc`):
    /// `Create(action 0x84)` + `Send()` (client replies with action **132**),
    /// `CLoginNoticeMgr::SendVersionMsg()`, then
    /// `CMobileSDKData::SetLoginServerOver(true)` (writes `this+0xf1`).
    ///
    /// Why we need it: `CFDlgLoading::DoStateChange` @ `0x125e692` only runs
    /// `CNewFunctionOpenMgr::SetInitStatus(true)` when loading progress
    /// `[dlg+0x280] >= 0x400` **and** `IsLoginServerOver()`. `SetInitStatus`
    /// is the *sole* writer of `mgr+0x18`, and `ProcessFuncStatus` @ `0x15a362e`
    /// early-returns while `mgr+0x18 == 0` — so without action 251 **every**
    /// `SetFunctionFlag` (action 471) is a no-op and all func-gated buttons
    /// (Forge = func 6) stay hidden.
    ///
    /// Requires `IdUser` (field 1) == the client's hero id: `GetPlayerEjb`
    /// with `bool=1` compares against `CHero+0x1bc`.
    pub(super) fn login_server_over(&mut self, cid: u64) {
        let p = &self.players[&cid];
        let id = p.h.id as u64;
        let now = ms();
        let body = Pb::new()
            .v(1, id).v(3, 0).v(9, now).v(12, 251u64)
            .v(14, p.h.x as u64).v(15, p.h.y as u64).v(17, p.h.map as u64)
            .out();
        if self.trace {
            println!("[FORGE {cid}] send 0x273e action=251 (login-server-over)");
        }
        self.send(cid, 0x273e, &body);
    }

    /// Generic Forge opcode ack (echo back) until per-opcode logic is added.
    pub(super) fn forge_ack(&mut self, cid: u64, ty: u16, body: &[u8]) {
        if self.trace {
            let hex: String = body.iter().take(32).map(|b| format!("{b:02x}")).collect();
            println!("[FORGE {cid}] ack 0x{ty:04x} {hex}");
        }
        self.send(cid, ty, body);
    }

    /// `CMsgDataArray` (0x2834) — the Forge system's generic data-array packet.
    ///
    /// Payload after the 4-byte net header: `[type u8][count u8][pad u16]
    /// [count × u32 LE]`. Client builder `CMsgDataArray::CreateEijjjjj`
    /// @0xfff41c writes len u16 @+0, opcode u16 @+2, type @+4, count @+5,
    /// fields @+8; `take_packets` strips the header, so `body` starts at the
    /// type byte. `CMsgDataArray::Process` @0xfff3b0 is EMPTY — outcomes are
    /// delivered as ordinary item updates (0x2784) + system talk.
    pub(super) fn forge_data_array(&mut self, cid: u64, body: &[u8]) {
        let Some(&ty) = body.first() else { return };
        let count = *body.get(1).unwrap_or(&0) as usize;
        let fields: Vec<u32> = body.get(4..).unwrap_or(&[]).chunks_exact(4).take(count)
            .map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect();
        match ty {
            6 => self.forge_up_level(cid, &fields),
            _ if self.trace => println!("[FORGE {cid}] data-array type {ty} fields {fields:?}"),
            _ => {}
        }
    }

    /// Forge array type 6: equipment level-up (the Upgrade tab).
    ///
    /// Sent by `CFDlgForgingUpLevel::SendUpLevelMsg(b,i)` @0x141d818 →
    /// `CHero::UpLevelItem(uid, 0x109a01, cnt, 0x109a00, cnt2)` @0xe3dcd4 →
    /// `CMsgDataArray::CreateEijjjjj(6, ...)`:
    /// `fields = [item uid, unbound-stone type, count, bound-stone type, count]`.
    ///
    /// Target type: `CHero::GetNextUpgradeItem(type)` @0xfe9768 = first
    /// `type+10k` present in the client's itemtype config (type ladder groups
    /// 000-009, 013-019, 023-029, …; blade 601007 "Lv. 5" → 601017 "Lv. 10").
    /// On success the item's **type** changes (level lives in the type, the
    /// client derives display/stats from its own per-type config); stones are
    /// consumed either way. Announcements: 0x2784 action 3 for the equipment
    /// and each stone stack (or 0x2799 removal when a stack empties), plus a
    /// system talk line.
    pub(super) fn forge_up_level(&mut self, cid: u64, f: &[u32]) {
        if f.len() < 5 {
            return;
        }
        let (uid, sa, ca, sb, cb) = (f[0], f[1], f[2], f[3], f[4]);
        let h = &self.players[&cid].h;
        let Some(old_typ) = h.items.iter().find(|it| it.id == uid).map(|it| it.typ) else {
            println!("[FORGE {cid}] up-level: item {uid} not found");
            return;
        };
        if sa != STONE_UNBOUND && sa != STONE_BOUND && sa != 0
            || sb != STONE_UNBOUND && sb != STONE_BOUND && sb != 0
        {
            println!("[FORGE {cid}] up-level: unexpected stone types {sa:#x}/{sb:#x}");
            return;
        }
        let owned = |typ: u32| h.items.iter().filter(|it| it.typ == typ && it.pos == 0)
            .map(|it| it.count).sum::<u32>();
        if owned(sa) < ca || owned(sb) < cb {
            println!("[FORGE {cid}] up-level: not enough stones (need {ca}x{sa} + {cb}x{sb}, have {} + {})", owned(sa), owned(sb));
            return;
        }
        let new_typ = old_typ + 10;
        let success = rand::thread_rng().gen_bool(UPLEVEL_RATE);
        let taken = {
            let h = &mut self.players.get_mut(&cid).unwrap().h;
            if success {
                if let Some(it) = h.items.iter_mut().find(|it| it.id == uid) {
                    it.typ = new_typ;
                }
            }
            let mut taken = Vec::new();
            for (typ, n) in [(sa, ca), (sb, cb)] {
                if n > 0 {
                    taken.extend(take_type(h, typ, n));
                }
            }
            taken
        };
        for it in &taken {
            self.send_taken(cid, it);
        }
        if success {
            if let Some(it) = self.players[&cid].h.items.iter().find(|it| it.id == uid) {
                if !self.d.items.items.contains_key(&new_typ) {
                    println!("[FORGE {cid}] up-level: type {new_typ} missing from items.json (client still shows it)");
                }
                self.send(cid, 0x2784, &item::item_info(it, 3, 0));
            }
            if self.trace {
                println!("[FORGE {cid}] up-level OK: {uid} typ {old_typ} -> {new_typ}, stones {:?}", taken.iter().map(|t| (t.typ, t.count)).collect::<Vec<_>>());
            }
            self.send(cid, 0x27c3, &talk(2005, "Forge upgrade succeeded!"));
        } else {
            if self.trace {
                println!("[FORGE {cid}] up-level FAILED: {uid} typ {old_typ} kept, stones {:?}", taken.iter().map(|t| (t.typ, t.count)).collect::<Vec<_>>());
            }
            self.send(cid, 0x27c3, &talk(2005, "Forge upgrade failed, stones lost."));
        }
    }

    /// Re-send the function-open flag while a retry is scheduled (see `ready()`).
    /// Every `SetFunctionFlag` call re-runs `ProcessFuncStatus`, so a late send
    /// flips the client's status bit3 once its init state is ready.
    pub(super) fn forge_tick(&mut self, now: Instant) {
        let due: Vec<u64> = self.players.iter()
            .filter_map(|(c, p)| p.forge_retry.filter(|(t, _)| now >= *t).map(|_| *c))
            .collect();
        for cid in due {
            let tries = self.players[&cid].forge_retry.unwrap().1;
            self.login_server_over(cid);
            self.forge_open(cid);
            // CNewFunctionOpenMgr skips PostCmd(0xcf0, 0x711) when old_status == 0,
            // leaving [1809-1020] (Lineage) stranded off-screen at x=10150 in 1809.ini.
            // Sending CMsgXueMai action 2 right after forge_open forces CDlgNewMenu::ResetBtnsPos().
            if self.players.get(&cid).is_some_and(|p| p.h.reborn >= 1 || p.h.level >= 130 || !p.h.lineage_profs.is_empty()) {
                self.send_lineage_refresh(cid);
            }
            let p = self.players.get_mut(&cid).unwrap();
            p.forge_retry = if tries + 1 < 8 {
                Some((now + Duration::from_secs(5), tries + 1))
            } else {
                None
            };
        }
    }
}
