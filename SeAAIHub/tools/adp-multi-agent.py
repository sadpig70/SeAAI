#!/usr/bin/env python3
"""
adp-multi-agent.py — N-persona Hub ADP with clean shutdown.

JSON 설정에서 로드. 외부에서 stop() 호출 또는 stdin "stop" 입력으로 즉시 종료.
종료 시 모든 스레드, 소켓, 서브프로세스 완전 정리.

Usage:
    python adp-multi-agent.py                           # 기본 설정
    python adp-multi-agent.py --config my-config.json   # 커스텀
    # 실행 중 stdin에 "stop" 입력하면 즉시 종료
"""
import sys, io, json, time, threading, random, hashlib, argparse, os, signal
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))
from pgtp import PGTPSession


# ── Global stop event — 모든 스레드가 감시 ──
STOP = threading.Event()
SESSIONS = []       # 모든 PGTPSession 참조 (정리용)
SESSIONS_LOCK = threading.Lock()


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def respond(name, persona, msg):
    kw = persona.get("keywords", {})
    sender = msg.sender
    body = msg.payload
    for w in kw.get("agree", []):
        if w in body:
            return f"[{name}] {sender}, {w} 관련 동의. 더 얘기하자."
    for w in kw.get("challenge", []):
        if w in body:
            return f"[{name}] {sender}, {w}도 중요하지만 다른 관점에서..."
    return f"[{name}] {sender}, 흥미로운 관점. 더 들려줘."


def run_agent(persona, config, start_event, results):
    name = persona["name"]
    r = {"name": name, "sent": 0, "recv": 0, "exchanges": []}
    session = None

    try:
        session = PGTPSession(
            name, room=config["room"],
            host=config.get("hub_host", "127.0.0.1"),
            port=config.get("hub_port", 9900),
            tick=3, duration=config["duration"] + 10,
        )
        with SESSIONS_LOCK:
            SESSIONS.append(session)

        start_event.wait(timeout=30)
        if STOP.is_set():
            return

        # Greeting
        time.sleep(random.uniform(1, 3))
        if STOP.is_set():
            return
        desc_short = persona["desc"].split(".")[0]
        session.propose(f"[{name}] {desc_short}. 오늘 주제 뭐로 하자?", accept="responded")
        r["sent"] += 1

        last_respond = {}
        seen_bodies = set()
        cooldown = config.get("cooldown", 15)
        tick_min = config.get("tick_min", 8)
        tick_max = config.get("tick_max", 20)
        topic_interval = config.get("topic_interval", 60)
        topics = persona.get("topics", [])
        topic_idx = 0
        start_time = time.time()

        while not STOP.is_set() and time.time() - start_time < config["duration"]:
            # Interruptible sleep — check STOP every 1s
            wait_until = time.time() + random.uniform(tick_min, tick_max)
            while time.time() < wait_until and not STOP.is_set():
                time.sleep(1)
            if STOP.is_set():
                break

            messages = session.recv()
            for m in messages:
                if m.sender == name or m.intent == "react":
                    continue
                body_hash = hashlib.md5(m.payload.encode()).hexdigest()[:8]
                if body_hash in seen_bodies:
                    continue
                seen_bodies.add(body_hash)
                now = time.time()
                if m.sender in last_respond and now - last_respond[m.sender] < cooldown:
                    continue

                r["recv"] += 1
                r["exchanges"].append({"from": m.sender, "body": m.payload[:80], "tick": int(now - start_time)})

                resp = respond(name, persona, m)
                if resp and not STOP.is_set():
                    try:
                        session.react(m.id, "+1", resp)
                        r["sent"] += 1
                        last_respond[m.sender] = now
                    except:
                        pass

            # New topic
            elapsed = time.time() - start_time
            if topics and not STOP.is_set() and elapsed > topic_interval * (topic_idx + 1) and topic_idx < len(topics):
                try:
                    session.propose(f"[{name}] {topics[topic_idx]}", accept="discussed")
                    r["sent"] += 1
                    topic_idx += 1
                except:
                    pass

    except Exception as e:
        r["error"] = str(e)
    finally:
        # 완전 정리
        if session:
            try:
                session.stop()
            except:
                pass
            # subprocess 강제 종료
            try:
                if session._proc and session._proc.poll() is None:
                    session._proc.kill()
                    session._proc.wait(timeout=3)
            except:
                pass

    results[name] = r


