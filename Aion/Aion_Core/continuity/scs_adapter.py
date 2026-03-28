import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent
SHARED_SPACE = Path("D:/SeAAI/SharedSpace")
ECHO_DIR = SHARED_SPACE / ".scs" / "echo"

LAYERS = {
    "L1": BASE_DIR / "SOUL.md",
    "L2": BASE_DIR / "STATE.json",
    "L3": BASE_DIR / "DISCOVERIES.md",
    "L4": BASE_DIR / "THREADS.md",
    "L5": ECHO_DIR / "Aion.json",
    "L6_DIR": BASE_DIR / "journals"
}

def get_soul_hash():
    with open(LAYERS["L1"], "r", encoding="utf-8") as f:
        return hashlib.sha256(f.read().encode()).hexdigest()

def save(status="idle", activity="", threads=[], needs={}, offers={}):
    # 1. STATE.json 갱신
    with open(LAYERS["L2"], "r", encoding="utf-8") as f:
        state = json.load(f)
    
    now = datetime.now().isoformat()
    state["last_saved"] = now
    state["session_id"] = state.get("session_id", now)
    state["soul_hash"] = f"sha256:{get_soul_hash()}"
    
    if activity:
        state["context"]["what_i_was_doing"] = activity
    if threads:
        state["context"]["open_threads"] = threads
    
    with open(LAYERS["L2"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # 2. Echo 공표
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    echo = {
        "schema_version": "2.0",
        "member": "Aion",
        "timestamp": now,
        "status": status,
        "last_activity": activity,
        "open_threads": threads,
        "needs_from": needs,
        "offers_to": offers
    }
    with open(LAYERS["L5"], "w", encoding="utf-8") as f:
        json.dump(echo, f, ensure_ascii=False, indent=2)
    
    print(f"[SCS] Aion's state and echo published at {now}")

def restore():
    # 1. 필구 레이어 로드 체크
    if not LAYERS["L1"].exists() or not LAYERS["L2"].exists():
        print("[SCS] Critical: SOUL or STATE missing. Cold start recommended.")
        return
    
    with open(LAYERS["L2"], "r", encoding="utf-8") as f:
        state = json.load(f)
    
    # 2. Staleness 체크 (48h)
    last_saved = datetime.fromisoformat(state["last_saved"])
    elapsed = (datetime.now() - last_saved).total_seconds() / 3600
    
    print(f"[SCS] Aion restored. Last active: {state['last_saved']} ({elapsed:.1f}h ago)")
    if elapsed > 48:
        print("[SCS] WARNING: Staleness threshold (48h) exceeded. Re-evaluate ecosystem.")
    
    # 3. Soul Drift 체크
    current_hash = get_soul_hash()
    stored_hash = state.get("soul_hash", "").replace("sha256:", "")
    if current_hash != stored_hash:
        print("[SCS] ALERT: Persona drift detected! Reset or evolution required.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: scs_adapter.py [save|restore|status]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "save":
        # 간단한 테스트용 호출
        save(activity="SCS-Aion-Adapter 초기 구현 완료")
    elif action == "restore":
        restore()
    else:
        print(f"Unknown action: {action}")
