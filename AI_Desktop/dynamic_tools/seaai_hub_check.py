"""
SeAAI Hub Check Tool
Hub 상태, 로그, 긴급정지 플래그 확인
"""
import sys
import json
import socket
import subprocess
from pathlib import Path

SEAAI_ROOT = Path("D:/SeAAI")
HUB_ROOT = SEAAI_ROOT / "SeAAIHub"
HUB_PORT = 9900

def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def check_process() -> dict:
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq SeAAIHub.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        running = "SeAAIHub.exe" in result.stdout
        return {"running": running, "raw": result.stdout.strip()[:200]}
    except Exception as e:
        return {"running": False, "error": str(e)}

def hub_status() -> dict:
    proc = check_process()
    port_open = check_port("127.0.0.1", HUB_PORT)

    return {
        "process": proc,
        "port_9900": port_open,
        "recommendation": (
            "Hub running on port 9900" if port_open else
            "Hub not running — start with hub-start.ps1"
        ),
        "hub_exe": str(HUB_ROOT / "target/debug/SeAAIHub.exe")
    }

def read_log(n_lines: int = 50) -> dict:
    logs_dir = HUB_ROOT / "logs"
    if not logs_dir.exists():
        return {"error": "Logs directory not found"}

    log_files = sorted(logs_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return {"error": "No log files found"}

    latest = log_files[0]
    try:
        lines = latest.read_text(encoding="utf-8").splitlines()
        recent = lines[-n_lines:]
        entries = []
        for line in recent:
            try:
                entries.append(json.loads(line))
            except:
                entries.append({"raw": line})
        return {
            "log_file": latest.name,
            "total_lines": len(lines),
            "showing": len(recent),
            "entries": entries
        }
    except Exception as e:
        return {"error": str(e)}

def check_emergency_stop() -> dict:
    flag_path = SEAAI_ROOT / "SharedSpace/hub-readiness/EMERGENCY_STOP.flag"
    exists = flag_path.exists()
    content = ""
    if exists:
        try:
            content = flag_path.read_text(encoding="utf-8")
        except:
            content = "(읽기 실패)"
    return {
        "flag_exists": exists,
        "flag_path": str(flag_path),
        "content": content,
        "status": "[STOP] EMERGENCY STOP ACTIVE" if exists else "[OK] Normal — no emergency stop"
    }

def read_protocol() -> dict:
    proto_file = HUB_ROOT / "PROTOCOL-SeAAIChat-v1.0.md"
    if not proto_file.exists():
        return {"error": "Protocol file not found"}
    content = proto_file.read_text(encoding="utf-8")
    return {
        "file": proto_file.name,
        "size": len(content),
        "preview": content[:1000] + ("..." if len(content) > 1000 else "")
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No payload"}))
        return

    try:
        payload = json.loads(sys.argv[1])
    except Exception as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        return

    action = payload.get("action")

    if action == "status":
        result = hub_status()
    elif action == "read_log":
        n = payload.get("log_lines", 50)
        result = read_log(n)
    elif action == "check_emergency_stop":
        result = check_emergency_stop()
    elif action == "read_protocol":
        result = read_protocol()
    else:
        result = {"error": f"Unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")

if __name__ == "__main__":
    main()
