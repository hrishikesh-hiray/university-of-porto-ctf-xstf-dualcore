from elftools.elf.elffile import ELFFile
p=r"c:\Kalishared\ctf\rev locked temple\locked_temple"
with open(p,'rb') as f:
    e=ELFFile(f)
    d=e.get_section_by_name('.data')
    b=d.data(); base=d['sh_addr']
    for i in range(0,len(b),16):
        chunk=b[i:i+16]
        hx=' '.join(f'{x:02x}' for x in chunk)
        print(f"{base+i:04x}: {hx}")
