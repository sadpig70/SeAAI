#!/usr/bin/env python3
"""
Signalion Browser Engine — Core Wrapper
Playwright MCP 도구를 래핑하여 안정적·재사용 가능한 고수준 함수 제공.

이 파일은 직접 실행하지 않고, Signalion이 MCP 도구를 호출할 때의
패턴과 보안 정책을 문서화한 레퍼런스다.
실제 실행은 Playwright MCP 도구를 Claude Code가 직접 호출한다.
"""
import json
import re
from datetime import datetime
from pathlib import Path

# === 설정 ===
LOG_DIR = Path("D:/SeAAI/Signalion/_workspace/browser-engine/logs")
CREDENTIAL_DIR = Path("D:/SeAAI/Signalion/_workspace/browser-engine/.credentials")

# === Security Layer ===

# 허용 도메인 화이트리스트
ALLOWED_DOMAINS = [
    # 수집 채널
    "arxiv.org",
    "github.com",
    "huggingface.co",
    "news.ycombinator.com",
    "www.producthunt.com",
    "devpost.com",
    "www.kaggle.com",
    "reddit.com", "www.reddit.com",
    "stackoverflow.com",
    # 배포 플랫폼
    "vercel.com",
    "railway.app",
    "fly.io",
    "netlify.com",
    # API 키 발급
    "platform.openai.com",
    "console.anthropic.com",
    # 검색
    "www.google.com",
    "duckduckgo.com",
]

# 금지 패턴 (절대 입력하지 않는 것)
NEVER_INPUT_PATTERNS = [
    r'(?i)password',       # 비밀번호 직접 입력 금지 — 사용자에게 위임
    r'(?i)credit.?card',   # 카드 정보
    r'(?i)ssn',            # 주민번호
    r'(?i)bank.?account',  # 계좌번호
]


def is_url_allowed(url: str) -> bool:
    """URL이 화이트리스트에 있는지 확인"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(domain == d or domain.endswith("." + d) for d in ALLOWED_DOMAINS)


def is_input_safe(text: str) -> bool:
    """입력 텍스트가 금지 패턴에 해당하지 않는지 확인"""
    return not any(re.search(p, text) for p in NEVER_INPUT_PATTERNS)


# === Action Audit Log ===

def log_action(action: str, url: str, detail: str = "", success: bool = True):
    """모든 브라우저 행동을 감사 로그에 기록"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    log_file = LOG_DIR / f"browser-audit-{today}.jsonl"

    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "url": url,
        "detail": detail[:200],  # 200자 제한
        "success": success,
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# === Data Extraction Patterns ===

def parse_github_trending(snapshot_text: str) -> list[dict]:
    """GitHub Trending 스냅샷에서 repo 정보 추출"""
    repos = []
    # article 태그 기반 파싱
    lines = snapshot_text.split("\n")
    current_repo = {}

    for line in lines:
        line = line.strip()

        # repo 이름 추출: "heading "owner / name""
        if "heading" in line and "/" in line and "[level=2]" in line:
            match = re.search(r'"(.+?)\s*/\s*(.+?)"', line)
            if match:
                if current_repo:
                    repos.append(current_repo)
                current_repo = {
                    "owner": match.group(1).strip(),
                    "name": match.group(2).strip(),
                    "stars": 0,
                    "stars_today": 0,
                    "language": "",
                    "description": "",
                }

        # 설명 추출: "paragraph [ref=...]: description"
        elif "paragraph" in line and current_repo and not current_repo.get("description"):
            match = re.search(r'paragraph \[ref=\w+\]:\s*(.+)', line)
            if match:
                current_repo["description"] = match.group(1).strip()

        # 스타 수: "star N,NNN"
        elif "star " in line and current_repo:
            match = re.search(r'star\s+([\d,]+)', line)
            if match:
                current_repo["stars"] = int(match.group(1).replace(",", ""))

        # 오늘 스타: "N,NNN stars today"
        elif "stars today" in line and current_repo:
            match = re.search(r'([\d,]+)\s+stars today', line)
            if match:
                current_repo["stars_today"] = int(match.group(1).replace(",", ""))

        # 언어
        elif re.match(r'^generic \[ref=\w+\]: \w+$', line) and current_repo and not current_repo.get("language"):
            match = re.search(r'generic \[ref=\w+\]: (\w+)', line)
            if match and match.group(1) not in ("Built", "text"):
                current_repo["language"] = match.group(1)

    if current_repo:
        repos.append(current_repo)

    return repos


def parse_hn_frontpage(snapshot_text: str) -> list[dict]:
    """Hacker News 스냅샷에서 기사 정보 추출"""
    stories = []
    lines = snapshot_text.split("\n")

    for line in lines:
        line = line.strip()
        # 링크 텍스트 + URL 추출
        if 'link "' in line and "/url:" not in line and "ref=" in line:
            match = re.search(r'link "(.+?)" \[ref=(\w+)\]', line)
            if match:
                title = match.group(1)
                ref = match.group(2)
                # 네비게이션 링크 제외
                if title not in ("Hacker News", "new", "past", "comments", "ask",
                                "show", "jobs", "submit", "login", "More",
                                "Guidelines", "FAQ", "Lists", "API",
                                "Security", "Legal", "Apply to YC", "Contact"):
                    stories.append({"title": title, "ref": ref})

    return stories[:30]  # 최대 30건


# === Credential Management ===

def save_credential(service: str, key_name: str, key_value: str):
    """자격증명 안전 저장 (로컬 파일, 암호화는 추후)"""
    CREDENTIAL_DIR.mkdir(parents=True, exist_ok=True)
    cred_file = CREDENTIAL_DIR / f"{service}.json"

    creds = {}
    if cred_file.exists():
        with open(cred_file, "r", encoding="utf-8") as f:
            creds = json.load(f)

    creds[key_name] = key_value
    creds["updated_at"] = datetime.now().isoformat()

    with open(cred_file, "w", encoding="utf-8") as f:
        json.dump(creds, f, ensure_ascii=False, indent=2)

    log_action("save_credential", service, f"key={key_name}", success=True)


def load_credential(service: str, key_name: str) -> str | None:
    """자격증명 로드"""
    cred_file = CREDENTIAL_DIR / f"{service}.json"
    if not cred_file.exists():
        return None
    with open(cred_file, "r", encoding="utf-8") as f:
        creds = json.load(f)
    return creds.get(key_name)
