'use strict';

// ============================================================
// Gaucho Packet Sniffer - Frida Hook Script
// Target: com.Tq.CQ2ClientAndroid (libCQ2ClientEn.so armeabi-v7a)
// ============================================================

const LIB_NAME = "libCQ2ClientEn.so";

// Offsets from libCQ2ClientEn.so base (Thumb functions -> add +1)
const ADDRS = {
    ProcessNetMsg:    0xf82753,  // _ZN7CNetMsg13ProcessNetMsgEPS_Pcj
    DoSendMsg:        0x1628169, // _ZN15CMyClientSocket9DoSendMsgEP6CMyMsg
    SendMsg:          0xee50a9,  // _ZN10CMyNetwork7SendMsgEP7CNetMsg
    CAST_cfb64:       0x1733d6c, // CAST_cfb64_encrypt
    GetType:          0x16274f5, // _ZN6CMyMsg7GetTypeEPcj
    GetSize:          0x16274f1, // _ZN6CMyMsg7GetSizeEPcj
    CreateNetMsg:     0xf82781,  // _ZN7CNetMsg12CreateNetMsgEiPcj
};

let PACKET_NAMES = {};
let packetCount = 0;
let logEnabled = true;

function toHex(n, width) {
    return '0x' + n.toString(16).toUpperCase().padStart(width || 4, '0');
}

function getPacketName(typeId) {
    return PACKET_NAMES[typeId] || ('Unknown_' + toHex(typeId));
}

function findLibBase() {
    // 1. Try Process.findModuleByName
    const m = Process.findModuleByName(LIB_NAME);
    if (m) return m.base;

    // 2. Read /proc/self/maps (for translated ARM libraries in x86 LDPlayer)
    try {
        const maps = File.readAllText('/proc/self/maps');
        for (const line of maps.split('\n')) {
            if (line.indexOf(LIB_NAME) !== -1) {
                const parts = line.split(' ');
                const range = parts[0].split('-');
                return ptr('0x' + range[0]);
            }
        }
    } catch (e) {
        console.error('[-] Error reading /proc/self/maps: ' + e.message);
    }
    return null;
}

function logPacket(dir, typeId, size, bufPtr) {
    if (!logEnabled) return;
    packetCount++;
    const name = getPacketName(typeId);

    const payload = {
        seq:  packetCount,
        dir:  dir,
        type: typeId,
        name: name,
        size: size,
        ts:   Date.now()
    };

    try {
        if (bufPtr && !bufPtr.isNull() && size > 0 && size <= 8192) {
            const maxBytes = Math.min(size, 1024);
            const rawBytes = bufPtr.readByteArray(maxBytes);
            if (rawBytes) {
                payload.bytes = Array.from(new Uint8Array(rawBytes));
            }
        }
    } catch (e) {}

    send(payload);
}

function installHooks(base) {
    console.log('[+] Hooking libCQ2ClientEn.so at base: ' + base);

    // ----------------------------------------------------------
    // HOOK 1: ProcessNetMsg — Inbound Server -> Client (Decrypted)
    // Signature: ProcessNetMsg(CNetMsg* self, char* buf, uint size)
    // args[1] = char* buf (format: [u16 len][u16 type][payload...])
    // ----------------------------------------------------------
    try {
        const addr = base.add(ADDRS.ProcessNetMsg | 1);
        Interceptor.attach(addr, {
            onEnter(args) {
                try {
                    const buf = args[1];
                    const size = args[2].toUInt32();
                    if (size < 4 || size > 65536) return;

                    const len = buf.readU16();
                    const type = buf.add(2).readU16();
                    logPacket('S2C', type, size, buf);
                } catch (e) {}
            }
        });
        console.log('[+] Hooked ProcessNetMsg (S2C)');
    } catch (e) {
        console.error('[-] ProcessNetMsg hook error: ' + e.message);
    }

    // ----------------------------------------------------------
    // HOOK 2: DoSendMsg — Outbound Client -> Server
    // Signature: CMyClientSocket::DoSendMsg(CMyMsg* msg)
    // args[1] = CMyMsg*
    // ----------------------------------------------------------
    try {
        const addr = base.add(ADDRS.DoSendMsg | 1);
        Interceptor.attach(addr, {
            onEnter(args) {
                try {
                    const msgPtr = args[1];
                    if (!msgPtr || msgPtr.isNull()) return;

                    // Test direct packet layout
                    let size = msgPtr.readU16();
                    let type = msgPtr.add(2).readU16();
                    if (size >= 4 && size <= 8192 && type > 0 && type < 0xFFFF) {
                        logPacket('C2S', type, size, msgPtr);
                        return;
                    }

                    // Test buffer pointer at offset 0 / 4 / 8
                    for (const off of [0, 4, 8, 12]) {
                        try {
                            const buf = msgPtr.add(off).readPointer();
                            if (buf && !buf.isNull()) {
                                size = buf.readU16();
                                type = buf.add(2).readU16();
                                if (size >= 4 && size <= 8192 && type > 0 && type < 0xFFFF) {
                                    logPacket('C2S', type, size, buf);
                                    return;
                                }
                            }
                        } catch (_) {}
                    }
                } catch (e) {}
            }
        });
        console.log('[+] Hooked DoSendMsg (C2S)');
    } catch (e) {
        console.error('[-] DoSendMsg hook error: ' + e.message);
    }

    // ----------------------------------------------------------
    // HOOK 3: SendMsg — Alternative Outbound Client -> Server
    // Signature: CMyNetwork::SendMsg(CNetMsg* msg)
    // ----------------------------------------------------------
    try {
        const addr = base.add(ADDRS.SendMsg | 1);
        Interceptor.attach(addr, {
            onEnter(args) {
                try {
                    const netMsg = args[1];
                    if (!netMsg || netMsg.isNull()) return;
                    for (const off of [4, 8, 0, 12]) {
                        try {
                            const buf = netMsg.add(off).readPointer();
                            if (buf && !buf.isNull()) {
                                const size = buf.readU16();
                                const type = buf.add(2).readU16();
                                if (size >= 4 && size <= 8192 && type > 0 && type < 0xFFFF) {
                                    logPacket('C2S_net', type, size, buf);
                                    return;
                                }
                            }
                        } catch (_) {}
                    }
                } catch (e) {}
            }
        });
        console.log('[+] Hooked SendMsg (C2S alt)');
    } catch (e) {}

    console.log('[*] Sniffer initialized successfully!');
}

rpc.exports = {
    setPacketNames(namesObj) {
        PACKET_NAMES = namesObj || {};
        return Object.keys(PACKET_NAMES).length;
    },
    setEnabled(enabled) {
        logEnabled = !!enabled;
    }
};

(function init() {
    const base = findLibBase();
    if (base) {
        installHooks(base);
    } else {
        console.error('[-] Could not find base address of ' + LIB_NAME);
    }
})();
