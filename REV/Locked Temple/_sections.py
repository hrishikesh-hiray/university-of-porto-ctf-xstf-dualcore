from elftools.elf.elffile import ELFFile
p=r"c:\Kalishared\ctf\rev locked temple\locked_temple"
with open(p,'rb') as f:
    e=ELFFile(f)
    for i,s in enumerate(e.iter_sections()):
        print(f"{i:2d} {s.name:20s} addr={s['sh_addr']:#x} size={s['sh_size']} off={s['sh_offset']:#x}")
