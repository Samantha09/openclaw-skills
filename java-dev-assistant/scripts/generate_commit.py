#!/usr/bin/env python3
"""
Generate conventional commit message based on changes.
Follows Conventional Commits specification.
"""

import subprocess
import json
import sys
import argparse


def get_changed_files():
    """Get list of changed files."""
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
    """Get diff statistics."""
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
    """Detect scope from changed files."""
    scopes = set()
    for f in files:
        if '/' in f:
            # Extract module/package name
            parts = f.split('/')
            if len(parts) > 1:
                scopes.add(parts[0])
    
    return list(scopes)[0] if scopes else None


def generate_commit_message(commit_type, description, scope=None, body=None, footer=None):
    """Generate conventional commit message."""
    
    # Header
    if scope:
        header = f"{commit_type}({scope}): {description}"
    else:
        header = f"{commit_type}: {description}"
    
    # Build message
    message = header
    
    if body:
        message += f"\n\n{body}"
    
    if footer:
        message += f"\n\n{footer}"
    
    return message


def main():
    parser = argparse.ArgumentParser(description='Generate conventional commit message')
    parser.add_argument('--type', '-t', required=True, 
                       choices=['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore'],
                       help='Commit type')
    parser.add_argument('--description', '-d', required=True,
                       help='Short description')
    parser.add_argument('--scope', '-s', help='Scope (auto-detected if not provided)')
    parser.add_argument('--body', '-b', help='Commit body')
    parser.add_argument('--breaking', action='store_true', help='Mark as breaking change')
    parser.add_argument('--issues', help='Related issues (comma-separated)')
    
    args = parser.parse_args()
    
    # Get changed files
    changed_files = get_changed_files()
    
    if not changed_files:
        print("Error: No staged changes found. Stage your changes with 'git add' first.", file=sys.stderr)
        sys.exit(1)
    
    # Auto-detect scope if not provided
    scope = args.scope
    if not scope:
        scope = detect_scope(changed_files)
    
    # Build body
    body = args.body
    if not body:
        diff_stat = get_diff_stat()
        if diff_stat:
            body = "Changes:\n" + diff_stat
    
    # Build footer
    footer_parts = []
    if args.breaking:
        footer_parts.append("BREAKING CHANGE: This commit introduces breaking changes")
    if args.issues:
        issues_list = [i.strip() for i in args.issues.split(',')]
        footer_parts.extend([f"Closes #{i}" for i in issues_list])
    
    footer = "\n".join(footer_parts) if footer_parts else None
    
    # Generate commit message
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
