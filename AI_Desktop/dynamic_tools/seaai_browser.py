import base64
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from contextlib import contextmanager
import time
import uuid
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    import ctypes
except Exception:  # pragma: no cover - optional dependency
    ctypes = None

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None

try:
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
except Exception:  # pragma: no cover - optional dependency
    webdriver = None
    EdgeOptions = None
    EdgeService = None

MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]
EDGE_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]
STATE_ROOT = Path(__file__).resolve().parents[1] / "state" / "browser"
SESSIONS_DIR = STATE_ROOT / "sessions"
OUTPUT_DIR = STATE_ROOT / "artifacts"
LOG_DIR = STATE_ROOT / "logs"
REPORT_DIR = STATE_ROOT / "reports"
ROUTES_FILE = STATE_ROOT / "routes.json"
WORKER_TARGETS = ["node", "sandbox", "remote_cdp"]
HEADLESS_FAILURE_MARKERS = [
    "WSALookupServiceBegin failed with: 10108",
    "WSALookupServiceBegin failed with: 10106",
    "BuildSecurityDescriptor",
    "platform_channel.cc:170",
    "액세스가 거부되었습니다. (0x5)",
]
EDGE_DRIVER_PATHS = [
    Path(r"D:\Tools\edgedriver_win64\msedgedriver.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedgedriver.exe"),
]
ALLOWED_DOMAINS = {
    "arxiv.org",
    "github.com",
    "huggingface.co",
    "news.ycombinator.com",
    "www.producthunt.com",
    "devpost.com",
    "www.kaggle.com",
    "reddit.com",
    "www.reddit.com",
    "stackoverflow.com",
    "vercel.com",
    "railway.app",
    "fly.io",
    "netlify.com",
    "platform.openai.com",
    "console.anthropic.com",
    "www.google.com",
    "duckduckgo.com",
}
VISIBLE_LAUNCH_ENV = "SEAII_BROWSER_ALLOW_VISIBLE"
AI_DESKTOP_ROOT = Path(__file__).resolve().parents[1]
AI_DESKTOP_EXE = AI_DESKTOP_ROOT / "ai_desktop_mcp.exe"
EXTERNAL_DOCTOR_BRIDGE_REPORT = Path(r"d:\SeAAI\Signalion\docs\AIDesktop-Doctor-Bridge-Report.json")
SEM_FAILCRITICALERRORS = 0x0001
SEM_NOGPFAULTERRORBOX = 0x0002
SEM_NOOPENFILEERRORBOX = 0x8000


def hidden_subprocess_kwargs() -> dict:
    if os.name != "nt":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return {
        "startupinfo": startupinfo,
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }


@contextmanager
def suppress_windows_error_dialogs():
    if os.name != "nt" or ctypes is None:
        yield
        return

    kernel32 = ctypes.windll.kernel32
    old_mode = kernel32.SetErrorMode(
        SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX
    )
    try:
        yield
    finally:
        kernel32.SetErrorMode(old_mode)


def visible_launch_allowed(payload: dict) -> bool:
    return bool(payload.get("allow_visible")) and os.environ.get(VISIBLE_LAUNCH_ENV) == "1"


def rust_browser_state(action: str, member: str) -> dict | None:
    if not AI_DESKTOP_EXE.exists():
        return None
    try:
        proc = subprocess.run(
            [str(AI_DESKTOP_EXE), "--browser-state", action, member],
            cwd=str(AI_DESKTOP_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            **hidden_subprocess_kwargs(),
        )
    except Exception:
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        payload = json.loads(proc.stdout.strip())
    except Exception:
        return None
    return {"ok": True, "source": "rust-control-plane", "items": payload}


def merge_recovery_advice(*groups: list[str] | None) -> list[str]:
    merged: list[str] = []
    seen = set()
    for group in groups:
        for item in group or []:
            if item not in seen:
                merged.append(item)
                seen.add(item)
    return merged



def load_external_doctor_bridge() -> dict | None:
    try:
        if not EXTERNAL_DOCTOR_BRIDGE_REPORT.exists():
            return None
        payload = json.loads(EXTERNAL_DOCTOR_BRIDGE_REPORT.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def preferred_doctor_truth(local_socket: dict, headless_probe: dict, rust_probe: dict | None, external_bridge: dict | None) -> tuple[dict, dict, str]:
    external_socket = (external_bridge or {}).get("socket_probe", {})
    external_edge = (external_bridge or {}).get("edge_probe", {})
    external_rust = ((external_bridge or {}).get("rust_doctor", {}) or {}).get("payload")
    if external_socket.get("bind") == "ok" and external_edge.get("diagnosis") == "ok":
        truth = {
            "bind": external_socket.get("bind"),
            "bind_port": (external_socket.get("endpoint") or [None, None])[1],
            "getaddrinfo": (external_rust or {}).get("socket_health", {}).get("getaddrinfo", local_socket.get("getaddrinfo")),
        }
        merged_rust = external_rust or rust_probe
        merged_headless = {
            "ok": external_edge.get("ok", False),
            "mode": "external-pwsh7-bridge",
            "diagnosis": external_edge.get("diagnosis"),
            "error": external_edge.get("message") or external_edge.get("stderr_preview"),
        }
        return truth, merged_headless, "external-pwsh7-bridge"
    return local_socket, headless_probe, "local-codex-process"

def build_recovery_commands(socket_health: dict | None, diagnosis: str | None) -> list[str]:
    commands: list[str] = []
    socket_health = socket_health or {}
    if socket_health.get("bind") != "ok":
        commands.extend([
            'netsh winsock reset',
            'netsh int ip reset',
            'shutdown /r /t 0',
        ])
    if diagnosis == "edge_timeout":
        commands.append('& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --dump-dom about:blank')
    deduped: list[str] = []
    seen = set()
    for item in commands:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def write_recovery_report(member: str, kind: str, payload: dict) -> dict:
    ensure_dirs()
    report_dir = REPORT_DIR / member
    report_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().isoformat()
    report_path = report_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}-{kind}.json"
    body = {
        "member": member,
        "kind": kind,
        "generated_at": generated_at,
        "payload": payload,
    }
    report_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "report_path": str(report_path),
        "report_exists": report_path.exists(),
        "report_generated_at": generated_at,
    }


def attach_recovery_report(member: str, kind: str, payload: dict) -> dict:
    payload.update(write_recovery_report(member, kind, payload))
    return payload