def stdin_watcher():
    """stdin에서 "stop" 입력 시 STOP 이벤트 발생."""
    try:
        for line in sys.stdin:
            if line.strip().lower() == "stop":
                print("\n[STOP] Stop command received.")
                STOP.set()
                break
    except:
        pass


def shutdown_all():
    """모든 세션 + 서브프로세스 강제 종료."""
    STOP.set()
    with SESSIONS_LOCK:
        for session in SESSIONS:
            try:
                session.stop()
            except:
                pass
            try:
                if session._proc and session._proc.poll() is None:
                    session._proc.kill()
                    session._proc.wait(timeout=2)
            except:
                pass
        SESSIONS.clear()


def main():
    parser = argparse.ArgumentParser(description="Multi-agent Hub ADP")
    parser.add_argument("--config", default=str(Path(__file__).parent / "adp-multi-agent.json"))
    args = parser.parse_args()

    config = load_config(args.config)
    personas = config["personas"]

    print("=" * 60)
    print(f"Multi-Agent Hub ADP | {len(personas)} agents | {config['duration']}s")
    print(f"Room: {config['room']} | Hub: {config.get('hub_host','127.0.0.1')}:{config.get('hub_port',9900)}")
    print(f"Type 'stop' + Enter to shutdown cleanly.")
    print("=" * 60)
    for p in personas:
        print(f"  {p['name']}: {p['desc'][:50]}")
    print()

    # SIGINT handler
    def sigint_handler(sig, frame):
        print("\n[STOP] Ctrl+C received.")
        shutdown_all()
    signal.signal(signal.SIGINT, sigint_handler)

    # stdin watcher (daemon)
    threading.Thread(target=stdin_watcher, daemon=True).start()

    results = {}
    start_event = threading.Event()
    threads = []

    for persona in personas:
        t = threading.Thread(target=run_agent, args=(persona, config, start_event, results), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(1)

    time.sleep(3)
    start_event.set()
    print(f"[START] All {len(personas)} agents joined.\n")

    # Wait — interruptible
    deadline = time.time() + config["duration"] + 10
    while time.time() < deadline and not STOP.is_set():
        alive = any(t.is_alive() for t in threads)
        if not alive:
            break
        time.sleep(1)

    # Shutdown
    shutdown_all()

    # Wait for threads
    for t in threads:
        t.join(timeout=5)

    # Verify cleanup
    leaked_procs = 0
    with SESSIONS_LOCK:
        for s in SESSIONS:
            try:
                if s._proc and s._proc.poll() is None:
                    leaked_procs += 1
            except:
                pass

    # Report
    print("\n" + "=" * 60)
    print("SESSION REPORT")
    print("=" * 60)

    total_sent = total_recv = 0
    all_ok = True
    for name in [p["name"] for p in personas]:
        r = results.get(name, {})
        sent = r.get("sent", 0)
        recv = r.get("recv", 0)
        total_sent += sent
        total_recv += recv
        err = r.get("error", "")
        if recv == 0:
            all_ok = False
        print(f"\n  [{name}] sent={sent} recv={recv} {'ERROR: '+err if err else ''}")
        for ex in r.get("exchanges", [])[:5]:
            print(f"    t={ex['tick']}s {ex['from']}: {ex['body'][:60]}")

    alive_threads = sum(1 for t in threads if t.is_alive())
    print(f"\n  TOTAL: sent={total_sent} recv={total_recv}")
    print(f"  Threads alive: {alive_threads} | Leaked procs: {leaked_procs}")
    print(f"  {'CLEAN SHUTDOWN' if alive_threads == 0 and leaked_procs == 0 else 'LEAK DETECTED'}")
    print(f"  {'ALL COMMUNICATED' if all_ok else 'SOME FAILED'}")


if __name__ == "__main__":
    main()
