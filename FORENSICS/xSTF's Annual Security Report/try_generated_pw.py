import itertools,re,time
from pypdf import PdfReader
text=open('report_text.txt',encoding='utf-8').read().lower()
words=sorted(set(re.findall(r"[a-zA-Z]{3,}",text)))
core=[w for w in words if w not in {'the','and','for','was','with','this','that','were','from','not','only','all','use','made','into','still','live','none'}]
seeds=set(core)
seeds.update(['xstf','binks','appendix','security','report','internal','confidential','legacy','archived','password','policies','document','documents'])
years=['2025','2026','2024','123','1234','12345','01','30','0130','1230']
syms=['','!','@','#','$','*','_','-','.']
cands=set(['','1234','12345','123456','password','qwerty'])
for w in seeds:
    cands.add(w)
    cands.add(w.capitalize())
    cands.add(w.upper())
    for y in years:
        cands.add(w+y); cands.add(w.capitalize()+y); cands.add(w+y+'!'); cands.add(w+'_'+y)
    for s in ['!','@','#','$','123','2025']:
        cands.add(w+s); cands.add(s+w)
# pair combos for short important words
short=[w for w in seeds if len(w)<=10]
for a in short:
    for b in ['xstf','security','report','internal','binks','appendix']:
        cands.add(a+b); cands.add(a+'_'+b); cands.add(a+'-'+b)
        cands.add((a+b).capitalize())
# length constraints typical
cands={p for p in cands if 1<=len(p)<=24}
print('candidates',len(cands))
start=time.time(); tried=0
for p in cands:
    rr=PdfReader('appendix.pdf')
    try: ok=rr.decrypt(p)
    except Exception: ok=0
    tried+=1
    if ok:
        print('PASS',repr(p),'ok',ok,'tried',tried,'time',time.time()-start)
        txt='\n'.join((pg.extract_text() or '') for pg in rr.pages)
        print(txt[:5000])
        open('appendix_text.txt','w',encoding='utf-8').write(txt)
        break
else:
    print('no hit after',tried,'time',time.time()-start)
