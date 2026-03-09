from pypdf import PdfReader
r = PdfReader('appendix.pdf')
print('encrypted', r.is_encrypted)
cands = ['', 'appendix', 'Appendix', 'Binks', 'binks', 'xSTF', 'xstf', '2025', '2025-Security-Report', 'security', 'report', 'confidential', 'internal', 'xSTF2025', 'binks2025']
found = False
for p in cands:
    rr = PdfReader('appendix.pdf')
    try:
        ok = rr.decrypt(p)
    except Exception:
        ok = 0
    if ok:
        print('PASS', repr(p), '->', ok)
        txt = '\n'.join((pg.extract_text() or '') for pg in rr.pages)
        print(txt[:4000])
        open('appendix_text.txt', 'w', encoding='utf-8').write(txt)
        found = True
        break
if not found:
    print('no candidate matched')
