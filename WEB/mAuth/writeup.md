# mAuth (web) - Full Writeup

## Challenge Info
- Category: Web
- Challenge name: `mAuth`
- Flag format: `upCTF{...}`
- Important note from prompt: server certificate is self-signed, so TLS verification must be disabled on the client side.

## Final Flag
`upCTF{n3v3r_m4k3_youuuur_0wn_mtls_Usm3SchLTtUDe05991e1}`

## High-Level Summary
This challenge is a chained vulnerability:
1. TLS proxy access control is based on `SNI` and a secret ALPN token.
2. Backend routing is based on HTTP `Host` header, not SNI.
3. `admin-app` exposes `/logs` that renders attacker-controlled logs via `render_template_string`, leading to SSTI.
4. SSTI is used to make an internal request to `/flag` with trusted header `X-Proxy-Authenticated: true`.

The key bug is trust boundary confusion plus unsafe template rendering.

## Architecture
From the provided code and compose:
- `tls-proxy` listens on 443 (mapped to host port 9000 locally).
- `public-app` listens on 5000 and has `/flag` protected by `X-Proxy-Authenticated: true`.
- `admin-app` listens on 5001 and has:
  - `/clean` to clear logs
  - `/logs` to render `/tmp/app.log` as Jinja template
- Shared logs volume means user-controlled public-app request bodies become admin-app template input.

## Source Analysis

### 1) Proxy logic: split trust model
In `proxy/proxy.c`:
- Access check (`check_access`) allows normal users when `SNI == challenge.com` and secret ALPN is present.
- Admin access (`SNI == admin.challenge.com`) requires client cert.
- Routing decision later uses parsed `Host` header:
  - `Host: admin.challenge.com` routes to admin backend.
  - otherwise routes to public backend.

This creates an SNI/Host mismatch primitive:
- Use `SNI=challenge.com` to pass non-admin access policy.
- Send `Host: admin.challenge.com` to route to admin backend anyway.

### 2) ALPN "secret" generation weakness
Proxy requires a specific ALPN protocol generated every 5 minutes:
- `srand(window)` where `window = time(NULL) / 300`
- then 3x `rand()` to build `ctf-%08x-%08x-%08x`

On Alpine/musl, `rand()` implementation is deterministic and easy to reproduce:
- `seed = s - 1`
- `seed = 6364136223846793005 * seed + 1` (mod 2^64)
- output is `seed >> 33`

So attacker can compute current ALPN token offline.

### 3) Admin SSTI
In `admin-app/app.py`:
- `/logs` reads `/tmp/app.log` and returns `render_template_string(log_content)`.

In `public-app/app.py`:
- Every POST body is logged into `/tmp/app.log`.

Thus POST body to public app is a Jinja payload that later executes when admin visits `/logs`.

### 4) Header trust abuse
In `public-app/app.py`:
- `/flag` only checks `X-Proxy-Authenticated == true`.

Using SSTI code execution in admin app, we can issue an internal HTTP request to `public-app:5000/flag` with forged trusted header.

## Full Exploit Chain
1. Connect TLS to target with:
   - `SNI=challenge.com`
   - `ALPN=<computed secret>`
   - cert verification disabled (`self-signed` challenge cert)
2. Send request with `Host: admin.challenge.com` to reach admin endpoints.
3. Call `/clean` to reset logs.
4. Send POST to public route with Jinja payload in body (this is logged).
5. Call admin `/logs` to execute payload.
6. Payload performs internal request to `/flag` with header `X-Proxy-Authenticated: true`.
7. Extract `upCTF{...}` from response body/log output.

## Solver Used
A Python solver (`solve.py`) was created that:
- Reproduces musl `rand()` ALPN token.
- Tries small time-window offsets for clock skew.
- Sends raw HTTP over TLS sockets using desired SNI and Host.
- Injects SSTI and extracts flag via regex.
- Supports remote host/port (`--host`, `--port`).

## Commands Executed

### Local build and run
```powershell
Set-Location c:\Kalishared\ctf\webmauth\challenge
docker compose down -v
docker compose up -d --build
docker compose ps
```

### Local solve
```powershell
C:/Users/Hrishikesh/AppData/Local/Microsoft/WindowsApps/python3.12.exe solve.py --host 127.0.0.1 --port 9000
```

### Remote solve (live instance)
```powershell
C:/Users/Hrishikesh/AppData/Local/Microsoft/WindowsApps/python3.12.exe solve.py --host 46.225.117.62 --port 30013
```

Output:
```text
[*] Trying internal target: 127.0.0.1
[+] Flag: upCTF{n3v3r_m4k3_youuuur_0wn_mtls_Usm3SchLTtUDe05991e1}
```

## Why This Works
- Proxy assumes SNI and Host are aligned. They are attacker-controlled and independent.
- "Secret" ALPN based on predictable PRNG/time is not a secret.
- Rendering logs as templates creates direct code execution from user input.
- Internal trust based on plain header without cryptographic integrity allows privilege spoofing once code execution is obtained.

## Security Lessons
1. Never split security decisions and routing decisions across different unbound inputs (SNI vs Host) without strict consistency checks.
2. Do not treat deterministic time-based tokens as authentication secrets.
3. Never pass untrusted content into `render_template_string`.
4. Do not trust security headers unless they are set and protected by an authenticated gateway boundary.
5. Defense-in-depth matters: any single one of these fixes would have broken this exploit chain.

## Suggested Fixes
- Enforce `Host` to match validated SNI exactly; reject mismatch.
- Remove ALPN-based secret auth entirely, or use signed/session-bound proof.
- Replace `render_template_string(log_content)` with safe escaping/plain text render.
- Protect `/flag` with proper server-side auth context, not raw client-supplied header.
- Isolate logs and avoid sharing attacker-controlled logs directly into admin-rendered templates.

## Artifacts
- Exploit script: `challenge/solve.py`
- This writeup: `challenge/writeup.md`
