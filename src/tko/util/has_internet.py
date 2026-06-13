from __future__ import annotations

import socket


def has_internet(timeout: float = 3.0) -> bool:
    hosts: list[tuple[str, int]] = [
        ("1.1.1.1", 53),
        ("8.8.8.8", 53),
    ]

    for host, port in hosts:
        try:
            with socket.create_connection((host, port), timeout):
                return True
        except OSError:
            pass

    return False
