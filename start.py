#!/usr/bin/env python3
"""
Starter del Portal ILAR (modo local)
- Levanta Uvicorn
- Espera /health
- Abre /loading (servida por FastAPI) en una sola pestaña
"""

import os
import sys
import time
import socket
import webbrowser
import threading
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import uvicorn  # pip install uvicorn

# ---------- Utilidades ----------
def find_free_port(start_port: int = 8000, max_tries: int = 50) -> int:
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No se encontró un puerto libre")

def wait_for_health(url: str, timeout_s: int = 60, interval_s: float = 0.5) -> bool:
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            req = Request(url, headers={"User-Agent": "health-check"})
            with urlopen(req, timeout=2) as resp:
                if 200 <= resp.getcode() < 300:
                    return True
        except (URLError, HTTPError):
            pass
        time.sleep(interval_s)
    return False

# ---------- Arranque ----------
def run_uvicorn(port: int):
    # main:app debe existir en main.py
    uvicorn.run("main:app", host="127.0.0.1", port=port, log_level="info", reload=False)

def open_browser_when_ready(port: int):
    health = f"http://127.0.0.1:{port}/health"
    loading = f"http://127.0.0.1:{port}/loading"

    if wait_for_health(health, timeout_s=90):
        webbrowser.open(loading)
        print(f"🌐 Abriendo navegador en: {loading}")
    else:
        # Fallback (por si /health no responde a tiempo)
        root = f"http://127.0.0.1:{port}"
        webbrowser.open(root)
        print(f"⚠️ /health no respondió a tiempo. Abriendo {root}")

def main():
    # Asegurar carpetas típicas (no obligatorio, pero útil)
    for d in ("templates", "static"):
        Path(d).mkdir(exist_ok=True)

    port = find_free_port(8000)

    # Hilo servidor
    server_thread = threading.Thread(target=run_uvicorn, args=(port,), daemon=True)
    server_thread.start()

    # Hilo navegador (espera /health y abre /loading)
    browser_thread = threading.Thread(target=open_browser_when_ready, args=(port,), daemon=True)
    browser_thread.start()

    try:
        # Mantener proceso vivo (Ctrl+C para salir)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario")

if __name__ == "__main__":
    main()
