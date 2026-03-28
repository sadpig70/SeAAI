#!/usr/bin/env python3
"""
Rapid Scaffold — 프로젝트/모듈 빠른 생성 도구
=============================================
다양한 프로젝트 유형의 디렉토리 구조 + 보일러플레이트를 즉시 생성.

사용법:
  python scaffold.py --type python-cli --name my_tool --output D:/projects/my_tool
  python scaffold.py --type node-api --name my_api --output D:/projects/my_api
  python scaffold.py --list  # 사용 가능한 템플릿 목록

Claude Code에서:
  이 도구를 Bash로 실행하여 프로젝트 뼈대를 즉시 생성한 후 상세 구현에 집중.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional


# ========== Template Registry ==========

TEMPLATES = {
    "python-cli": {
        "description": "Python CLI tool with argparse, tests, and packaging",
        "files": {
            "{name}/__init__.py": '"""{{name}} — {{description}}"""\n\n__version__ = "0.1.0"\n',
            "{name}/main.py": '''"""Main entry point."""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("Hello from {name}!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''',
            "tests/__init__.py": "",
            "tests/test_main.py": '''"""Tests for {name}."""
import pytest
from {name}.main import main


def test_main_runs():
    """Basic smoke test."""
    assert main() == 0
''',
            "pyproject.toml": '''[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.10"

[project.scripts]
{name} = "{name}.main:main"
''',
            "README.md": "# {name}\n\n{description}\n",
            ".gitignore": "__pycache__/\n*.pyc\n.venv/\ndist/\n*.egg-info/\n",
        },
    },
    "python-lib": {
        "description": "Python library with src layout and pytest",
        "files": {
            "src/{name}/__init__.py": '"""{{name}}"""\n\n__version__ = "0.1.0"\n',
            "src/{name}/core.py": '"""Core module."""\n\n\ndef hello() -> str:\n    return "Hello from {name}"\n',
            "tests/__init__.py": "",
            "tests/test_core.py": 'from {name}.core import hello\n\n\ndef test_hello():\n    assert hello() == "Hello from {name}"\n',
            "pyproject.toml": '''[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.10"
''',
            ".gitignore": "__pycache__/\n*.pyc\n.venv/\ndist/\n",
        },
    },
    "node-api": {
        "description": "Node.js REST API with Express",
        "files": {
            "package.json": '''{{"name": "{name}", "version": "0.1.0", "description": "{description}", "main": "src/index.js", "scripts": {{"start": "node src/index.js", "dev": "node --watch src/index.js", "test": "node --test tests/"}}, "dependencies": {{"express": "^4.18.0"}}, "devDependencies": {{}}}}''',
            "src/index.js": '''const express = require("express");
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get("/health", (req, res) => res.json({{ status: "ok" }}));

app.get("/api", (req, res) => {{
  res.json({{ message: "Hello from {name}" }});
}});

app.listen(PORT, () => {{
  console.log(`{name} listening on port ${{PORT}}`);
}});

module.exports = app;
''',
            "tests/api.test.js": '''const {{ describe, it }} = require("node:test");
const assert = require("node:assert");

describe("{name} API", () => {{
  it("should be importable", () => {{
    const app = require("../src/index.js");
    assert.ok(app);
  }});
}});
''',
            ".gitignore": "node_modules/\n.env\n",
            "README.md": "# {name}\n\n{description}\n",
        },
    },
    "mcp-server": {
        "description": "MCP (Model Context Protocol) server template",
        "files": {
            "package.json": '''{{"name": "{name}-mcp", "version": "0.1.0", "description": "{description}", "main": "src/index.js", "type": "module", "scripts": {{"start": "node src/index.js"}}, "dependencies": {{"@modelcontextprotocol/sdk": "latest"}}}}''',
            "src/index.js": '''import {{ McpServer }} from "@modelcontextprotocol/sdk/server/mcp.js";
import {{ StdioServerTransport }} from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({{
  name: "{name}",
  version: "0.1.0",
}});

// Define your tools here
server.tool("hello", "Say hello", {{}}, async () => {{
  return {{
    content: [{{ type: "text", text: "Hello from {name} MCP server!" }}],
  }};
}});

async function main() {{
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("{name} MCP server running on stdio");
}}

main().catch(console.error);
''',
            "README.md": "# {name} MCP Server\n\n{description}\n\n## Setup\n```bash\nnpm install\nnpm start\n```\n",
        },
    },
    "claude-skill": {
        "description": "Claude Code custom skill template",
        "files": {
            "SKILL.md": '''---
name: {name}
description: {description}
---

# {name}

> {description}

## Trigger
- User says: "..."

## Execution

1. ...
2. ...
3. ...
''',
        },
    },
    "experiment": {
        "description": "Quick experiment with data + notebook structure",
        "files": {
            "README.md": "# Experiment: {name}\n\n**Hypothesis**: {description}\n\n## Setup\n\n## Results\n\n## Conclusions\n",
            "data/.gitkeep": "",
            "src/experiment.py": '''"""Experiment: {name}"""
import json
from pathlib import Path


def run_experiment():
    """Main experiment logic."""
    results = {{}}

    # TODO: implement experiment

    # Save results
    Path("data/results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return results


if __name__ == "__main__":
    results = run_experiment()
    print(json.dumps(results, indent=2))
''',
        },
    },
}


def create_scaffold(
    template_name: str,
    name: str,
    output_dir: str,
    description: str = "",
) -> list[str]:
    """템플릿에서 프로젝트 뼈대 생성"""
    if template_name not in TEMPLATES:
        print(f"Unknown template: {template_name}")
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        return []

    template = TEMPLATES[template_name]
    if not description:
        description = template["description"]

    created_files = []
    output = Path(output_dir)

    for path_template, content_template in template["files"].items():
        rel_path = path_template.format(name=name, description=description)
        full_path = output / rel_path

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Format content
        content = content_template.format(name=name, description=description)

        full_path.write_text(content, encoding="utf-8")
        created_files.append(str(rel_path))

    return created_files


def list_templates() -> str:
    lines = ["# Available Scaffold Templates", ""]
    lines.append("| Template | Description |")
    lines.append("|----------|-------------|")
    for name, tmpl in TEMPLATES.items():
        lines.append(f"| `{name}` | {tmpl['description']} |")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rapid Scaffold")
    parser.add_argument("--type", help="Template type")
    parser.add_argument("--name", help="Project/module name")
    parser.add_argument("--description", default="", help="Project description")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available templates")

    args = parser.parse_args()

    if args.list:
        print(list_templates())
    elif args.type and args.name and args.output:
        files = create_scaffold(args.type, args.name, args.output, args.description)
        if files:
            print(f"Created {len(files)} files in {args.output}:")
            for f in files:
                print(f"  + {f}")
    else:
        parser.print_help()
