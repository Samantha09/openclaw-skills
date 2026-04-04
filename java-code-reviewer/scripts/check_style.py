#!/usr/bin/env python3
"""
对 Java 文件执行基础风格检查。
检查项：行长度、魔法值、Tab 字符、通配符导入、System.out.print、TODO/FIXME 注释。
"""

import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict

MAX_LINE_LENGTH = 120


def check_file(file_path: Path) -> List[Dict]:
    """检查单个 Java 文件的风格问题。"""
    issues = []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        return [{"file": str(file_path), "line": 0, "level": "ERROR", "message": f"无法读取文件: {e}"}]

    in_multiline_comment = False

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line

        # 处理多行注释边界
        if "/*" in line and "*/" not in line:
            in_multiline_comment = True
        if in_multiline_comment and "*/" in line:
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue

        # 1. Tab 字符
        if "\t" in raw_line:
            issues.append(
                {
                    "file": str(file_path),
                    "line": idx,
                    "level": "WARNING",
                    "category": "格式",
                    "message": "发现 Tab 字符，应使用 4 个空格缩进。",
                }
            )

        # 2. 行长度
        if len(raw_line) > MAX_LINE_LENGTH:
            issues.append(
                {
                    "file": str(file_path),
                    "line": idx,
                    "level": "SUGGESTION",
                    "category": "格式",
                    "message": f"行长度 {len(raw_line)} 超过 {MAX_LINE_LENGTH} 字符限制。",
                }
            )

        stripped = raw_line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        # 3. 通配符导入
        if re.match(r"^import\s+[^;]*\.\*\s*;", stripped):
            issues.append(
                {
                    "file": str(file_path),
                    "line": idx,
                    "level": "WARNING",
                    "category": "规范",
                    "message": "使用通配符导入，应显式导入具体类。",
                }
            )

        # 4. System.out.print
        if "System.out.print" in stripped:
            issues.append(
                {
                    "file": str(file_path),
                    "line": idx,
                    "level": "WARNING",
                    "category": "规范",
                    "message": "使用 System.out.print 输出，建议改为 SLF4J 日志。",
                }
            )

        # 5. 魔法值（简单规则）
        # 排除字符串声明（有名字的）、return 语句中的简单布尔/数字
        magic_match = re.search(r"=\s*([\"'][^\"']{3,}[\"']|\d{3,})\s*;", stripped)
        if magic_match and not stripped.startswith("final ") and not stripped.startswith("private final"):
            # 放宽：带明显语义的关键字不算
            if not any(kw in stripped for kw in ["message", "msg", "desc", "name", "key", "error"]):
                issues.append(
                    {
                        "file": str(file_path),
                        "line": idx,
                        "level": "SUGGESTION",
                        "category": "规范",
                        "message": f"存在疑似魔法值 {magic_match.group(1)}，建议提取为具名常量。",
                    }
                )

        # 6. TODO / FIXME 标记
        if "TODO" in stripped or "FIXME" in stripped:
            issues.append(
                {
                    "file": str(file_path),
                    "line": idx,
                    "level": "SUGGESTION",
                    "category": "可维护性",
                    "message": "存在 TODO/FIXME 注释，请确认是否需要在合并前处理。",
                }
            )

    return issues


def main():
    parser = argparse.ArgumentParser(description="Java 基础风格检查")
    parser.add_argument("paths", nargs="+", help="要检查的 Java 文件或目录")
    parser.add_argument("--max-line-length", type=int, default=120, help="最大行长度")
    parser.add_argument("--fail-on-warning", action="store_true", help="发现 WARNING 时返回非零退出码")

    args = parser.parse_args()
    global MAX_LINE_LENGTH
    MAX_LINE_LENGTH = args.max_line_length

    java_files: List[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".java":
            java_files.append(path)
        elif path.is_dir():
            java_files.extend(path.rglob("*.java"))

    if not java_files:
        print("未找到 Java 文件。")
        sys.exit(0)

    all_issues = []
    for f in sorted(java_files):
        issues = check_file(f)
        all_issues.extend(issues)

    # 输出
    for issue in all_issues:
        print(f"[{issue['level']}] {issue['file']}:{issue['line']} {issue['message']}")

    summary = {
        "ERROR": 0,
        "BLOCKER": 0,
        "WARNING": 0,
        "SUGGESTION": 0,
    }
    for issue in all_issues:
        summary[issue["level"]] = summary.get(issue["level"], 0) + 1

    print(f"\n检查完成。文件数: {len(java_files)}, 问题数: {len(all_issues)}")

    if summary["ERROR"] > 0 or summary["BLOCKER"] > 0:
        sys.exit(2)
    if args.fail_on_warning and summary["WARNING"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
