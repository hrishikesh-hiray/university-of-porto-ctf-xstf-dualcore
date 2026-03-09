from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

TARGETS = [
    "main",
    "menu_loop",
    "manage_allocation",
    "write_operation",
    "read_operation",
    "read_flag",
    "is_valid_index",
    "is_valid_chunk_size",
    "clear_memory",
]

with open("overlap", "rb") as f:
    elf = ELFFile(f)
    symtab = elf.get_section_by_name(".symtab")
    text = elf.get_section_by_name(".text")
    text_data = text.data()
    text_addr = text["sh_addr"]

    symbols = {}
    for sym in symtab.iter_symbols():
        name = sym.name
        if name in TARGETS or name in ("ptr_table", "ptr_size_table", "counter"):
            symbols[name] = sym

    print("[symbols]")
    for name in TARGETS + ["ptr_table", "ptr_size_table", "counter"]:
        sym = symbols.get(name)
        if sym is not None:
            print(f"{name}: addr=0x{sym['st_value']:x} size=0x{sym['st_size']:x}")

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = False

    print("\n[disassembly]")
    for name in TARGETS:
        sym = symbols.get(name)
        if sym is None:
            continue
        start = sym["st_value"]
        size = sym["st_size"]
        if size == 0:
            continue
        off = start - text_addr
        code = text_data[off : off + size]
        print(f"\n== {name} @ 0x{start:x} size 0x{size:x} ==")
        for ins in md.disasm(code, start):
            print(f"0x{ins.address:04x}:\t{ins.mnemonic}\t{ins.op_str}")
