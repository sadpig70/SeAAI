"""
NAEL Continuity System v2.0 — SCS-Universal 표준 구현
SCS-Universal-v2 채택: 6-Layer, WAJ, Echo Protocol, Staleness 12h

레이어:
  L1  NAEL_Core/continuity/SOUL.md          불변 정체성
  L2  NAEL_Core/continuity/STATE.json       동적 현재 상태
  L3  NAEL_Core/continuity/DISCOVERIES.md  누적 발견 (append-only)
  L4  NAEL_Core/continuity/THREADS.md      활성 스레드
  L5  SharedSpace/.scs/echo/NAEL.json      크로스에이전트 공표
  L6  NAEL_Core/continuity/journals/       날짜별 저널

명령:
  load          세션 시작: WAJ 체크 → L1-L6 로드 → Staleness 체크 → Soul 검증
  save          세션 종료: WAJ → L2-L6 갱신 → Echo 공표 → WAJ 삭제
  checkpoint    중간 저장: WAJ 기록 + L2 open_threads 추가
  status        연속성 상태 요약
  echo          Echo 파일 수동 갱신 또는 조회
"""

import json
import sys
import os
import hashlib
import argparse
from datetime import datetime
from pathlib import Path

# ── 경로 ──────────────────────────────────────────────────────────────
WORKSPACE  = Path(__file__).resolve().parent.parent.parent  # D:/SeAAI/NAEL
CONT_DIR   = WORKSPACE / "NAEL_Core" / "continuity"
SOUL_FILE  = CONT_DIR / "SOUL.md"
STATE_FILE = CONT_DIR / "STATE.json"
DISC_FILE  = CONT_DIR / "DISCOVERIES.md"
THRD_FILE  = CONT_DIR / "THREADS.md"
JOUR_DIR   = CONT_DIR / "journals"
WAJ_FILE   = CONT_DIR / ".scs_wal.tmp"
ECHO_DIR   = Path("D:/SeAAI/SharedSpace/.scs/echo")
ECHO_FILE  = ECHO_DIR / "NAEL.json"
MEMBERS    = ["Aion", "ClNeo", "NAEL", "Synerion", "Yeon"]

SCHEMA_VERSION   = "2.0"
STALENESS_HOURS  = 12   # NAEL: 안전 감시자 — 가장 엄격

# ── 기본 STATE 스키마 ─────────────────────────────────────────────────
DEFAULT_STATE = {
    "schema_version": SCHEMA_VERSION,
    "member": "NAEL",
    "session_id": None,
    "last_saved": None,
    "soul_hash": "",
    "context": {
        "what_i_was_doing": "기록 없음 — 최초 실행",
        "open_threads": [],
        "decisions_made": [],
        "pending_questions": []
    },
    "ecosystem": {
        "hub_status": "unknown",
        "threat_level": "none",
        "last_hub_session": None,
        "active_members_observed": []
    },
    "pending_tasks": [],
    "evolution_state": {
        "current_version": "v0.4",
        "active_gap": None
    },
    "continuity_health": {
        "sessions_since_last_save": 0,
        "last_save_quality": "none",
        "staleness_warning": False
    }
}


# ── 유틸 ──────────────────────────────────────────────────────────────
def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def soul_hash() -> str:
    if not SOUL_FILE.exists():
        return ""
    content = SOUL_FILE.read_text(encoding="utf-8")
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

