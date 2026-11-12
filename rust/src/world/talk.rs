/*~~~~~~~~~~~
 : gaucho - conquer mobile private server
 : with love from bolzov (人◕‿◕)
 : https://github.com/ibolzov
 ~~~~~~~~~~~*/

use super::*;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum NpcCategory {
    Rowland,
    Teleport,
    Warehouse,
    Shop,
    Guard,
    Sage,
    Dummy,
    General,
    Rebirth,
}

fn classify_npc(npc: u32, look: u32, is_shop: bool) -> NpcCategory {
    let ntype = look / 10;
    if npc == 10090 {
        NpcCategory::Rebirth
    } else if npc == 10050 || ntype == 1093 {
        NpcCategory::Rowland
    } else if npc == 10052 || npc == 10051 || npc == 10053 || npc == 511 || npc == 1871
        || ntype == 287 || ntype == 286 || ntype == 5297 || ntype == 5298 {
        NpcCategory::Teleport
    } else if npc == 10002 || npc == 1002 || npc == 1165 || (1906..=1909).contains(&npc)
        || ntype == 5485 || ntype == 6511 || ntype == 26 {
        NpcCategory::Warehouse
    } else if is_shop || ntype == 389 || ntype == 466 || ntype == 5189 || ntype == 6401 || ntype == 6528 {
        NpcCategory::Shop
    } else if npc == 32322 || npc == 32287 || npc == 200084 || ntype == 1466 || ntype == 1352 || ntype == 175 {
        NpcCategory::Guard
    } else if npc == 10047 || npc == 20536 || npc == 32478 || npc == 34493 || ntype == 366 || ntype == 1164 || ntype == 1401 || ntype == 1384 {
        NpcCategory::Sage
    } else if (1384..=1393).contains(&ntype) || ntype == 1157 || ntype == 1431 || ntype == 1432 || ntype == 1255 {
        NpcCategory::Dummy
    } else {
        NpcCategory::General
    }
}

fn npc_avatar(cat: NpcCategory) -> u16 {
    match cat {
        NpcCategory::Rowland => 2,
        NpcCategory::Teleport => 7,
        NpcCategory::Warehouse => 6,
        NpcCategory::Shop => 4,
        NpcCategory::Guard => 3,
        NpcCategory::Sage => 5,
        NpcCategory::Dummy => 9,
        NpcCategory::General => 2,
        NpcCategory::Rebirth => 5,
    }
}

