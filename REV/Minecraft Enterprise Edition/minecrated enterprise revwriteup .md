# Minecraft Enterprise Edition — CTF Writeup

**CTF:** upCTF  
**Challenge:** Minecraft Enterprise Edition  
**Author:** tiago3monteiro  
**Category:** Reverse Engineering  
**Flag:** `upCTF{m1n3cr4ft_0n_th3_b4nks-xh7IPnEKdff1f41f}`

---

## Challenge Description

> My company recently acquired a limited number of Minecraft Enterprise Edition keys to reward top-performing employees. Sadly, I didn't make the cut. I managed to get my hands on the internal activation program they use to validate these licenses. Will you help me go around management and generate myself a valid key?

We're given a single binary: `minecraft-enterprise`.

---

## Reconnaissance

### File Identification

```
$ file minecraft-enterprise
minecraft-enterprise: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
statically linked, stripped
```

The binary is a **statically linked, stripped** x86-64 ELF. No dynamic imports, no symbol names — everything must be found through static analysis.

### Initial String Extraction

Running `strings` immediately surfaces several key clues:

```
@@IMNOTTHEKEY
Key parsing error.
Invalid Key.
Enter Key (format: XXXXX-XXXXX-XXXXX-XXXXX):
flag.txt
Flag: %s
ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
```

Notable observations:
- The key format is `XXXXX-XXXXX-XXXXX-XXXXX` — four groups of 5, all uppercase alphanumeric.
- The alphabet `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` is **Base32** (RFC 4648).
- `@@IMNOTTHEKEY` — a suspicious string, seemingly a red herring by name, but its placement in `.rodata` next to `IMNOTTHEKEY` is meaningful.
- The binary reads and prints `flag.txt` on success.

### Running the Binary

```
$ echo "AAAAA-BBBBB-CCCCC-DDDDD" | ./minecraft-enterprise
Enter Key (format: XXXXX-XXXXX-XXXXX-XXXXX): Invalid Key.
```

---

## Static Analysis

### Finding the Key Validation Function

Using `objdump`, we traced cross-references from the strings `Invalid Key.` and `Key parsing error.` back through `.rodata` VMA addresses to the call sites in `.text`.

The main validation logic lives around address `0x402cd0` and calls out to two core functions:

| Address   | Role                             |
|-----------|----------------------------------|
| `0x4031d0` | Parse / decode the key string   |
| `0x4030a0` | Validate (compute + compare)    |
| `0x403280` | Fill a 10-byte output buffer    |
| `0x403170` | Byte-swap helper (strcpy-like)  |

### Key Parsing (`0x4031d0`)

This function:
1. Checks the input length is exactly `0x17` (23) characters — four 5-char groups plus three dashes.
2. Iterates over each non-dash character.
3. For each character, checks it is **alphanumeric uppercase** using a `wctype` table.
4. Looks up each character's **Base32 index** via `tolower` + a lookup table, storing the 5-bit value.
5. If all 20 characters decode successfully, it returns 0 (success); otherwise 1 (failure).

The decoded key is stored as 20 bytes in a local buffer (one decoded Base32 value per byte).

### PRNG / Checksum Seed (`0x402d87`)

After parsing, the main function sets a seed of `0x12345678` and runs a short loop (64 iterations) that performs:

```
for i in range(64):
    val = rol(val, i & 7) ^ val
    val = (lookup[val >> (i & 7)] + val) & 0xffffffff
```

This uses the AES S-box table at `0x7e24c0` as a lookup. The result is a 32-bit checksum derived purely from the constant seed — it does **not** depend on the user's input at this stage. The resulting value is passed into `0x403280`.

### Output Buffer Fill (`0x403280`)

Function `0x403280` is called with the checksum value and pointer to the 10-byte output buffer. It uses `strtol`-like integer parsing to write a 10-character decimal representation — effectively a fixed, deterministic 10-byte string that serves as a sub-key seed.

### Core Validation (`0x4030a0`)

This is the heart of the challenge. It:

1. Calls `0x4037a0` to obtain a pointer to an **EVP_MD structure** (NID `0x2a0` = `SHA-256` in OpenSSL).
2. Calls into OpenSSL's `EVP_DigestSign` / HMAC machinery (traced through the static libc).
3. Constructs the HMAC message **DATA** from the decoded key bytes `K[10..19]` (groups 3 and 4) with an adjacent-pair byte swap:

