#!/usr/bin/env python
"""Bind IPv4 + IPv6 (V6ONLY) then exec gunicorn on those FDs.

Fly proxy probes 0.0.0.0:8000; service health checks use the IPv6 6PN address.
Gunicorn cannot --bind both without Address-already-in-use on dual-stack kernels.
"""
from __future__ import annotations

import os
import socket

PORT = int(os.environ.get("PORT", "8000"))


def listen(family: int, address: tuple, *, v6only: bool | None = None) -> socket.socket:
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if v6only is not None:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1 if v6only else 0)
    sock.bind(address)
    sock.listen(2048)
    os.set_inheritable(sock.fileno(), True)
    return sock


def main() -> None:
    sockets = [
        listen(socket.AF_INET, ("0.0.0.0", PORT)),
        listen(socket.AF_INET6, ("::", PORT), v6only=True),
    ]
    args = [
        "gunicorn",
        "--workers",
        "1",
        "--threads",
        "2",
        "--timeout",
        "60",
    ]
    for sock in sockets:
        args.extend(["--bind", f"fd://{sock.fileno()}"])
    args.append("config.wsgi:application")
    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
