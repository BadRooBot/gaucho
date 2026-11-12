import capstone

with open('work_mod/base_decoded/lib/armeabi-v7a/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

def disas(addr, size, name):
    print(f"=== {name} (0x{addr:08x}, sz {size}) ===")
    code = data[addr : addr + size]
    for ins in md.disasm(code, addr):
        print(f"0x{ins.address:08x}:  {ins.mnemonic:8s} {ins.op_str}")
    print()

disas(0x015a3bc4, 92, "CNewFunctionOpenMgr::SetFunctionFlag")
disas(0x015a3c20, 112, "CNewFunctionOpenMgr::SetInitStatus")
disas(0x015a35bc, 88, "CNewFunctionOpenMgr::IsFunctionStatus(int, int, bool)")
disas(0x015a3614, 250, "CNewFunctionOpenMgr::ProcessFuncStatus (start)")

