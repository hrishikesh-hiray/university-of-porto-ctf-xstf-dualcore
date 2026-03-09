# BluPage (MISC) - Writeup

## Challenge Info
- Name: `BluPage`
- Category: `MISC`
- Hint text: "A big friend of mine tried to work as a front-end dev, shipped a minimal page and forgot that the web isn't just what you see."
- Target: `http://46.225.117.62:30005`
- Flag format: `upCTF{...}` (case-sensitive)

## TL;DR
The web page source leaked a prefetched archive: `/assets/artifacts.zip`.
Inside it were two image fragments (`f_left.png`, `f_right.png`).
- `f_left.png` had a tampered PNG signature (`PNX` instead of `PNG`) and, once repaired, revealed the prefix text.
- `f_right.png` contained the suffix hidden in the blue-channel LSB bitstream.
Combining both parts gave the final flag.

Final flag:

`upCTF{PNG_hdrs_4r3_sn34ky}`

---

## Step 1: Initial Recon
Fetch the page and inspect source/headers instead of only visual UI.

### Observations
Main page looked minimal and non-interactive:
- Title/body only suggested hidden content.

`robots.txt` returned:
```txt
User-agent: *
Disallow: /static
```
This hinted there were interesting static assets not linked visibly.

Reading page HTML exposed:
```html
<link rel="prefetch" href="/assets/artifacts.zip" as="fetch" crossorigin>
<link rel="stylesheet" href="/static/style.css">
<script src="/static/touch.js"></script>
```
The key clue is the hidden prefetch to `/assets/artifacts.zip`.

---

## Step 2: Download and Inspect Archive
Downloaded archive and listed contents:

```powershell
Invoke-WebRequest -UseBasicParsing "http://46.225.117.62:30005/assets/artifacts.zip" -OutFile artifacts.zip
Expand-Archive -Path artifacts.zip -DestinationPath artifacts -Force
Get-ChildItem artifacts
```

Output:
- `f_left.png`
- `f_right.png`

At first glance both looked like PNG files, but one was intentionally malformed.

---

## Step 3: Validate PNG Signatures
Checked magic bytes:

```powershell
# Example idea
# Read first 8 bytes and print hex
```

### Findings
- `f_left.png` signature started with `89 50 4E 58 ...` (`PNX`)
- `f_right.png` signature started with `89 50 4E 47 ...` (`PNG`)

So `f_left.png` had one byte modified (`X`) to break standard decoders.

---

## Step 4: Repair Left Image and OCR Prefix
Repaired signature byte in `f_left.png`:
- Replace `\x89PNX` with `\x89PNG`
- Save as `f_left_fixed.png`

Python snippet used:

```python
from pathlib import Path

left = Path("artifacts/f_left.png").read_bytes()
if left[:4] == b"\x89PNX":
    left = b"\x89PNG" + left[4:]
Path("artifacts/f_left_fixed.png").write_bytes(left)
```

Ran OCR on repaired image and preprocessing variants (threshold/invert/scale).
Consistent extracted text from left side:

`xCTF{PNG_hdrs_`

Because OCR can confuse leading characters (`x`/`X`/`u`), this was treated as a near-certain structural prefix with one uncertain first letter.

---

## Step 5: Extract Hidden Suffix from Right Image (Stego)
`f_right.png` is almost fully black, classic indicator of bit-level hiding.

Extracted LSB streams by channel and converted bits to bytes.
The useful payload was in:
- Channel: `B` (blue)
- Bit plane: `0` (LSB)
- Standard bit order / no offset

Recovered clear suffix:

`4r3_sn34ky}`

---

## Step 6: Reconstruct Candidate Flag
Combine recovered parts:
- Prefix from repaired-left OCR: `?CTF{PNG_hdrs_`
- Suffix from right stego: `4r3_sn34ky}`

Candidate string:
- `xCTF{PNG_hdrs_4r3_sn34ky}`

Then apply known challenge requirement provided later:
- Flag format is `upCTF{...}` (case-sensitive)

Normalized final flag:

`upCTF{PNG_hdrs_4r3_sn34ky}`

---

## Why This Works
- The challenge theme says the page was "minimal" and "web isn't just what you see".
- The secret was in non-visual web data (prefetched asset).
- Archive contained intentionally split/obfuscated evidence:
1. Broken PNG header (`hdrs` clue in final flag text).
2. Hidden LSB tail in second image.

So the intended solve path is web recon + file format awareness + light steganography.

---

## Reproduction Script (All-in-One Outline)

```python
# 1) Download zip
# 2) Extract files
# 3) Fix f_left signature PNX->PNG
# 4) OCR fixed left for prefix
# 5) LSB extract from f_right blue channel bit0 for suffix
# 6) Combine and apply required upCTF{...} format
```

---

## Final Answer

`upCTF{PNG_hdrs_4r3_sn34ky}`
