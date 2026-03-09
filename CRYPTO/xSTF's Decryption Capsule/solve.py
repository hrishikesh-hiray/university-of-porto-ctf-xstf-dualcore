#!/usr/bin/env python3
import os
import re
import socket
import sys
import time
from typing import List, Optional

BLOCK = 16
TARGET = b"xSTF is the best portuguese CTF team :P"
MAX_RETRIES = 4


def pkcs7_pad(data: bytes, block_size: int = BLOCK) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


class CapsuleClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(8)
        self.buf = b""
        self.queries = 0
        self._drain_banner()

    def _read_until_prompt(self) -> bytes:
        data = b""

        # Keep reading until we see the challenge prompt or the socket closes.
        while True:
            prompt_idx = self.buf.find(b"\n>")
            if prompt_idx != -1:
                idx = prompt_idx + 2
                data += self.buf[:idx]
                self.buf = self.buf[idx:]
                break

            chunk = self.sock.recv(8192)
            if not chunk:
                data += self.buf
                self.buf = b""
                break

            self.buf += chunk

        return data

    def _drain_banner(self) -> None:
        self._read_until_prompt()

    def query(self, payload: bytes) -> bytes:
        last_err = None
        wire = payload.hex().encode() + b"\n"

        for _ in range(MAX_RETRIES):
            try:
                self.sock.sendall(wire)
                self.queries += 1
                return self._read_until_prompt()
            except (TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
                last_err = exc
                time.sleep(0.15)

        raise RuntimeError(f"Query failed after retries: {last_err}")

    def query_many(self, payloads: List[bytes]) -> List[bytes]:
        if not payloads:
            return []

        last_err = None
        wire = b"".join(p.hex().encode() + b"\n" for p in payloads)

        for _ in range(MAX_RETRIES):
            try:
                self.sock.sendall(wire)
                self.queries += len(payloads)
                return [self._read_until_prompt() for _ in payloads]
            except (TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
                last_err = exc
                time.sleep(0.15)

        raise RuntimeError(f"Batch query failed after retries: {last_err}")

    def is_padding_valid(self, iv: bytes, cblock: bytes) -> bool:
        out = self.query(iv + cblock)
        # Valid padding reaches plaintext comparison branch.
        if b"you ain't got lil bro" in out or b"Yeah it is!" in out:
            return True
        return False

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass


def recover_intermediate(client: CapsuleClient, cblock: bytes, label: str) -> bytes:
    """Recover I = D_k(cblock) using IV control and padding oracle."""
    attack = bytearray(BLOCK)
    interm = bytearray(BLOCK)

    for idx in range(BLOCK - 1, -1, -1):
        pad = BLOCK - idx

        for j in range(idx + 1, BLOCK):
            attack[j] = interm[j] ^ pad

        attempts: List[bytes] = []
        for guess in range(256):
            attack[idx] = guess
            attempts.append(bytes(attack) + cblock)

        outs = client.query_many(attempts)

        found: Optional[int] = None
        for guess, out in enumerate(outs):
            if b"you ain't got lil bro" in out or b"Yeah it is!" in out:
                found = guess
                break

        if found is None:
            raise RuntimeError(f"No valid byte found at position {idx}")

        # Rare edge-case guard for last byte where multiple valid paddings may occur.
        if idx == BLOCK - 1:
            test = bytearray(attack)
            test[idx] = found
            test[idx - 1] ^= 1
            if client.is_padding_valid(bytes(test), cblock):
                # Continue searching for an alternative valid guess.
                alt = None
                extra_attempts: List[bytes] = []
                for guess in range(found + 1, 256):
                    attack[idx] = guess
                    extra_attempts.append(bytes(attack) + cblock)
                extra_outs = client.query_many(extra_attempts)
                for i, out in enumerate(extra_outs):
                    if b"you ain't got lil bro" in out or b"Yeah it is!" in out:
                        alt = found + 1 + i
                        break
                if alt is not None:
                    found = alt

        interm[idx] = found ^ pad
        print(f"[+] {label} byte {idx:02d} solved  q={client.queries}")

    return bytes(interm)


def build_forged_ciphertext(client: CapsuleClient, wanted_plain: bytes) -> bytes:
    padded = pkcs7_pad(wanted_plain)
    pblocks = [padded[i:i + BLOCK] for i in range(0, len(padded), BLOCK)]
    n = len(pblocks)

    cblocks = [b"\x00" * BLOCK for _ in range(n)]

    # Start from last block: pick random C_n, recover I_n, derive C_{n-1}, continue backwards.
    cblocks[-1] = os.urandom(BLOCK)
    print(f"[*] target blocks: {n}")

    for i in range(n - 1, 0, -1):
        interm_i = recover_intermediate(client, cblocks[i], f"I[{i}]")
        cblocks[i - 1] = bytes(x ^ y for x, y in zip(interm_i, pblocks[i]))
        print(f"[*] built C[{i - 1}]  total_q={client.queries}")

    # Recover I_1 to derive IV.
    interm_1 = recover_intermediate(client, cblocks[0], "I[0]")
    iv = bytes(x ^ y for x, y in zip(interm_1, pblocks[0]))
    print(f"[*] IV recovered  total_q={client.queries}")

    return iv + b"".join(cblocks)


def extract_flag(text: str) -> str:
    m = re.search(r"upCTF\{[^\r\n}]*\}", text)
    return m.group(0) if m else ""


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = CapsuleClient(host, port)
    try:
        payload = build_forged_ciphertext(client, TARGET)
        out_b = client.query(payload)
        out = out_b.decode("latin1", errors="ignore")
        print(out)

        flag = extract_flag(out)
        if flag:
            print(f"[+] Flag: {flag}")
        else:
            print("[-] Flag not found in output. If connection reset, rerun script.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
