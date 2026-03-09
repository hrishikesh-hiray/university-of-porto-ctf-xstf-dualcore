# Hidden Signal (100) - Writeup

## Challenge
- Name: `Hidden Signal`
- Points: `100`
- Author: `ritinha`
- Prompt:
  - `A leaked password database. The data looks random. It isn't. Find the signal. Flag Example: upCTF{result}`

## Files Provided
- `passwords.txt`

## Initial Observation
The file is mostly uppercase letters, but there are occasional embedded substrings containing lowercase letters, digits, and underscores.

That strongly suggests deliberate steganography in the text stream.

## Hypothesis
The hidden signal is encoded in the lowercase/digit/underscore chunks, while the uppercase bulk acts as noise.

## Extraction Strategy
1. Extract only substrings matching `[a-z0-9_]{5,}` to confirm whether hidden tokens exist.
2. Check token statistics (count and length).
3. If tokens are fixed-length, perform per-position frequency analysis.
4. Reconstruct the hidden message by taking the most frequent character at each position.

## Commands Used (PowerShell)

### 1) Extract candidate hidden tokens
```powershell
Set-Location 'c:\Kalishared\ctf\ctfhiofddentect cryto'
$text = Get-Content -Raw 'passwords.txt'
[regex]::Matches($text, '[a-z0-9_]{5,}') | ForEach-Object { $_.Value }
```

This returns many suspicious tokens like:
- `uzh90v1v450n2rnqtil78y00g`
- `dal5fhx2s3b9t3_k4g00e3xke`
- `hku0uvswox5x32dl_lirmljn4`

### 2) Verify token structure
```powershell
Set-Location 'c:\Kalishared\ctf\ctfhiofddentect cryto'
$t=[regex]::Matches((Get-Content -Raw passwords.txt),'[a-z0-9_]{5,}')|%{$_.Value}
"count=$($t.Count)"
$t|%{$_.Length}|Group-Object|Sort-Object Name|%{"len $($_.Name): $($_.Count)"}
"underscore-dist:"
$t|%{([regex]::Matches($_,'_').Count)}|Group-Object|Sort-Object Name|%{"u$($_.Name): $($_.Count)"}
```

Key result:
- `count=4000`
- `len 25: 4000`

All hidden tokens are exactly 25 characters long.

### 3) Per-position frequency analysis
```powershell
Set-Location 'c:\Kalishared\ctf\ctfhiofddentect cryto'
$t=[regex]::Matches((Get-Content -Raw passwords.txt),'[a-z0-9_]{25}')|%{$_.Value}
0..24 | ForEach-Object {
  $i=$_
  $chars=$t|%{$_.Substring($i,1)}
  $top=$chars|Group-Object|Sort-Object Count -Descending|Select-Object -First 3
  "pos ${i}: " + (($top|%{"$($_.Name):$($_.Count)"}) -join ', ')
}
```

Most frequent character at each index:
- 0: `m`
- 1: `4`
- 2: `r`
- 3: `k`
- 4: `0`
- 5: `v`
- 6: `_`
- 7: `w`
- 8: `4`
- 9: `s`
- 10: `_`
- 11: `h`
- 12: `3`
- 13: `r`
- 14: `3`
- 15: `_`
- 16: `4`
- 17: `l`
- 18: `l`
- 19: `_`
- 20: `4`
- 21: `l`
- 22: `0`
- 23: `n`
- 24: `g`

Reconstructed signal:
- `m4rk0v_w4s_h3r3_4ll_4l0ng`

## Flag
`upCTF{m4rk0v_w4s_h3r3_4ll_4l0ng}`

## Why This Works
The challenge embeds a structured hidden channel in a noisy corpus. The repeated fixed-length lowercase/digit/underscore tokens behave like samples from a probabilistic process, and taking the mode per position reveals the intended plaintext.

## Notes
- If `rg` (ripgrep) is unavailable on Windows, PowerShell regex extraction works perfectly.
- A quick sanity check is that the recovered phrase is meaningful and CTF-style leetspeak.
