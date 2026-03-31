#!/usr/bin/env python3
"""
Signalion 환경 변수 관리자
.env 파일에서 API 키를 로드하여 사용.

사용법:
    from env_manager import get_key, list_keys, has_key

    # API 키 로드
    token = get_key("GITHUB_TOKEN")

    # 키 존재 확인
    if has_key("OPENAI_API_KEY"):
        ...

    # 전체 키 목록 (값은 마스킹)
    list_keys()
"""
import os
from pathlib import Path

# .env 파일 위치: 프로젝트 루트
ENV_FILE = Path("D:/SeAAI/Signalion/.env")


def load_env():
    """
    .env 파일을 파싱하여 os.environ에 로드.
    python-dotenv 없이 직접 구현 (외부 의존성 제거).
    """
    if not ENV_FILE.exists():
        return False

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 빈 줄, 주석 건너뜀
            if not line or line.startswith("#"):
                continue
            # KEY=VALUE 파싱
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # 따옴표 제거
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            # os.environ에 설정 (기존 값이 없을 때만)
            if key not in os.environ:
                os.environ[key] = value

    return True


def get_key(key_name: str, default: str = "") -> str:
    """API 키 로드. .env → os.environ 순서로 탐색."""
    # 아직 로드 안 됐으면 로드
    if not os.environ.get("_SIGNALION_ENV_LOADED"):
        if load_env():
            os.environ["_SIGNALION_ENV_LOADED"] = "1"

    return os.environ.get(key_name, default)


def has_key(key_name: str) -> bool:
    """키 존재 여부 확인."""
    return bool(get_key(key_name))


def list_keys() -> dict:
    """전체 키 목록 반환. 값은 마스킹 처리."""
    load_env()

    known_keys = [
        "X_BEARER_TOKEN",
        "GITHUB_TOKEN", "HUGGINGFACE_TOKEN",
        "KAGGLE_USERNAME", "KAGGLE_KEY",
        "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
        "VERCEL_TOKEN", "RAILWAY_TOKEN",
        "PRODUCTHUNT_TOKEN",
    ]

    result = {}
    for key in known_keys:
        value = os.environ.get(key, "")
        if value:
            # 마스킹: 앞 4자 + *** + 뒤 4자
            if len(value) > 12:
                masked = value[:4] + "***" + value[-4:]
            else:
                masked = "***set***"
            result[key] = masked
        else:
            result[key] = "(not set)"

    return result


def print_status():
    """키 상태 출력."""
    keys = list_keys()
    print(f".env file: {'EXISTS' if ENV_FILE.exists() else 'NOT FOUND'}")
    print(f"Location: {ENV_FILE}")
    print(f"\nKey Status:")
    for key, status in keys.items():
        marker = "O" if status != "(not set)" else "X"
        print(f"  [{marker}] {key}: {status}")


if __name__ == "__main__":
    print_status()