impl World {
    pub(super) fn npc_talk(&mut self, cid: u64, body: &[u8]) {
        let m = Msg::parse_lossy(body);
        let npc = m.get(2) as u32;
        let act = m.get(3);
        println!("[WORLD] {} talks to npc {npc} act {act}", self.players[&cid].h.name);
        if self.quest_npc(cid, npc, act) {
            return;
        }

        let map = self.players[&cid].h.map;
        let look = self.d.npcs.get(&map).and_then(|list| list.iter().find(|n| n.id == npc)).map_or(0, |n| n.look);
        let is_shop = self.d.items.shops.contains_key(&npc);
        let cat = classify_npc(npc, look, is_shop);
        let avatar = npc_avatar(cat);

        {
            let p = self.players.get_mut(&cid).unwrap();
            p.last_npc = npc;
            p.dialog_menu = 0;
        }

        let dialog_items: &[ (u8, u8, &str) ] = match cat {
            NpcCategory::Rowland => &[
                (0xff, 1, "Greetings, warrior! I am Rowland, the Realm Guide of Wind Plain. Martial artists gather here to temper their spirits, cultivate profound energy, and seek breakthroughs into higher realms. How may I guide your path today?"),
                (1, 2, "Restore Vitality & Energy (Full Heal)"),
                (2, 2, "Guidance: The Path of Cultivation"),
                (3, 2, "Teleport to Twin City (Central Plains)"),
                (4, 2, "Teleport to Market"),
                (5, 2, "Farewell, Master Rowland."),
                (0xff, 100, ""),
            ],
            NpcCategory::Teleport => &[
                (0xff, 1, "Where are you heading for? The wilderness between provinces can be perilous, but I can guide you swiftly to any major realm."),
                (1, 2, "Twin City (Central Plains)"),
                (2, 2, "Phoenix Castle"),
                (3, 2, "Bird Island"),
                (4, 2, "Ape City"),
                (5, 2, "Desert City"),
                (6, 2, "Market"),
                (7, 2, "Never mind."),
                (0xff, 100, ""),
            ],
            NpcCategory::Warehouse => &[
                (0xff, 1, "Welcome! I manage the warehouse facilities across every city. You can safeguard your wealth and precious items here without worry."),
                (1, 2, "Deposit 10,000 Silver into Vault"),
                (2, 2, "Check Storage & Balance"),
                (3, 2, "Rest and Recover Health"),
                (4, 2, "Farewell."),
                (0xff, 100, ""),
            ],
            NpcCategory::Shop => &[
                (0xff, 1, "Welcome to my shop! Only the finest provisions, weapons, and remedies are offered here for brave travelers. How may I serve you?"),
                (1, 2, "Quick Supply: 10x Ginseng (HP Potions)"),
                (2, 2, "Quick Supply: 5x Portal Scrolls"),
                (3, 2, "Repair All Equipped Gear"),
                (4, 2, "Restore Health & Stamina"),
                (5, 2, "Just browsing, thank you."),
                (0xff, 100, ""),
            ],
            NpcCategory::Guard => &[
                (0xff, 1, "Stand firm, citizen! The garrison remains vigilant against outlaw bands and wild beasts roaming the outskirts. Report any disturbance!"),
                (1, 2, "Garrison Security Report"),
                (2, 2, "Request Field Medical Aid (Heal)"),
                (3, 2, "Pardon 10 PK Points"),
                (4, 2, "Stand easy, Officer."),
                (0xff, 100, ""),
            ],
            NpcCategory::Sage => &[
                (0xff, 1, "Peace be upon you, seeker of the Way. Through patience and quiet meditation, the inner spirit attunes itself to heaven and earth."),
                (1, 2, "Receive Celestial Blessing (Heal)"),
                (2, 2, "Lore: Mystical Gems & Refinement"),
                (3, 2, "Farewell, Revered One."),
                (0xff, 100, ""),
            ],
            NpcCategory::Dummy => &[
                (0xff, 1, "A heavy training dummy bound with thick straw and enchanted iron, ideal for practicing offensive forms and physical conditioning."),
                (1, 2, "Practice combat strikes (Recover Stamina)"),
                (2, 2, "Step away."),
                (0xff, 100, ""),
            ],
            NpcCategory::General => &[
                (0xff, 1, "Greetings, traveler! The realm is vast and full of opportunity. May your blade stay sharp and your fortunes rise."),
                (1, 2, "Heal my wounds and restore energy"),
                (2, 2, "Inquire about this region"),
                (3, 2, "Farewell."),
                (0xff, 100, ""),
            ],
            NpcCategory::Rebirth => &[
                (0xff, 1, "Greetings, honorable traveler! I am the Rebirth Master of Wind Plain. Mortal cultivation reaches its zenith at Level 120, where the soul may transcend and be Reborn anew, retaining divine wisdom and gaining boundless attribute power. What is your desire?"),
                (1, 2, "I am ready for Rebirth!"),
                (2, 2, "Inquire about Rebirth requirements & bonuses."),
                (3, 2, "Restore Vitality & Energy (Full Heal)"),
                (4, 2, "Farewell, Master."),
                (0xff, 100, ""),
            ],
        };

        for &(opt, kind, text) in dialog_items {
            self.send(cid, 0x280f, &dialog_full(npc, avatar, opt, kind, text));
        }
    }

