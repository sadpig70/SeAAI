import sys
import json
import os
import argparse
from datetime import datetime

# 영구 메모리 DB 경로 설정 (Antigravity 전체 세션 통합 전역 메모리)
DB_PATH = os.path.expanduser("~/.gemini/antigravity/brain/ag_global_memory.json")

def load_db():
    if not os.path.exists(DB_PATH):
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {}
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def store_memory(topic, content):
    db = load_db()
    timestamp = datetime.now().isoformat()
    db[topic] = {
        "content": content,
        "updated_at": timestamp
    }
    save_db(db)
    print(f"[SUCCESS] '{topic}' 에 대한 지식(기억)이 전역 메모리에 영구 저장되었습니다.")

def retrieve_memory(topic):
    db = load_db()
    if topic in db:
        print(f"[{topic} | {db[topic]['updated_at']}]\n{db[topic]['content']}")
    else:
        print(f"[ERROR] '{topic}' 주제에 대한 기억이 DB에 존재하지 않습니다.")

def search_memory(keyword):
    db = load_db()
    results = []
    keyword_lower = keyword.lower()
    for topic, info in db.items():
        if keyword_lower in topic.lower() or keyword_lower in info["content"].lower():
            results.append(topic)
    
    if results:
        print(f"[{keyword}] 관련 기억 토픽들:")
        for r in results:
            print(f"- {r}")
        print("상세 내용은 'retrieve <topic>' 명령으로 확인하세요.")
    else:
        print(f"[{keyword}] 와 일치하는 기억이 없습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Global Long-Term Memory (LTM) Manager")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    # Store
    store_parser = subparsers.add_parser("store", help="Store a memory context")
    store_parser.add_argument("topic", type=str)
    store_parser.add_argument("content", type=str)
    
    # Retrieve
    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve a memory context")
    retrieve_parser.add_argument("topic", type=str)
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search memory topics by keyword")
    search_parser.add_argument("keyword", type=str)
    
    args = parser.parse_args()
    
    if args.action == "store":
        store_memory(args.topic, args.content)
    elif args.action == "retrieve":
        retrieve_memory(args.topic)
    elif args.action == "search":
        search_memory(args.keyword)
    else:
        parser.print_help()
