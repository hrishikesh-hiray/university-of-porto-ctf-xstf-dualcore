from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.x86 import *
p=r"c:\Kalishared\ctf\rev locked temple\locked_temple"
with open(p,'rb') as f:
    e=ELFFile(f)
    text=e.get_section_by_name('.text')
    code=text.data(); base=text['sh_addr']
    # map plt targets
    rel=e.get_section_by_name('.rela.plt'); dynsym=e.get_section(rel['sh_link']); plt=e.get_section_by_name('.plt.sec')
    plt_map={plt['sh_addr']+i*0x10:dynsym.get_symbol(r['r_info_sym']).name for i,r in enumerate(rel.iter_relocations())}
    md=Cs(CS_ARCH_X86, CS_MODE_64); md.detail=True
    for ins in md.disasm(code, base):
        line=f"{ins.address:04x}: {ins.mnemonic:6s} {ins.op_str}"
        if ins.mnemonic=='call' and ins.operands and ins.operands[0].type==X86_OP_IMM:
            tgt=ins.operands[0].imm
            if tgt in plt_map:
                line += f"    ; {plt_map[tgt]}"
            else:
                line += f"    ; {tgt:#x}"
        print(line)
