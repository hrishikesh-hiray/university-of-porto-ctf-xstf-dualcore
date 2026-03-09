# University Of Porto CTF - xSTF Writeups

> Flags format: `upCTF{...}` (case-sensitive)

Central repository for challenge writeups, helper scripts, artifacts, and local solve notes from the xSTF CTF platform.

Event platform: https://ctf.xstf.pt/

---

## Quick Snapshot

| Item | Value |
|---|---|
| Categories | `CRYPTO`, `FORENSICS`, `MISC`, `OSINT`, `PWN`, `REV`, `WEB` |
| Total Challenge Folders | `24` |
| Main Goal | Keep all writeups, scripts, artifacts, and solve notes in one place |

## Table of Contents

- [Overview](#overview)
- [Repository Stats](#repository-stats)
- [Directory Tree](#directory-tree)
- [Challenge Index](#challenge-index)
- [How To Use This Repo](#how-to-use-this-repo)
- [Notes](#notes)
- [Disclaimer](#disclaimer)

## Overview

This repository is organized by major CTF categories:

- `CRYPTO`
- `FORENSICS`
- `MISC`
- `OSINT`
- `PWN`
- `REV`
- `WEB`

Each challenge directory typically contains:

- A writeup file (`writeup.md` or similarly named variant)
- Challenge binaries/files/archives
- Optional helper scripts used during solving (`solve.py`, analysis scripts, exploit builders, etc.)

## Repository Stats

| Category | Count |
|---|---|
| `CRYPTO` | 5 |
| `FORENSICS` | 1 |
| `MISC` | 4 |
| `OSINT` | 1 |
| `PWN` | 3 |
| `REV` | 5 |
| `WEB` | 5 |

Total top-level categories: `7`  
Total challenge folders (top-level per category): `24`

## Directory Tree

```text
University Of Porto CTF/
|- README.md
|- CRYPTO/
|  |- Árvore Genealógica/
|  |  `- writeup .md
|  |- Hidden Signal/
|  |  |- passwords.txt
|  |  `- writeup.md
|  |- LH  RH/
|  |  |- handout.py
|  |  `- writeup.md
|  |- vibedns/
|  |  `- writeup.md
|  `- xSTF's Decryption Capsule/
|     |- chall (1).py
|     |- solve.py
|     `- writeup.md
|- FORENSICS/
|  `- xSTF's Annual Security Report/
|     |- 2025-Security-Report.pdf
|     |- appendix.pdf
|     |- multiple cracking/inspection scripts
|     `- writeup.md
|- MISC/
|  |- BluPage/
|  |  `- writeup.md
|  |- Deoxyribonucleic acid/
|  |  |- sample.txt
|  |  `- writeup.md
|  |- Get off the ISS/
|  |  |- handout/ , handout.zip
|  |  |- page.html , tmp_index.html
|  |  `- wreiteup.md
|  `- Jailed/
|     |- chall.py
|     `- writeup.md
|- OSINT/
|  `- Left Behind/
|     `- writeup.md
|- PWN/
|  |- car-museum/
|  |  `- writeup .md
|  |- EU Filter/
|  |  |- eufilter/ , unzipped/
|  |  |- exploit payload generators (.js)
|  |  `- writeup.md
|  `- Generous Allocator/
|     |- overlap
|     |- libc.so.6
|     |- solve.py
|     `- writeup.md
|- REV/
|  |- Inconspicuous Program/
|  |  |- inconspicuous
|  |  `- writeup.mdf
|  |- Locked Temple/
|  |  |- locked_temple
|  |  |- disasm/analysis helper scripts
|  |  `- writeup.md
|  |- Minecraft Enterprise Edition/
|  |  `- minecrated enterprise revwriteup .md
|  |- Old Calculator/
|  |  `- calculatorwriteup.md
|  `- Wasmbler/
|     `- writeup .md
`- WEB/
   |- 0day on ipaddress/
   |  |- Dockerfile , server.py
   |  |- flag files
   |  |- README.md
   |  `- writup.md
   |- mAuth/
   |  |- admin-app/ , proxy/ , public-app/
   |  |- docker-compose.yml
   |  |- solve.py
   |  `- writeup.md
   |- Media-meeting/
   |  `- media-meeting/
   |     |- docker-compose.yaml
   |     |- solve scripts
   |     `- writeup.md
   |- Microsoft Axel/
   |  `- microsoft-axel/
   |     |- app.py
   |     `- writeup.md
   `- Post Builder/
      |- post-builder/
      |- post-builder.zip
      `- writeup.md
```

## Challenge Index

### CRYPTO

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| CRYPTO | Árvore Genealógica | Cryptography | `upCTF{0_m33s1_é_p3qu3n1n0-DsRMlOMoa37607ab}` | [writeup](<CRYPTO/Árvore Genealógica/writeup .md>) |
| CRYPTO | Hidden Signal | Cryptography | `upCTF{m4rk0v_w4s_h3r3_4ll_4l0ng}` | [writeup](<CRYPTO/Hidden Signal/writeup.md>) |
| CRYPTO | LH RH | Cryptography | `upCTF{H0p3_y0u_d1dnt_us3_41_1_sw3ar_th1s_1s_n1ce...If you are CR7 and you solved this, I love you}` | [writeup](<CRYPTO/LH  RH/writeup.md>) |
| CRYPTO | vibedns | Cryptography | `upCTF{ev3n_wh3n_1ts_crypto_1ts_alw4ys_Dn5_EDs2SH5yf7465f8e}` | [writeup](<CRYPTO/vibedns/writeup.md>) |
| CRYPTO | xSTF's Decryption Capsule | Cryptography | `upCTF{p4dd1ng_0r4cl3_s4ys_xSTF_1s_num3r0_un0-SSUceavt62de7854}` | [writeup](<CRYPTO/xSTF's Decryption Capsule/writeup.md>) |

### FORENSICS

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| FORENSICS | xSTF's Annual Security Report | Forensics | `upCTF{V3ry_b4d_S3cUriTy_P0stUr3}` | [writeup](<FORENSICS/xSTF's Annual Security Report/writeup.md>) |

### MISC

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| MISC | BluPage | Miscellaneous | `upCTF{PNG_hdrs_4r3_sn34ky}` | [writeup](<MISC/BluPage/writeup.md>) |
| MISC | Deoxyribonucleic acid | Miscellaneous | `upCTF{DnA_IsCh3pear_Th3n_R4M}` | [writeup](<MISC/Deoxyribonucleic acid/writeup.md>) |
| MISC | Get off the ISS | Miscellaneous | `upCTF{fl4t_e4rth3rs_cou1d_n3v3r-6KepCQ1d003f538d}` | [writeup](<MISC/Get off the ISS/wreiteup.md>) |
| MISC | Jailed | Miscellaneous | `upCTF{fmt_str1ng5_4r3nt_0nly_a_C_th1ng-p0eX6TzJaa01685e}` | [writeup](<MISC/Jailed/writeup.md>) |

### OSINT

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| OSINT | Left Behind | OSINT | `upCTF{John_Stephen}` | [writeup](<OSINT/Left Behind/writeup.md>) |

### PWN

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| PWN | car-museum | Binary Exploitation | `upCTF{c4tc4ll1ng_1s_n0t_c00l-evlbx4ka2ad216ce}` | [writeup](<PWN/car-museum/writeup .md>) |
| PWN | EU Filter | Binary Exploitation | `upCTF{jus7_s4y_1ts_f0r_7h3_ch1ldr3n-9sMH3wbG1be9a3de}` | [writeup](<PWN/EU Filter/writeup.md>) |
| PWN | Generous Allocator | Binary Exploitation | `upCTF{h34d3r_1nclud3d_by_m4ll0c-c2hSGa8Nc900ce90}` | [writeup](<PWN/Generous Allocator/writeup.md>) |

### REV

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| REV | Inconspicuous Program | Reverse Engineering | `upCTF{I_w4s_!a110wed_t0_write_m4lw4r3}` | [writeup](<REV/Inconspicuous Program/writeup.mdf>) |
| REV | Locked Temple | Reverse Engineering | `upCTF{01122301_7}` | [writeup](<REV/Locked Temple/writeup.md>) |
| REV | Minecraft Enterprise Edition | Reverse Engineering | `upCTF{m1n3cr4ft_0n_th3_b4nks-xh7IPnEKdff1f41f}` | [writeup](<REV/Minecraft Enterprise Edition/minecrated enterprise revwriteup .md>) |
| REV | Old Calculator | Reverse Engineering | `upCTF{1F41L3DC4LCF0RTH1S}` | [writeup](<REV/Old Calculator/calculatorwriteup.md>) |
| REV | Wasmbler | Reverse Engineering | `upCTF{n3rd_squ4d_4ss3mbl3_c0de_7f2b1d}` | [writeup](<REV/Wasmbler/writeup .md>) |

### WEB

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| WEB | 0day on ipaddress | Web Exploitation | `upCTF{h0w_c4n_1_wr1t3_t0_4n_ip4ddress?!-FsEyppln13d4d191}` | [writeup](<WEB/0day on ipaddress/writup.md>) |
| WEB | mAuth | Web Exploitation | `upCTF{n3v3r_m4k3_youuuur_0wn_mtls_Usm3SchLTtUDe05991e1}` | [writeup](<WEB/mAuth/writeup.md>) |
| WEB | Media-meeting | Web Exploitation | `upCTF{xsL34ks_4r3_pr33ty-NVzmDaUq93dba364}` | [writeup](<WEB/Media-meeting/media-meeting/writeup.md>) |
| WEB | Microsoft Axel | Web Exploitation | `upCTF{4x3l_0d4y_w1th4_tw1st-D4eH1LN0da079878}` | [writeup](<WEB/Microsoft Axel/microsoft-axel/writeup.md>) |
| WEB | Post Builder | Web Exploitation | `upCTF{r34ct_js_1s_still_j4v4scr1pt-WOlvfjOl2b4494e6}` | [writeup](<WEB/Post Builder/writeup.md>) |

## Disclaimer

These writeups are shared for educational purposes only.

