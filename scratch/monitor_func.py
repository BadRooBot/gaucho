import frida
import sys
import time

js_code = """
var mod = Process.findModuleByName("libCQ2ClientEn.so");
if (mod) {
    var lib = mod.base;
    console.log("[+] libCQ2ClientEn.so base: " + lib);

    var SetInitStatus_addr = lib.add(0x15a3c20);
    var ProcessFuncStatus_addr = lib.add(0x15a3614);
    var ProcessFuncButton_addr = lib.add(0x15a2e98);
    var SetFunctionFlag_addr = lib.add(0x15a3bc4);
    
    // CNewFunctionOpenMgr::Instance()
    var Instance_addr = lib.add(0xcfd3cc);
    var Instance = new NativeFunction(Instance_addr, 'pointer', []);
    
    rpc.exports = {
        checkState: function() {
            var mgr = Instance();
            var initStatus = mgr.add(0x18).readU8();
            var flagLow = mgr.add(0x8).readU32();
            var flagHigh = mgr.add(0xc).readU32();
            return {
                mgr: mgr.toString(),
                initStatus: initStatus,
                flagLow: flagLow.toString(16),
                flagHigh: flagHigh.toString(16)
            };
        },
        forceInit: function() {
            var mgr = Instance();
            var SetInit = new NativeFunction(SetInitStatus_addr, 'void', ['pointer', 'bool']);
            SetInit(mgr, 1);
            return "SetInitStatus(1) forced!";
        },
        openWindow: function(dlgId, childId) {
            var OpenWin_addr = lib.add(0x13aa5cc);
            var OpenWin = new NativeFunction(OpenWin_addr, 'void', ['int', 'int']);
            OpenWin(dlgId, childId);
            return "OpenWindow(" + dlgId + ", " + childId + ") called!";
        }
    };
}
"""

device = frida.get_usb_device()
pid = device.get_process("Gaucho").pid
session = device.attach(pid)
script = session.create_script(js_code)

def on_message(message, data):
    if message['type'] == 'send':
        print("[*]", message['payload'])
    elif message['type'] == 'error':
        print("[!]", message['stack'])

script.on('message', on_message)
script.load()

print("[+] Script loaded successfully!")
state = script.exports_sync.check_state()
print("[+] Current CNewFunctionOpenMgr State:", state)

session.detach()
