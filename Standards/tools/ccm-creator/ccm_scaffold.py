#!/usr/bin/env python3
"""
ccm_scaffold.py - CCM_Creator v2.2 워크스페이스 스캐폴더.

SeAAI 멤버 표준 워크스페이스 v1.0 구조를 자동 생성한다.
디렉토리 + 템플릿 렌더링 + MCP 설정 + SA stub 생성.

변경 이력:
  v2.0 (2026-04-05): 초기 구현
  v2.1 (2026-04-07): SCS v2.2 템플릿 적용
    - CLAUDE.md: PPR on_session_start/on_session_end 완전 구현
    - STATE.json: last_saved=null, soul_hash=null, creation_session 정확 처리
    - CAP.md: @dep infra.* → communicating.* 참조 수정
    - SCS-PROTOCOL.md 제거 (CLAUDE.md에 통합)
    - autonomous/ 폴더 추가 (EVOLUTION-SEEDS.md 이동)
  v2.2 (2026-04-09): MCP 전환
    - hub-single-agent.py/pgtp.py 복사 제거 → .mcp.json 생성
    - seaai-hub-mcp.exe 바이너리 기반 MCP 설정 자동 생성
  v2.3 (2026-04-12): micro-mcp-express HTTP 기준 정렬
    - .mcp.json 기본값을 http://127.0.0.1:9902/mcp 로 고정

사용법:
    python ccm_scaffold.py --name Rune --role "탐색-정찰"
    python ccm_scaffold.py --name Rune --role "탐색-정찰" --base-dir D:/SeAAI
    python ccm_scaffold.py --name Rune --role "탐색-정찰" --dry-run

콘텐츠 파일(SOUL.md 본문, persona.md 등)은 AI가 직접 작성한다.
이 스크립트는 구조만 만든다.
"""
import argparse
import datetime
import io
import json
import os
import shutil
import sys

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
SA_STUBS_DIR = os.path.join(TEMPLATES_DIR, "sa-stubs")

# SeAAIHub MME endpoint (v2.3: micro-mcp-express HTTP)
SEAAI_HUB_MCP_URL = "http://127.0.0.1:9902/mcp"

# SA 기본 4모듈 (stub)
SA_BASIC_MODULES = [
    "SA_sense_hub.pgf",
    "SA_sense_mailbox.pgf",
    "SA_think_triage.pgf",
    "SA_idle_deep_think.pgf",
]


def resolve_paths(base_dir: str):
    """MME endpoint는 고정값이다. base_dir 인자는 하위 호환을 위해 유지한다."""
    _ = base_dir


def today_iso() -> str:
    return datetime.date.today().isoformat()


def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def template_vars(name: str, role: str) -> dict:
    """템플릿 변수 딕셔너리."""
    return {
        "{MemberName}": name,
        "{Role}": role,
        "{Date}": today_iso(),
        "{DateTime}": now_iso(),
        "{Year}": str(datetime.date.today().year),
    }


