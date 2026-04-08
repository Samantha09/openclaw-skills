#!/usr/bin/env python3
"""
分析 git diff 以识别受影响的 Python 模块。
支持暂存区变更和分支对比。
"""

import subprocess
import json
import re
import argparse
from pathlib import Path


def get_changed_files(mode="cached", base=None):
    """获取变更文件列表。"""
    try:
        if mode == "branch" and base:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base}...HEAD"],
                capture_output=True, text=True, check=True,
            )
        else:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True,
            )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def get_diff_content(file_path, mode="cached", base=None):
    """获取指定文件的 diff 内容。"""
    try:
        if mode == "branch" and base:
            result = subprocess.run(
                ["git", "diff", f"{base}...HEAD", file_path],
                capture_output=True, text=True, check=True,
            )
        else:
            result = subprocess.run(
                ["git", "diff", "--cached", file_path],
                capture_output=True, text=True, check=True,
            )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def extract_python_symbols(diff_content):
    """从 Python diff 中提取函数和类定义。"""
    symbols = []
    # 匹配 def/class 定义
    patterns = [
        (r"^[+]\s*(?:async\s+)?def\s+(\w+)", "function"),
        (r"^[+]\s*class\s+(\w+)", "class"),
    ]
    for line in diff_content.split("\n"):
        for pattern, kind in patterns:
            match = re.match(pattern, line)
            if match:
                symbols.append({"name": match.group(1), "kind": kind})
    return symbols


def analyze_changes(base=None):
    """主分析函数。"""
    mode = "branch" if base else "cached"
    changed_files = get_changed_files(mode=mode, base=base)

    if not changed_files:
        label = f"{base}...HEAD" if base else "暂存区"
        return {"error": f"未找到{label}的变更。"}

    py_files = [f for f in changed_files if f.endswith(".py")]

    result = {
        "变更文件总数": len(changed_files),
        "Python文件": [],
        "其他文件": [f for f in changed_files if not f.endswith(".py")],
        "摘要": {
            "修改的模块": [],
            "新增的函数": [],
            "新增的类": [],
        },
    }

    for file_path in py_files:
        diff_content = get_diff_content(file_path, mode=mode, base=base)
        symbols = extract_python_symbols(diff_content)
        module_name = Path(file_path).stem

        file_info = {
            "路径": file_path,
            "模块": module_name,
            "符号": symbols,
        }
        result["Python文件"].append(file_info)
        result["摘要"]["修改的模块"].append(module_name)
        for sym in symbols:
            if sym["kind"] == "function":
                result["摘要"]["新增的函数"].append(f"{module_name}.{sym['name']}")
            elif sym["kind"] == "class":
                result["摘要"]["新增的类"].append(f"{module_name}.{sym['name']}")

    # 去重
    result["摘要"]["修改的模块"] = sorted(set(result["摘要"]["修改的模块"]))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分析 git diff 中受影响的 Python 模块")
    parser.add_argument("--base", "-b", help="基准分支名（如 main），不指定则分析暂存区")
    args = parser.parse_args()

    print(json.dumps(analyze_changes(base=args.base), indent=2, ensure_ascii=False))
