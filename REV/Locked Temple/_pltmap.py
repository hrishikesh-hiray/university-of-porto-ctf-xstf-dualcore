from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
p=r"c:\Kalishared\ctf\rev locked temple\locked_temple"
with open(p,'rb') as f:
    e=ELFFile(f)
    rel=e.get_section_by_name('.rela.plt')
    dynsym=e.get_section(rel['sh_link'])
    plt=e.get_section_by_name('.plt.sec')
    base=plt['sh_addr']
    print('plt.sec base',hex(base))
    for i,r in enumerate(rel.iter_relocations()):
        sym=dynsym.get_symbol(r['r_info_sym'])
        print(i,hex(base+i*0x10),sym.name,'got',hex(r['r_offset']))
