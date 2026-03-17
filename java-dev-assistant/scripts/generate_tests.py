#!/usr/bin/env python3
"""
Generate test cases based on code changes.
Analyzes modified Java files and suggests test scenarios.
"""

import subprocess
import json
import re
import argparse
from pathlib import Path


def get_changed_java_files():
    """Get list of changed Java files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return [f for f in files if f.endswith('.java') and not f.endswith('Test.java')]
    except subprocess.CalledProcessError:
        return []


def parse_java_file(file_path):
    """Parse Java file to extract class and method information."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return None
    
    # Extract package
    package_match = re.search(r'package\s+([\w.]+);', content)
    package = package_match.group(1) if package_match else ""
    
    # Extract class name
    class_match = re.search(r'(?:public\s+)?(?:class|interface|enum)\s+(\w+)', content)
    class_name = class_match.group(1) if class_match else Path(file_path).stem
    
    # Extract public methods
    method_pattern = r'(?:public\s+)(?:static\s+)?(?:\w+[\w\<\>\[\]]*\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
    methods = re.findall(method_pattern, content)
    
    # Filter out common non-testable methods
    skip_methods = {'main', 'toString', 'equals', 'hashCode', 'compareTo'}
    methods = [m for m in methods if m not in skip_methods]
    
    return {
        "package": package,
        "class_name": class_name,
        "methods": methods,
        "file_path": file_path
    }


def generate_test_cases(class_info):
    """Generate test case suggestions for a class."""
    test_cases = []
    
    for method in class_info["methods"]:
        test_case = {
            "method": method,
            "scenarios": [
                {
                    "name": f"{method}_normalCase",
                    "description": f"Test {method} with valid input",
                    "type": "positive"
                },
                {
                    "name": f"{method}_nullInput",
                    "description": f"Test {method} with null input",
                    "type": "edge"
                },
                {
                    "name": f"{method}_emptyInput",
                    "description": f"Test {method} with empty input",
                    "type": "edge"
                }
            ]
        }
        
        # Add boundary test for numeric methods
        if any(kw in method.lower() for kw in ['count', 'size', 'length', 'index', 'limit']):
            test_case["scenarios"].append({
                "name": f"{method}_boundaryValue",
                "description": f"Test {method} with boundary values (MAX/MIN)",
                "type": "boundary"
            })
        
        # Add exception test for methods that might throw
        if any(kw in method.lower() for kw in ['parse', 'validate', 'convert', 'process']):
            test_case["scenarios"].append({
                "name": f"{method}_invalidInput",
                "description": f"Test {method} with invalid input - expects exception",
                "type": "exception"
            })
        
        test_cases.append(test_case)
    
    return test_cases


def generate_test_class(class_info, test_cases):
    """Generate test class code."""
    package = class_info["package"]
    class_name = class_info["class_name"]
    
    lines = []
    
    # Package declaration
    if package:
        lines.append(f"package {package};")
        lines.append("")
    
    # Imports
    lines.extend([
        "import org.junit.jupiter.api.Test;",
        "import org.junit.jupiter.api.BeforeEach;",
        "import org.junit.jupiter.api.DisplayName;",
        "import static org.junit.jupiter.api.Assertions.*;",
        "import static org.mockito.Mockito.*;",
        "",
    ])
    
    # Class declaration
    lines.extend([
        f"class {class_name}Test {{",
        "",
        f"    private {class_name} target;",
        "",
        "    @BeforeEach",
        "    void setUp() {",
        f"        target = new {class_name}();",
        "    }",
        ""
    ])
    
    # Test methods
    for test_case in test_cases:
        method = test_case["method"]
        for scenario in test_case["scenarios"]:
            lines.extend([
                f"    @Test",
                f"    @DisplayName(\"{scenario['description']}\")",
                f"    void {scenario['name']}() {{",
                "        // Arrange",
                "        // TODO: Set up test data",
                "",
                "        // Act",
                f"        // TODO: Call target.{method}()",
                "",
                "        // Assert",
                "        // TODO: Verify results",
                "    }",
                ""
            ])
    
    lines.append("}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate test cases from code changes')
    parser.add_argument('--output-dir', '-o', default='src/test/java',
                       help='Output directory for test files')
    parser.add_argument('--format', '-f', choices=['json', 'code'], default='json',
                       help='Output format')
    
    args = parser.parse_args()
    
    changed_files = get_changed_java_files()
    
    if not changed_files:
        print("No changed Java files found (excluding test files).")
        return
    
    results = []
    
    for file_path in changed_files:
        class_info = parse_java_file(file_path)
        if not class_info:
            continue
        
        test_cases = generate_test_cases(class_info)
        
        result = {
            "source_file": file_path,
            "class_info": class_info,
            "test_cases": test_cases
        }
        
        if args.format == 'code':
            test_code = generate_test_class(class_info, test_cases)
            result["generated_test_code"] = test_code
            
            # Write to file
            test_file_name = f"{class_info['class_name']}Test.java"
            if class_info["package"]:
                package_path = class_info["package"].replace('.', '/')
                output_path = Path(args.output_dir) / package_path / test_file_name
            else:
                output_path = Path(args.output_dir) / test_file_name
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(test_code)
            
            result["output_file"] = str(output_path)
        
        results.append(result)
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
