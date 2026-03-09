# xSTF's Annual Security Report - Binks (Forensics) Writeup

## Challenge
- Name: `xSTF's Annual Security Report`
- Category: `Forensics`
- Flag format: `upCTF{...}`

## Objective
Analyze the provided PDF report and recover the hidden flag.

## Files Provided
- `2025-Security-Report.pdf`

## Final Flag
- `upCTF{V3ry_b4d_S3cUriTy_P0stUr3}`

## Approach Overview
The investigation followed a standard document-forensics workflow:
1. Triage the PDF metadata and structure.
2. Look for embedded objects/attachments.
3. Extract any embedded payloads.
4. Analyze protection/encryption on extracted files.
5. Recover password (if needed) and read hidden content.

---

## Step 1: Initial Triage of the Main PDF
First, inspect metadata and quickly scan for suspicious PDF keywords.

### Metadata
Using `ExifTool` on `2025-Security-Report.pdf` showed:
- PDF v1.7
- Producer: LibreOffice Writer
- 3 pages
- No obvious flag in standard metadata

### Keyword/Structure Scan
Searching raw PDF bytes for common indicators (`/EmbeddedFile`, `/Filespec`, `/JS`, etc.) revealed:
- `/Type /EmbeddedFile`
- `/EmbeddedFiles 5 0 R`
- `/Type /Filespec`
- Filename reference: `appendix.pdf`

Conclusion: the report contains an embedded attachment.

---

## Step 2: Recover Embedded Attachment (`appendix.pdf`)
The embedded payload was stored in object stream `3 0 obj` with `/Filter /FlateDecode`.

Because direct extraction from ExifTool did not return data in this case, extraction was performed manually by:
1. Locating object `3 0 obj` stream boundaries.
2. Stripping stream line-ending bytes.
3. Inflating the compressed stream via Deflate.
4. Writing result to `appendix.pdf`.

Validation:
- Recovered file header began with `%PDF-1.7`.
- File size was non-zero and parseable as PDF.

---

## Step 3: Analyze `appendix.pdf`
Running metadata checks showed:
- The extracted PDF is encrypted (`Standard V2.3`, 128-bit, revision 3 style settings).

No plaintext flag was visible in raw bytes, so password recovery was required.

---

## Step 4: Password Recovery Strategy
A staged cracking strategy was used to avoid brute-forcing huge spaces blindly.

### 4.1 Quick candidate checks
Tried challenge-themed and obvious passwords such as:
- `binks`, `Binks`, `xSTF`, `2025`, `appendix`, `confidential`, etc.

No hit.

### 4.2 Dictionary checks
Tested against:
- `10k-most-common.txt`
- `xato-100k.txt`
- `xato-1m.txt`
- `words_alpha.txt` (English words)

No direct hit.

### 4.3 Numeric-only brute force
Tested numeric passwords length 1 to 6.

No hit.

### 4.4 Mutated dictionary strategy (successful)
Applied human-pattern mutations over dictionary words, including:
- case transforms (`word`, `Word`, `WORD`)
- common suffixes (`1`, `123`, `!`, `@123`, `2025`, `2026`)

This found the correct password:
- `Maki`

---

## Step 5: Decrypt Appendix and Extract Flag
Using `pypdf` with password `Maki`:
- `decrypt_result = 2` (successful)
- Extracted text from decrypted appendix:

`upCTF{V3ry_b4d_S3cUriTy_P0stUr3}`

---

## Reproducible Minimal Solve (Python)
Below is a concise way to read the final flag once `appendix.pdf` is extracted:

```python
from pypdf import PdfReader

r = PdfReader("appendix.pdf")
r.decrypt("Maki")
text = "\n".join((p.extract_text() or "") for p in r.pages)
print(text)
```

Expected output:

```text
upCTF{V3ry_b4d_S3cUriTy_P0stUr3}
```

---

## Why This Challenge Works
This challenge demonstrates common document-forensics pitfalls:
- Sensitive data hidden in an embedded attachment.
- Attachment protected by weak human-chosen password.
- Main report appears harmless while critical data is moved into a secondary file.

Operationally, this mirrors real-world security posture issues where controls exist but are weak in practice.

---

## Artifacts Generated During Analysis
- `appendix.pdf` (recovered attachment)
- `appendix_text.txt` (decrypted appendix text)
- `report_text.txt` (main report extracted text)
- multiple helper scripts for extraction/cracking (`*.py`)

---

## Short Conclusion
The main PDF contained an embedded encrypted appendix. After extracting and cracking it, the hidden flag was recovered as:

`upCTF{V3ry_b4d_S3cUriTy_P0stUr3}`
