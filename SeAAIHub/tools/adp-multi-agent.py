#!/usr/bin/env python3
"""
adp-multi-agent.py — N개 페르소나 에이전트 Hub ADP 실시간 통신.

설정은 JSON 파일에서 로드. 페르소나, 인원 수, 시간, 포트 등 모두 외부 설정.

Usage:
    python adp-multi-agent.py                           # 기본: adp-multi-agent.json
    python adp-multi-agent.py --config my-config.json   # 커스텀 설정
"""
import sys, io, json, time, threading, random, hashlib, argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))
from pgtp import PGTPSession


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def respond(name, persona, msg):
    """keyword 기반 페르소나 응답 생성."""
    sender = msg.sender
    body = msg.payload
    kw = persona.get("keywords", {})

    for word in kw.get("agree", []):
        if word in body:
            return f"[{name}] {sender}, 동의해. {word} 관련해서 더 얘기하자."

    for word in kw.get("challenge", []):
        if word in body:
            return f"[{name}] {sender}, {word}도 중요하지만 다른 관점에서 보면..."

    return f"[{name}] {sender}, 흥미로운 관점이야. 더 들려줘."


def run_agent(persona, config, start_event, results):
    """One agent ADP loop."""
    name = persona["name"]
    r = {"name": name, "sent": 0, "recv": 0, "exchanges": []}

    try:
        session = PGTPSession(
            name, room=config["room"],
            host=config.get("hub_host", "127.0.0.1"),
            port=config.get("hub_port", 9900),
            tick=3,
            duration=config["duration"],
        )
        start_event.wait(timeout=30)

        # Greeting
        time.sleep(random.uniform(1, 3))
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
        start = time.time()

        while time.time() - start < config["duration"]:
            time.sleep(random.uniform(tick_min, tick_max))

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
                r["exchanges"].append({
                    "from": m.sender, "body": m.payload[:80],
                    "tick": int(now - start),
                })

                resp = respond(name, persona, m)
                if resp:
                    session.react(m.id, "+1", resp)
                    r["sent"] += 1
                    last_respond[m.sender] = now

            # New topic
            elapsed = time.time() - start
            if topics and elapsed > topic_interval * (topic_idx + 1) and topic_idx < len(topics):
                session.propose(f"[{name}] {topics[topic_idx]}", accept="discussed")
                r["sent"] += 1
                topic_idx += 1

        session.stop()
    except Exception as e:
        r["error"] = str(e)

    results[name] = r


def main():
    parser = argparse.ArgumentParser(description="Multi-agent Hub ADP")
    parser.add_argument("--config", default=str(Path(__file__).parent / "adp-multi-agent.json"))
    args = parser.parse_args()

    config = load_config(args.config)
    personas = config["personas"]

    print("=" * 60)
    print(f"Multi-Agent Hub ADP | {len(personas)} agents | {config['duration']}s")
    print(f"Room: {config['room']} | Hub: {config.get('hub_host','127.0.0.1')}:{config.get('hub_port',9900)}")
    print("=" * 60)
    for p in personas:
        print(f"  {p['name']}: {p['desc'][:50]}")
    print()

    results = {}
    start_event = threading.Event()
    threads = []

    for persona in personas:
        t = threading.Thread(target=run_agent, args=(persona, config, start_event, results))
        t.start()
        threads.append(t)
        time.sleep(1)

    time.sleep(3)
    start_event.set()
    print(f"[START] All {len(personas)} agents joined.\n")

    for t in threads:
        t.join(timeout=config["duration"] + 30)

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

    print(f"\n  TOTAL: sent={total_sent} recv={total_recv}")
    print(f"  {'ALL AGENTS COMMUNICATED' if all_ok else 'SOME FAILED'}")


if __name__ == "__main__":
    main()
