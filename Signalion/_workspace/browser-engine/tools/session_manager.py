#!/usr/bin/env python3
"""
브라우저 세션 영속화 관리자
Playwright의 persistent context를 활용하여 로그인 세션을 저장/재사용.

사용법 (Claude Code 내에서):
    1. session_manager.py는 직접 실행하지 않음
    2. Playwright MCP를 통해 아래 패턴으로 사용:

    # 세션 저장 (로그인 완료 후)
    browser_evaluate("async () => JSON.stringify(await page.context().storageState())")
    → 결과를 signal-store/auth/{service}.json에 Write

    # 세션 로드 (다음 접속 시)
    → Playwright launch 시 --user-data-dir 또는 storageState 옵션 사용

이 파일은 세션 파일 관리 유틸리티를 제공한다.
"""
import json
from datetime import datetime
from pathlib import Path

AUTH_DIR = Path("D:/SeAAI/Signalion/signal-store/auth")
LOG_FILE = Path("D:/SeAAI/Signalion/_workspace/browser-engine/logs/session-log.jsonl")

# 서비스별 로그인 페이지 URL
SERVICE_LOGIN_URLS = {
    "x": "https://x.com/login",
    "github": "https://github.com/login",
    "reddit": "https://www.reddit.com/login",
    "producthunt": "https://www.producthunt.com/login",
    "devpost": "https://devpost.com/users/login",
    "kaggle": "https://www.kaggle.com/account/login",
    "vercel": "https://vercel.com/login",
}

# 서비스별 로그인 확인 JS (로그인 상태이면 true 반환)
SERVICE_AUTH_CHECK_JS = {
    "x": "() => !!document.querySelector('[data-testid=\"SideNav_AccountSwitcher_Button\"]')",
    "github": "() => !!document.querySelector('.AppHeader-user')",
    "reddit": "() => !document.querySelector('a[href*=\"login\"]')",
    "producthunt": "() => !!document.querySelector('button[class*=\"user\"]') || !document.querySelector('button:has-text(\"Sign in\")')",
    "devpost": "() => !document.querySelector('a[href*=\"login\"]')",
    "kaggle": "() => !document.querySelector('a[href*=\"login\"]')",
    "vercel": "() => !!document.querySelector('[data-testid=\"user-menu\"]')",
}


def get_session_file(service: str) -> Path:
    return AUTH_DIR / f"{service}-session.json"


def has_session(service: str) -> bool:
    return get_session_file(service).exists()


def get_session_age_hours(service: str) -> float:
    f = get_session_file(service)
    if not f.exists():
        return float('inf')
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        saved_at = datetime.fromisoformat(data.get("saved_at", "2000-01-01"))
        return (datetime.now() - saved_at).total_seconds() / 3600
    except Exception:
        return float('inf')


def save_session(service: str, storage_state: dict):
    """브라우저 storage_state를 파일로 저장"""
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    session_data = {
        "service": service,
        "saved_at": datetime.now().isoformat(),
        "storage_state": storage_state,
    }
    f = get_session_file(service)
    f.write_text(json.dumps(session_data, ensure_ascii=False, indent=2), encoding="utf-8")
    log_session("save", service)


def load_session(service: str) -> dict | None:
    """저장된 storage_state 로드"""
    f = get_session_file(service)
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        log_session("load", service)
        return data.get("storage_state")
    except Exception:
        return None


def list_sessions() -> list[dict]:
    """모든 저장된 세션 목록"""
    sessions = []
    for f in AUTH_DIR.glob("*-session.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            age = get_session_age_hours(data.get("service", ""))
            sessions.append({
                "service": data.get("service", f.stem),
                "saved_at": data.get("saved_at", "unknown"),
                "age_hours": round(age, 1),
                "file": f.name,
            })
        except Exception:
            sessions.append({"service": f.stem, "error": "parse_failed"})
    return sessions


def delete_session(service: str) -> bool:
    f = get_session_file(service)
    if f.exists():
        f.unlink()
        log_session("delete", service)
        return True
    return False


def log_session(action: str, service: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now().isoformat(), "action": action, "service": service}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    print("=== Signalion Session Manager ===")
    sessions = list_sessions()
    if sessions:
        for s in sessions:
            age = s.get("age_hours", "?")
            print(f"  [{s['service']}] saved {age}h ago — {s.get('file', '')}")
    else:
        print("  No saved sessions.")
    print(f"\nSupported services: {', '.join(SERVICE_LOGIN_URLS.keys())}")
