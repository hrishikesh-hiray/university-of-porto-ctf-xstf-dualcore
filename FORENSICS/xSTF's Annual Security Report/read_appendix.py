from pypdf import PdfReader
pw='Maki'
r=PdfReader('appendix.pdf')
print('encrypted',r.is_encrypted)
ok=r.decrypt(pw)
print('decrypt_result',ok)
text='\n'.join((p.extract_text() or '') for p in r.pages)
print(text)
open('appendix_text.txt','w',encoding='utf-8').write(text)
