/*+++++++++++++++
 + Lineage / XueMai (血脉) system — opcode 0x28a1
 + CMsgXueMaiPB protobuf handler
 +++++++++++++++*/

use crate::hero::LineageProf;
use crate::net::proto::Pb;
use crate::world::World;

impl World {
    /// Encode CMsgXueMai (0x28a1) for a player with a specific unAction.
    pub(super) fn lineage_packet_bytes(&self, cid: u64, action: u32) -> Vec<u8> {
        let h = &self.players[&cid].h;

        // cur_prof_sort = first (main) lineage prof, or 0 if none
        let cur_sort = h.lineage_profs.first().map(|p| p.prof_sort).unwrap_or(0);

        let mut pb = Pb::new()
            .v(1, action as u64)                 // unAction: 0=sync, 2=refresh UI (1809 HUD)
            .v(2, h.lineage_xuemai as u64)       // unXueMaiCount
            .v(3, cur_sort as u64)               // unCurProfSort
            .v(5, h.id as u64);                  // idUser

        // lstProf — repeated field 4, each sub-message encoded separately
        for prof in &h.lineage_profs {
            let sub = Pb::new()
                .v(1, prof.prof_sort as u64)
                .v(2, prof.level as u64)
                .v(3, prof.exp as u64)
                .v(4, prof.prob as u64)
                .out();
            pb = pb.b(4, &sub);
        }

        // CRITICAL: bGuide (field 6) MUST always be explicitly set to 0.
        // If omitted or non-zero, the client calls SetDoBloodGuide(true),
        // which locks user input (screen becomes unclickable) and triggers a tutorial overlay.
        pb = pb.v(6, if h.lineage_guide { 1 } else { 0 });

        pb.out()
    }

    /// Build and send CMsgXueMai (0x28a1) sync to client (unAction=0).
    pub(super) fn send_lineage(&self, cid: u64) {
        let bytes = self.lineage_packet_bytes(cid, 0);
        self.send(cid, 0x28a1, &bytes);
    }

    /// Build and send CMsgXueMai (0x28a1) UI refresh to client (unAction=2).
    /// unAction=2 calls PostCmd(0xcf0, 0x711) in the client, which immediately
    /// refreshes GUI 1809 (the right-side menu) and makes the Lineage button appear.
    pub(super) fn send_lineage_refresh(&self, cid: u64) {
        let bytes = self.lineage_packet_bytes(cid, 2);
        self.send(cid, 0x28a1, &bytes);
    }

    /// Handle incoming CMsgXueMai packet (0x28a1) from client.
    pub(super) fn on_lineage(&mut self, cid: u64, body: &[u8]) {
        use crate::net::proto::Msg;
        let Some(msg) = Msg::parse(body) else {
            self.send_lineage(cid);
            return;
        };
        let action = msg.get(1);
        println!("[LINEAGE] cid={cid} action={action}");
        match action {
            0 => {
                self.send_lineage(cid);
                self.send_lineage_refresh(cid);
            }
            2 => self.send_lineage_refresh(cid),
            3 => {
                // Refine / Upgrade request
                self.send_lineage(cid);
                self.send_lineage_refresh(cid);
            }
            5 => {
                // Save inheritance request
                self.send_lineage(cid);
                self.send_lineage_refresh(cid);
            }
            _ => {
                self.send_lineage(cid);
            }
        }
    }

    /// Ensure player has at least one Lineage prof entry and base xuemai points.
    pub(super) fn lineage_ensure(&mut self, cid: u64) {
        let h = &mut self.players.get_mut(&cid).unwrap().h;
        if h.lineage_profs.is_empty() {
            let sort = class_to_prof_sort(h.class);
            if sort > 0 {
                h.lineage_profs.push(LineageProf {
                    prof_sort: sort,
                    level: 1,
                    exp: 0,
                    prob: 50,
                });
            }
            if h.reborn >= 2 {
                let second_sort = if sort == 1 { 2 } else { 1 };
                h.lineage_profs.push(LineageProf {
                    prof_sort: second_sort,
                    level: 1,
                    exp: 0,
                    prob: 50,
                });
            }
            if h.lineage_xuemai == 0 {
                h.lineage_xuemai = 50000;
            }
        }
    }

    /// Auto-grant Lineage prof entries based on reborn class if character has reborn >= 1 and no profs yet.
    pub(super) fn lineage_init_for_reborn(&mut self, cid: u64) {
        if self.players.get(&cid).is_some_and(|p| p.h.reborn >= 1 && p.h.lineage_profs.is_empty()) {
            self.lineage_ensure(cid);
        }
    }
}

/// Map class code → CMsgXueMai unProfSort (from cn_res.ini STR_PROF_NAME_*)
fn class_to_prof_sort(class: u32) -> u32 {
    let base = if class >= 1000 { class / 1000 } else { class / 10 };
    match base {
        1 | 11 | 12 | 15 | 50..=59 => 1,  // Trojan
        2 | 20..=27 => 2,            // Warrior
        4 | 40..=47 => 4,            // Archer
        5 | 60..=67 => 5,            // Ninja
        6 | 70..=77 => 6,            // Monk / Saint
        7 | 80..=87 => 7,            // Pirate
        8 | 90..=97 => 8,            // Dragon Warrior
        9 | 100..=107 => 9,          // Thunderstriker
        10 | 13 | 130..=137 => 13,   // Water Taoist
        14 | 140..=147 => 14,        // Fire Taoist
        16 | 160..=167 => 16,        // Windwalker
        _ => 1,                      // Default to Trojan
    }
}