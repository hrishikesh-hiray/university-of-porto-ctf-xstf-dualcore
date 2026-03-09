import re
b=open('appendix.pdf','rb').read()
for n in [18,19]:
    m=re.search(rb'\n'+str(n).encode()+rb'\s+0\s+obj\b', b)
    if not m:
        print('obj',n,'not found'); continue
    s=m.start()+1
    e=b.find(b'endobj', s)
    obj=b[s:e+6]
    print('\n===',n,'===')
    print(obj.decode('latin1','replace'))
