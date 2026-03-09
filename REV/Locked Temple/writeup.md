# Locked Temple (500) - Reverse Engineering Writeup

## Challenge

- Name: `Locked Temple`
- Category: Reverse
- Author: `slyfenon`
- Prompt: Find the correct 8-step pressure plate sequence over plate IDs:

```text
0  1
2  3
```

- Flag format:

```text
upCTF{PlateOrder_SECRETDIGIT}
```

## Goal

Recover:

1. The exact 8-plate order (`PlateOrder`)
2. The trailing `SECRETDIGIT`

without relying on a Linux GUI runtime.

## Files

Workspace contained a single ELF binary:

- `locked_temple` (ELF64, Linux)

## Environment Notes

Host was Windows, binary was Linux ELF. Instead of executing the SDL app, I solved it statically.

Python tools used:

- `pyelftools`
- `capstone`

Install command:

```powershell
pip install pyelftools capstone
```

## Step 1 - Identify Binary Type and High-Level Structure

Magic bytes:

```text
7F 45 4C 46
```

Section summary (important parts):

- `.text` at `0x11e0` (program logic)
- `.data` at `0x4000` (encoded constants/state)
- `.rodata` minimal (only window title `Locked Temple`)

This immediately suggests key values are not in plain strings.

## Step 2 - Disassemble `.text` and Locate Input/Validation Logic

Main loop behavior (from disassembly):

- SDL event loop reads keyboard input (`W/A/S/D`) and updates cursor position.
- Cursor is matched against 4 allowed plate coordinates stored in `.data`.
- Matching plate ID is pushed into a sequence buffer via function at `0x1c40`.
- Once 8 entries are collected, validator runs inside `0x1c40`.

Important functions:

- `0x1bc0`: startup deobfuscation/init
- `0x1c40`: sequence append + 8-byte validator
- `0x1ce0`: returns solved flag (`state+0xC`)
- `0x1b40`: draw special success glyph (used after solved state)

## Step 3 - Decode `.data` Contents

Raw `.data` dump around interesting region:

```text
4010: 12 13 14 15 16 17 18 19
4018: 72 23 91 12 64 75 82 53
4020: 71 22 90 11 63 74 81 52
4040: 03 00 00 00 09 00 00 00
4060: 02 00 00 00 01 00 00 00
4068: 07 00 00 00 01 00 00 00
4070: 02 00 00 00 06 00 00 00
4078: 07 00 00 00 06 00 00 00
```

`0x1bc0` deobfuscates arrays in-place:

1. XOR 8 bytes at `0x4020` with sequence `0,5,10,...,35`
2. XOR 8 bytes at `0x4018` with sequence `0,8,16,...,56`
3. XOR 8 bytes at `0x4010` with sequence `0,10,20,...,70`

The validator in `0x1c40` uses the first decoded array (from `0x4020`).

## Step 4 - Reconstruct Validator Algorithm

Core logic in `0x1c40` after 8 inputs collected:

- Inputs are stored as 8 bytes of values in `{0,1,2,3}`.
- It computes expected values using decoded key bytes and rolling transformations.
- For each position `i`, it compares:

```text
input[i] == (computed_byte & 0x3)
```

- Any mismatch resets sequence buffer.
- Full match sets solved marker:

```text
[state + 0xC] = 1
```

### Python Reproduction Script

```python
key = [0x71,0x22,0x90,0x11,0x63,0x74,0x81,0x52]
for i in range(8):
    key[i] ^= (i * 5) & 0xff

# key => [0x71, 0x27, 0x9a, 0x1e, 0x77, 0x6d, 0x9f, 0x71]

def rol8(v, n):
    n %= 8
    return ((v << n) | (v >> (8 - n))) & 0xff

def check(inp):
    esi = 0x0b
    rdx = 1
    eax = key[0] ^ 0x55
    while True:
        ecx = inp[rdx - 1]
        if (eax & 3) != ecx:
            return False
        if rdx == 8:
            return True
        eax = esi ^ 0x55
        eax ^= key[rdx]
        if ecx & 1:
            eax = rol8(eax, 4)
        rdx += 1
        esi += 0x0b

sol = []
for n in range(4**8):
    x = n
    inp = [0] * 8
    for i in range(8):
        inp[i] = x & 3
        x >>= 2
    if check(inp):
        sol.append(''.join(map(str, inp)))

print(sol)
```

Output:

```text
['01122301']
```

Unique valid plate order:

```text
01122301
```

## Step 5 - Determine `SECRETDIGIT`

`[state+0xC]=1` only indicates solved status, but challenge asks for a `SECRETDIGIT` in the flag.

After solved state is true, main loop calls function `0x1b40` which draws a specific golden glyph using 3 line segments:

1. Top horizontal line
2. Upper-right vertical line
3. Lower-right vertical line

This is the canonical 7-segment-style shape for digit:

```text
7
```

So `SECRETDIGIT = 7`.

## Final Flag

```text
upCTF{01122301_7}
```

## Quick Submission Note

If your platform rejects once, verify:

- Exact case: `upCTF`
- No spaces
- Exactly 8 digits in plate order
- Underscore before digit

Canonical solved value from static reversing is:

```text
upCTF{01122301_7}
```
