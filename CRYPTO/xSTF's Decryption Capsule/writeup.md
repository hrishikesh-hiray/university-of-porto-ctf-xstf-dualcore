# xSTF's Decryption Capsule - Detailed Writeup

## Challenge Info
- Category: Cryptography
- Service behavior: accepts hex input, treats first 16 bytes as IV and the rest as AES-CBC ciphertext.
- Goal condition: decrypted plaintext must equal:

```text
xSTF is the best portuguese CTF team :P
```

- Flag format: `upCTF{...}`

## Source Code Review
The challenge code (from `chall (1).py`) does the following:

1. Generates a random AES key once per process:

```python
KEY = os.urandom(16)
```

2. Parses attacker-controlled input as:
- `iv = data[:16]`
- `ciphertext = data[16:]`

3. Decrypts with CBC:

```python
cipher = AES.new(KEY, AES.MODE_CBC, iv=iv)
decrypted = cipher.decrypt(ciphertext)
```

4. Tries PKCS#7 unpadding and catches errors:

```python
plaintext = unpad(decrypted, AES.block_size).decode('latin1')
```

5. If plaintext equals the target phrase, prints `/flag.txt`.

## Vulnerability
This service is a **padding oracle**:
- If padding is invalid, we get a padding-related exception string.
- If padding is valid, code continues and prints either:
  - `you ain't got lil bro` (valid padding but wrong plaintext), or
  - `Yeah it is!` + flag (valid padding and exact target phrase).

That binary distinction leaks whether guessed bytes produce valid PKCS#7 padding.

Because IV is attacker-controlled and CBC plaintext is:

```text
P_i = D_k(C_i) XOR C_{i-1}
```

(with `C_0 = IV`), we can recover intermediate values `I_i = D_k(C_i)` byte-by-byte and then forge previous blocks so plaintext becomes any chosen message.

## Attack Strategy
We need forged ciphertext that decrypts to the exact target phrase.

### 1. Pad target plaintext
Let target be:

```text
xSTF is the best portuguese CTF team :P
```

Apply PKCS#7 padding to 16-byte blocks.

### 2. Work backwards from last block
- Choose random final ciphertext block `C_n`.
- Use padding oracle to recover `I_n = D_k(C_n)`.
- Compute previous block:

```text
C_{n-1} = I_n XOR P_n
```

Repeat upward until `C_1` is known.

### 3. Recover first intermediate and derive IV
Recover `I_1 = D_k(C_1)` via oracle and compute:

```text
IV = I_1 XOR P_1
```

Now `IV || C_1 || ... || C_n` decrypts exactly to desired plaintext.

### 4. Send forged payload
Service prints `Yeah it is!` and then `/flag.txt`.

## Solver Implementation Notes (`solve.py`)
The exploit script uses a pure socket client with reliability improvements:

- Prompt-aware buffered reads (`\n>`).
- Query retries (`MAX_RETRIES`).
- Batched oracle requests (`query_many`) for speed.
- Byte-by-byte intermediate recovery with progress logs.
- Final regex extraction of `upCTF{...}`.

### Why batching mattered
Naive oracle attacks do many round-trips (up to 256 queries per byte). For short-lived instances this is too slow. `query_many` sends many guesses in one burst and reads all responses in sequence, significantly reducing latency overhead.

## How To Run
From challenge directory:

```powershell
& ".\.venv\Scripts\python.exe" ".\solve.py" 46.225.117.62 30011
```

General form:

```powershell
& ".\.venv\Scripts\python.exe" ".\solve.py" <host> <port>
```

## Successful Output (Excerpt)

```text
[*] target blocks: 3
...
[*] IV recovered  total_q=12519
Yeah it is!
upCTF{p4dd1ng_0r4cl3_s4ys_xSTF_1s_num3r0_un0-SSUceavt62de7854}

[+] Flag: upCTF{p4dd1ng_0r4cl3_s4ys_xSTF_1s_num3r0_un0-SSUceavt62de7854}
```

## Final Flag

```text
upCTF{p4dd1ng_0r4cl3_s4ys_xSTF_1s_num3r0_un0-SSUceavt62de7854}
```

## Security Takeaways
- Never expose padding validity differences in decrypt APIs.
- Use authenticated encryption modes (AES-GCM, ChaCha20-Poly1305).
- If CBC must be used, verify MAC before decrypting, and return uniform errors.
- Avoid direct decryption oracles on attacker-controlled ciphertext.