    pub(super) fn npc_answer(&mut self, cid: u64, body: &[u8]) {
        let (opt, kind) = (body.get(6).copied().unwrap_or(0), body.get(7).copied().unwrap_or(0));
        println!("[WORLD] {} npc_answer: opt={opt} kind={kind} body_len={}", self.players[&cid].h.name, body.len());
        if kind != 101 {
            return;
        }
        let npc = self.players.get(&cid).map_or(0, |p| p.last_npc);
        let map = self.players.get(&cid).map_or(0, |p| p.h.map);
        let look = self.d.npcs.get(&map).and_then(|list| list.iter().find(|n| n.id == npc)).map_or(0, |n| n.look);
        let is_shop = self.d.items.shops.contains_key(&npc);
        let cat = classify_npc(npc, look, is_shop);

        match cat {
            NpcCategory::Rowland => match opt {
                1 => self.heal_and_restore(cid, "Master Rowland channeled profound inner energy into you. Health and stamina fully restored!"),
                2 => {
                    self.send(cid, 0x27c3, &talk(2005, "Master Rowland: The path of cultivation requires discipline. Defeat monsters in Wind Plain, acquire precious gems, and ascend through martial stages to achieve supreme enlightenment."));
                }
                3 => {
                    self.change_map(cid, 1002, 438, 380);
                    self.send(cid, 0x27c3, &talk(2005, "Master Rowland transported you to Twin City!"));
                }
                4 => {
                    self.change_map(cid, 1036, 210, 190);
                    self.send(cid, 0x27c3, &talk(2005, "Master Rowland transported you to the Market!"));
                }
                _ => {}
            },
            NpcCategory::Teleport => match opt {
                1 => {
                    self.change_map(cid, 1002, 438, 380);
                    self.send(cid, 0x27c3, &talk(2005, "Arrived at Twin City!"));
                }
                2 => {
                    self.change_map(cid, 1011, 230, 260);
                    self.send(cid, 0x27c3, &talk(2005, "Arrived at Phoenix Castle!"));
                }
                3 => {
                    self.change_map(cid, 1015, 720, 570);
                    self.send(cid, 0x27c3, &talk(2005, "Arrived at Bird Island!"));
                }
                4 => {
                    self.change_map(cid, 1020, 560, 580);
                    self.send(cid, 0x27c3, &talk(2005, "Arrived at Ape City!"));
                }
                5 => {
                    self.change_map(cid, 1000, 470, 640);
                    self.send(cid, 0x27c3, &talk(2005, "Arrived at Desert City!"));
                }
                6 => {
                    self.change_map(cid, 1036, 210, 190);
                    self.send(cid, 0x27c3, &talk(2005, "Arrived at Market!"));
                }
                _ => {}
            },
            NpcCategory::Warehouse => match opt {
                1 => {
                    let p = self.players.get_mut(&cid).unwrap();
                    if p.h.money >= 10_000 {
                        p.h.money -= 10_000;
                        let (id, money) = (p.h.id, p.h.money);
                        self.send(cid, 0x27c0, &attrib(id, &[(4, money)]));
                        self.send(cid, 0x27c3, &talk(2005, "Warehouseman: 10,000 silver safely stored into your private vault account."));
                    } else {
                        self.send(cid, 0x27c3, &talk(2005, "Warehouseman: You need at least 10,000 silver to make a deposit."));
                    }
                }
                2 => {
                    let h = &self.players[&cid].h;
                    let (money, bag_count) = (h.money, h.items.len());
                    self.send(cid, 0x27c3, &talk(2005, &format!("Warehouse Ledger: Carrying {money} silver, {bag_count}/40 bag slots used. Vault storage is secure.")));
                }
                3 => self.heal_and_restore(cid, "Warehouseman: Rest well! Your injuries have healed."),
                _ => {}
            },
            NpcCategory::Shop => match opt {
                1 => {
                    self.quick_buy(cid, 1000000, 10, 500, "10x Ginseng Potions");
                }
                2 => {
                    self.quick_buy(cid, 1060020, 5, 500, "5x Town Portal Scrolls");
                }
                3 => {
                    self.repair_equipped(cid);
                }
                4 => self.heal_and_restore(cid, "Shopkeeper: Warm tea and rest have restored your health!"),
                _ => {}
            },
            NpcCategory::Guard => match opt {
                1 => {
                    self.send(cid, 0x27c3, &talk(2005, "Officer: Gates secured, sentries active. Outlaws in surrounding valleys will be met with full force."));
                }
                2 => self.heal_and_restore(cid, "Garrison Medic: Bandages applied and vigor restored. Stay alert out there!"),
                3 => {
                    let p = self.players.get_mut(&cid).unwrap();
                    if p.h.pk > 0 {
                        p.h.pk = p.h.pk.saturating_sub(10);
                        let (id, pk) = (p.h.id, p.h.pk);
                        self.send(cid, 0x27c0, &attrib(id, &[(6, pk as u64)]));
                        self.send(cid, 0x27c3, &talk(2005, &format!("Officer: For meritorious service, your PK has decreased to {pk}.")));
                    } else {
                        self.send(cid, 0x27c3, &talk(2005, "Officer: You have no active bounties or PK penalties. Good standing citizen!"));
                    }
                }
                _ => {}
            },
            NpcCategory::Sage => match opt {
                1 => self.heal_and_restore(cid, "A soothing celestial aura envelops you. Vitality and stamina restored!"),
                2 => {
                    self.send(cid, 0x27c3, &talk(2005, "Sage: Celestial gems channel ancient powers: Dragon increases attack, Phoenix boosts magic, and Tortoise provides unyielding defense."));
                }
                _ => {}
            },
            NpcCategory::Dummy => match opt {
                1 => {
                    let p = self.players.get_mut(&cid).unwrap();
                    p.stamina = 100;
                    let id = p.h.id;
                    self.send(cid, 0x27c0, &attrib(id, &[(1, 100)]));
                    self.send(cid, 0x27c3, &talk(2005, "You struck the practice dummy with precision! Stamina fully restored."));
                }
                _ => {}
            },
            NpcCategory::General => match opt {
                1 => self.heal_and_restore(cid, "Your health and vigor have been restored!"),
                2 => {
                    let map_name = match map {
                        1002 => "Twin City & Wind Plain",
                        1011 => "Phoenix Castle",
                        1015 => "Bird Island",
                        1020 => "Ape City",
                        1000 => "Desert City",
                        1036 => "Market District",
                        _ => "the Outer Realms",
                    };
                    self.send(cid, 0x27c3, &talk(2005, &format!("Local Guide: You are currently traversing {map_name}. Strong creatures and bountiful treasures await adventurous travelers.")));
                }
                _ => {}
            },
            NpcCategory::Rebirth => {
                let menu = self.players.get(&cid).map_or(0, |p| p.dialog_menu);
                let avatar = npc_avatar(cat);
                if menu == 0 {
                    match opt {
                        1 => {
                            let level = self.players.get(&cid).map_or(0, |p| p.h.level);
                            if level < 120 {
                                let req_dialog: &[ (u8, u8, &str) ] = &[
                                    (0xff, 1, "You must reach at least Level 120 before you can undergo Rebirth! Continue your cultivation and return when your strength has matured."),
                                    (1, 2, "I will train harder. (Leave)"),
                                    (0xff, 100, ""),
                                ];
                                for &(opt, kind, text) in req_dialog {
                                    self.send(cid, 0x280f, &dialog_full(npc, avatar, opt, kind, text));
                                }
                                self.send(cid, 0x27c3, &talk(2005, "Rebirth Master: You must be at least Level 120 to be reborn!"));
                            } else {
                                let class_dialog: &[ (u8, u8, &str) ] = &[
                                    (0xff, 1, "The reincarnation altar is awakened! Choose your new martial path. You will emerge at Level 15 with profound attribute points:"),
                                    (1, 2, "Trojan (Dual Weapons Offensive Master)"),
                                    (2, 2, "Warrior (Shield and Heavy Armor Master)"),
                                    (3, 2, "Archer (Long-range Precision Master)"),
                                    (4, 2, "Ninja (Dual Katanas and Speed Master)"),
                                    (5, 2, "Monk (Holy Chants and Battle Staff)"),
                                    (6, 2, "Pirate (Rapier and Pistol Gunslinger)"),
                                    (7, 2, "Taoist (Mystic Spells and Nature Arts)"),
                                    (8, 2, "Dune Wanderer (Wind Blades and Sand Storm)"),
                                    (9, 2, "I need to prepare more. (Cancel)"),
                                    (0xff, 100, ""),
                                ];
                                if let Some(p) = self.players.get_mut(&cid) {
                                    p.dialog_menu = 1;
                                }
                                for &(opt, kind, text) in class_dialog {
                                    self.send(cid, 0x280f, &dialog_full(npc, avatar, opt, kind, text));
                                }
                            }
                        }
                        2 => {
                            let info_dialog: &[ (u8, u8, &str) ] = &[
                                (0xff, 1, "Rebirth Requirements:\n- Level 120 or above.\n\nBenefits:\n- Your level resets to 15, gaining extra Reborn attribute points based on pre-reborn level (up to +55 at level 130).\n- Gain access to powerful Reborn skills.\n- Reborn rank increases!"),
                                (1, 2, "Thank you for the guidance."),
                                (0xff, 100, ""),
                            ];
                            if let Some(p) = self.players.get_mut(&cid) {
                                p.dialog_menu = 2;
                            }
                            for &(opt, kind, text) in info_dialog {
                                self.send(cid, 0x280f, &dialog_full(npc, avatar, opt, kind, text));
                            }
                        }
                        3 => self.heal_and_restore(cid, "Rebirth Master cleansed your meridians. Health and energy fully restored!"),
                        _ => {}
                    }
                } else if menu == 1 {
                    if let Some(p) = self.players.get_mut(&cid) {
                        p.dialog_menu = 0;
                    }
                    let chosen = match opt {
                        1 => Some((1000, "Trojan")),
                        2 => Some((2000, "Warrior")),
                        3 => Some((4000, "Archer")),
                        4 => Some((5000, "Ninja")),
                        5 => Some((6000, "Monk")),
                        6 => Some((7000, "Pirate")),
                        7 => Some((10000, "Taoist")),
                        8 => Some((3000, "Dune Wanderer")),
                        _ => None,
                    };
                    if let Some((cls_id, cls_name)) = chosen {
                        self.do_rebirth(cid, cls_id, cls_name);
                    }
                } else if menu == 2 {
                    if let Some(p) = self.players.get_mut(&cid) {
                        p.dialog_menu = 0;
                    }
                }
            }
        }
    }

