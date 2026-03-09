# Wasmbler (upCTF) - Detailed Writeup

## Challenge Info
- Name: `Wasmbler`
- Category: Web / Reverse Engineering (WASM)
- Author tag shown: `tmv11`
- Flag format: `upCTF{...}`
- Endpoint: `http://46.225.117.62:30003`

## TL;DR
The page loads an Emscripten bundle (`challenge.js`) and calls:
- `Module.ccall('check_flag', 'number', ['string'], [input])`

The real checker is inside `challenge.wasm` as export `check_flag`.
`check_flag` runs a custom stack-based bytecode VM over 387 bytes of program data and returns 1 only for a valid 38-byte input. The fastest reliable solve is:
1. recover VM instruction semantics from `challenge.wat`,
2. emulate symbolically with Z3,
3. constrain format `upCTF{...}` and solve `check_flag(input) != 0`.

Recovered flag:

```text
upCTF{n3rd_squ4d_4ss3mbl3_c0de_7f2b1d}
```

---

## 1. Initial Recon
### 1.1 Root page
`GET /` returns HTML with one input box and this logic:

```html
const ok = Module.ccall('check_flag', 'number', ['string'], [v]);
m.textContent = ok ? 'correct' : 'wrong';
```

It also loads:

```html
<script src="challenge.js"></script>
```

So the full check happens client-side in WASM.

### 1.2 Discovering wasm file name
From `challenge.js`:

```js
function findWasmBinary() {
  return locateFile('challenge.wasm');
}
```

So the key assets are:
- `challenge.js`
- `challenge.wasm`

---

## 2. Extracting and Inspecting WASM
### 2.1 Download assets
Example commands:

```powershell
curl.exe -sS http://46.225.117.62:30003/challenge.js -o challenge.js
curl.exe -sS http://46.225.117.62:30003/challenge.wasm -o challenge.wasm
```

### 2.2 Disassemble wasm
If `wabt` CLI is unavailable, Binaryen works:

```powershell
npm init -y
npm install binaryen --silent
npx wasm-dis challenge.wasm -o challenge.wat
```

### 2.3 Locate checker
In `challenge.wat` exports:
- `(export "check_flag" (func $17))`

`func $17` is the checker.

---

## 3. What `check_flag` Actually Does
`check_flag` first checks length via `strlen` helper (`func $18`):
- required length is exactly `38` bytes
- if not, returns `0`

Then it sets up a VM state in linear memory and executes a loop while `pc < 387`.

## 3.1 Bytecode source and VM tables
From data segment at memory base `65536`:
- `65536..` contains VM bytecode stream
- at `65924` there are 68 bytes copied to `66000`
- those bytes include dispatch table values `1..13` and RNG seed `0x1337BEEF`

Important constants:
- code length: `387`
- dispatch table length: `13`
- seed init: `0x1337BEEF`

## 3.2 Dispatch randomization
After each executed instruction, checker shuffles dispatch table (Fisher-Yates-like) using LCG:

```c
seed = (seed * 1103515245 + 12345) & 0x7fffffff;
j = seed % (n + 1);
swap(dispatch[n], dispatch[j]);
```

for `n = 12 .. 1`.

So opcode meaning changes every VM step; static opcode->operation mapping is not fixed.

## 3.3 VM operations (functions 1..13)
The resolved function IDs implement:

1. `push_imm8` (next byte from bytecode)
2. `push_input[idx]` (`idx` from stack; reads C-string byte)
3. `add`
4. `sub`
5. `xor`
6. `or`
7. `and`
8. `shl` by `(a & 7)`
9. `shr` by `(a & 7)`
10. `rol8`
11. `ror8`
12. `mod` as `b % (a | 1)`
13. `eq` -> pushes `1` if equal else `0`

All results are reduced to 8-bit values.

After full execution, checker returns top-of-stack byte (`0` or nonzero). Correct flag yields `1`.

---

## 4. Why Brute Force Is Not Practical
Random format-valid inputs consistently returned 0 in large samples (20k tested).
The VM effectively encodes a tight exact constraint system over 38 input bytes with dynamic opcode remapping, making naive mutation/fuzz brute force inefficient.

Symbolic execution is the right approach.

---

## 5. Symbolic Solve with Z3
## 5.1 Strategy
Model input bytes `c0..c37` as 8-bit symbolic variables.
Apply format constraints:
- prefix `upCTF{`
- suffix `}` at index 37
- optional printable range for interior bytes

Re-implement VM exactly (including dispatch shuffles each step), but on Z3 bit-vectors.
Add constraint:

```text
vm_output != 0
```

Ask solver for one satisfying model.

## 5.2 Result
Z3 returns:

```text
upCTF{n3rd_squ4d_4ss3mbl3_c0de_7f2b1d}
```

---

## 6. Validation
Local validation against exported checker:

```js
const M = require('./challenge.js');
const f = 'upCTF{n3rd_squ4d_4ss3mbl3_c0de_7f2b1d}';
let t = setInterval(() => {
  if (typeof M.ccall === 'function') {
    console.log(M.ccall('check_flag', 'number', ['string'], [f]));
    clearInterval(t);
  }
}, 10);
```

Output was:

```text
1
```

So the candidate is confirmed correct.

---

## 7. Key Takeaways
- Emscripten web challenges often hide logic in WASM export functions, not JS.
- If opcode dispatch is reshuffled per instruction, treat mapping as VM state.
- For short fixed-length flags with heavy bitwise arithmetic, symbolic execution is usually fastest.
- Data segment constants (`dispatch`, seed, bytecode blob) are often enough to fully reconstruct checker semantics.

---

## Final Flag

```text
upCTF{n3rd_squ4d_4ss3mbl3_c0de_7f2b1d}
```
