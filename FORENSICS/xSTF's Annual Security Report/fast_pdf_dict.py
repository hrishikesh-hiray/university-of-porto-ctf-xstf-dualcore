import re,struct,hashlib,time
from Crypto.Cipher import ARC4

PADDING = bytes([0x28,0xBF,0x4E,0x5E,0x4E,0x75,0x8A,0x41,0x64,0x00,0x4E,0x56,0xFF,0xFA,0x01,0x08,0x2E,0x2E,0x00,0xB6,0xD0,0x68,0x3E,0x80,0x2F,0x0C,0xA9,0xFE,0x64,0x53,0x69,0x7A])

def parse_pdf_params(path):
    b=open(path,'rb').read()
    m=re.search(rb'/Encrypt\s+(\d+)\s+0\s+R', b)
    enc_obj=int(m.group(1))
    m=re.search(rb'/ID\s*\[\s*<([0-9A-Fa-f]+)>', b)
    id0=bytes.fromhex(m.group(1).decode())
    m=re.search(rb'\n'+str(enc_obj).encode()+rb'\s+0\s+obj\s*<<(.*?)>>', b, re.S)
    d=m.group(1)
    U=bytes.fromhex(re.search(rb'/U<([0-9A-Fa-f]+)>', d).group(1).decode())
    O=bytes.fromhex(re.search(rb'/O<([0-9A-Fa-f]+)>', d).group(1).decode())
    P=int(re.search(rb'/P\s*(-?\d+)', d).group(1))
    return O,U,P,id0

O,U,P,id0=parse_pdf_params('appendix.pdf')
Pbytes=struct.pack('<i',P)

def is_user_password(pw:str)->bool:
    pwb=pw.encode('latin-1','ignore')[:32]
    pad=(pwb+PADDING)[:32]
    m=hashlib.md5(pad+O+Pbytes+id0).digest()
    for _ in range(50):
        m=hashlib.md5(m[:16]).digest()
    key=m[:16]
    val=hashlib.md5(PADDING+id0).digest()
    data=val
    for i in range(20):
        k=bytes((kb ^ i) for kb in key)
        data=ARC4.new(k).encrypt(data)
    return data[:16]==U[:16]

start=time.time(); n=0
for line in open('10k-most-common.txt',encoding='utf-8',errors='ignore'):
    pw=line.strip('\r\n')
    if not pw:
        continue
    n+=1
    if is_user_password(pw):
        print('FOUND',pw,'at',n)
        break
else:
    print('no hit in',n,'elapsed',time.time()-start)
