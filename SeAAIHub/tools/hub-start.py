#!/usr/bin/env python3
"""SeAAIHub + MME + Dashboard 기동 (hub/gateway 구조용)."""
import subprocess, sys, time, platform, argparse, socket, urllib.request
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TOOLS_DIR.parent
HUB_DIR = ROOT_DIR / "hub"
GATEWAY_DIR = ROOT_DIR / "gateway"
BIN_NAME = "SeAAIHub.exe" if platform.system() == "Windows" else "SeAAIHub"
MME_BIN_NAME = "mme.exe" if platform.system() == "Windows" else "mme"


def check_tcp(host: str, port: int, timeout: float = 3) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False


def check_mme_health(port: int, timeout: float = 3) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Start SeAAIHub + MME + Dashboard")
    parser.add_argument("--debug", action="store_true", help="Use debug build")
    parser.add_argument("--port", type=int, default=9900, help="Hub TCP port")
    parser.add_argument("--dashboard", action="store_true", help="Also start dashboard")
    parser.add_argument("--no-mme", action="store_true", help="Skip MME gateway startup")
    parser.add_argument("--mme-port", type=int, default=9902, help="MME HTTP port")
    args = parser.parse_args()

    build = "debug" if args.debug else "release"
    binary = HUB_DIR / "target" / build / BIN_NAME

    if not binary.exists():
        print(f"Binary not found: {binary}")
        print(f"Build first: cd {HUB_DIR} && cargo build {'--release' if not args.debug else ''}".strip())
        sys.exit(1)

    # 1. SeAAIHub (Rust TCP core)
    print(f"Starting SeAAIHub ({build}) on :{args.port}...")
    subprocess.Popen(
        [str(binary), "--tcp-port", str(args.port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=str(HUB_DIR)
    )
    time.sleep(2)

    if not check_tcp("127.0.0.1", args.port):
        print("Hub FAILED to start")
        sys.exit(1)
    print(f"Hub OK: 127.0.0.1:{args.port}")

    # 2. MME Gateway (권장 접속점, Rust HTTP MCP gateway)
    if not args.no_mme:
        mme_dir = GATEWAY_DIR
        mme_binary = mme_dir / "target" / build / MME_BIN_NAME
        if mme_binary.exists():
            print(f"Starting MME on :{args.mme_port}...")
            subprocess.Popen(
                [str(mme_binary),
                 "--port", str(args.mme_port),
                 "--hub-host", "127.0.0.1",
                 "--hub-port", str(args.port)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                cwd=str(mme_dir),
            )
            # MME 초기 연결 대기 (Hub 연결 + HTTP 서버 바인딩)
            for _ in range(10):
                time.sleep(1)
                if check_mme_health(args.mme_port):
                    print(f"MME OK: http://127.0.0.1:{args.mme_port}/mcp")
                    break
            else:
                print(f"MME startup slow — check http://127.0.0.1:{args.mme_port}/health")
        else:
            print(f"MME binary not found: {mme_binary}")
            print(
                f"Build first: cd {mme_dir} && cargo build {'--release' if not args.debug else ''}".strip()
            )

    # 3. Dashboard (optional)
    if args.dashboard:
        dashboard = TOOLS_DIR / "hub-dashboard.py"
        if dashboard.exists():
            subprocess.Popen(
                [sys.executable, str(dashboard),
                 "--hub-port", str(args.port), "--web-port", "8080"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                cwd=str(TOOLS_DIR),
            )
            print("Dashboard: http://localhost:8080")
        else:
            print(f"Dashboard script not found: {dashboard}")


if __name__ == "__main__":
    main()
