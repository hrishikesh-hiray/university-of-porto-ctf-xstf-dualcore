from elftools.elf.elffile import ELFFile
import struct
p=r"c:\Kalishared\ctf\rev locked temple\locked_temple"
with open(p,'rb') as f:
    e=ELFFile(f)
    print('entry',hex(e.header['e_entry']))
    for name in ['.text','.rodata','.data','.bss','.dynsym','.symtab']:
        s=e.get_section_by_name(name)
        if s:
            print(name,hex(s['sh_addr']),s['sh_size'])
    r=e.get_section_by_name('.rodata')
    d=r.data()
    print('rodata first 256 hex:')
    print(d[:256].hex())
    out=[]
    cur=[]
    base=r['sh_addr']
    for i,b in enumerate(d):
        if 32<=b<=126:
            cur.append((i,b))
        else:
            if len(cur)>=4:
                s=''.join(chr(x[1]) for x in cur)
                out.append((base+cur[0][0],s))
            cur=[]
    if len(cur)>=4:
        s=''.join(chr(x[1]) for x in cur)
        out.append((base+cur[0][0],s))
    print('strings in rodata:')
    for a,s in out[:100]:
        print(hex(a),s)
    print('small dwords in rodata (0..10), first 80 hits:')
    c=0
    for i in range(0,len(d)-4,4):
        v=struct.unpack_from('<I',d,i)[0]
        if v<=10:
            print(hex(base+i),v)
            c+=1
            if c>=80: break
