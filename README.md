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

| Challenge Type | Challenge Name | Category | Flag | Writeup |
|---|---|---|---|---|
| CRYPTO | Árvore Genealógica | Cryptography | - | [writeup](<CRYPTO/Árvore Genealógica/writeup .md>) |
| CRYPTO | Hidden Signal | Cryptography | - | [writeup](<CRYPTO/Hidden Signal/writeup.md>) |
| CRYPTO | LH RH | Cryptography | - | [writeup](<CRYPTO/LH  RH/writeup.md>) |
| CRYPTO | vibedns | Cryptography | - | [writeup](<CRYPTO/vibedns/writeup.md>) |
| CRYPTO | xSTF's Decryption Capsule | Cryptography | - | [writeup](<CRYPTO/xSTF's Decryption Capsule/writeup.md>) |
| FORENSICS | xSTF's Annual Security Report | Forensics | - | [writeup](<FORENSICS/xSTF's Annual Security Report/writeup.md>) |
| MISC | BluPage | Miscellaneous | - | [writeup](<MISC/BluPage/writeup.md>) |
| MISC | Deoxyribonucleic acid | Miscellaneous | - | [writeup](<MISC/Deoxyribonucleic acid/writeup.md>) |
| MISC | Get off the ISS | Miscellaneous | - | [writeup](<MISC/Get off the ISS/wreiteup.md>) |
| MISC | Jailed | Miscellaneous | - | [writeup](<MISC/Jailed/writeup.md>) |
| OSINT | Left Behind | OSINT | - | [writeup](<OSINT/Left Behind/writeup.md>) |
| PWN | car-museum | Binary Exploitation | - | [writeup](<PWN/car-museum/writeup .md>) |
| PWN | EU Filter | Binary Exploitation | - | [writeup](<PWN/EU Filter/writeup.md>) |
| PWN | Generous Allocator | Binary Exploitation | - | [writeup](<PWN/Generous Allocator/writeup.md>) |
| REV | Inconspicuous Program | Reverse Engineering | - | [writeup](<REV/Inconspicuous Program/writeup.mdf>) |
| REV | Locked Temple | Reverse Engineering | - | [writeup](<REV/Locked Temple/writeup.md>) |
| REV | Minecraft Enterprise Edition | Reverse Engineering | - | [writeup](<REV/Minecraft Enterprise Edition/minecrated enterprise revwriteup .md>) |
| REV | Old Calculator | Reverse Engineering | - | [writeup](<REV/Old Calculator/calculatorwriteup.md>) |
| REV | Wasmbler | Reverse Engineering | - | [writeup](<REV/Wasmbler/writeup .md>) |
| WEB | 0day on ipaddress | Web Exploitation | - | [writeup](<WEB/0day on ipaddress/writup.md>) |
| WEB | mAuth | Web Exploitation | - | [writeup](<WEB/mAuth/writeup.md>) |
| WEB | Media-meeting | Web Exploitation | - | [writeup](<WEB/Media-meeting/media-meeting/writeup.md>) |
| WEB | Microsoft Axel | Web Exploitation | - | [writeup](<WEB/Microsoft Axel/microsoft-axel/writeup.md>) |
| WEB | Post Builder | Web Exploitation | - | [writeup](<WEB/Post Builder/writeup.md>) |

