#!/usr/bin/env python3
"""
基于变更生成规范提交信息。
遵循 Conventional Commits 规范。
"""

import subprocess
import argparse
from pathlib import Path


def get_changed_files():
    """获取变更文件列表。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def get_diff_stat():
    """获取 diff 统计信息。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--stat"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def detect_scope(files):
    """从变更文件中检测范围。"""
    scopes = set()
    for f in files:
        parts = f.split("/")
        if len(parts) > 1:
            scopes.add(parts[0])
        else:
            scopes.add(Path(f).stem)
    return sorted(scopes)[0] if scopes else None


def detect_type(files):
    """根据变更文件自动检测提交类型。"""
    if any("test" in f.lower() for f in files):
        return "test"
    if all(f.endswith(".md") or f.startswith("docs/") for f in files):
        return "docs"
    return None


def main():
    parser = argparse.ArgumentParser(description="生成规范提交信息")
    parser.add_argument("--type", "-t",
                        choices=["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"],
                        help="提交类型（不指定则自动检测）")
    parser.add_argument("--description", "-d", required=True, help="简短描述")
    parser.add_argument("--scope", "-s", help="范围（不指定则自动检测）")
    parser.add_argument("--body", "-b", help="提交正文")
    parser.add_argument("--breaking", action="store_true", help="标记为破坏性变更")
    parser.add_argument("--issues", help="相关问题（逗号分隔）")

    args = parser.parse_args()

    changed_files = get_changed_files()
    if not changed_files:
        print("错误：未找到已暂存的变更。请先用 git add 暂存。")
        return

    # 自动检测
    commit_type = args.type or detect_type(changed_files) or "feat"
    scope = args.scope or detect_scope(changed_files)

    # 标题
    header = f"{commit_type}({scope}): {args.description}" if scope else f"{commit_type}: {args.description}"
    if args.breaking:
        header = header.replace(":", "!:", 1) if "!" not in header else header

    message = header

    # 正文
    body = args.body
    if not body:
        diff_stat = get_diff_stat()
        if diff_stat:
            body = "变更：\n" + diff_stat
    if body:
        message += f"\n\n{body}"

    # 页脚
    footer_parts = []
    if args.breaking:
        footer_parts.append("BREAKING CHANGE: 此提交包含破坏性变更")
    if args.issues:
        for i in args.issues.split(","):
            footer_parts.append(f"修复 #{i.strip()}")
    if footer_parts:
        message += "\n\n" + "\n".join(footer_parts)

    print(message)


if __name__ == "__main__":
    main()
