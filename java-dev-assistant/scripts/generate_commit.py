#!/usr/bin/env python3
"""
基于变更生成规范提交信息。
遵循 Conventional Commits 规范。
"""

import subprocess
import json
import sys
import argparse


def get_changed_files():
    """获取变更文件列表。"""
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


def get_diff_stat():
    """获取 diff 统计信息。"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--stat'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def detect_scope(files):
    """从变更文件中检测范围。"""
    scopes = set()
    for f in files:
        if '/' in f:
            # 提取模块/包名
            parts = f.split('/')
            if len(parts) > 1:
                scopes.add(parts[0])
    
    return list(scopes)[0] if scopes else None


def generate_commit_message(commit_type, description, scope=None, body=None, footer=None):
    """生成规范提交信息。"""
    
    # 标题
    if scope:
        header = f"{commit_type}({scope}): {description}"
    else:
        header = f"{commit_type}: {description}"
    
    # 构建消息
    message = header
    
    if body:
        message += f"\n\n{body}"
    
    if footer:
        message += f"\n\n{footer}"
    
    return message


def main():
    parser = argparse.ArgumentParser(description='生成规范提交信息')
    parser.add_argument('--type', '-t', required=True, 
                       choices=['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore'],
                       help='提交类型')
    parser.add_argument('--description', '-d', required=True,
                       help='简短描述')
    parser.add_argument('--scope', '-s', help='范围（如未提供则自动检测）')
    parser.add_argument('--body', '-b', help='提交正文')
    parser.add_argument('--breaking', action='store_true', help='标记为破坏性变更')
    parser.add_argument('--issues', help='相关问题（逗号分隔）')
    
    args = parser.parse_args()
    
    # 获取变更文件
    changed_files = get_changed_files()
    
    if not changed_files:
        print("错误：未找到已暂存的变更。请先用 'git add' 暂存您的变更。", file=sys.stderr)
        sys.exit(1)
    
    # 如未提供则自动检测范围
    scope = args.scope
    if not scope:
        scope = detect_scope(changed_files)
    
    # 构建正文
    body = args.body
    if not body:
        diff_stat = get_diff_stat()
        if diff_stat:
            body = "变更：\n" + diff_stat
    
    # 构建页脚
    footer_parts = []
    if args.breaking:
        footer_parts.append("BREAKING CHANGE: 此提交包含破坏性变更")
    if args.issues:
        issues_list = [i.strip() for i in args.issues.split(',')]
        footer_parts.extend([f"修复 #{i}" for i in issues_list])
    
    footer = "\n".join(footer_parts) if footer_parts else None
    
    # 生成提交信息
    commit_msg = generate_commit_message(
        args.type,
        args.description,
        scope,
        body,
        footer
    )
    
    print(commit_msg)


if __name__ == "__main__":
    main()
