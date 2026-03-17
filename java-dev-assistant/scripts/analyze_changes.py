#!/usr/bin/env python3
"""
分析 git diff 以识别受影响的 Java 组件。
输出 JSON 格式的变更文件、类和 method 信息。
"""

import subprocess
import json
import re
import sys
from pathlib import Path


def get_git_diff():
    """获取已暂存变更的 git diff。"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def get_diff_content(file_path):
    """获取指定文件的 diff 内容。"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def extract_java_methods(diff_content):
    """从 Java diff 中提取方法签名。"""
    methods = []
    # 匹配 diff 中的方法声明模式
    method_pattern = r'^[+].*(?:public|private|protected|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)'
    
    for line in diff_content.split('\n'):
        match = re.match(method_pattern, line)
        if match:
            methods.append(match.group(1))
    
    return list(set(methods))


def analyze_changes():
    """主分析函数。"""
    changed_files = get_git_diff()
    
    if not changed_files:
        return {
            "error": "未找到已暂存的变更。请先用 'git add' 暂存您的变更。"
        }
    
    java_files = [f for f in changed_files if f.endswith('.java')]
    
    result = {
        "变更文件总数": len(changed_files),
        "Java文件": [],
        "其他文件": [f for f in changed_files if not f.endswith('.java')],
        "摘要": {
            "修改的类": [],
            "新增的方法": [],
            "修改的方法": []
        }
    }
    
    for file_path in java_files:
        diff_content = get_diff_content(file_path)
        methods = extract_java_methods(diff_content)
        
        class_name = Path(file_path).stem
        
        file_info = {
            "路径": file_path,
            "类名": class_name,
            "受影响的方法": methods
        }
        result["Java文件"].append(file_info)
        result["摘要"]["修改的类"].append(class_name)
        result["摘要"]["修改的方法"].extend(methods)
    
    # 去重
    result["摘要"]["修改的类"] = list(set(result["摘要"]["修改的类"]))
    result["摘要"]["修改的方法"] = list(set(result["摘要"]["修改的方法"]))
    
    return result


if __name__ == "__main__":
    analysis = analyze_changes()
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