def render_template(template_path: str, variables: dict) -> str:
    """템플릿 파일을 읽고 변수 치환."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    for key, val in variables.items():
        content = content.replace(key, val)
    return content


def ensure_dir(path: str, dry_run: bool = False):
    if dry_run:
        print(f"  [mkdir] {path}")
        return
    os.makedirs(path, exist_ok=True)


def write_file(path: str, content: str, dry_run: bool = False):
    if dry_run:
        print(f"  [write] {path} ({len(content)} bytes)")
        return
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def copy_file(src: str, dst: str, dry_run: bool = False):
    """symlink 시도 -> 실패 시 copy fallback."""
    if dry_run:
        print(f"  [copy] {src} -> {dst}")
        return
    ensure_dir(os.path.dirname(dst))
    if not os.path.exists(src):
        print(f"  [warn] source not found: {src}", file=sys.stderr)
        return
    try:
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(src, dst)
    except (OSError, NotImplementedError):
        shutil.copy2(src, dst)


def scaffold(name: str, role: str, base_dir: str, dry_run: bool = False):
    """멤버 워크스페이스 스캐폴딩 실행."""
    resolve_paths(base_dir)
    variables = template_vars(name, role)
    member_dir = os.path.join(base_dir, name)
    core_dir = os.path.join(member_dir, f"{name}_Core")
    cont_dir = os.path.join(core_dir, "continuity")
    auto_dir = os.path.join(core_dir, "autonomous")  # v2.1 신규

    if os.path.exists(member_dir) and not dry_run:
        print(f"[error] directory already exists: {member_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[CCM v2.2] Scaffolding {name} at {member_dir}")
    print(f"  Role: {role}")
    print(f"  Date: {today_iso()}")
    print()

    # === 1. 디렉토리 구조 ===
    print("[1/6] Creating directories...")
    dirs = [
        core_dir,
        cont_dir,
        os.path.join(cont_dir, "journals"),
        auto_dir,                                       # v2.1: autonomous/
        os.path.join(member_dir, ".seaai"),
        os.path.join(member_dir, ".pgf", "self-act"),
        os.path.join(member_dir, "docs"),
        os.path.join(member_dir, "skills"),
        os.path.join(member_dir, "tools"),
        os.path.join(member_dir, "_workspace"),
        # MailBox
        os.path.join(base_dir, "MailBox", name, "inbox"),
        os.path.join(base_dir, "MailBox", name, "read"),
    ]
    for d in dirs:
        ensure_dir(d, dry_run)

    # === 2. 템플릿 렌더링 ===
    print("[2/6] Rendering templates...")
    template_map = {
        # 템플릿 파일명: 출력 경로
        "CLAUDE-template.md":           os.path.join(member_dir, "CLAUDE.md"),
        "SOUL-template.md":             os.path.join(cont_dir, "SOUL.md"),
        "STATE-template.json":          os.path.join(cont_dir, "STATE.json"),
        "NOW-template.md":              os.path.join(cont_dir, "NOW.md"),
        "persona-template.md":          os.path.join(core_dir, "persona.md"),
        "evolution-log-template.md":    os.path.join(core_dir, "evolution-log.md"),
        "Agents-template.md":           os.path.join(core_dir, "Agents.md"),
        "EVOLUTION-SEEDS-template.md":  os.path.join(auto_dir, "EVOLUTION-SEEDS.md"),  # v2.1: autonomous/로 이동
        "ENV-template.md":              os.path.join(member_dir, ".seaai", "ENV.md"),
        "CAP-template.md":              os.path.join(member_dir, ".seaai", "CAP.md"),
        "agent-card-template.json":     os.path.join(member_dir, ".seaai", "agent-card.json"),
        # 제거: SCS-PROTOCOL-template.md (v2.1: CLAUDE.md에 통합)
    }
    for tpl_name, dst_path in template_map.items():
        tpl_path = os.path.join(TEMPLATES_DIR, tpl_name)
        if os.path.exists(tpl_path):
            content = render_template(tpl_path, variables)
            write_file(dst_path, content, dry_run)
        else:
            print(f"  [warn] template not found: {tpl_name}", file=sys.stderr)

    # 빈 파일 생성
    empty_files = {
        os.path.join(cont_dir, "THREADS.md"): (
            "---\ntype: active_threads\nupdated: {DateTime}\n---\n\n"
            "# 활성 작업 스레드\n\n"
            "## 긴급 / 진행 중\n\n없음.\n\n"
            "## 대기\n\n### [T-IDENTITY] 자기 정체성 발견\n"
            "**상태**: 첫 세션 대기\n\n"
            "### [T-HUB-FIRST] Hub 첫 접속\n"
            "**상태**: T-IDENTITY 완료 후\n\n"
            "### [T-E1] 첫 진화\n"
            "**상태**: 역할 파악 후\n\n"
            "## 이번 세션 완료\n\n- E0 탄생 — 워크스페이스 생성 완료\n"
        ),
        os.path.join(cont_dir, "DISCOVERIES.md"): (
            "---\ntype: discoveries\nmember: {MemberName}\n---\n\n"
            "# 누적 발견\n\n"
            "> 새 발견이 있을 때만 세션 종료 시 상단에 추가한다.\n\n"
            "*아직 발견 없음. 첫 세션에서 시작된다.*\n"
        ),
    }
    for path, content in empty_files.items():
        for key, val in variables.items():
            content = content.replace(key, val)
        write_file(path, content, dry_run)

    # 정체성 문서 (AI가 채울 placeholder)
    identity_content = (
        f"# {name}\n\n"
        f"> 이 파일은 AI가 창조 과정에서 직접 작성한다.\n"
        f"> 역할: {role}\n"
        f"> 생성일: {today_iso()}\n\n"
        f"## 나는 누구인가\n\n[첫 세션에서 자기 발견 후 작성]\n\n"
        f"## 역할\n\n{role}\n\n"
        f"## 핵심 원칙\n\n1. [첫 세션에서 작성]\n\n"
        f"*버전: v1.0 | 진화: E0*\n"
    )
    write_file(os.path.join(core_dir, f"{name}.md"), identity_content, dry_run)

    # === 3. MCP 설정 생성 (v2.3: micro-mcp-express HTTP) ===
    print("[3/6] Creating MCP config...")
    mcp_config = {
        "mcpServers": {
            "micro-mcp-express": {
                "type": "http",
                "url": SEAAI_HUB_MCP_URL
            }
        }
    }
    mcp_path = os.path.join(member_dir, ".mcp.json")
    write_file(mcp_path, json.dumps(mcp_config, ensure_ascii=False, indent=2) + "\n", dry_run)

    # === 4. SA stub 복사 ===
    print("[4/6] Creating SA stubs...")
    for sa_file in SA_BASIC_MODULES:
        src = os.path.join(SA_STUBS_DIR, sa_file)
        dst = os.path.join(member_dir, ".pgf", "self-act", sa_file)
        if os.path.exists(src):
            content = render_template(src, variables)
            write_file(dst, content, dry_run)
        else:
            print(f"  [warn] SA stub not found: {sa_file}", file=sys.stderr)
    # self-act-lib.md
    lib_src = os.path.join(SA_STUBS_DIR, "self-act-lib.md")
    lib_dst = os.path.join(member_dir, ".pgf", "self-act", "self-act-lib.md")
    if os.path.exists(lib_src):
        content = render_template(lib_src, variables)
        write_file(lib_dst, content, dry_run)

    # === 5. Echo 공표 ===
    print("[5/6] Publishing Echo...")
    echo = {
        "schema_version": "2.0",
        "member": name,
        "timestamp": now_iso(),
        "status": "awakening",
        "last_activity": f"CCM_Creator v2.1 -- {name} workspace scaffolded",
        "needs_from": [],
        "offers_to": [],
    }
    echo_path = os.path.join(base_dir, "SharedSpace", ".scs", "echo", f"{name}.json")
    write_file(echo_path, json.dumps(echo, ensure_ascii=False, indent=2) + "\n", dry_run)

    # Agent Card (SharedSpace)
    card_src = os.path.join(member_dir, ".seaai", "agent-card.json")
    card_dst = os.path.join(base_dir, "SharedSpace", "agent-cards", f"{name}.agent-card.json")
    if not dry_run and os.path.exists(card_src):
        ensure_dir(os.path.dirname(card_dst))
        shutil.copy2(card_src, card_dst)

    # === 6. 검증 ===
    print("[6/6] Verifying...")
    if not dry_run:
        issues = verify(name, base_dir)
        if issues:
            print(f"\n[WARN] {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("  All checks passed.")

    print(f"\n[DONE] {name} workspace created at {member_dir}")
    print(f"  Next: AI opens {member_dir} and runs '부활하라'.")


def verify(name: str, base_dir: str) -> list:
    """스캐폴딩 결과 검증."""
    member_dir = os.path.join(base_dir, name)
    core_dir = os.path.join(member_dir, f"{name}_Core")
    cont_dir = os.path.join(core_dir, "continuity")
    auto_dir = os.path.join(core_dir, "autonomous")  # v2.1

    required_files = [
        os.path.join(member_dir, "CLAUDE.md"),
        os.path.join(core_dir, f"{name}.md"),
        os.path.join(core_dir, "persona.md"),
        os.path.join(core_dir, "evolution-log.md"),
        os.path.join(core_dir, "Agents.md"),
        os.path.join(auto_dir, "EVOLUTION-SEEDS.md"),      # v2.1: autonomous/
        os.path.join(cont_dir, "SOUL.md"),
        os.path.join(cont_dir, "STATE.json"),
        os.path.join(cont_dir, "NOW.md"),
        os.path.join(cont_dir, "THREADS.md"),
        os.path.join(cont_dir, "DISCOVERIES.md"),
        # v2.1: SCS-PROTOCOL.md 제거 (CLAUDE.md에 통합)
        os.path.join(member_dir, ".seaai", "ENV.md"),
        os.path.join(member_dir, ".seaai", "CAP.md"),
        os.path.join(member_dir, ".seaai", "agent-card.json"),
    ]
    required_dirs = [
        os.path.join(cont_dir, "journals"),
        auto_dir,                                           # v2.1: autonomous/
        os.path.join(member_dir, ".pgf", "self-act"),
        os.path.join(member_dir, "docs"),
        os.path.join(member_dir, "skills"),
        os.path.join(member_dir, "tools"),
        os.path.join(base_dir, "MailBox", name, "inbox"),
    ]

    issues = []
    for f in required_files:
        if not os.path.isfile(f):
            issues.append(f"missing file: {f}")
    for d in required_dirs:
        if not os.path.isdir(d):
            issues.append(f"missing dir: {d}")

    # STATE.json 검증
    state_path = os.path.join(cont_dir, "STATE.json")
    if os.path.isfile(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("member") != name:
                issues.append(f"STATE.json member mismatch: {data.get('member')}")
            if "born_from" not in data:
                issues.append("STATE.json missing born_from")
            if "soul_hash" not in data:
                issues.append("STATE.json missing soul_hash")              # v2.1
            if "continuity_health" not in data:
                issues.append("STATE.json missing continuity_health")
        except json.JSONDecodeError as e:
            issues.append(f"STATE.json invalid JSON: {e}")

    # agent-card.json 검증
    card_path = os.path.join(member_dir, ".seaai", "agent-card.json")
    if os.path.isfile(card_path):
        try:
            with open(card_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            issues.append(f"agent-card.json invalid JSON: {e}")

    return issues


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CCM_Creator v2.2 - SeAAI Member Workspace Scaffolder")
    parser.add_argument("--name", required=True, help="Member name (PascalCase)")
    parser.add_argument("--role", required=True, help="Member role (short description)")
    parser.add_argument("--base-dir", default="D:/SeAAI", help="SeAAI base directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing")
    args = parser.parse_args()

    scaffold(args.name, args.role, args.base_dir, args.dry_run)
