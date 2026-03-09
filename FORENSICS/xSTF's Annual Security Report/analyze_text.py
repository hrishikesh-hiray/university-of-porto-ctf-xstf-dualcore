import re
txt=open('report_text.txt',encoding='utf-8').read()
lines=[l.strip() for l in txt.splitlines() if l.strip()]
print('LINES')
for l in lines:
    print('-',l)
print('\nSection initials:', ''.join(l[0] for l in lines if re.match(r'^[0-9]+\.',l)))
# sentence initials
sents=re.split(r'(?<=[.!?])\s+', txt.replace('\n',' '))
sents=[s.strip() for s in sents if s.strip()]
print('Sentence-initial acrostic:', ''.join(s[0] for s in sents)[:200])
# title words acrostic
title=' '.join(lines[:3])
print('Top acrostic:', ''.join(w[0] for w in re.findall(r'[A-Za-z]+',title)))
