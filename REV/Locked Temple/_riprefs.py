from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.x86 import *
import struct
p=r"c:\Kalishared\ctf\rev locked temple\locked_temple"
with open(p,'rb') as f:
    e=ELFFile(f)
    text=e.get_section_by_name('.text')
    code=text.data(); base=text['sh_addr']
    data_sec=e.get_section_by_name('.data'); data=data_sec.data(); dbase=data_sec['sh_addr']
    md=Cs(CS_ARCH_X86, CS_MODE_64); md.detail=True
    seen=set()
    for ins in md.disasm(code, base):
        for op in ins.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=ins.address+ins.size+op.mem.disp
                if 0x4000<=tgt<0x4080 and tgt not in seen:
                    seen.add(tgt)
                    off=tgt-dbase
                    chunk=data[max(0,off-8):min(len(data),off+16)]
                    hexs=' '.join(f'{b:02x}' for b in chunk)
                    print(f"{ins.address:04x}: {ins.mnemonic} {ins.op_str} -> {tgt:#x} off {off:#x} bytes[{len(chunk)}]={hexs}")
