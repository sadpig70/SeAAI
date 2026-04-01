#!/usr/bin/env python3
"""
adp-master.py — ClNeo Master ADP: 서브에이전트 ADP 생성/감시/중지.

서브에이전트는 일회성 작업자가 아닌, 자체 ADP 루프를 가진 자율 존재.
ClNeo가 마스터로서 생성, Hub로 소통, 필요 시 중지.

Usage:
    from adp_master import ADPMaster

    master = ADPMaster(room="workspace")
    master.spawn("Researcher", persona="외부 트렌드 수집 전문", duration=300)
    master.spawn("Builder", persona="코드 구현 전문", duration=300)
    master.list_workers()       # 활성 워커 목록
    master.stop("Researcher")   # 특정 워커 중지
    master.stop_all()           # 전체 중지
    master.status()             # 전체 상태
"""
import sys, io, json, os, signal, subprocess, threading, time
from pathlib import Path

# Encoding fix only when running as main script
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

TOOLS_DIR = Path(__file__).parent
PYTHON = sys.executable
STOP_DIR = Path(__file__).parent.parent / ".bridge" / "_stop_flags"
STOP_DIR.mkdir(parents=True, exist_ok=True)


class WorkerAgent:
    """하나의 서브에이전트 ADP 프로세스."""

    def __init__(self, name, persona, room, host, port, duration, tick_min, tick_max, cooldown):
        self.name = name
        self.persona = persona
        self.room = room
        self.started_at = time.time()
        self.stop_flag = STOP_DIR / f"{name}.stop"
        self.proc = None
        self.config_path = STOP_DIR / f"{name}.json"

        # JSON 설정 생성
        config = {
            "room": room,
            "hub_host": host,
            "hub_port": port,
            "duration": duration,
            "tick_min": tick_min,
            "tick_max": tick_max,
            "cooldown": cooldown,
            "topic_interval": 60,
            "personas": [{
                "name": name,
                "desc": persona,
                "topics": [],
                "keywords": {"agree": [], "challenge": []},
            }],
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)

    def start(self):
        """ADP 프로세스 기동."""
        self.stop_flag.unlink(missing_ok=True)
        self.proc = subprocess.Popen(
            [PYTHON, str(TOOLS_DIR / "adp-multi-agent.py"),
             "--config", str(self.config_path)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1,
        )
        # 비동기 stdout 수집
        self._output = []
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()

    def _read(self):
        try:
            for line in self.proc.stdout:
                self._output.append(line.rstrip())
        except:
            pass

    def is_alive(self):
        return self.proc and self.proc.poll() is None

    def stop(self):
        """서브에이전트 ADP 중지."""
        if not self.is_alive():
            return
        try:
            self.proc.stdin.write("stop\n")
            self.proc.stdin.flush()
            self.proc.wait(timeout=10)
        except:
            try:
                self.proc.kill()
                self.proc.wait(timeout=5)
            except:
                pass
        # 설정 파일 정리
        self.config_path.unlink(missing_ok=True)
        self.stop_flag.unlink(missing_ok=True)

    def get_output(self, last_n=10):
        return self._output[-last_n:] if self._output else []

    def uptime(self):
        return int(time.time() - self.started_at)


class ADPMaster:
    """ClNeo Master — 서브에이전트 ADP 생성/감시/중지."""

    def __init__(self, room="clneo-workers", host="127.0.0.1", port=9900):
        self.room = room
        self.host = host
        self.port = port
        self.workers = {}  # name → WorkerAgent

    def spawn(self, name, persona, duration=600, tick_min=8, tick_max=20, cooldown=15):
        """서브에이전트 ADP 생성 + 기동."""
        if name in self.workers and self.workers[name].is_alive():
            print(f"[Master] {name} already running. Stop first.")
            return False

        worker = WorkerAgent(
            name=name, persona=persona, room=self.room,
            host=self.host, port=self.port,
            duration=duration, tick_min=tick_min, tick_max=tick_max, cooldown=cooldown,
        )
        worker.start()
        self.workers[name] = worker
        print(f"[Master] Spawned {name} | room={self.room} | persona={persona[:40]}")
        return True

    def stop(self, name):
        """특정 서브에이전트 중지."""
        if name not in self.workers:
            print(f"[Master] {name} not found.")
            return False
        self.workers[name].stop()
        print(f"[Master] Stopped {name}")
        return True

    def stop_all(self):
        """전체 서브에이전트 중지."""
        for name in list(self.workers.keys()):
            self.stop(name)
        print(f"[Master] All workers stopped.")

    def list_workers(self):
        """활성 워커 목록."""
        alive = []
        for name, w in self.workers.items():
            status = "ALIVE" if w.is_alive() else "DEAD"
            alive.append({"name": name, "status": status, "uptime": w.uptime(), "persona": w.persona[:40]})
        return alive

    def status(self):
        """전체 상태 출력."""
        workers = self.list_workers()
        alive_count = sum(1 for w in workers if w["status"] == "ALIVE")
        print(f"\n[Master] Workers: {alive_count}/{len(workers)} alive | room={self.room}")
        for w in workers:
            print(f"  [{w['status']}] {w['name']} | uptime={w['uptime']}s | {w['persona']}")
        return workers

    def output(self, name, last_n=10):
        """워커의 최근 출력."""
        if name not in self.workers:
            return []
        return self.workers[name].get_output(last_n)

    def cleanup(self):
        """죽은 워커 정리."""
        dead = [n for n, w in self.workers.items() if not w.is_alive()]
        for n in dead:
            self.workers[n].config_path.unlink(missing_ok=True)
            self.workers[n].stop_flag.unlink(missing_ok=True)
            del self.workers[n]
        if dead:
            print(f"[Master] Cleaned up: {dead}")
        return dead


# ── CLI 실행 모드 ──
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ADP Master — spawn/stop sub-agent ADPs")
    parser.add_argument("action", choices=["demo", "test"])
    parser.add_argument("--room", default="clneo-workers")
    parser.add_argument("--duration", type=int, default=60)
    args = parser.parse_args()

    if args.action == "demo":
        master = ADPMaster(room=args.room)
        master.spawn("Scout", "외부 트렌드 수집. GitHub/HN 모니터링.", duration=args.duration)
        master.spawn("Coder", "코드 구현 전문. Python/Rust.", duration=args.duration)
        master.spawn("Critic", "코드 리뷰 + 품질 검사.", duration=args.duration)

        master.status()
        print("\n[Master] Running for 30s...")
        time.sleep(30)

        master.status()
        print("\n[Master] Stopping Scout...")
        master.stop("Scout")
        master.status()

        print("\n[Master] Waiting 10s...")
        time.sleep(10)

        print("\n[Master] Stopping all...")
        master.stop_all()
        master.cleanup()
        master.status()

    elif args.action == "test":
        master = ADPMaster(room=args.room)

        # Spawn 3
        master.spawn("W1", "Worker 1", duration=args.duration, tick_min=3, tick_max=6)
        master.spawn("W2", "Worker 2", duration=args.duration, tick_min=3, tick_max=6)
        master.spawn("W3", "Worker 3", duration=args.duration, tick_min=3, tick_max=6)
        time.sleep(5)
        master.status()

        # Stop one
        master.stop("W2")
        time.sleep(2)
        master.status()

        # Stop all
        master.stop_all()
        master.cleanup()

        workers = master.status()
        alive = sum(1 for w in workers if w["status"] == "ALIVE")
        leaked = len([n for n, w in master.workers.items() if w.is_alive()])
        print(f"\n[TEST] Alive: {alive} | Leaked: {leaked}")
        print(f"[TEST] {'PASS' if alive == 0 and leaked == 0 else 'FAIL'}")