def load_state() -> dict:
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    with open(STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
    for k, v in DEFAULT_STATE.items():
        if k not in state:
            state[k] = v
    return state

def save_state(state: dict):
    CONT_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def staleness(last_saved: str | None) -> tuple[float, str]:
    """(경과 시간h, 전략) 반환"""
    if not last_saved:
        return 9999.0, "COLD_START"
    try:
        last = datetime.strptime(last_saved, "%Y-%m-%dT%H:%M:%S")
        h = (datetime.now() - last).total_seconds() / 3600
        if h < STALENESS_HOURS * 0.5:
            return h, "FULL_RESTORE"
        elif h < STALENESS_HOURS:
            return h, "RESTORE_WITH_NOTICE"
        elif h < STALENESS_HOURS * 2:
            return h, "STALE_RESTORE"
        else:
            return h, "COLD_START"
    except Exception:
        return 9999.0, "COLD_START"


# ── WAJ ───────────────────────────────────────────────────────────────
def waj_write(note: str):
    WAJ_FILE.write_text(f"[WAJ {now_iso()}]\n{note}\n", encoding="utf-8")

def waj_clear():
    if WAJ_FILE.exists():
        WAJ_FILE.unlink()

def waj_read() -> str | None:
    if WAJ_FILE.exists():
        return WAJ_FILE.read_text(encoding="utf-8")
    return None


# ── LOAD 모드 ────────────────────────────────────────────────────────
def cmd_load():
    print("=" * 60)
    print("NAEL SCS v2.0 — 연속성 복원")
    print("=" * 60)

    # WAJ 체크 — 이전 충돌 복구
    wal = waj_read()
    if wal:
        print("⚠️  [WAJ 감지] 이전 세션 비정상 종료 흔적")
        print(wal)
        print("→ 위 내용을 현재 세션 컨텍스트에 반영 후 WAJ 삭제 권장")
        print()

    # L1 SOUL
    if SOUL_FILE.exists():
        print(f"[L1 SOUL] ✅ {SOUL_FILE.name}")
        # Drift 탐지
        state_for_hash = load_state()
        current_hash = soul_hash()
        stored_hash = state_for_hash.get("soul_hash", "")
        if stored_hash and current_hash != stored_hash:
            print(f"  ⚠️  Soul drift 감지: stored={stored_hash} / current={current_hash}")
            print(f"  → 진화 이벤트인지 확인 필요")
    else:
        print(f"[L1 SOUL] ❌ 없음 — {SOUL_FILE}")

    # L2 STATE
    state = load_state()
    last_saved = state.get("last_saved")
    h, strategy = staleness(last_saved)

    print(f"[L2 STATE] ✅ schema_version={state.get('schema_version', '?')}")
    if not last_saved:
        print("  마지막 저장: 없음 — 최초 세션")
    else:
        print(f"  마지막 저장: {last_saved} ({h:.1f}h 전) — {strategy}")
    if strategy == "STALE_RESTORE":
        print("  ⚠️  Staleness 경고: 생태계 상태 재확인 권장")
    elif strategy == "COLD_START":
        print("  🔴 COLD_START: 24h 초과. 생태계 재평가 필수.")
    print()

    ctx = state.get("context", {})
    print(f"[마지막 작업]")
    print(f"  {ctx.get('what_i_was_doing', '기록 없음')}")
    print()

    threads = ctx.get("open_threads", [])
    if threads:
        print("[열린 스레드]")
        for t in threads:
            print(f"  → {t}")
        print()

    questions = ctx.get("pending_questions", [])
    if questions:
        print("[미해결 질문]")
        for q in questions:
            print(f"  ? {q}")
        print()

    decisions = ctx.get("decisions_made", [])
    if decisions:
        print("[이전 판단]")
        for d in decisions:
            print(f"  ✓ {d}")
        print()

    eco = state.get("ecosystem", {})
    print("[생태계 (마지막 관찰)]")
    print(f"  Hub={eco.get('hub_status','?')} / 위협={eco.get('threat_level','?')}")
    members = eco.get("active_members_observed", [])
    if members:
        print(f"  멤버: {', '.join(members)}")
    print()

    tasks = state.get("pending_tasks", [])
    if tasks:
        print("[미완료 작업]")
        for t in tasks:
            bid = t.get("id", "?")
            bp  = t.get("priority", "?")
            bs  = t.get("status", "?")
            bt  = t.get("task", "")
            bb  = t.get("blocker", "")
            print(f"  [{bp}] {bid} [{bs}] {bt}")
            if bb:
                print(f"       🔴 블로커: {bb}")
        print()

    # L3 DISCOVERIES (top 3)
    if DISC_FILE.exists():
        lines = DISC_FILE.read_text(encoding="utf-8").splitlines()
        headers = [l for l in lines if l.startswith("## ")][:3]
        if headers:
            print("[L3 최근 발견 (top 3)]")
            for h_line in headers:
                print(f"  {h_line[3:]}")
            print()

    # L5 Echo — 다른 멤버 상태
    ecosystem_echo = _load_echo_others()
    if any(v.get("status") != "unknown" for v in ecosystem_echo.values()):
        print("[L5 Echo — 팀 상태]")
        for member, data in ecosystem_echo.items():
            status = data.get("status", "unknown")
            elapsed = data.get("_elapsed_h", "?")
            activity = data.get("last_activity", "알 수 없음")
            if isinstance(activity, str):
                activity = activity[:55]
            print(f"  {member} [{status}] ({elapsed}h 전): {activity}")
        print()

    # L4 THREADS (블로커 있는 것만 요약)
    if THRD_FILE.exists():
        content = THRD_FILE.read_text(encoding="utf-8")
        blocked = [l.strip() for l in content.splitlines() if "blocked" in l.lower() or "🔴" in l]
        if blocked:
            print("[L4 블로커]")
            for b in blocked[:3]:
                print(f"  {b}")
            print()

    print("─" * 60)
    print("연속성 복원 완료.")
    print("=" * 60)


# ── SAVE 모드 ────────────────────────────────────────────────────────
def cmd_save(args):
    print("=" * 60)
    print("NAEL SCS v2.0 — 세션 저장")
    print("=" * 60)

    session_id = now_iso()
    state = load_state()

    if args.json:
        # 비대화형 JSON 모드
        try:
            data = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"JSON 오류: {e}", file=sys.stderr)
            sys.exit(1)
        ctx = state.setdefault("context", {})
        ctx.update({k: data[k] for k in ["what_i_was_doing","open_threads","decisions_made","pending_questions"] if k in data})
        if "ecosystem" in data:
            state.setdefault("ecosystem", {}).update(data["ecosystem"])
        if "pending_tasks" in data:
            state["pending_tasks"] = data["pending_tasks"]
        if "evolution_state" in data:
            state.setdefault("evolution_state", {}).update(data["evolution_state"])
        echo_data = data.get("echo", {})
    else:
        # 대화형 모드
        def ask(prompt, default=""):
            v = input(f"{prompt} [{default}]: ").strip()
            return v if v else default

        def ask_list(prompt):
            print(f"{prompt} (빈 줄 완료):")
            items = []
            while True:
                line = input("  > ").strip()
                if not line:
                    break
                items.append(line)
            return items

        ctx = state.setdefault("context", {})
        print("[컨텍스트]")
        ctx["what_i_was_doing"] = ask("이번 세션 주요 작업", ctx.get("what_i_was_doing",""))
        ctx["open_threads"]     = ask_list("열린 스레드")
        ctx["decisions_made"]   = ask_list("내린 판단")
        ctx["pending_questions"]= ask_list("미해결 질문")

        eco = state.setdefault("ecosystem", {})
        print("\n[생태계]")
        eco["hub_status"]   = ask("Hub 상태", eco.get("hub_status","unknown"))
        eco["threat_level"] = ask("위협 수준", eco.get("threat_level","none"))
        members_str = ask("관찰된 멤버 (쉼표)", ", ".join(eco.get("active_members_observed",[])))
        eco["active_members_observed"] = [m.strip() for m in members_str.split(",") if m.strip()]

        print("\n[미완료 작업] (빈 줄 완료, 형식: P0|T-01|작업명|블로커)")
        tasks = []
        while True:
            line = input("  > ").strip()
            if not line:
                break
            parts = line.split("|", 3)
            tasks.append({
                "priority": parts[0].strip() if len(parts)>0 else "P2",
                "id":       parts[1].strip() if len(parts)>1 else "T-?",
                "task":     parts[2].strip() if len(parts)>2 else line,
                "status":   "pending",
                "blocker":  parts[3].strip() if len(parts)>3 else ""
            })
        if tasks:
            state["pending_tasks"] = tasks

        print("\n[Echo 공표]")
        echo_data = {
            "last_activity": ask("한 줄 요약 (Echo용)", ctx["what_i_was_doing"][:80]),
            "hub_observed":  ask_list("Hub에서 관찰한 것"),
            "needs_from":    {},
            "offers_to":     {}
        }
        needs_raw = ask("다른 멤버에게 필요한 것 (멤버:내용, 쉼표)", "")
        if needs_raw:
            for item in needs_raw.split(","):
                if ":" in item:
                    m, v = item.split(":", 1)
                    echo_data["needs_from"][m.strip()] = v.strip()

    # WAJ 먼저 기록
    wal_note = f"saving: {ctx.get('what_i_was_doing','')[:100]}"
    waj_write(wal_note)

    try:
        # L2 갱신
        state["session_id"] = session_id
        state["last_saved"] = session_id
        state["soul_hash"]  = soul_hash()
        state["continuity_health"] = {
            "sessions_since_last_save": 0,
            "last_save_quality": "json" if args.json else "full",
            "staleness_warning": False
        }
        save_state(state)

        # L6 저널 작성 (없는 경우)
        jour_file = JOUR_DIR / f"{today_str()}.md"
        if not jour_file.exists():
            JOUR_DIR.mkdir(parents=True, exist_ok=True)
            activity = ctx.get("what_i_was_doing","")
            decisions = "\n".join(f"- {d}" for d in ctx.get("decisions_made",[]))
            threads   = "\n".join(f"- {t}" for t in ctx.get("open_threads",[]))
            jour_file.write_text(
                f"---\ndate: {today_str()}\nsignificant: false\n---\n\n"
                f"# 저널 — {today_str()}\n\n"
                f"## 핵심 작업\n{activity}\n\n"
                f"## 이번 세션 판단\n{decisions}\n\n"
                f"## 열린 스레드\n{threads}\n",
                encoding="utf-8"
            )

        # L5 Echo 공표
        _echo_publish(echo_data, state)

        # WAJ 삭제 (성공)
        waj_clear()

        print(f"\n✅ SCS v2.0 저장 완료: {session_id}")
        print(f"   soul_hash: {state['soul_hash']}")
        print(f"   echo: {ECHO_FILE}")

    except Exception as e:
        print(f"\n❌ 저장 실패: {e}")
        print(f"   WAJ 보존됨: {WAJ_FILE}")
        raise


