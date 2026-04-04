#!/usr/bin/env python3
"""
基于 git diff 生成结构化代码审查报告。
输出 Markdown / JSON 格式的审查建议。
"""

import subprocess
import json
import argparse
import re
from pathlib import Path
from datetime import datetime


def get_diff(base_branch="main", head="HEAD"):
    """获取指定范围的 git diff。"""
    try:
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...{head}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def get_changed_files(base_branch="main", head="HEAD"):
    """获取变更文件列表。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}...{head}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def extract_diff_hunks(diff_text):
    """按文件提取 diff hunk 信息。"""
    files = {}
    current_file = None
    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            current_file = line.split(" b/")[-1]
            files[current_file] = {"added_lines": 0, "removed_lines": 0, "hunks": []}
        elif current_file and line.startswith("+") and not line.startswith("+++"):
            files[current_file]["added_lines"] += 1
        elif current_file and line.startswith("-") and not line.startswith("---"):
            files[current_file]["removed_lines"] += 1
    return files


def scan_common_issues(file_path, diff_text):
    """基于 diff 文本扫描常见简单问题。"""
    issues = []
    lines = diff_text.split("\n")
    line_no = 0

    for line in lines:
        if line.startswith("@@"):
            # 提取新增行起始行号
            match = re.search(r"\+\d+", line)
            line_no = int(match.group(0)[1:]) if match else 0
        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:]

            # 魔法值检查（简单规则）
            if re.search(r"=\s*[\"'][^\"']+[\"'];", content) and not content.strip().startswith("//"):
                if any(kw in content for kw in ["error", "msg", "message", "desc", "name", "key"]):
                    issues.append(
                        {
                            "file": file_path,
                            "line": line_no,
                            "level": "SUGGESTION",
                            "category": "规范",
                            "message": "存在疑似魔法值字符串，建议提取为常量或配置。",
                        }
                    )

            # System.out.print 检查
            if "System.out.print" in content:
                issues.append(
                    {
                        "file": file_path,
                        "line": line_no,
                        "level": "WARNING",
                        "category": "规范",
                        "message": "使用 System.out.print 输出日志，建议改用 SLF4J。",
                    }
                )

            # 捕获 Exception/Throwable
            if re.search(r"catch\s*\(\s*(Exception|Throwable)", content):
                issues.append(
                    {
                        "file": file_path,
                        "line": line_no,
                        "level": "WARNING",
                        "category": "正确性",
                        "message": "捕获过于宽泛的异常（Exception/Throwable），建议捕获具体异常类型。",
                    }
                )

            line_no += 1
        elif line.startswith(" ") and not line.startswith("   "):
            line_no += 1

    return issues


def generate_markdown_report(diff_stats, issues, base_branch, head):
    """生成 Markdown 审查报告。"""
    lines = []
    lines.append(f"# 代码审查报告")
    lines.append(f"")
    lines.append(f"- **分支对比**: `{base_branch}` ... `{head}`")
    lines.append(f"- **生成时间**: {datetime.now().isoformat()}")
    lines.append(f"- **变更文件数**: {len(diff_stats)}")
    lines.append(f"")

    # 统计
    blocker = [i for i in issues if i["level"] == "BLOCKER"]
    warning = [i for i in issues if i["level"] == "WARNING"]
    suggestion = [i for i in issues if i["level"] == "SUGGESTION"]

    lines.append(f"## 审查摘要")
    lines.append(f"")
    lines.append(f"| 级别 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 阻塞 (BLOCKER) | {len(blocker)} |")
    lines.append(f"| 警告 (WARNING) | {len(warning)} |")
    lines.append(f"| 建议 (SUGGESTION) | {len(suggestion)} |")
    lines.append(f"")

    if not issues:
        lines.append("> ✅ 自动扫描未发现问题，建议人工 review 业务逻辑和测试覆盖。")
        return "\n".join(lines)

    lines.append(f"## 发现的问题")
    lines.append(f"")

    for level, items in [("BLOCKER", blocker), ("WARNING", warning), ("SUGGESTION", suggestion)]:
        if not items:
            continue
        lines.append(f"### {level}")
        lines.append(f"")
        for issue in items:
            lines.append(f"- **{issue['file']}:{issue['line']}**  ")
            lines.append(f"  `{issue['category']}` - {issue['message']}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"*本报告由自动脚本生成，仅供参考，最终审查结论需结合人工判断。*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="基于 git diff 生成代码审查报告")
    parser.add_argument("--base", "-b", default="main", help="基准分支")
    parser.add_argument("--head", default="HEAD", help="目标分支或提交")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    diff_text = get_diff(args.base, args.head)
    if not diff_text:
        print(f"未获取到 {args.base}...{args.head} 的 diff，请确认分支存在且有变更。")
        return

    diff_stats = extract_diff_hunks(diff_text)
    all_issues = []

    # 按文件扫描
    for file_path in diff_stats:
        if not file_path.endswith(".java"):
            continue
        file_diff = ""
        in_file = False
        for line in diff_text.split("\n"):
            if line.startswith("diff --git"):
                in_file = line.endswith(f" b/{file_path}")
            if in_file:
                file_diff += line + "\n"
        issues = scan_common_issues(file_path, file_diff)
        all_issues.extend(issues)

    if args.format == "json":
        report = {
            "meta": {
                "base": args.base,
                "head": args.head,
                "generated_at": datetime.now().isoformat(),
            },
            "summary": {
                "changed_files": len(diff_stats),
                "blocker": len([i for i in all_issues if i["level"] == "BLOCKER"]),
                "warning": len([i for i in all_issues if i["level"] == "WARNING"]),
                "suggestion": len([i for i in all_issues if i["level"] == "SUGGESTION"]),
            },
            "issues": all_issues,
        }
        output = json.dumps(report, indent=2, ensure_ascii=False)
    else:
        output = generate_markdown_report(diff_stats, all_issues, args.base, args.head)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"报告已保存至: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
