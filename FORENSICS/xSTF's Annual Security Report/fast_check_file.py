import re
import struct
import hashlib
import time
import sys
from Crypto.Cipher import ARC4

PADDING = bytes([
    0x28, 0xBF, 0x4E, 0x5E, 0x4E, 0x75, 0x8A, 0x41,
    0x64, 0x00, 0x4E, 0x56, 0xFF, 0xFA, 0x01, 0x08,
    0x2E, 0x2E, 0x00, 0xB6, 0xD0, 0x68, 0x3E, 0x80,
    0x2F, 0x0C, 0xA9, 0xFE, 0x64, 0x53, 0x69, 0x7A,
])

def parse_pdf_params(path: str):
    b = open(path, "rb").read()
    enc = int(re.search(rb"/Encrypt\s+(\d+)\s+0\s+R", b).group(1))
    id0 = bytes.fromhex(re.search(rb"/ID\s*\[\s*<([0-9A-Fa-f]+)>", b).group(1).decode())
    d = re.search(rb"\n" + str(enc).encode() + rb"\s+0\s+obj\s*<<(.*?)>>", b, re.S).group(1)
    u = bytes.fromhex(re.search(rb"/U<([0-9A-Fa-f]+)>", d).group(1).decode())
    o = bytes.fromhex(re.search(rb"/O<([0-9A-Fa-f]+)>", d).group(1).decode())
    p = int(re.search(rb"/P\s*(-?\d+)", d).group(1))
    return o, u, struct.pack("<i", p), id0

def is_user_password(pw: str, o: bytes, u: bytes, pbytes: bytes, id0: bytes) -> bool:
    pwb = pw.encode("latin-1", "ignore")[:32]
    pad = (pwb + PADDING)[:32]
    m = hashlib.md5(pad + o + pbytes + id0).digest()
    for _ in range(50):
        m = hashlib.md5(m[:16]).digest()
    key = m[:16]
    data = hashlib.md5(PADDING + id0).digest()
    for i in range(20):
        k = bytes((kb ^ i) for kb in key)
        data = ARC4.new(k).encrypt(data)
    return data[:16] == u[:16]

def main():
    wordlist = sys.argv[1] if len(sys.argv) > 1 else "10k-most-common.txt"
    o, u, pbytes, id0 = parse_pdf_params("appendix.pdf")
    start = time.time()
    n = 0
    with open(wordlist, encoding="utf-8", errors="ignore") as f:
        for line in f:
            pw = line.rstrip("\r\n")
            if not pw:
                continue
            n += 1
            if is_user_password(pw, o, u, pbytes, id0):
                print(f"FOUND {pw} at {n} elapsed {time.time() - start:.2f}s")
                return
    print(f"no hit {n} elapsed {time.time() - start:.2f}s")

if __name__ == "__main__":
    main()
