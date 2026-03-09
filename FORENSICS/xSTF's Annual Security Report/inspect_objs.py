import re
b=open('2025-Security-Report.pdf','rb').read()
for m in re.finditer(rb'\n(\d+)\s+(\d+)\s+obj\b', b):
    i=m.start()+1
    n=int(m.group(1))
    e=b.find(b'endobj', i)
    if e==-1: continue
    obj=b[i:e+6]
    head=obj[:900]
    txt=''.join(chr(c) if 32<=c<127 or c in (10,13,9) else '.' for c in head)
    if any(k in txt for k in ['/Filespec','EmbeddedFile','appendix','/Names','/Encrypt','/Info','/Metadata','/Title','/Author','/Subject','/Keywords','/Desc']):
        print('\n=== OBJ',n,'===')
        print(txt)
