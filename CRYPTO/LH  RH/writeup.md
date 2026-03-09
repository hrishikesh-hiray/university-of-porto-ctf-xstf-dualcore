# Crypto Writeup: LH | RH

## Challenge Summary
We are given RSA parameters:

- `n`
- `e = 65537`
- `c`

And a construction hint in the source:

- Let `p = L|R`
- Let `q = R|L`

In the challenge code, the split size is `CR7 = 143` decimal digits, so both primes are built by concatenating two 143-digit decimal halves.

If we define:

- `X = 10^143`
- `p = A*X + B`
- `q = B*X + A`

where `A` and `B` are 143-digit integers, then:

`n = p*q = (A*B)*X^2 + (A^2 + B^2)*X + (A*B)`

This symmetry is the key to solving the challenge without factoring generic RSA.

## Given Public Values

```text
n = 13184777495081008136378701349850014746828643066078107459934895054885104642211158887687363814851481880536739392765231880911914473779382677713817869943051361672810349968815079826008147134282184038528606008903819389465003037971715429698635686502083228479158527194657308756285498668205015510210856933773632225424038806710198000445915830912691957546385857601215816162731398099364433431385564877501465481250464329970426956154629887038690532877247607885092909054430992070325775056580096677878409305289037435079906658919023437746158537338999806571810766980982205678495423068406683

e = 65537

c = 2495775681430782992362729479625745975452355744176335567477436185288072507322197414455082980603105950811079969359022065544386855789086367219752934247461840328294670145676669898544198555268488325770400741479499745546596113268440443979671562814955995222612911610171957602085975945183334365734071644232961413114059132813194282507921431908516772243706734149144798491044997348454739610191338901834287944798241073116954989258720378999841400983436377762960200739531431493883077810036013077582843786006467028277252503510122737756053076230600350568886788079832668863643974698548661
```

## Core Math Derivation
Write `n` in base `X = 10^143`:

`n = d3*X^3 + d2*X^2 + d1*X + d0`

From the expansion above:

- low chunk: `d0 = A*B (mod X)`
- high chunk relation includes carry from `A*B` into `X^3`
- middle chunk corresponds to `A^2 + B^2` with carry adjustments

The practical recovery strategy:

1. Extract base-`X` chunks `d0,d1,d2,d3` from `n`.
2. Enumerate tiny carry possibilities (only a few values).
3. Recover:
   - `u = A*B`
   - `v = A^2 + B^2`
4. Use identities:
   - `(A+B)^2 = v + 2u`
   - `(A-B)^2 = v - 2u`
5. Require both to be perfect squares.
6. Solve:
   - `A = ((A+B) + (A-B))/2`
   - `B = ((A+B) - (A-B))/2`
7. Rebuild `p,q` and verify `p*q == n`.
8. Compute RSA private exponent and decrypt.

## Solver (Reproducible)

```python
from math import isqrt

n = int("13184777495081008136378701349850014746828643066078107459934895054885104642211158887687363814851481880536739392765231880911914473779382677713817869943051361672810349968815079826008147134282184038528606008903819389465003037971715429698635686502083228479158527194657308756285498668205015510210856933773632225424038806710198000445915830912691957546385857601215816162731398099364433431385564877501465481250464329970426956154629887038690532877247607885092909054430992070325775056580096677878409305289037435079906658919023437746158537338999806571810766980982205678495423068406683")
e = 65537
c = int("2495775681430782992362729479625745975452355744176335567477436185288072507322197414455082980603105950811079969359022065544386855789086367219752934247461840328294670145676669898544198555268488325770400741479499745546596113268440443979671562814955995222612911610171957602085975945183334365734071644232961413114059132813194282507921431908516772243706734149144798491044997348454739610191338901834287944798241073116954989258720378999841400983436377762960200739531431493883077810036013077582843786006467028277252503510122737756053076230600350568886788079832668863643974698548661")

X = 10**143

# Decompose n in base X: n = d3*X^3 + d2*X^2 + d1*X + d0
parts = []
t = n
for _ in range(4):
    parts.append(t % X)
    t //= X

d0, d1, d2, d3 = parts

found = False
for carry2 in range(8):
    # k links d2 and d0 through carry from middle multiplication
    k = d2 - d0 + carry2 * X
    if k < 0:
        continue

    u1 = d3 - carry2
    if u1 < 0:
        continue

    # u = A*B, v = A^2 + B^2 (after carry corrections)
    u = u1 * X + d0
    t1 = d1 + k * X
    v = t1 - u1
    if v < 0:
        continue

    sp = v + 2 * u  # (A+B)^2
    sm = v - 2 * u  # (A-B)^2
    if sm < 0:
        continue

    rp = isqrt(sp)
    rm = isqrt(sm)
    if rp * rp != sp or rm * rm != sm:
        continue

    A = (rp + rm) // 2
    B = (rp - rm) // 2
    if A < 0 or B < 0:
        continue
    if A * B != u:
        continue

    p = A * X + B
    q = B * X + A
    if p * q != n:
        continue

    # Optional sanity check: both halves should be 143 digits
    if len(str(A)) != 143 or len(str(B)) != 143:
        continue

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)

    msg = m.to_bytes((m.bit_length() + 7) // 8, "big")
    print(msg.decode())
    found = True
    break

if not found:
    print("No valid decomposition found")
```

## Recovered Flag

```text
upCTF{H0p3_y0u_d1dnt_us3_41_1_sw3ar_th1s_1s_n1ce...If you are CR7 and you solved this, I love you}
```

## Why This Works
This RSA is weak because `p` and `q` are not independent random primes. They are deterministic decimal rotations of each other. That gives a strong algebraic structure in base `10^143`, reducing the problem to solving a constrained system with tiny carry search and perfect-square checks.

In short: this is not generic RSA factoring; it is exploitation of key-generation structure.