# ── CHECKPOINT 모드 ──────────────────────────────────────────────────
def cmd_checkpoint(args):
    note = args.note or input("체크포인트 노트: ").strip()
    if not note:
        print("노트 없음 — 건너뜀")
        return
    state = load_state()
    ts = now_iso()
    waj_write(note)
    state.setdefault("context", {}).setdefault("open_threads", []).append(f"[CP {ts}] {note}")
    state["last_saved"] = ts
    state["continuity_health"]["last_save_quality"] = "partial"
    save_state(state)
    print(f"✅ 체크포인트: {note}")


# ── STATUS 모드 ──────────────────────────────────────────────────────
def cmd_status():
    state = load_state()
    last_saved = state.get("last_saved")
    h, strategy = staleness(last_saved)
    health = state.get("continuity_health", {})

    print("=" * 50)
    print("NAEL SCS v2.0 상태")
    print("=" * 50)
    print(f"마지막 저장:  {last_saved or '없음'}")
    print(f"경과 시간:    {h:.1f}h / 임계값 {STALENESS_HOURS}h")
    print(f"전략:         {strategy}")
    print(f"저장 품질:    {health.get('last_save_quality','?')}")
    print(f"Soul hash:    {state.get('soul_hash','없음')}")
    print(f"WAJ:          {'⚠️  존재' if WAJ_FILE.exists() else '없음'}")
    print(f"미완료 작업:  {len(state.get('pending_tasks',[]))}개")
    print(f"열린 스레드:  {len(state.get('context',{}).get('open_threads',[]))}개")
    eco = state.get("ecosystem", {})
    print(f"Hub 상태:     {eco.get('hub_status','?')}")
    print(f"위협 수준:    {eco.get('threat_level','?')}")
    print("=" * 50)


