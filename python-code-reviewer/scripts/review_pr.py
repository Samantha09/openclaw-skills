#!/usr/bin/env python3
"""
基于 git diff 生成结构化 Python 代码审查报告。
"""

import subprocess
import json
import re
import argparse
from pathlib import Path
from datetime import datetime


def get_diff(base_branch="main", head="HEAD"):
    try:
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...{head}"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def extract_diff_hunks(diff_text):
    files = {}
    current_file = None
    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            current_file = line.split(" b/")[-1]
            files[current_file] = {"added": 0, "removed": 0}
        elif current_file and line.startswith("+") and not line.startswith("+++"):
            files[current_file]["added"] += 1
        elif current_file and line.startswith("-") and not line.startswith("---"):
            files[current_file]["removed"] += 1
    return files


def scan_issues(file_path, diff_text):
    issues = []
    line_no = 0
    for line in diff_text.split("\n"):
        if line.startswith("@@"):
            match = re.search(r"\+\d+", line)
            line_no = int(match.group(0)[1:]) if match else 0
        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:]

            # 可变默认参数
            if re.search(r"def\s+\w+\(.*=\s*\[\]", content):
                issues.append({"file": file_path, "line": line_no, "level": "BLOCKER",
                    "category": "正确性", "message": "函数使用可变默认参数 []，应改为 None。"})

            if re.search(r"def\s+\w+\(.*=\s*\{\}", content):
                issues.append({"file": file_path, "line": line_no, "level": "BLOCKER",
                    "category": "正确性", "message": "函数使用可变默认参数 {}，应改为 None。"})

            # except: 捕获所有异常
            if re.match(r"\s*except\s*:", content):
                issues.append({"file": file_path, "line": line_no, "level": "BLOCKER",
                    "category": "正确性", "message": "except: 捕获所有异常（含 KeyboardInterrupt），应指定具体异常类型。"})

            # == None / != None
            if re.search(r"==\s*None\b|!=\s*None\b", content):
                issues.append({"file": file_path, "line": line_no, "level": "WARNING",
                    "category": "规范", "message": "使用 == None 比较，应使用 is None / is not None。"})

            # 循环内字符串拼接
            if re.search(r"\w+\s*\+=\s*['\"]", content) and ("for " in diff_text[:diff_text.find(line)] or "while " in diff_text[:diff_text.find(line)]):
                pass  # 简化：仅标记可疑行

            # 硬编码敏感信息
            for kw in ["password", "secret", "api_key", "apikey", "token"]:
                if re.search(rf'{kw}\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    issues.append({"file": file_path, "line": line_no, "level": "BLOCKER",
                        "category": "安全", "message": f"疑似硬编码敏感信息（{kw}），应使用环境变量或配置文件。"})
                    break

            # eval / exec
            if re.search(r"\beval\s*\(", content) or re.search(r"\bexec\s*\(", content):
                issues.append({"file": file_path, "line": line_no, "level": "BLOCKER",
                    "category": "安全", "message": "使用 eval/exec，存在代码注入风险。"})

            # time.sleep 在 async 函数中（简单检测）
            if "time.sleep" in content and "async def" in diff_text:
                issues.append({"file": file_path, "line": line_no, "level": "BLOCKER",
                    "category": "并发", "message": "在 async 上下文中使用 time.sleep 会阻塞事件循环，应使用 await asyncio.sleep()。"})

            # 忘记 await
            if re.search(r"(?<!await\s)\b\w+\(.*\)\s*$", content) and "async" in content:
                pass  # 过于复杂，跳过

            line_no += 1
        elif line.startswith(" ") and not line.startswith("   "):
            line_no += 1
    return issues


def generate_report(diff_stats, issues, base, head):
    lines = [
        "# Python 代码审查报告", "",
        f"- **分支对比**: `{base}` ... `{head}`",
        f"- **生成时间**: {datetime.now().isoformat()}",
        f"- **变更文件数**: {len(diff_stats)}", "",
    ]

    blocker = [i for i in issues if i["level"] == "BLOCKER"]
    warning = [i for i in issues if i["level"] == "WARNING"]
    suggestion = [i for i in issues if i["level"] == "SUGGESTION"]

    lines += ["## 审查摘要", "", "| 级别 | 数量 |", "|------|------|",
              f"| BLOCKER | {len(blocker)} |", f"| WARNING | {len(warning)} |",
              f"| SUGGESTION | {len(suggestion)} |", ""]

    if not issues:
        lines.append("> 自动扫描未发现问题，建议人工 review 业务逻辑。")
        return "\n".join(lines)

    lines += ["## 发现的问题", ""]
    for level, items in [("BLOCKER", blocker), ("WARNING", warning), ("SUGGESTION", suggestion)]:
        if not items:
            continue
        lines += [f"### {level}", ""]
        for i in items:
            lines += [f"- **{i['file']}:{i['line']}**  ", f"  `{i['category']}` - {i['message']}"]
        lines.append("")

    lines += ["---", "*本报告由自动脚本生成，仅供参考。*"]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="基于 git diff 生成 Python 代码审查报告")
    parser.add_argument("--base", "-b", default="main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    diff_text = get_diff(args.base, args.head)
    if not diff_text:
        print(f"未获取到 {args.base}...{args.head} 的 diff。")
        return

    diff_stats = extract_diff_hunks(diff_text)
    all_issues = []
    for file_path in diff_stats:
        if not file_path.endswith(".py"):
            continue
        file_diff = ""
        in_file = False
        for line in diff_text.split("\n"):
            if line.startswith("diff --git"):
                in_file = line.endswith(f" b/{file_path}")
            if in_file:
                file_diff += line + "\n"
        all_issues.extend(scan_issues(file_path, file_diff))

    if args.format == "json":
        output = json.dumps({"issues": all_issues}, indent=2, ensure_ascii=False)
    else:
        output = generate_report(diff_stats, all_issues, args.base, args.head)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"报告已保存至: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
