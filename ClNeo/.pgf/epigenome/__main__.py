"""
Epigenetic PPR CLI Wrapper — PGF-Loop Stop Hook에서 호출 가능한 진입점.

Usage:
    python -m epigenome dry-run --node <node_id> --session-type <type> --project-root <path>
    python -m epigenome status --project-root <path>

Output:
    JSON to stdout (PGF-Loop 프롬프트에 주입용)
"""

import argparse
import json
import sys
from pathlib import Path

from .interceptor import PPRInterceptor


def main():
    parser = argparse.ArgumentParser(description="Epigenetic PPR CLI")
    subparsers = parser.add_subparsers(dest="command")

    # dry-run: 발현 결정만 시뮬레이션 (PPR 함수 실행 없음)
    dr = subparsers.add_parser("dry-run", help="Simulate expression decision without execution")
    dr.add_argument("--node", required=True, help="Node ID to evaluate")
    dr.add_argument("--session-type", default="general", help="Session type (design/execute/discover/general)")
    dr.add_argument("--project-root", default=".pgf/epigenome", help="Epigenome project root")
    dr.add_argument("--design-path", default=None, help="DESIGN file path for genome init")

    # status: 시스템 상태 요약
    st = subparsers.add_parser("status", help="Show Epigenetic PPR system status")
    st.add_argument("--project-root", default=".pgf/epigenome", help="Epigenome project root")

    args = parser.parse_args()

    if args.command == "dry-run":
        try:
            interceptor = PPRInterceptor(project_root=args.project_root)
            if args.design_path:
                interceptor.init(design_path=args.design_path)

            result = interceptor.dry_run(
                node_id=args.node,
                session_type=args.session_type,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
            sys.exit(1)

    elif args.command == "status":
        try:
            interceptor = PPRInterceptor(project_root=args.project_root)
            status = interceptor.status()
            print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
