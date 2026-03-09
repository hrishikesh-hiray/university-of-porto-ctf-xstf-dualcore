# emulate validator at 0x1c40 after init-deobfuscation
key = [0x71,0x22,0x90,0x11,0x63,0x74,0x81,0x52]
# apply first deobf loop (xor with 0,5,10,...)
for i in range(8):
    key[i] ^= (i*5) & 0xff
print('decoded key:', [hex(x) for x in key])

def rol8(v,n):
    n%=8
    return ((v<<n)|(v>>(8-n))) & 0xff

def check(inp):
    esi=0x0b
    rdx=1
    ecx=0
    eax=key[0]
    eax ^= 0x55
    while True:
        ecx=inp[rdx-1]
        if (eax & 3) != ecx:
            return False
        if rdx==8:
            return True
        eax=esi
        eax ^= 0x55
        eax ^= key[rdx]
        if ecx & 1:
            eax = rol8(eax,4)
        rdx += 1
        esi += 0x0b

sol=[]
for n in range(4**8):
    x=n
    inp=[0]*8
    for i in range(8):
        inp[i]=x&3
        x >>=2
    if check(inp):
        sol.append(inp)
print('solutions',len(sol))
for s in sol[:30]:
    print(''.join(str(d) for d in s))
