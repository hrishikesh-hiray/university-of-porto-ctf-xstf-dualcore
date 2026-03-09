import re
b=open('appendix.pdf','rb').read()
for pat in [rb'trailer', rb'/Encrypt', rb'/ID', rb'/Info', rb'startxref']:
    i=b.find(pat)
    print(pat, i)
print('--- snippets ---')
for m in re.finditer(rb'/Encrypt\s+(\d+)\s+(\d+)\s+R', b):
    print('Encrypt ref', m.group(1), m.group(2), 'at', m.start())
    print(b[m.start()-80:m.start()+120])
for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\s*<<[^>]*?/Filter/Standard[^>]*?>>', b, flags=re.S):
    print('possible encrypt obj', m.group(1), m.start())
    print(b[m.start():m.start()+400])
