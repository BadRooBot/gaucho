import frida, sys

device = frida.get_usb_device()
session = device.attach(23861)

js_code = """
var mod = Process.findModuleByName("libCQ2ClientEn.so");
console.log("libCQ2ClientEn.so base:", mod.base);

var innerPtrAddr = mod.base.add(0x02e99894);
var mgrPtr = innerPtrAddr.readPointer();
console.log("CNewFunctionOpenMgr instance:", mgrPtr);

if (!mgrPtr.isNull()) {
    var initStatus = mgrPtr.add(0x18).readU8();
    var flag = mgrPtr.add(0x8).readU64();
    console.log("Current initStatus:", initStatus, "flag:", flag.toString(16));
    
    // Call SetInitStatus(true)
    var setInitStatus = new NativeFunction(mod.base.add(0x015a3c20).or(1), 'void', ['pointer', 'bool']);
    console.log("Calling SetInitStatus(true)...");
    setInitStatus(mgrPtr, 1);
    
    var newInitStatus = mgrPtr.add(0x18).readU8();
    console.log("New initStatus:", newInitStatus);
    
    // Refresh GUI 1809
    var postCmd = new NativeFunction(mod.base.add(0xce7ad8), 'void', ['int', 'int']);
    postCmd(0xcf0, 0x711);
    postCmd(0xcf0, 0x714);
    console.log("Posted 0xcf0, 0x711 and 0x714");
}
"""

script = session.create_script(js_code)
def on_message(message, data):
    print("Frida msg:", message)
script.on('message', on_message)
script.load()
