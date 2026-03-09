# Arvore Genealogica (Crypto) - Detailed Writeup

## Challenge Info
- Category: Crypto
- Difficulty: easy
- Title: `Arvore Genealogica`
- Description hint (PT): "So primos atras de primos atras da fortuna do papi cris."
- Service: `http://46.225.117.62:30014`

## Goal
Recover the correct bank code and obtain the flag from the remote service.

## 1. Initial Recon
Open the root page and inspect linked files.

Main observations from `/`:
- A family tree UI is loaded from `script.js`.
- A button redirects to `banco.html` (`Aceder ao Cofre do Banco`).

From `banco.html`:
- Password input field (`bankCode`)
- Button calls `verifyCode()` from `bank-script.js`

From `bank-script.js`:
- `verifyCode()` sends a POST request to `/api/verify-code` with JSON body:

```json
{"code":"<user_input>"}
```

If success:
- Server returns JSON containing `flag`
- Frontend stores flag in `localStorage` and redirects to `/dashboard.html`

So the real target is: derive valid `code` for `/api/verify-code`.

## 2. Extract Crypto Material from `script.js`
Inside the family tree data, one member includes RSA parameters:

- `n = ...` (very large modulus)
- `e = 0x10001` (65537)
- `c = ...` (ciphertext)

Additional hints in other family nodes:
- "... ate 100000 era perto e que basta 'descobrir um que o outro e obvio'"
- "... valor perto de 2**777"

These strongly suggest weak RSA prime generation with one prime close to `2**777` and small search space.

## 3. Attack Strategy
Given RSA:
- `n = p * q`
- `e = 65537`
- `c = m^e mod n`

If one prime `p` is near `2**777`, we can search for a divisor near that value:

1. Set `base = 2**777`
2. For offsets `d` in `[0, 100000]`, test candidates `base-d` and `base+d`
3. Check if `n % candidate == 0`
4. Once divisor found, compute:
   - `q = n // p`
   - `phi = (p-1)*(q-1)`
   - `d = e^{-1} mod phi`
   - `m = c^d mod n`
5. Convert `m` to bytes/string to recover plaintext bank code.

## 4. Reproducible Solver Script

```python
import math

n = 625884537996922021301000341433932506927375585765524880339408244299388166616607970182814658884261038589890375258726352401200713142307149681483775252604692104227832166709807990289415964013032746766172102239270024433627974944278194240214614719847340322457045111198478821355004842741718270057503827331434371408025925605481105486995996528014519769908400670772699182920499677705809631318990058839592839709710458652675562071292900519774414030358230173117805552929123198203307
e = 65537
c = 62318722105864475633070267247974102130492586860223395750014121141640728228140922787683482348993303220123956188779410980859089837155685153563184703318488138798553149093011757720494639060509132811288893681789241883011105101728028235229519920858485960028687937326165670672221777501503866767604530227335608355547324683970157050707878702259507869498079204990540446272961682199498306150812336216294150630212362402674654569608827746982122255526272178602585754110118148113502

base = 1 << 777
p = None

for delta in range(0, 100001):
    candidates = (base,) if delta == 0 else (base - delta, base + delta)
    for cand in candidates:
        if cand > 1 and n % cand == 0:
            p = cand
            break
    if p is not None:
        break

if p is None:
    raise RuntimeError("No factor found in +/-100000 around 2**777")

q = n // p
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)

plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big").decode()
print("Recovered bank code:", plaintext)
```

## 5. Recovered Secret
The decrypted plaintext is:

`S3cr3t_to_p4pis_f0rtune`

This is the required `code` for the bank endpoint.

## 6. Submit to Endpoint

Example request:

```http
POST /api/verify-code HTTP/1.1
Host: 46.225.117.62:30014
Content-Type: application/json

{"code":"S3cr3t_to_p4pis_f0rtune"}
```

Server response:

```json
{"success":true,"flag":"upCTF{0_m33s1_é_p3qu3n1n0-DsRMlOMoa37607ab}","message":"Bem-vindo ao seu cofre secreto, papi cris!"}
```

## 7. Final Flag
`upCTF{0_m33s1_é_p3qu3n1n0-DsRMlOMoa37607ab}`

## 8. Why This Works
The RSA setup is breakable because one prime factor is intentionally close to a known anchor (`2**777`) and within a tiny offset range. Instead of hard factoring a ~1555-bit modulus, the challenge leaks enough structure to reduce factorization to a short brute-force divisor search.

## 9. Defensive Takeaway
Do not generate RSA primes with predictable structure (for example, "near a known value"). Prime generation must be uniformly random and cryptographically strong; otherwise RSA collapses.
