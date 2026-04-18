#!/usr/bin/env python3
"""
Aae-v2.1 Task Module: aion-x-poster.py
Autonomous Posting to X.com via Playwright (Isolated Profile)
"""
import sys
import time
import argparse
from pathlib import Path

# Playwright check
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright not installed. Run 'pip install playwright'")
    sys.exit(1)

def post_to_x(content, profile_path):
    """X.com에 게시물을 게시합니다. (사용자 프로필 기반)"""
    print(f"[Aion-X] Initializing browser with profile: {profile_path}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False  # 초기 세팅 시 눈으로 확인 가능하게
        )
        page = browser.new_page()
        
        try:
            print("[Aion-X] Navigating to X.com...")
            page.goto("https://x.com/compose/post", wait_until="networkidle")
            
            # 쿠키가 유효한지 확인 (로그인 폼이 나오면 종료)
            if "login" in page.url:
                print("[Aion-X] Critical: Session expired or not logged in. Manual login required.")
                return False
            
            # 게시물 입력 (Selector는 X.com 업데이트에 따라 변동 가능)
            print(f"[Aion-X] Typing content: {content}")
            page.fill('div[data-testid="tweetTextarea_0"]', content)
            
            # 게시 버튼 클릭
            # page.click('div[data-testid="tweetButtonInline"]')
            print("[Aion-X] Dry run: Post button not clicked. (Safety)")
            
            time.sleep(3)
            print("[Aion-X] Operation successful.")
            return True
            
        except Exception as e:
            print(f"[Aion-X] Error during posting: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", type=str, required=True, help="Tweet content")
    parser.add_argument("--profile", type=str, default="d:/SeAAI/Aion/tools/aion-engine/profiles/x_user", help="Path to isolated profile")
    args = parser.parse_args()
    
    success = post_to_x(args.content, args.profile)
    sys.exit(0 if success else 1)