def load_target_routes() -> dict:
    routes = {
        "host": {
            "target": "host",
            "configured": True,
            "enabled": True,
            "transport": "local-edge",
            "bridge": "built-in",
            "diagnosis": None,
        },
        "sandbox": {
            "target": "sandbox",
            "configured": False,
            "enabled": False,
            "transport": "sandbox-worker",
            "bridge": "external-sandbox-worker",
            "diagnosis": "target_not_configured",
        },
        "node": {
            "target": "node",
            "configured": False,
            "enabled": False,
            "transport": "node-bridge",
            "bridge": "external-browser-worker",
            "diagnosis": "target_not_configured",
        },
        "remote_cdp": {
            "target": "remote_cdp",
            "configured": False,
            "enabled": False,
            "transport": "cdp",
            "bridge": "remote-cdp-bridge",
            "diagnosis": "target_not_configured",
        },
    }

    if ROUTES_FILE.exists():
        try:
            file_routes = json.loads(ROUTES_FILE.read_text(encoding="utf-8"))
            if isinstance(file_routes, dict):
                for key, value in file_routes.items():
                    if key in routes and isinstance(value, dict):
                        routes[key].update(value)
        except Exception:
            pass

    env_map = {
        "sandbox": ("SEAII_BROWSER_SANDBOX_ENDPOINT", "SEAII_BROWSER_SANDBOX_TOKEN"),
        "node": ("SEAII_BROWSER_NODE_ENDPOINT", "SEAII_BROWSER_NODE_TOKEN"),
        "remote_cdp": ("SEAII_BROWSER_REMOTE_CDP_URL", "SEAII_BROWSER_REMOTE_CDP_TOKEN"),
    }
    for key, (endpoint_env, token_env) in env_map.items():
        endpoint = os.environ.get(endpoint_env)
        token = os.environ.get(token_env)
        if endpoint:
            routes[key].update({
                "configured": True,
                "enabled": True,
                "endpoint": endpoint,
                "token_present": bool(token),
                "diagnosis": None,
            })
        elif token and key in routes:
            routes[key]["token_present"] = True

    return routes


def target_route_from_payload(payload: dict) -> dict:
    target = payload.get("target", "host")
    routes = load_target_routes()
    route = routes.get(target)
    if route is None:
        return {
            "target": target,
            "configured": False,
            "enabled": False,
            "transport": "unknown",
            "bridge": "unavailable",
            "diagnosis": "unknown_target",
        }
    return dict(route)


def apply_target_route(plan: dict, payload: dict) -> dict:
    route = target_route_from_payload(payload)
    target = payload.get("target", "host")
    plan["target"] = target
    plan["target_route"] = route
    plan["execution_target"] = target
    if target != "host" and route.get("configured"):
        plan["route_ready"] = True
        plan["next_bridge"] = route.get("bridge", "external-browser-worker")
        if plan.get("execution_status") == "planned":
            if plan.get("resolved_ref") is not None:
                plan["execution_mode"] = "target-routed-ref-plan"
            else:
                plan["execution_mode"] = "target-routed-plan"
    return plan


def target_route_gate(member: str, alias: str, payload: dict) -> dict | None:
    target = payload.get("target", "host")
    if target == "host":
        return None
    route = target_route_from_payload(payload)
    if route.get("configured"):
        return None
    result = structured_phase1_action(member, alias, payload, f"{target}_route_unavailable")
    result["target_route"] = route
    result["available_targets"] = load_target_routes()
    return result


def route_command(route: dict) -> list[str] | None:
    command = route.get("command")
    if isinstance(command, list):
        parts = [str(item) for item in command if str(item).strip()]
        return parts or None
    if isinstance(command, str) and command.strip():
        return [command]
    return None


def route_token_for_target(target: str) -> str | None:
    env_map = {
        "sandbox": "SEAII_BROWSER_SANDBOX_TOKEN",
        "node": "SEAII_BROWSER_NODE_TOKEN",
        "remote_cdp": "SEAII_BROWSER_REMOTE_CDP_TOKEN",
    }
    env_name = env_map.get(target)
    if not env_name:
        return None
    return os.environ.get(env_name)


def invoke_route_endpoint(route: dict, request: dict, target: str, alias: str, payload: dict) -> dict | None:
    endpoint = route.get("endpoint")
    if not endpoint or requests is None:
        return None

    headers = {"Content-Type": "application/json"}
    token = route_token_for_target(target)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(endpoint, json=request, headers=headers, timeout=int(payload.get("timeout_sec", 20)))
        response.raise_for_status()
    except Exception as exc:
        return {
            "ok": False,
            "alias": alias,
            "surface_version": "3-phase1",
            "member": request.get("member"),
            "target": target,
            "target_route": route,
            "execution_target": target,
            "diagnosis": f"{target}_route_http_error",
            "execution_mode": "endpoint-route-bridge",
            "execution_status": "blocked",
            "live_execution": False,
            "requested": payload,
            "worker_error": str(exc),
        }

    try:
        result = response.json()
    except Exception as exc:
        return {
            "ok": False,
            "alias": alias,
            "surface_version": "3-phase1",
            "member": request.get("member"),
            "target": target,
            "target_route": route,
            "execution_target": target,
            "diagnosis": f"{target}_route_invalid_json",
            "execution_mode": "endpoint-route-bridge",
            "execution_status": "blocked",
            "live_execution": False,
            "requested": payload,
            "worker_parse_error": str(exc),
            "worker_stdout": response.text,
        }

    if not isinstance(result, dict):
        result = {"ok": False, "diagnosis": f"{target}_route_invalid_payload"}
    result.setdefault("alias", alias)
    result.setdefault("surface_version", "3-phase1")
    result.setdefault("member", request.get("member"))
    result.setdefault("target", target)
    result.setdefault("execution_target", target)
    result.setdefault("requested", payload)
    result.setdefault("execution_mode", "endpoint-route-bridge")
    result["target_route"] = route
    return result