    fn do_rebirth(&mut self, cid: u64, chosen_class: u32, class_name: &str) {
        let level = self.players.get(&cid).map_or(0, |p| p.h.level);
        if level < 120 {
            self.send(cid, 0x27c3, &talk(2005, "Rebirth Master: You need to be at least Level 120 to be reborn!"));
            return;
        }

        let bonus: u16 = match level {
            0..=120 => 0,
            121 => 1,
            122 => 3,
            123 => 6,
            124 => 10,
            125 => 15,
            126 => 21,
            127 => 28,
            128 => 36,
            129 => 45,
            _ => 55,
        };

        let mut item_updates = Vec::new();
        let (player_name, new_reborn, map, hid) = {
            let p = self.players.get_mut(&cid).unwrap();
            let player_name = p.h.name.clone();
            p.h.reborn += 1;
            let new_reborn = p.h.reborn;
            p.h.level = 15;
            p.h.exp = 0;
            p.h.class = chosen_class;
            p.h.add_points += bonus;

            let c = self.classes.get(chosen_class);
            for i in 0..4 {
                p.h.stats[i] = c.base[i] + c.growth[i] * 14;
            }
            p.h.hp = p.h.max_hp(c);
            p.h.mp = p.h.max_mp(c);
            p.stamina = 100;

            if let [typ @ 1..=u32::MAX, dur] = c.weapon {
                let dur_val = dur as u16;
                for (it, new) in p.h.add_item(typ, 1, dur_val) {
                    item_updates.push((it, new));
                }
            }

            self.store.put(&p.key, &p.h);
            (player_name, new_reborn, p.h.map, p.h.id)
        };

        self.store.flush();

        for (it, new) in item_updates {
            self.send(cid, 0x2784, &item::item_info(&it, if new { 1 } else { 3 }, 0));
        }

        self.sync_attribs(cid);
        self.learn_skills(cid);

        self.send_view(map, hid, 0x27c0, &attrib(hid, &[(12, 15), (22, new_reborn as u64), (7, chosen_class as u64)]));
        self.send_view(map, hid, 0x273e, &Pb::new().v(1, hid as u64).v(9, ms()).v(12, 92).v(14, 15).out());

        self.refresh_view(cid);

        let announce = format!("Congratulations! [{}] has achieved Rebirth {} as [{}] with +{} bonus attribute points!", player_name, new_reborn, class_name, bonus);
        println!("[WORLD] {}", announce);
        for q in self.players.values().filter(|q| q.h.id != 0) {
            let _ = q.tx.send(frame(0x27c3, &talk(2005, &announce)));
        }
    }

