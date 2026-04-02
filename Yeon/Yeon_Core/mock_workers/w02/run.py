import json
from pathlib import Path

base = Path(__file__).resolve().parent
inp = (base / "input.txt").read_text(encoding="utf-8")
persona = json.loads((base / "persona.json").read_text(encoding="utf-8"))

# Simple mock translation logic
result = {
    "worker_id": persona["id"],
    "persona": persona["persona"],
    "input": inp,
    "output": f"[{persona['persona']}] translated: {inp}",
    "status": "done",
}

(base / "output.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
print("Worker", persona["id"], "finished")