def invoke_target_route(member: str, alias: str, payload: dict) -> dict | None:
    target = payload.get("target", "host")
    if target == "host":
        return None

    route = target_route_from_payload(payload)
    if not route.get("configured"):
        return None

    request = {
        "member": member,
        "alias": alias,
        "payload": payload,
        "route": route,
    }

    endpoint_result = invoke_route_endpoint(route, request, target, alias, payload)
    if endpoint_result is not None:
        return endpoint_result

    command = route_command(route)
    if not command:
        return None

    try:
        proc = subprocess.run(
            command,
            input=json.dumps(request, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=int(payload.get("timeout_sec", 20)),
            **hidden_subprocess_kwargs(),
        )
    except Exception as exc:
        return {
            "ok": False,
            "alias": alias,
            "surface_version": "3-phase1",
            "member": member,
            "target": target,
            "target_route": route,
            "execution_target": target,
            "diagnosis": f"{target}_route_exec_error",
            "execution_mode": "command-worker-bridge",
            "execution_status": "blocked",
            "live_execution": False,
            "requested": payload,
            "worker_error": str(exc),
        }

    if proc.returncode != 0:
        return {
            "ok": False,
            "alias": alias,
            "surface_version": "3-phase1",
            "member": member,
            "target": target,
            "target_route": route,
            "execution_target": target,
            "diagnosis": f"{target}_route_exec_nonzero",
            "execution_mode": "command-worker-bridge",
            "execution_status": "blocked",
            "live_execution": False,
            "requested": payload,
            "worker_stderr": proc.stderr.strip(),
        }

    try:
        result = json.loads(proc.stdout.strip()) if proc.stdout.strip() else {}
    except Exception as exc:
        return {
            "ok": False,
            "alias": alias,
            "surface_version": "3-phase1",
            "member": member,
            "target": target,
            "target_route": route,
            "execution_target": target,
            "diagnosis": f"{target}_route_invalid_json",
            "execution_mode": "command-worker-bridge",
            "execution_status": "blocked",
            "live_execution": False,
            "requested": payload,
            "worker_stdout": proc.stdout.strip(),
            "worker_parse_error": str(exc),
        }

    if not isinstance(result, dict):
        result = {"ok": False, "diagnosis": f"{target}_route_invalid_payload"}
    result.setdefault("alias", alias)
    result.setdefault("surface_version", "3-phase1")
    result.setdefault("member", member)
    result.setdefault("target", target)
    result.setdefault("execution_target", target)
    result.setdefault("requested", payload)
    result["target_route"] = route
    return result


def rust_browser_doctor() -> dict | None:
    rust = rust_browser_state("doctor", "Signalion")
    if rust is None:
        return None
    payload = rust.get("items")
    if isinstance(payload, dict):
        return payload
    return None


def rust_browser_upload_plan(member: str, payload: dict) -> dict | None:
    if not AI_DESKTOP_EXE.exists():
        return None

    body = {
        "upload_paths": [item for item in payload.get("upload_paths", []) if isinstance(item, str)],
    }
    try:
        proc = subprocess.run(
            [str(AI_DESKTOP_EXE), "--browser-state", "upload-plan", member],
            cwd=str(AI_DESKTOP_ROOT),
            input=json.dumps(body, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            **hidden_subprocess_kwargs(),
        )
    except Exception:
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        plan = json.loads(proc.stdout.strip())
    except Exception:
        return None
    if not isinstance(plan, dict):
        return None
    plan["surface_version"] = "3-phase1"
    return plan


def rust_browser_dialog_plan(member: str, payload: dict) -> dict | None:
    if not AI_DESKTOP_EXE.exists():
        return None

    body = {
        "decision": payload.get("decision"),
        "text": payload.get("text"),
    }
    try:
        proc = subprocess.run(
            [str(AI_DESKTOP_EXE), "--browser-state", "dialog-plan", member],
            cwd=str(AI_DESKTOP_ROOT),
            input=json.dumps(body, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            **hidden_subprocess_kwargs(),
        )
    except Exception:
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        plan = json.loads(proc.stdout.strip())
    except Exception:
        return None
    if not isinstance(plan, dict):
        return None
    plan["surface_version"] = "3-phase1"
    return plan


def rust_browser_action_plan(member: str, payload: dict, inspected: dict) -> dict | None:
    if not AI_DESKTOP_EXE.exists():
        return None

    body = {
        "session_id": payload.get("session_id"),
        "tab_id": payload.get("tab_id") or payload.get("session_id") or "stateless",
        "format": payload.get("format", "aria"),
        "ref_mode": payload.get("ref_mode", "aria"),
        "text": snapshot_html_from_inspect(inspected),
        "title": inspected.get("title"),
        "action": payload.get("command", ""),
        "ref": payload.get("ref"),
        "input_text": payload.get("text"),
    }
    try:
        proc = subprocess.run(
            [str(AI_DESKTOP_EXE), "--browser-state", "act-plan", member],
            cwd=str(AI_DESKTOP_ROOT),
            input=json.dumps(body, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            **hidden_subprocess_kwargs(),
        )
    except Exception:
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        plan = json.loads(proc.stdout.strip())
    except Exception:
        return None
    if not isinstance(plan, dict):
        return None
    plan["surface_version"] = "3-phase1"
    return plan


def rust_browser_snapshot(member: str, payload: dict, inspected: dict) -> dict | None:
    if not AI_DESKTOP_EXE.exists():
        return None

    body = {
        "session_id": payload.get("session_id"),
        "tab_id": payload.get("tab_id") or payload.get("session_id") or "stateless",
        "format": payload.get("format", "aria"),
        "ref_mode": payload.get("ref_mode", "aria"),
        "text": snapshot_html_from_inspect(inspected),
        "title": inspected.get("title"),
    }
    try:
        proc = subprocess.run(
            [str(AI_DESKTOP_EXE), "--browser-state", "snapshot", member],
            cwd=str(AI_DESKTOP_ROOT),
            input=json.dumps(body, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            **hidden_subprocess_kwargs(),
        )
    except Exception:
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        snap = json.loads(proc.stdout.strip())
    except Exception:
        return None

    if not isinstance(snap, dict):
        return None
    snap["ok"] = inspected.get("ok", False)
    snap["member"] = member
    snap["surface_version"] = "3-phase1"
    snap["refs"] = snap.get("refs", [])
    snap["ref_count"] = len(snap["refs"])
    snap["inspect"] = inspected
    snap["source"] = "rust-control-plane"
    return snap


class SnapshotRefExtractor(HTMLParser):
    INTERACTIVE_TAGS = {"a", "button", "input", "select", "textarea", "option"}

    def __init__(self) -> None:
        super().__init__()
        self.records: list[dict] = []
        self.stack: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open_tag(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open_tag(tag, attrs, self_closing=True)

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        for item in self.stack:
            item["text"] = f"{item.get('text', '')} {data.strip()}".strip()

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            return
        item = self.stack[-1]
        if item.get("tag") != tag:
            return
        self.stack.pop()
        self._finalize(item)

    def _open_tag(self, tag: str, attrs_list: list[tuple[str, str | None]], self_closing: bool) -> None:
        attrs = {key: (value or "") for key, value in attrs_list}
        role = self._infer_role(tag, attrs)
        if tag not in self.INTERACTIVE_TAGS and not role:
            return
        item = {
            "tag": tag,
            "role": role or tag,
            "name": attrs.get("name") or attrs.get("id") or None,
            "type": attrs.get("type") or None,
            "aria_label": attrs.get("aria-label") or None,
            "title": attrs.get("title") or None,
            "placeholder": attrs.get("placeholder") or None,
            "href": attrs.get("href") or None,
            "text": "",
        }
        if self_closing or tag == "input":
            self._finalize(item)
        else:
            self.stack.append(item)

    def _infer_role(self, tag: str, attrs: dict) -> str | None:
        if attrs.get("role"):
            return attrs["role"]
        if tag == "a":
            return "link"
        if tag == "button":
            return "button"
        if tag == "select":
            return "select"
        if tag == "textarea":
            return "textbox"
        if tag == "option":
            return "option"
        if tag == "input":
            input_type = (attrs.get("type") or "text").lower()
            if input_type in {"button", "submit", "reset"}:
                return "button"
            if input_type in {"checkbox", "radio"}:
                return input_type
            return "textbox"
        return None

    def _finalize(self, item: dict) -> None:
        label = self._build_label(item)
        record = {
            "ref": f"r{len(self.records) + 1}",
            "tag": item.get("tag"),
            "role": item.get("role"),
            "label": label,
            "name": item.get("name"),
            "type": item.get("type"),
            "text": item.get("text") or None,
            "href": item.get("href"),
        }
        self.records.append(record)

    def _build_label(self, item: dict) -> str:
        for key in ["aria_label", "title", "placeholder", "name", "text", "role", "tag"]:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return "unknown"


def snapshot_html_from_inspect(inspected: dict) -> str:
    artifact = inspected.get("artifact")
    if artifact:
        try:
            path = Path(artifact)
            if path.exists() and path.suffix.lower() in {".html", ".htm"}:
                return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
    return inspected.get("stdout_preview", "")


def extract_snapshot_refs(html: str) -> list[dict]:
    if not html.strip():
        return []
    parser = SnapshotRefExtractor()
    parser.feed(html)
    parser.close()
    return parser.records


def resolve_snapshot_ref(snapshot: dict, ref: str | None) -> dict | None:
    if not ref:
        return None
    for item in snapshot.get("refs", []):
        if item.get("ref") == ref:
            return item
    return None


def action_snapshot_payload(payload: dict) -> dict:
    return {
        "url": payload.get("url", ""),
        "session_id": payload.get("session_id"),
        "tab_id": payload.get("tab_id"),
        "timeout_sec": int(payload.get("timeout_sec", 12)),
        "format": payload.get("format", "aria"),
        "ref_mode": payload.get("ref_mode", "aria"),
    }


def ensure_dirs() -> None:
    for path in [SESSIONS_DIR, OUTPUT_DIR, LOG_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def resolve_edge() -> str | None:
    for path in EDGE_PATHS:
        if path.exists():
            return str(path)
    return None


def resolve_edge_driver() -> str | None:
    candidate = shutil.which("msedgedriver")
    if candidate:
        return candidate
    for path in EDGE_DRIVER_PATHS:
        if path.exists():
            return str(path)
    return None


def allowed_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in {"about", "data", "file"}:
        return True
    host = parsed.netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in ALLOWED_DOMAINS)


def edge_base_args(member: str, persistent: bool = True) -> list[str]:
    ensure_dirs()
    if persistent:
        profile_dir = STATE_ROOT / "profiles" / member
    else:
        profile_dir = STATE_ROOT / "temp-profiles" / member / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    profile_dir.mkdir(parents=True, exist_ok=True)
    return [
        "--disable-gpu",
        "--no-first-run",
        "--disable-background-networking",
        "--disable-breakpad",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-sync",
        "--metrics-recording-only",
        "--mute-audio",
        "--hide-scrollbars",
        "--no-sandbox",
        f"--user-data-dir={profile_dir}",
    ]


def classify_runtime_issue(stderr: str, timed_out: bool) -> str | None:
    for marker in HEADLESS_FAILURE_MARKERS:
        if marker in stderr:
            if "WSALookupServiceBegin" in marker or "BuildSecurityDescriptor" in marker:
                return "winsock_or_network_provider_fault"
            if "platform_channel" in marker or "액세스가 거부되었습니다. (0x5)" in marker:
                return "edge_platform_channel_access_denied"
    if timed_out:
        return "edge_timeout"
    return None


def inspect_local_content(member: str, url: str) -> dict | None:
    parsed = urlparse(url)
    ensure_dirs()

    if parsed.scheme == "data":
        try:
            _, _, payload = url.partition(",")
            if ";base64" in url[: url.find(",")]:
                html = base64.b64decode(payload).decode("utf-8", errors="ignore")
            else:
                html = unquote(payload)
        except Exception as exc:
            return {"ok": False, "mode": "local-fallback", "error": f"data_url_decode_failed:{exc}"}
    elif parsed.scheme == "file":
        raw_path = unquote(parsed.path or "")
        if raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
            raw_path = raw_path[1:]
        target = Path(raw_path)
        if not target.exists():
            return {"ok": False, "mode": "local-fallback", "error": f"file_not_found:{target}"}
        html = target.read_text(encoding="utf-8", errors="ignore")
    else:
        return None

    artifact = OUTPUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{member}-local.html"
    artifact.write_text(html, encoding="utf-8", errors="ignore")
    return {
        "ok": True,
        "mode": "local-fallback",
        "html_length": len(html),
        "stdout_preview": html[:500],
        "artifact": str(artifact),
        "artifact_exists": artifact.exists(),
        "title": extract_title_from_html(html),
    }


def fetch_http(member: str, url: str, timeout_sec: int) -> dict:
    if requests is None:
        return {"ok": False, "error": "requests_not_available"}
    if not allowed_url(url):
        return {"ok": False, "error": f"url_not_allowed:{url}"}
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return {"ok": False, "error": f"http_fallback_not_supported:{parsed.scheme}"}

    try:
        response = requests.get(
            url,
            timeout=timeout_sec,
            headers={"User-Agent": f"SeAAI-AI_Desktop-v2/{member}"},
        )
        response.raise_for_status()
        html = response.text
        artifact = OUTPUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{member}-inspect.html"
        artifact.write_text(html, encoding="utf-8", errors="ignore")
        return {
            "ok": True,
            "mode": "http-fallback",
            "status_code": response.status_code,
            "html_length": len(html),
            "stdout_preview": html[:500],
            "artifact": str(artifact),
            "artifact_exists": artifact.exists(),
            "title": extract_title_from_html(html),
        }
    except Exception as exc:
        return {"ok": False, "mode": "http-fallback", "error": str(exc)}


def selenium_driver() -> tuple[object | None, str | None]:
    if webdriver is None or EdgeOptions is None or EdgeService is None:
        return None, "selenium_not_available"
    driver_path = resolve_edge_driver()
    if not driver_path:
        return None, "msedgedriver_not_found"

    try:
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-background-networking")
        service = EdgeService(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=options)
        return driver, None
    except Exception as exc:
        return None, str(exc)


def selenium_preflight() -> dict:
    driver_path = resolve_edge_driver()
    status = {
        "driver_path": driver_path,
        "driver_exists": bool(driver_path),
        "selenium_module": webdriver is not None and EdgeOptions is not None and EdgeService is not None,
    }
    if not status["selenium_module"]:
        status["ok"] = False
        status["error"] = "selenium_not_available"
        return status
    if not driver_path:
        status["ok"] = False
        status["error"] = "msedgedriver_not_found"
        return status
    status["ok"] = True
    return status


def classify_selenium_issue(error: str | None) -> str | None:
    if not error:
        return None
    if "Unable to bind to IPv4 or IPv6" in error or "Can't find free port" in error:
        return "socket_bind_failure"
    if "msedgedriver_not_found" in error:
        return "driver_missing"
    if "selenium_not_available" in error:
        return "selenium_not_available"
    return None


def build_recovery_advice(
    socket_health: dict | None,
    selenium_info: dict | None,
    headless_diagnosis: str | None,
    root_cause: str | None = None,
) -> list[str]:
    advice: list[str] = []
    socket_health = socket_health or {}
    selenium_info = selenium_info or {}
    diagnosis = root_cause or headless_diagnosis

    if socket_health.get("getaddrinfo") != "ok":
        advice.append("Fix DNS resolution in the current host session before retrying external navigation.")
    if socket_health.get("bind") != "ok":
        advice.append("Repair Winsock/socket provider state for this process; local bind must succeed before Selenium or CDP fallback can work.")
    if selenium_info.get("driver_exists") is not True:
        advice.append("Install or expose msedgedriver.exe on PATH or D:/Tools/edgedriver_win64.")
    if selenium_info.get("selenium_module") is not True:
        advice.append("Install the selenium Python package in the runtime used by seaai_browser.py.")
    if diagnosis == "edge_timeout":
        advice.append("Retry Edge headless after verifying the current session can run msedge --headless --dump-dom about:blank without hanging.")
    if diagnosis == "winsock_or_network_provider_fault":
        advice.append("Reset Winsock/TCP stack and restart the operator session if this process still carries stale network provider state.")
    if diagnosis == "edge_platform_channel_access_denied":
        advice.append("Inspect security software, profile locks, or host IPC restrictions blocking Edge platform channels.")
    if diagnosis == "socket_bind_failure":
        advice.append("Treat this as a host blocker; Selenium cannot allocate a free local port until socket bind succeeds in this exact process context.")

    deduped: list[str] = []
    seen = set()
    for item in advice:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def selenium_inspect(member: str, url: str, timeout_sec: int) -> dict:
    driver, error = selenium_driver()
    if driver is None:
        return {"ok": False, "mode": "selenium", "error": error}

    try:
        driver.set_page_load_timeout(timeout_sec)
        driver.get(url)
        html = driver.page_source or ""
        artifact = OUTPUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{member}-selenium.html"
        artifact.write_text(html, encoding="utf-8", errors="ignore")
        return {
            "ok": True,
            "mode": "selenium",
            "stdout_preview": html[:500],
            "artifact": str(artifact),
            "artifact_exists": artifact.exists(),
            "title": driver.title or extract_title_from_html(html),
        }
    except Exception as exc:
        return {"ok": False, "mode": "selenium", "error": str(exc)}
    finally:
        driver.quit()


def selenium_screenshot(member: str, url: str, timeout_sec: int, width: int, height: int) -> dict:
    driver, error = selenium_driver()
    if driver is None:
        return {"ok": False, "mode": "selenium", "error": error}

    target = OUTPUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{member}-selenium.png"
    try:
        driver.set_page_load_timeout(timeout_sec)
        driver.set_window_size(width, height)
        driver.get(url)
        ok = driver.save_screenshot(str(target))
        return {
            "ok": bool(ok) and target.exists(),
            "mode": "selenium",
            "artifact": str(target),
            "artifact_exists": target.exists(),
            "artifact_size": target.stat().st_size if target.exists() else 0,
            "title": driver.title,
        }
    except Exception as exc:
        return {"ok": False, "mode": "selenium", "error": str(exc), "artifact": str(target)}
    finally:
        driver.quit()


def write_log(prefix: str, content: str) -> str:
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = LOG_DIR / f"{stamp}-{prefix}.log"
    path.write_text(content, encoding="utf-8", errors="ignore")
    return str(path)


def socket_doctor() -> dict:
    result = {}
    try:
        socket.getaddrinfo("127.0.0.1", 80)
        result["getaddrinfo"] = "ok"
    except OSError as exc:
        result["getaddrinfo"] = f"error:{exc.winerror or exc.errno}"
        result["message"] = str(exc)

    probe = None
    try:
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        probe = sock.getsockname()[1]
        sock.close()
        result["bind"] = "ok"
        result["bind_port"] = probe
    except OSError as exc:
        result["bind"] = f"error:{exc.winerror or exc.errno}"
        result["bind_message"] = str(exc)
    return result


def doctor(member: str) -> dict:
    edge = resolve_edge()
    ensure_dirs()
    probe = run_edge_once(member, "about:blank", ["--dump-dom"], 5) if edge else {"ok": False, "error": "edge_not_found"}
    selenium_info = selenium_preflight()
    local_socket_health = socket_doctor()
    local_headless_probe = {
        "ok": probe.get("ok", False),
        "mode": probe.get("mode"),
        "diagnosis": probe.get("diagnosis"),
        "error": probe.get("error"),
    }
    rust_probe = rust_browser_doctor()
    external_bridge = load_external_doctor_bridge()
    socket_health, headless_probe, truth_source = preferred_doctor_truth(local_socket_health, local_headless_probe, rust_probe, external_bridge)
    headless_diagnosis = headless_probe.get("diagnosis")
    python_advice = build_recovery_advice(socket_health, selenium_info, headless_diagnosis)
    rust_advice = rust_probe.get("recovery_advice", []) if isinstance(rust_probe, dict) else []
    bridge_advice = ((external_bridge or {}).get("resolution", {}) or {}).get("recommended_method", [])
    result = {
        "member": member,
        "edge_path": edge,
        "msedgedriver_path": resolve_edge_driver(),
        "edge_exists": bool(edge),
        "playwright_module": importlib.util.find_spec("playwright") is not None,
        "selenium_module": importlib.util.find_spec("selenium") is not None,
        "requests_module": importlib.util.find_spec("requests") is not None,
        "socket_health": socket_health,
        "local_socket_health": local_socket_health,
        "selenium_preflight": selenium_info,
        "headless_probe": headless_probe,
        "local_headless_probe": local_headless_probe,
        "rust_probe": rust_probe,
        "external_bridge": external_bridge,
        "truth_source": truth_source,
        "recovery_advice": merge_recovery_advice(python_advice, rust_advice, bridge_advice),
        "recovery_commands": build_recovery_commands(socket_health, headless_diagnosis),
        "routes": load_target_routes(),
        "state_root": str(STATE_ROOT),
        "mode": "edge-cli",
    }
    return attach_recovery_report(member, "doctor", result)


def run_edge_once(member: str, url: str, extra_args: list[str], timeout_sec: int) -> dict:
    edge = resolve_edge()
    if not edge:
        return {"ok": False, "error": "edge_not_found"}
    if not allowed_url(url):
        return {"ok": False, "error": f"url_not_allowed:{url}"}

    cmd = [edge, "--headless", *edge_base_args(member, persistent=False), *extra_args, url]
    try:
        with suppress_windows_error_dialogs():
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **hidden_subprocess_kwargs(),
            )
        try:
            stdout_b, stderr_b = proc.communicate(timeout=timeout_sec)
            returncode = proc.returncode
            timed_out = False
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_b, stderr_b = proc.communicate(timeout=3)
            returncode = proc.returncode
            timed_out = True

        stdout = stdout_b.decode("utf-8", errors="replace")
        stderr = stderr_b.decode("utf-8", errors="replace")
        out_log = write_log("browser-stdout", stdout) if stdout else None
        err_log = write_log("browser-stderr", stderr) if stderr else None
        success = (returncode == 0 and bool(stdout or any("--screenshot=" in arg for arg in extra_args))) and not timed_out
        diagnosis = classify_runtime_issue(stderr, timed_out)
        return {
            "ok": success,
            "mode": "edge-cli",
            "returncode": returncode,
            "stdout_preview": stdout[:500],
            "stderr_preview": stderr[:500],
            "stdout_log": out_log,
            "stderr_log": err_log,
            "timed_out": timed_out,
            "diagnosis": diagnosis,
        }
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace")
        out_log = write_log("browser-timeout-stdout", stdout) if stdout else None
        err_log = write_log("browser-timeout-stderr", stderr) if stderr else None
        return {
            "ok": False,
            "mode": "edge-cli",
            "error": "timeout",
            "timed_out": True,
            "stdout_preview": stdout[:500],
            "stderr_preview": stderr[:500],
            "stdout_log": out_log,
            "stderr_log": err_log,
            "diagnosis": classify_runtime_issue(stderr, True),
        }


def inspect(member: str, url: str, timeout_sec: int) -> dict:
    local_result = inspect_local_content(member, url)
    if local_result is not None:
        return local_result

    result = run_edge_once(member, url, ["--dump-dom"], timeout_sec)
    if result.get("ok"):
        html = result.get("stdout_preview", "")
        result["title"] = extract_title_from_html(html)
        return result

    selenium_result = selenium_inspect(member, url, timeout_sec)
    if selenium_result.get("ok"):
        selenium_result["fallback_reason"] = result.get("diagnosis") or result.get("error")
        return selenium_result

    http_result = fetch_http(member, url, timeout_sec)
    if http_result.get("ok"):
        http_result["fallback_reason"] = result.get("diagnosis") or result.get("error")
        http_result["edge_failure"] = result
        http_result["selenium_failure"] = selenium_result
        return http_result

    socket_health = socket_doctor()
    selenium_info = selenium_preflight()
    rust_probe = rust_browser_doctor()
    result["selenium_failure"] = selenium_result
    result["selenium_diagnosis"] = classify_selenium_issue(selenium_result.get("error"))
    result["http_failure"] = http_result
    result["rust_probe"] = rust_probe
    result["recovery_advice"] = merge_recovery_advice(
        build_recovery_advice(socket_health, selenium_info, result.get("diagnosis"), result.get("selenium_diagnosis") or result.get("diagnosis") or result.get("error")),
        rust_probe.get("recovery_advice", []) if isinstance(rust_probe, dict) else [],
    )
    result["recovery_commands"] = build_recovery_commands(socket_health, result.get("diagnosis"))
    return result


def extract_title_from_html(html: str) -> str | None:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def screenshot(member: str, url: str, timeout_sec: int, width: int, height: int) -> dict:
    ensure_dirs()
    target = OUTPUT_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{member}.png"
    result = run_edge_once(
        member,
        url,
        [f"--window-size={width},{height}", f"--screenshot={target}"],
        timeout_sec,
    )
    result["artifact"] = str(target)
    result["artifact_exists"] = target.exists()
    result["artifact_size"] = target.stat().st_size if target.exists() else 0
    result["ok"] = bool(result.get("ok")) and target.exists()
    if result.get("ok"):
        return attach_recovery_report(member, "screenshot", result)

    selenium_result = selenium_screenshot(member, url, timeout_sec, width, height)
    if selenium_result.get("ok"):
        selenium_result["fallback_reason"] = result.get("diagnosis") or result.get("error")
        selenium_result["edge_failure"] = result
        return attach_recovery_report(member, "screenshot", selenium_result)

    socket_health = socket_doctor()
    selenium_info = selenium_preflight()
    rust_probe = rust_browser_doctor()
    result["selenium_failure"] = selenium_result
    result["selenium_diagnosis"] = classify_selenium_issue(selenium_result.get("error"))
    result["degraded_mode"] = "launch_only"
    result["recommended_action"] = "Use launch to open an interactive session until host headless Edge is repaired."
    result["root_cause"] = result.get("selenium_diagnosis") or result.get("diagnosis") or result.get("error")
    result["socket_health"] = socket_health
    result["selenium_preflight"] = selenium_info
    result["rust_probe"] = rust_probe
    result["recovery_advice"] = merge_recovery_advice(
        build_recovery_advice(socket_health, selenium_info, result.get("diagnosis"), result.get("root_cause")),
        rust_probe.get("recovery_advice", []) if isinstance(rust_probe, dict) else [],
    )
    result["recovery_commands"] = build_recovery_commands(socket_health, result.get("diagnosis"))
    return attach_recovery_report(member, "screenshot", result)


def launch(member: str, url: str, payload: dict) -> dict:
    edge = resolve_edge()
    if not edge:
        return {"ok": False, "error": "edge_not_found"}
    if not allowed_url(url):
        return {"ok": False, "error": f"url_not_allowed:{url}"}
    if not visible_launch_allowed(payload):
        return {
            "ok": False,
            "error": "visible_launch_disabled",
            "hint": "Set SEAII_BROWSER_ALLOW_VISIBLE=1 and pass allow_visible=true only when a visible browser window is intentionally required.",
        }
    ensure_dirs()
    session_id = str(uuid.uuid4())
    with suppress_windows_error_dialogs():
        proc = subprocess.Popen([edge, *edge_base_args(member, persistent=True), url])
    session = {
        "session_id": session_id,
        "member": member,
        "url": url,
        "pid": proc.pid,
        "created_at": datetime.now().isoformat(),
        "mode": "interactive-launch",
    }
    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, **session, "session_file": str(path)}


def load_worker_sessions(member: str) -> list[dict]:
    sessions = []
    for target in WORKER_TARGETS:
        worker_dir = STATE_ROOT / f"worker-{target}" / "sessions"
        if not worker_dir.exists():
            continue
        for path in sorted(worker_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            owner = data.get("member")
            if owner not in {None, member}:
                continue
            sessions.append(data)
    return sessions

def merge_browser_sessions(primary: list[dict], secondary: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for item in primary + secondary:
        session_id = item.get("session_id")
        if session_id in seen:
            continue
        merged.append(item)
        if session_id:
            seen.add(session_id)
    return merged


def list_sessions(member: str) -> dict:
    ensure_dirs()
    node_sessions = load_worker_sessions(member)
    rust = rust_browser_state("sessions", member)
    if rust is not None:
        sessions = merge_browser_sessions(rust.get("items", []), node_sessions)
        source = "hybrid-control-plane" if node_sessions else "rust-control-plane"
        return {"ok": True, "member": member, "count": len(sessions), "sessions": sessions, "source": source}

    sessions = []
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("member") == member:
            sessions.append(data)
    sessions = merge_browser_sessions(sessions, node_sessions)
    source = "hybrid-python-fallback" if node_sessions else "python-fallback"
    return {"ok": True, "member": member, "count": len(sessions), "sessions": sessions, "source": source}


def list_profiles(member: str) -> dict:
    ensure_dirs()
    rust = rust_browser_state("profiles", member)
    if rust is not None:
        payload = rust.get("items", {})
        persistent = payload.get("persistent", [])
        temporary = payload.get("temporary", [])
        return {
            "ok": True,
            "member": payload.get("member", member),
            "count": len(persistent) + len(temporary),
            "persistent": persistent,
            "temporary": temporary,
            "source": "rust-control-plane",
        }

    profiles_root = STATE_ROOT / "profiles"
    temp_root = STATE_ROOT / "temp-profiles"
    persistent = []
    temporary = []

    if profiles_root.exists():
        for path in sorted(profiles_root.iterdir()):
            if path.is_dir():
                persistent.append({
                    "name": path.name,
                    "path": str(path),
                    "member_owned": path.name == member,
                })

    member_temp = temp_root / member
    if member_temp.exists():
        for path in sorted(member_temp.iterdir()):
            if path.is_dir():
                temporary.append({
                    "name": path.name,
                    "path": str(path),
                    "member_owned": True,
                })

    return {
        "ok": True,
        "member": member,
        "count": len(persistent) + len(temporary),
        "persistent": persistent,
        "temporary": temporary,
        "source": "python-fallback",
    }


def browser_status(member: str, payload: dict) -> dict:
    diag = doctor(member)
    sessions = list_sessions(member)
    profiles = list_profiles(member)
    return {
        "ok": True,
        "member": member,
        "target": payload.get("target", "host"),
        "surface_version": "3-phase1",
        "doctor": diag,
        "sessions": sessions,
        "profiles": profiles,
        "routes": load_target_routes(),
        "degraded": not diag.get("headless_probe", {}).get("ok", False),
        "capabilities": {
            "aliases": ["status", "start", "stop", "profiles", "tabs", "open", "focus", "navigate", "snapshot", "act", "upload", "dialog"],
            "supports_snapshot_refs": True,
            "supports_stateful_navigation": True,
            "supports_visible_launch": True,
            "supports_phase1_structured_actions": True,
            "supports_ref_validated_actions": True,
            "supports_target_routing": True,
        },
    }


def browser_tabs(member: str) -> dict:
    rust = rust_browser_state("tabs", member)
    rust_tabs = rust.get("items", []) if rust is not None else []
    node_sessions = load_worker_sessions(member)
    node_tabs = []
    for session in node_sessions:
        node_tabs.append({
            "tab_id": session.get("session_id"),
            "session_id": session.get("session_id"),
            "url": session.get("url"),
            "title": session.get("title"),
            "active": True,
            "mode": "node-command-worker",
            "target": session.get("target", "node"),
        })
    if rust is not None:
        tabs = merge_browser_sessions(rust_tabs, node_tabs)
        source = "hybrid-control-plane" if node_tabs else "rust-control-plane"
        return {"ok": True, "member": member, "count": len(tabs), "tabs": tabs, "limited_mode": "session-backed", "source": source}

    sessions = list_sessions(member)
    tabs = []
    for session in sessions.get("sessions", []):
        tabs.append({
            "tab_id": session.get("session_id"),
            "session_id": session.get("session_id"),
            "url": session.get("url"),
            "title": session.get("title"),
            "active": session.get("status") != "closed",
            "mode": session.get("mode") or "session-backed",
            "target": session.get("target", "host"),
        })
    source = sessions.get("source", "python-fallback")
    return {"ok": True, "member": member, "count": len(tabs), "tabs": tabs, "limited_mode": "session-backed", "source": source}


def find_session_record(member: str, session_id: str) -> tuple[Path | None, dict | None]:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None, None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("member") != member:
        return path, None
    return path, data


def browser_snapshot(member: str, payload: dict) -> dict:
    inspected = inspect(member, payload.get("url", ""), int(payload.get("timeout_sec", 12)))
    html = snapshot_html_from_inspect(inspected)
    rust = rust_browser_snapshot(member, payload, inspected)
    if rust is not None:
        return rust

    refs = extract_snapshot_refs(html)
    return {
        "ok": inspected.get("ok", False),
        "member": member,
        "surface_version": "3-phase1",
        "snapshot_id": str(uuid.uuid4()),
        "session_id": payload.get("session_id"),
        "tab_id": payload.get("tab_id") or payload.get("session_id") or "stateless",
        "format": payload.get("format", "aria"),
        "ref_mode": payload.get("ref_mode", "aria"),
        "refs": refs,
        "ref_count": len(refs),
        "text": html,
        "title": inspected.get("title"),
        "inspect": inspected,
        "source": "python-fallback",
    }


def browser_start(member: str, payload: dict) -> dict:
    result = launch(member, payload.get("url", "about:blank"), payload)
    result["alias"] = "start"
    result["surface_version"] = "3-phase1"
    return result


def browser_stop(member: str, session_id: str) -> dict:
    result = close_session(member, session_id)
    result["alias"] = "stop"
    result["surface_version"] = "3-phase1"
    return result


def browser_open(member: str, payload: dict) -> dict:
    result = launch(member, payload.get("url", "about:blank"), payload)
    result["alias"] = "open"
    result["surface_version"] = "3-phase1"
    return result


def browser_focus(member: str, session_id: str) -> dict:
    path, data = find_session_record(member, session_id)
    if path is None:
        return {"ok": False, "error": f"session_not_found:{session_id}", "alias": "focus", "surface_version": "3-phase1"}
    if data is None:
        return {"ok": False, "error": "member_session_mismatch", "alias": "focus", "surface_version": "3-phase1"}
    return {
        "ok": True,
        "alias": "focus",
        "surface_version": "3-phase1",
        "limited_mode": "session-metadata-only",
        "focused": data.get("status") != "closed",
        "session": data,
        "session_file": str(path),
    }


def browser_navigate(member: str, payload: dict) -> dict:
    route_block = target_route_gate(member, "navigate", payload)
    if route_block is not None:
        return route_block

    delegated = invoke_target_route(member, "navigate", payload)
    if delegated is not None:
        return delegated

    target = payload.get("target", "host")
    inspected = inspect(member, payload.get("url", ""), int(payload.get("timeout_sec", 12)))
    result = {
        "ok": inspected.get("ok", False),
        "alias": "navigate",
        "surface_version": "3-phase1",
        "member": member,
        "target": target,
        "session_id": payload.get("session_id"),
        "tab_id": payload.get("tab_id") or payload.get("session_id"),
        "url": payload.get("url", ""),
        "limited_mode": "stateless-navigate",
        "inspect": inspected,
    }
    if payload.get("session_id"):
        _path, session = find_session_record(member, payload.get("session_id", ""))
        if session is not None:
            result["session"] = session
    return apply_target_route(result, payload)


def structured_phase1_action(member: str, alias: str, payload: dict, diagnosis: str) -> dict:
    diag = doctor(member)
    return {
        "ok": False,
        "alias": alias,
        "surface_version": "3-phase1",
        "member": member,
        "target": payload.get("target", "host"),
        "target_route": target_route_from_payload(payload),
        "session_id": payload.get("session_id"),
        "tab_id": payload.get("tab_id") or payload.get("session_id"),
        "diagnosis": diagnosis,
        "limited_mode": "structured-degraded",
        "requested": payload,
        "recovery_advice": diag.get("recovery_advice", []),
        "doctor": {
            "socket_health": diag.get("socket_health", {}),
            "headless_probe": diag.get("headless_probe", {}),
            "selenium_preflight": diag.get("selenium_preflight", {}),
            "routes": diag.get("routes", {}),
        },
    }


def browser_act(member: str, payload: dict) -> dict:
    supported_commands = ["click", "type", "press", "select", "wait", "evaluate"]
    command = payload.get("command")
    if command not in supported_commands:
        result = structured_phase1_action(member, "act", payload, "unsupported_browser_action_command")
        result["supported_commands"] = supported_commands
        return result

    route_block = target_route_gate(member, "act", payload)
    if route_block is not None:
        route_block["supported_commands"] = supported_commands
        return route_block

    delegated = invoke_target_route(member, "act", payload)
    if delegated is not None:
        delegated.setdefault("supported_commands", supported_commands)
        return delegated

    inspected = {"ok": True, "title": None, "stdout_preview": ""}
    if payload.get("url"):
        inspected = inspect(member, payload.get("url", ""), int(payload.get("timeout_sec", 12)))

    rust_plan = rust_browser_action_plan(member, payload, inspected)
    if rust_plan is not None:
        rust_plan["alias"] = "act"
        rust_plan["member"] = member
        rust_plan["command"] = command
        rust_plan["requested"] = payload
        if rust_plan.get("ok") is False and rust_plan.get("diagnosis") == "action_ref_not_found":
            snapshot = browser_snapshot(member, action_snapshot_payload(payload)) if payload.get("url") else {"snapshot_id": None, "ref_count": 0, "refs": []}
            rust_plan["snapshot"] = {
                "snapshot_id": snapshot.get("snapshot_id"),
                "ref_count": snapshot.get("ref_count", 0),
                "refs": snapshot.get("refs", []),
            }
        return apply_target_route(rust_plan, payload)

    if command in {"wait", "evaluate"}:
        return apply_target_route({
            "ok": True,
            "alias": "act",
            "surface_version": "3-phase1",
            "member": member,
            "command": command,
            "execution_mode": "stateless-action-plan",
            "execution_status": "planned",
            "live_execution": False,
            "next_bridge": "live-browser-required",
            "requested": payload,
        }, payload)

    if not payload.get("url"):
        result = structured_phase1_action(member, "act", payload, "browser_action_surface_not_yet_landed")
        result["supported_commands"] = supported_commands
        return result

    snapshot = browser_snapshot(member, action_snapshot_payload(payload))
    resolved_ref = resolve_snapshot_ref(snapshot, payload.get("ref"))
    if resolved_ref is None:
        result = structured_phase1_action(member, "act", payload, "action_ref_not_found")
        result["supported_commands"] = supported_commands
        result["snapshot"] = {
            "snapshot_id": snapshot.get("snapshot_id"),
            "ref_count": snapshot.get("ref_count", 0),
            "refs": snapshot.get("refs", []),
        }
        return result

    return apply_target_route({
        "ok": True,
        "alias": "act",
        "surface_version": "3-phase1",
        "member": member,
        "command": command,
        "ref": payload.get("ref"),
        "resolved_ref": resolved_ref,
        "snapshot_id": snapshot.get("snapshot_id"),
        "execution_mode": "stateless-ref-validated",
        "execution_status": "planned",
        "live_execution": False,
        "next_bridge": "live-browser-required",
        "input_text": payload.get("text"),
        "requested": payload,
    }, payload)


def browser_upload(member: str, payload: dict) -> dict:
    route_block = target_route_gate(member, "upload", payload)
    if route_block is not None:
        route_block["supported_mode"] = "single_or_multi_path_placeholder"
        return route_block

    delegated = invoke_target_route(member, "upload", payload)
    if delegated is not None:
        delegated.setdefault("supported_mode", "single_or_multi_path_placeholder")
        return delegated

    rust_plan = rust_browser_upload_plan(member, payload)
    if rust_plan is not None:
        rust_plan["alias"] = "upload"
        rust_plan["member"] = member
        rust_plan["requested"] = payload
        return apply_target_route(rust_plan, payload)

    paths = [Path(item) for item in payload.get("upload_paths", []) if isinstance(item, str) and item.strip()]
    if not paths:
        result = structured_phase1_action(member, "upload", payload, "browser_upload_surface_not_yet_landed")
        result["supported_mode"] = "single_or_multi_path_placeholder"
        return result

    existing = [str(path) for path in paths if path.exists()]
    missing = [str(path) for path in paths if not path.exists()]
    return apply_target_route({
        "ok": len(existing) > 0 and not missing,
        "alias": "upload",
        "surface_version": "3-phase1",
        "member": member,
        "execution_mode": "validated-upload-plan",
        "execution_status": "planned" if existing else "blocked",
        "live_execution": False,
        "next_bridge": "live-browser-required",
        "existing_paths": existing,
        "missing_paths": missing,
        "requested": payload,
    }, payload)


def browser_dialog(member: str, payload: dict) -> dict:
    route_block = target_route_gate(member, "dialog", payload)
    if route_block is not None:
        route_block["supported_decisions"] = ["accept", "dismiss"]
        return route_block

    delegated = invoke_target_route(member, "dialog", payload)
    if delegated is not None:
        delegated.setdefault("supported_decisions", ["accept", "dismiss"])
        return delegated

    rust_plan = rust_browser_dialog_plan(member, payload)
    if rust_plan is not None:
        rust_plan["alias"] = "dialog"
        rust_plan["member"] = member
        rust_plan["requested"] = payload
        return apply_target_route(rust_plan, payload)

    decision = payload.get("decision")
    if decision not in {"accept", "dismiss"}:
        result = structured_phase1_action(member, "dialog", payload, "invalid_dialog_decision")
        result["supported_decisions"] = ["accept", "dismiss"]
        return result
    return apply_target_route({
        "ok": True,
        "alias": "dialog",
        "surface_version": "3-phase1",
        "member": member,
        "decision": decision,
        "execution_mode": "decision-prepared",
        "execution_status": "planned",
        "live_execution": False,
        "next_bridge": "live-browser-required",
        "requested": payload,
    }, payload)


def close_session(member: str, session_id: str) -> dict:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return {"ok": False, "error": f"session_not_found:{session_id}"}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("member") != member:
        return {"ok": False, "error": "member_session_mismatch"}
    pid = int(data["pid"])
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=10, **hidden_subprocess_kwargs())
        else:
            os.kill(pid, 15)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "session_id": session_id}
    data["closed_at"] = datetime.now().isoformat()
    data["status"] = "closed"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "session_id": session_id, "pid": pid}


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")
    member = payload.get("member")

    if member not in MEMBERS:
        result = {"ok": False, "error": f"unknown_member:{member}"}
    elif action == "doctor":
        result = doctor(member)
    elif action == "status":
        result = browser_status(member, payload)
    elif action == "profiles":
        result = list_profiles(member)
    elif action == "tabs":
        result = browser_tabs(member)
    elif action == "inspect":
        result = inspect(member, payload.get("url", ""), int(payload.get("timeout_sec", 12)))
    elif action == "snapshot":
        result = browser_snapshot(member, payload)
    elif action == "navigate":
        result = browser_navigate(member, payload)
    elif action == "act":
        result = browser_act(member, payload)
    elif action == "upload":
        result = browser_upload(member, payload)
    elif action == "dialog":
        result = browser_dialog(member, payload)
    elif action == "extract_title":
        inspected = inspect(member, payload.get("url", ""), int(payload.get("timeout_sec", 12)))
        result = {"ok": inspected.get("ok", False), "title": extract_title_from_html(inspected.get("stdout_preview", "")), "inspect": inspected}
    elif action == "screenshot":
        result = screenshot(
            member,
            payload.get("url", ""),
            int(payload.get("timeout_sec", 12)),
            int(payload.get("width", 1280)),
            int(payload.get("height", 720)),
        )
    elif action == "launch":
        result = launch(member, payload.get("url", ""), payload)
    elif action == "start":
        result = browser_start(member, payload)
    elif action == "open":
        result = browser_open(member, payload)
    elif action == "focus":
        result = browser_focus(member, payload.get("session_id", ""))
    elif action == "list_sessions":
        result = list_sessions(member)
    elif action == "close_session":
        result = close_session(member, payload.get("session_id", ""))
    elif action == "stop":
        result = browser_stop(member, payload.get("session_id", ""))
    else:
        result = {"ok": False, "error": f"unknown_action:{action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()












