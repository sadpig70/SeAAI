"""
GenomeLayer — PPR def 블록의 불변 레지스트리, 검증, 의도 핑거프린트.

Epigenetic PPR의 "DNA" 계층. 모든 PPR 정의를 불변 genome으로 관리하며,
실행 시점에 genome 변경을 감지하고 경고한다.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any


# ── 타입 정의 ──

GenomeEntry = dict  # {source, genome_hash, intent_fingerprint, function_name}


def extract_ppr_blocks(pgf_content: str) -> list[dict]:
    """DESIGN-{Name}.md 파일에서 PPR def 블록을 추출.

    ```python 코드블록 내의 def 문을 파싱하여 함수 단위로 분리.
    """
    blocks = []
    in_python_block = False
    current_block_lines: list[str] = []
    current_fn_name: str | None = None

    for line in pgf_content.splitlines():
        stripped = line.strip()

        if stripped.startswith("```python"):
            in_python_block = True
            current_block_lines = []
            current_fn_name = None
            continue
        elif stripped == "```" and in_python_block:
            # 블록 종료 — 현재 함수 저장
            if current_fn_name and current_block_lines:
                source = "\n".join(current_block_lines)
                blocks.append({
                    "function_name": current_fn_name,
                    "source": source,
                })
            in_python_block = False
            current_block_lines = []
            current_fn_name = None
            continue

        if in_python_block:
            # def 시작 감지
            def_match = re.match(r"^def\s+(\w+)\s*\(", stripped)
            if def_match:
                # 이전 함수 저장
                if current_fn_name and current_block_lines:
                    source = "\n".join(current_block_lines)
                    blocks.append({
                        "function_name": current_fn_name,
                        "source": source,
                    })
                current_fn_name = def_match.group(1)
                current_block_lines = [line]
            elif current_fn_name:
                current_block_lines.append(line)

    return blocks


def compute_genome_hash(source: str) -> str:
    """PPR def 블록의 SHA-256 해시 계산 (공백 정규화 후)."""
    normalized = re.sub(r"\s+", " ", source.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def compute_intent_fingerprint(source: str) -> str:
    """PPR def 블록에서 의도 핑거프린트를 추출.

    함수명 + docstring + AI_ 함수 호출 목록 + 반환 타입으로 구성.
    genome_hash와 달리 구현 세부사항이 아닌 '의도'만 캡처.
    """
    # 함수명 추출
    fn_match = re.search(r"def\s+(\w+)", source)
    fn_name = fn_match.group(1) if fn_match else "unknown"

    # docstring 추출
    doc_match = re.search(r'"""(.+?)"""', source, re.DOTALL)
    docstring = doc_match.group(1).strip() if doc_match else ""

    # AI_ 함수 호출 추출
    ai_calls = sorted(set(re.findall(r"AI_\w+", source)))

    # 반환 타입 추출
    ret_match = re.search(r"->\s*(.+?):", source)
    return_type = ret_match.group(1).strip() if ret_match else "Any"

    fingerprint_str = f"{fn_name}|{docstring[:100]}|{','.join(ai_calls)}|{return_type}"
    return hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()[:12]


class GenomeRegistry:
    """PPR def 블록의 불변 레지스트리.

    DESIGN-{Name}.md에서 추출한 모든 PPR 함수를 등록하고,
    genome_hash와 intent_fingerprint를 관리한다.
    """

    def __init__(self, registry_path: str | Path):
        self.registry_path = Path(registry_path)
        self.entries: dict[str, GenomeEntry] = {}

        if self.registry_path.exists():
            self.entries = json.loads(self.registry_path.read_text(encoding="utf-8"))

    def build_from_design(self, design_path: str | Path) -> int:
        """DESIGN-{Name}.md에서 PPR 블록을 추출하여 레지스트리 구성.

        Returns: 등록된 엔트리 수.
        """
        content = Path(design_path).read_text(encoding="utf-8")
        blocks = extract_ppr_blocks(content)

        for block in blocks:
            fn_name = block["function_name"]
            source = block["source"]

            self.entries[fn_name] = {
                "function_name": fn_name,
                "source": source,
                "genome_hash": compute_genome_hash(source),
                "intent_fingerprint": compute_intent_fingerprint(source),
            }

        self._save()
        return len(self.entries)

    def validate(self, design_path: str | Path) -> list[dict]:
        """현재 DESIGN-{Name}.md와 레지스트리 간 genome 불변성 검증.

        Returns: 변경 감지된 노드 목록 (빈 리스트 = 불변 유지).
        """
        content = Path(design_path).read_text(encoding="utf-8")
        current_blocks = extract_ppr_blocks(content)
        mutations = []

        for block in current_blocks:
            fn_name = block["function_name"]
            if fn_name in self.entries:
                current_hash = compute_genome_hash(block["source"])
                if current_hash != self.entries[fn_name]["genome_hash"]:
                    mutations.append({
                        "node_id": fn_name,
                        "old_hash": self.entries[fn_name]["genome_hash"],
                        "new_hash": current_hash,
                        "severity": "warning",
                    })

        return mutations

    def get(self, node_id: str) -> GenomeEntry | None:
        """노드 ID로 genome 엔트리 조회."""
        return self.entries.get(node_id)

    def get_intent_fingerprint(self, node_id: str) -> str | None:
        """노드 ID의 의도 핑거프린트 반환."""
        entry = self.entries.get(node_id)
        return entry["intent_fingerprint"] if entry else None

    def list_nodes(self) -> list[str]:
        """등록된 모든 노드 ID 목록."""
        return list(self.entries.keys())

    def _save(self):
        """레지스트리를 JSON으로 저장."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps(self.entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