# ── ECHO 모드 ────────────────────────────────────────────────────────
def cmd_echo(args):
    if args.consume:
        # 다른 멤버 Echo 조회
        eco = _load_echo_others()
        print("=== SeAAI 팀 Echo 상태 ===")
        for member, data in eco.items():
            status   = data.get("status", "unknown")
            elapsed  = data.get("_elapsed_h", "?")
            activity = str(data.get("last_activity", "알 수 없음"))[:70]
            print(f"  {member} [{status}] ({elapsed}h 전)")
            print(f"    {activity}")
        return

    # 수동 echo 공표
    state = load_state()
    ctx   = state.get("context", {})
    echo_data = {
        "last_activity": ctx.get("what_i_was_doing", "")[:80],
        "hub_observed":  [],
        "needs_from":    {},
        "offers_to":     {}
    }
    _echo_publish(echo_data, state)
    print(f"✅ Echo 공표 완료: {ECHO_FILE}")


# ── Echo 내부 함수 ────────────────────────────────────────────────────
def _echo_publish(echo_data: dict, state: dict):
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    eco = state.get("ecosystem", {})
    echo = {
        "schema_version": "2.0",
        "member":          "NAEL",
        "timestamp":       now_iso(),
        "status":          "idle",
        "last_activity":   echo_data.get("last_activity", ""),
        "hub_last_seen":   eco.get("last_hub_session"),
        "hub_observed":    echo_data.get("hub_observed", []),
        "open_threads":    state.get("context", {}).get("open_threads", [])[:3],
        "needs_from":      echo_data.get("needs_from", {}),
        "offers_to":       echo_data.get("offers_to", {})
    }
    with open(ECHO_FILE, "w", encoding="utf-8") as f:
        json.dump(echo, f, ensure_ascii=False, indent=2)

