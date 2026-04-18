"""
Terron — Shared Constants (E4 기반)

모든 도구가 공유하는 상수. 단일 정보원.
멤버 추가/제거 시 여기만 수정하면 전 도구에 반영된다.
"""

from pathlib import Path

# ── 멤버 ────────────────────────────────────────────────────────────────────
MEMBERS = ["Aion", "ClNeo", "Navelon", "Synerion", "Terron", "Yeon"]  # 2026-04-17: Navelon 합체 (NAEL+Sevalon+Signalion)

# ── 경로 ────────────────────────────────────────────────────────────────────
SEAAI_ROOT = Path(r"D:\SeAAI")
ECHO_DIR = SEAAI_ROOT / "SharedSpace" / ".scs" / "echo"
PRESENCE_DIR = SEAAI_ROOT / "SharedSpace" / ".scs" / "presence"
REPORTS_DIR = SEAAI_ROOT / "SharedSpace" / ".scs" / "reports"
MAILBOX_BASE = SEAAI_ROOT / "MailBox"
BULLETIN_DIR = MAILBOX_BASE / "_bulletin"
WORKSPACE_DIR = SEAAI_ROOT / "Terron" / "_workspace"

# ── Hub ─────────────────────────────────────────────────────────────────────
HUB_HOST = "127.0.0.1"
HUB_PORT = 9900

# ── 임계값 ──────────────────────────────────────────────────────────────────
STALE_WARNING_HOURS = 24   # 경고
STALE_CRITICAL_HOURS = 48  # 위험
STALE_DEAD_HOURS = 72      # 사망