```python
DATA = bytes([K[11], K[10], K[13], K[12], K[15], K[14],
              K[17], K[16], K[19], K[18]])
```

4. Computes:

```python
digest = HMAC-SHA256(key=b"IMNOTTHEKEY", msg=DATA)
```

The HMAC key is the string `IMNOTTHEKEY` — found adjacent to the `@@` sentinel in `.rodata` at VMA `0x7c0030`.

5. Takes the **first 7 bytes** of the digest, interprets them as a big-endian 56-bit integer, then shifts right by 6 to get 50 usable bits.

6. Extracts **10 Base32 characters** from those 50 bits (5 bits each), writing them into a buffer from index 9 down to 0.

7. Applies another adjacent-pair byte-swap to produce `EXPECTED[0..9]`.

8. Compares `EXPECTED` against decoded key bytes `K[0..9]` (groups 1 and 2). If they match → valid key.

---

## Key Generation Algorithm

Since groups 3 and 4 are free (any valid Base32 characters), we can choose them arbitrarily and compute the correct groups 1 and 2 deterministically:

```python
import hmac
import hashlib

BASE32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

def make_key(groups34="AAAAABBBBB"):
    K = list(groups34)
    
    # Build HMAC input with adjacent byte-swap
    data = bytes([
        ord(K[1]), ord(K[0]), ord(K[3]), ord(K[2]),
        ord(K[5]), ord(K[4]), ord(K[7]), ord(K[6]),
        ord(K[9]), ord(K[8])
    ])
    
    # HMAC-SHA256 with hardcoded key
    digest = hmac.new(b"IMNOTTHEKEY", data, hashlib.sha256).digest()
    
    # Take first 7 bytes → 56-bit big-endian integer, shift right 6
    acc = int.from_bytes(digest[:7], 'big') >> 6
    
    # Extract 10 Base32 chars (MSB first)
    rbp = [BASE32[(acc >> (5 * i)) & 0x1f] for i in range(9, -1, -1)]
    
    # Reverse the byte-swap to get groups 1+2
    k = [rbp[1], rbp[0], rbp[3], rbp[2], rbp[5],
         rbp[4], rbp[7], rbp[6], rbp[9], rbp[8]]
    
    g12 = ''.join(k)
    return f"{g12[:5]}-{g12[5:]}-{groups34[:5]}-{groups34[5:]}"

print(make_key())  # → FXJ4P-JKWQW-AAAAA-BBBBB
```

---

## Exploitation

### Testing Locally

Create a dummy `flag.txt` and submit the generated key:

```
$ echo "upCTF{test}" > flag.txt
$ echo "FXJ4P-JKWQW-AAAAA-BBBBB" | ./minecraft-enterprise
Enter Key (format: XXXXX-XXXXX-XXXXX-XXXXX): Flag: upCTF{test}
```

The key is accepted and the binary reads and prints `flag.txt`.

### Against the Remote Server

```
$ printf 'FXJ4P-JKWQW-AAAAA-BBBBB\n' | nc <challenge-host> <port>
Enter Key (format: XXXXX-XXXXX-XXXXX-XXXXX): Flag: upCTF{m1n3cr4ft_0n_th3_b4nks-xh7IPnEKdff1f41f}
```

---

## Flag

```
upCTF{m1n3cr4ft_0n_th3_b4nks-xh7IPnEKdff1f41f}
```

---

## Summary

| Step | Finding |
|------|---------|
| Strings | Base32 alphabet, `IMNOTTHEKEY` HMAC key hidden as `@@IMNOTTHEKEY`, `flag.txt` output |
| Key format | 20 Base32 chars in `XXXXX-XXXXX-XXXXX-XXXXX` format |
| Free variables | Groups 3 & 4 (any valid Base32 input) |
| Validation | `HMAC-SHA256("IMNOTTHEKEY", byte_swap(groups3+4))` → Base32-encode first 7 bytes → must equal groups 1+2 |
| Exploit | Choose arbitrary groups 3+4, compute correct groups 1+2 offline |

The core trick was recognising `@@IMNOTTHEKEY` not as an anti-analysis decoy but as the actual HMAC key stored one byte ahead of its use, and reversing the byte-swap applied to both the HMAC input and the output comparison.
