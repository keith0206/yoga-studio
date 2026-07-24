#!/usr/bin/env python
"""Bind dual-stack then exec gunicorn on that FD.

Fly Proxy reaches the VM over private IPv4 (needs 0.0.0.0 / IPv4-mapped).
Service health checks use 6PN IPv6 (needs [::]).

Gunicorn's native --bind [::]:PORT often sets IPV6_V6ONLY=1 on Linux, so
IPv4 proxy probes fail. Pre-bind one AF_INET6 socket with V6ONLY=0 instead.
"""
from __future__ import annotations

import os
import socket

PORT = int(os.environ.get("PORT", "8000"))


def main() -> None:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind(("::", PORT))
    sock.listen(2048)
    os.set_inheritable(sock.fileno(), True)

    args = [
        "gunicorn",
        "--workers",
        "1",
        "--threads",
        "2",
        "--timeout",
        "60",
        "--bind",
        f"fd://{sock.fileno()}",
        "config.wsgi:application",
    ]
    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
