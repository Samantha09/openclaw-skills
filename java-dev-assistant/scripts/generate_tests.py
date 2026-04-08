#!/usr/bin/env python3
"""
基于代码变更生成测试用例。
分析修改的 Java 文件并建议测试场景。
"""

import subprocess
import json
import re
import argparse
from pathlib import Path


def get_changed_java_files():
    """获取变更的 Java 文件列表。"""
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
    """解析 Java 文件，提取类和方法信息。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None
    
    # 提取包名
    package_match = re.search(r'package\s+([\w.]+);', content)
    package = package_match.group(1) if package_match else ""
    
    # 提取类名
    class_match = re.search(r'(?:public\s+)?(?:class|interface|enum)\s+(\w+)', content)
    class_name = class_match.group(1) if class_match else Path(file_path).stem
    
    # 提取公共方法
    method_pattern = r'(?:public\s+)(?:static\s+)?(?:\w+[\w\<\>\[\]]*\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
    methods = re.findall(method_pattern, content)
    
    # 过滤掉常见的不可测试方法
    skip_methods = {'main', 'toString', 'equals', 'hashCode', 'compareTo'}
    methods = [m for m in methods if m not in skip_methods]
    
    return {
        "包名": package,
        "类名": class_name,
        "方法": methods,
        "文件路径": file_path
    }


def generate_test_cases(class_info):
    """为类生成测试用例建议。"""
    test_cases = []
    
    for method in class_info["方法"]:
        test_case = {
            "方法": method,
            "场景": [
                {
                    "名称": f"{method}_正常情况",
                    "描述": f"测试 {method} 的有效输入",
                    "类型": "正向"
                },
                {
                    "名称": f"{method}_空输入",
                    "描述": f"测试 {method} 的空输入",
                    "类型": "边界"
                },
                {
                    "名称": f"{method}_空值输入",
                    "描述": f"测试 {method} 的 null 输入",
                    "类型": "边界"
                }
            ]
        }
        
        # 为数值方法添加边界测试
        if any(kw in method.lower() for kw in ['count', 'size', 'length', 'index', 'limit']):
            test_case["场景"].append({
                "名称": f"{method}_边界值",
                "描述": f"测试 {method} 的边界值（最大/最小）",
                "类型": "边界"
            })
        
        # 为可能抛出异常的方法添加异常测试
        if any(kw in method.lower() for kw in ['parse', 'validate', 'convert', 'process']):
            test_case["场景"].append({
                "名称": f"{method}_无效输入",
                "描述": f"测试 {method} 的无效输入 - 预期抛出异常",
                "类型": "异常"
            })
        
        test_cases.append(test_case)
    
    return test_cases


def generate_test_class(class_info, test_cases):
    """生成测试类代码。"""
    package = class_info["包名"]
    class_name = class_info["类名"]
    
    lines = []
    
    # 包声明
    if package:
        lines.append(f"package {package};")
        lines.append("")
    
    # 导入
    lines.extend([
        "import org.junit.jupiter.api.Test;",
        "import org.junit.jupiter.api.BeforeEach;",
        "import org.junit.jupiter.api.DisplayName;",
        "import static org.junit.jupiter.api.Assertions.*;",
        "import static org.mockito.Mockito.*;",
        "",
    ])
    
    # 类声明
    lines.extend([
        f"public class {class_name}Test {{",
        "",
        f"    private {class_name} target;",
        "",
        "    @BeforeEach",
        "    void setUp() {",
        f"        target = new {class_name}();",
        "    }",
        ""
    ])
    
    # 测试方法
    for test_case in test_cases:
        method = test_case["方法"]
        for scenario in test_case["场景"]:
            lines.extend([
                f"    @Test",
                f"    @DisplayName(\"{scenario['描述']}\")",
                f"    void {scenario['名称']}() {{",
                "        // 准备",
                "        // TODO: 设置测试数据",
                "",
                "        // 执行",
                f"        // TODO: 调用 target.{method}()",
                "",
                "        // 验证",
                "        // TODO: 验证结果",
                "    }",
                ""
            ])
    
    lines.append("}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='从代码变更生成测试用例')
    parser.add_argument('--output-dir', '-o', default='src/test/java',
                       help='测试文件输出目录')
    parser.add_argument('--format', '-f', choices=['json', 'code'], default='json',
                       help='输出格式')
    
    args = parser.parse_args()
    
    changed_files = get_changed_java_files()
    
    if not changed_files:
        print("未找到变更的 Java 文件（排除测试文件）。")
        return
    
    results = []
    
    for file_path in changed_files:
        class_info = parse_java_file(file_path)
        if not class_info:
            continue
        
        test_cases = generate_test_cases(class_info)
        
        result = {
            "源文件": file_path,
            "类信息": class_info,
            "测试用例": test_cases
        }
        
        if args.format == 'code':
            test_code = generate_test_class(class_info, test_cases)
            result["生成的测试代码"] = test_code
            
            # 写入文件
            test_file_name = f"{class_info['类名']}Test.java"
            if class_info["包名"]:
                package_path = class_info["包名"].replace('.', '/')
                output_path = Path(args.output_dir) / package_path / test_file_name
            else:
                output_path = Path(args.output_dir) / test_file_name
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            result["输出文件"] = str(output_path)
        
        results.append(result)
    
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
