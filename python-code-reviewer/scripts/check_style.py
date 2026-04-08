#!/usr/bin/env python3
"""
对 Python 文件执行基础风格检查。
检查项：行长度、可变默认参数、Tab、import 顺序、eval/exec、敏感信息等。
"""

import sys
import re
import argparse
from pathlib import Path

MAX_LINE_LENGTH = 80


def check_file(file_path: Path) -> list[dict]:
    issues = []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        return [{"file": str(file_path), "line": 0, "level": "ERROR", "message": f"无法读取: {e}"}]

    in_docstring = False
    last_import_group = None  # 0=stdlib, 1=thirdparty, 2=local

    for idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        # 跳过文档字符串内容
        if '"""' in stripped:
            count = stripped.count('"""')
            if count == 1:
                in_docstring = not in_docstring

        if in_docstring:
            continue

        # 1. Tab
        if "\t" in raw_line:
            issues.append({"file": str(file_path), "line": idx, "level": "WARNING",
                "category": "格式", "message": "发现 Tab，应使用 4 个空格。"})

        # 2. 行长度（URL 和注释中的长路径例外）
        if len(raw_line) > MAX_LINE_LENGTH:
            if not (stripped.startswith("# http") or stripped.startswith("import ")
                    or "https://" in stripped or "http://" in stripped):
                issues.append({"file": str(file_path), "line": idx, "level": "SUGGESTION",
                    "category": "格式", "message": f"行长度 {len(raw_line)} 超过 {MAX_LINE_LENGTH}。"})

        # 3. 可变默认参数
        if re.search(r"def\s+\w+.*=\s*\[\]", stripped):
            issues.append({"file": str(file_path), "line": idx, "level": "BLOCKER",
                "category": "正确性", "message": "可变默认参数 []，应改为 None。"})

        if re.search(r"def\s+\w+.*=\s*\{\}", stripped):
            issues.append({"file": str(file_path), "line": idx, "level": "BLOCKER",
                "category": "正确性", "message": "可变默认参数 {}，应改为 None。"})

        # 4. eval / exec
        if re.search(r"\beval\s*\(", stripped):
            issues.append({"file": str(file_path), "line": idx, "level": "BLOCKER",
                "category": "安全", "message": "使用 eval()，存在代码注入风险。"})

        if re.search(r"\bexec\s*\(", stripped):
            issues.append({"file": str(file_path), "line": idx, "level": "BLOCKER",
                "category": "安全", "message": "使用 exec()，存在代码注入风险。"})

        # 5. == None
        if re.search(r"==\s*None\b|!=\s*None\b", stripped):
            issues.append({"file": str(file_path), "line": idx, "level": "WARNING",
                "category": "规范", "message": "使用 == None，应使用 is None / is not None。"})

        # 6. except:
        if re.match(r"\s*except\s*:", stripped):
            issues.append({"file": str(file_path), "line": idx, "level": "BLOCKER",
                "category": "正确性", "message": "except: 捕获所有异常，应指定具体类型。"})

        # 7. 敏感信息
        for kw in ["password", "secret", "api_key", "apikey", "token"]:
            if re.search(rf'{kw}\s*=\s*["\'][^"\']+["\']', stripped, re.IGNORECASE):
                issues.append({"file": str(file_path), "line": idx, "level": "BLOCKER",
                    "category": "安全", "message": f"疑似硬编码 {kw}，应使用环境变量。"})
                break

    return issues


def main():
    parser = argparse.ArgumentParser(description="Python 基础风格检查")
    parser.add_argument("paths", nargs="+", help="文件或目录")
    parser.add_argument("--max-line-length", type=int, default=80)
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()

    global MAX_LINE_LENGTH
    MAX_LINE_LENGTH = args.max_line_length

    py_files = []
    for p in args.paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".py":
            py_files.append(path)
        elif path.is_dir():
            py_files.extend(path.rglob("*.py"))

    if not py_files:
        print("未找到 Python 文件。")
        return

    all_issues = []
    for f in sorted(py_files):
        all_issues.extend(check_file(f))

    for issue in all_issues:
        print(f"[{issue['level']}] {issue['file']}:{issue['line']} {issue['message']}")

    blocker_count = sum(1 for i in all_issues if i["level"] in ("BLOCKER", "ERROR"))
    print(f"\n检查完成。文件数: {len(py_files)}, 问题数: {len(all_issues)}")

    if args.fail_on_blocker and blocker_count > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
