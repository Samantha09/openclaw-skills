#!/usr/bin/env python3
"""
Analyze git diff to identify affected Java components.
Outputs JSON with changed files, classes, and methods.
"""

import subprocess
import json
import re
import sys
from pathlib import Path


def get_git_diff():
    """Get the git diff of staged changes."""
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
    """Get diff content for a specific file."""
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
    """Extract method signatures from Java diff."""
    methods = []
    # Pattern to match method declarations in diff
    method_pattern = r'^[+].*(?:public|private|protected|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)'
    
    for line in diff_content.split('\n'):
        match = re.match(method_pattern, line)
        if match:
            methods.append(match.group(1))
    
    return list(set(methods))


def analyze_changes():
    """Main analysis function."""
    changed_files = get_git_diff()
    
    if not changed_files:
        return {
            "error": "No staged changes found. Stage your changes with 'git add' first."
        }
    
    java_files = [f for f in changed_files if f.endswith('.java')]
    
    result = {
        "total_files": len(changed_files),
        "java_files": [],
        "other_files": [f for f in changed_files if not f.endswith('.java')],
        "summary": {
            "classes_modified": [],
            "methods_added": [],
            "methods_modified": []
        }
    }
    
    for file_path in java_files:
        diff_content = get_diff_content(file_path)
        methods = extract_java_methods(diff_content)
        
        class_name = Path(file_path).stem
        
        file_info = {
            "path": file_path,
            "class_name": class_name,
            "methods_affected": methods
        }
        result["java_files"].append(file_info)
        result["summary"]["classes_modified"].append(class_name)
        result["summary"]["methods_modified"].extend(methods)
    
    # Remove duplicates
    result["summary"]["classes_modified"] = list(set(result["summary"]["classes_modified"]))
    result["summary"]["methods_modified"] = list(set(result["summary"]["methods_modified"]))
    
    return result


if __name__ == "__main__":
    analysis = analyze_changes()
    print(json.dumps(analysis, indent=2))
