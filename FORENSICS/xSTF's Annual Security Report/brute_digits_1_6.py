import re,struct,hashlib,time,itertools,string
from Crypto.Cipher import ARC4
PADDING = bytes([0x28,0xBF,0x4E,0x5E,0x4E,0x75,0x8A,0x41,0x64,0x00,0x4E,0x56,0xFF,0xFA,0x01,0x08,0x2E,0x2E,0x00,0xB6,0xD0,0x68,0x3E,0x80,0x2F,0x0C,0xA9,0xFE,0x64,0x53,0x69,0x7A])
def parse(path):
 b=open(path,'rb').read(); enc=int(re.search(rb'/Encrypt\s+(\d+)\s+0\s+R',b).group(1)); id0=bytes.fromhex(re.search(rb'/ID\s*\[\s*<([0-9A-Fa-f]+)>',b).group(1).decode()); d=re.search(rb'\n'+str(enc).encode()+rb'\s+0\s+obj\s*<<(.*?)>>',b,re.S).group(1); U=bytes.fromhex(re.search(rb'/U<([0-9A-Fa-f]+)>',d).group(1).decode()); O=bytes.fromhex(re.search(rb'/O<([0-9A-Fa-f]+)>',d).group(1).decode()); P=int(re.search(rb'/P\s*(-?\d+)',d).group(1)); return O,U,struct.pack('<i',P),id0
O,U,Pb,id0=parse('appendix.pdf')
def ok(pw):
 pad=(pw.encode('latin-1','ignore')[:32]+PADDING)[:32]; m=hashlib.md5(pad+O+Pb+id0).digest();
 for _ in range(50): m=hashlib.md5(m[:16]).digest(); key=m[:16]; data=hashlib.md5(PADDING+id0).digest();
 for i in range(20): data=ARC4.new(bytes((k^i) for k in key)).encrypt(data)
 return data[:16]==U[:16]
chars=string.digits
start=time.time(); n=0
for L in range(1,7):
 for tup in itertools.product(chars, repeat=L):
  pw=''.join(tup); n+=1
  if ok(pw): print('FOUND',pw,'tested',n,'elapsed',time.time()-start); raise SystemExit
 print('completed length',L,'tested',n,'elapsed',time.time()-start)
print('not found tested',n,'elapsed',time.time()-start)