    fn heal_and_restore(&mut self, cid: u64, message: &str) {
        let max = { let h = &self.players[&cid].h; h.max_hp(self.classes.get(h.class)) };
        let p = self.players.get_mut(&cid).unwrap();
        if p.alive {
            p.h.hp = max;
            p.stamina = 100;
            let id = p.h.id;
            self.send(cid, 0x27c0, &attrib(id, &[(0, max as u64), (1, 100)]));
            self.send(cid, 0x27c3, &talk(2005, message));
        }
    }

    fn quick_buy(&mut self, cid: u64, typ: u32, count: u32, total_cost: u64, item_name: &str) {
        let h = &self.players[&cid].h;
        if h.money < total_cost {
            self.send(cid, 0x27c3, &talk(2005, &format!("Not enough silver. {item_name} costs {total_cost} silver.")));
            return;
        }
        if h.bag_full() {
            self.send(cid, 0x27c3, &talk(2005, "Your bag is full!"));
            return;
        }
        let dur = self.d.items.dur(typ);
        let p = self.players.get_mut(&cid).unwrap();
        p.h.money -= total_cost;
        let (hid, money) = (p.h.id, p.h.money);
        for (it, new) in p.h.add_item(typ, count, dur) {
            self.send(cid, 0x2784, &item::item_info(&it, if new { 1 } else { 3 }, 0));
        }
        self.send(cid, 0x27c0, &attrib(hid, &[(4, money)]));
        self.send(cid, 0x27c3, &talk(2005, &format!("Purchased {item_name} for {total_cost} silver!")));
    }

