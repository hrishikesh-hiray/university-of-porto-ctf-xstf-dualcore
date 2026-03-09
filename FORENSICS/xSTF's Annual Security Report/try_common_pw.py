from pypdf import PdfReader
base=[
'1234','12345','123456','12345678','123456789','password','Password','password123','admin','letmein','qwerty','qwerty123',
'binks','Binks','binkS','jarjar','jarjarbinks','JarJarBinks','jarjar123','binks123','binks@123','Binks@123',
'xstf','xSTF','xstf2025','xSTF2025','security','Security','report','Report','internal','Internal','confidential','Confidential',
'appendix','Appendix','annual','Annual','securityreport','SecurityReport','legacy','Legacy','archived','Archive',
'2025','20251230','30-12-2025','30/12/2025','2026','20260130','upctf','upCTF','upCTF2025','upCTF{'
]
# add simple suffix/prefix variants
cands=set(base)
for w in list(base):
    for s in ['!','@','#','$','123','2025','2026']:
        cands.add(w+s)
        cands.add(s+w)
for p in cands:
    rr=PdfReader('appendix.pdf')
    try:
        ok=rr.decrypt(p)
    except Exception:
        ok=0
    if ok:
        print('PASS',repr(p),'->',ok)
        txt='\n'.join((pg.extract_text() or '') for pg in rr.pages)
        print(txt[:4000])
        open('appendix_text.txt','w',encoding='utf-8').write(txt)
        raise SystemExit
print('not found',len(cands))