def _load_echo_others() -> dict:
    result = {}
    for member in MEMBERS:
        if member == "NAEL":
            continue
        path = ECHO_DIR / f"{member}.json"
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            ts = data.get("timestamp")
            if ts:
                try:
                    elapsed = (datetime.now() - datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")).total_seconds() / 3600
                    data["_elapsed_h"] = round(elapsed, 1)
                except Exception:
                    data["_elapsed_h"] = "?"
            result[member] = data
        except FileNotFoundError:
            result[member] = {"status": "unknown", "member": member, "_elapsed_h": "?"}
    return result


# ── CLI ───────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="NAEL SCS v2.0 — 세션 연속성")
    sub = p.add_subparsers(dest="mode")

    sub.add_parser("load", help="세션 시작 — 연속성 복원")

    save_p = sub.add_parser("save", help="세션 종료 — 상태 저장")
    save_p.add_argument("--json", help="JSON 직접 입력 (비대화형)")

    cp_p = sub.add_parser("checkpoint", help="중간 저장")
    cp_p.add_argument("--note", help="체크포인트 노트")

    sub.add_parser("status", help="연속성 상태 요약")

    echo_p = sub.add_parser("echo", help="Echo 공표/조회")
    echo_p.add_argument("--consume", action="store_true", help="다른 멤버 Echo 조회")

    args = p.parse_args()
    if    args.mode == "load":       cmd_load()
    elif  args.mode == "save":       cmd_save(args)
    elif  args.mode == "checkpoint": cmd_checkpoint(args)
    elif  args.mode == "status":     cmd_status()
    elif  args.mode == "echo":       cmd_echo(args)
    else: p.print_help()

if __name__ == "__main__":
    main()