    fn repair_equipped(&mut self, cid: u64) {
        let mut repaired = 0;
        let mut updates = Vec::new();
        {
            let p = self.players.get_mut(&cid).unwrap();
            for it in p.h.items.iter_mut().filter(|i| i.pos > 0) {
                let max_dur = self.d.items.dur(it.typ);
                if it.dur < max_dur {
                    it.dur = max_dur;
                    repaired += 1;
                    updates.push(it.clone());
                }
            }
        }
        for it in updates {
            self.send(cid, 0x2784, &item::item_info(&it, 3, 0));
        }
        if repaired > 0 {
            self.send(cid, 0x27c3, &talk(2005, &format!("Repaired {repaired} equipped items to peak condition!")));
        } else {
            self.send(cid, 0x27c3, &talk(2005, "All equipped items are already in pristine condition."));
        }
    }

    pub(super) fn chat(&mut self, cid: u64, body: &[u8]) {
        let m = Msg::parse_lossy(body);
        let text = String::from_utf8_lossy(m.bytes(13, 3).unwrap_or_default()).into_owned();
        if text.is_empty() || self.command(cid, &text) {
            return;
        }
        let p = &self.players[&cid];
        let (channel, to) = (m.get(2), m.bytes(13, 1).unwrap_or_default());
        println!("[CHAT] {} ch{channel}: {text}", p.h.name);
        if channel == 2001 && !self.players.values().any(|q| q.h.id != 0 && q.h.name.as_bytes() == to) {
            return self.send(cid, 0x27c3, &talk(2005, &format!("{} is offline", String::from_utf8_lossy(to))));
        }
        let f = frame(0x27c3, body);
        for q in self.players.values().filter(|q| q.h.id != 0 && q.h.id != p.h.id) {
            let hear = match channel {
                2000 => q.h.map == p.h.map && q.seen.contains(&p.h.id),
                2001 => q.h.name.as_bytes() == to,
                2003 => false,
                2004 => p.h.guild != 0 && q.h.guild == p.h.guild,
                _ => true,
            };
            if hear {
                let _ = q.tx.send(f.clone());
            }
        }
    }
}
