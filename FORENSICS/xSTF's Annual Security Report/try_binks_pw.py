from pypdf import PdfReader
base=['binks','Binks','jarjar','JarJar','jarjarbinks','JarJarBinks','darthjarjar','DarthJarJar','xSTF','xstf','security','report','appendix','internal','confidential']
subs={
'a':['a','@','4'],
'i':['i','1','!'],
's':['s','$','5'],
'o':['o','0'],
'e':['e','3'],
'b':['b','8']
}

def variants(word):
    out={word}
    for idx,ch in enumerate(word):
        if ch.lower() in subs:
            cur=list(out)
            for w in cur:
                for rep in subs[ch.lower()]:
                    nw=w[:idx]+(rep.upper() if ch.isupper() else rep)+w[idx+1:]
                    out.add(nw)
    return out

cands=set(['1234','12345','123456','password','Password'])
for w in base:
    vs=variants(w)
    for v in vs:
        cands.add(v)
        cands.add(v+'!'); cands.add(v+'@123'); cands.add(v+'123'); cands.add(v+'2025'); cands.add(v+'2026')
        cands.add(v+'_2025'); cands.add(v+'-2025'); cands.add(v+'.2025')
        cands.add('2025'+v); cands.add('2026'+v)
for a in ['binks','jarjar','xSTF','security','report','appendix','internal']:
    for b in ['2025','2026','123','1234','!','@123']:
        cands.add(a+b); cands.add(a.capitalize()+b); cands.add(a.upper()+b)

print('trying',len(cands))
for p in cands:
    rr=PdfReader('appendix.pdf')
    try: ok=rr.decrypt(p)
    except Exception: ok=0
    if ok:
        print('PASS',repr(p),'->',ok)
        txt='\n'.join((pg.extract_text() or '') for pg in rr.pages)
        print(txt[:5000])
        open('appendix_text.txt','w',encoding='utf-8').write(txt)
        break
else:
    print('no hit')
