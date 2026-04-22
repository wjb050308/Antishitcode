"""
递归包装器 - 核心重构算法

考古学原理：将破碎文物重组为可识别形态
"""
import ast
from typing import List, Dict, Optional
from pathlib import Path
from .types import WrappedCode, TestCase


class RecursiveWrapper:
    """
    递归包装引擎
    
    将屎山代码递归包装成可测试单元
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.wrapped_functions: List[str] = []
        self.extracted_functions: List[str] = []
        self.dependencies: Dict[str, List[str]] = {}
        self.test_cases: List[TestCase] = []
    
    def _reset(self):
        """重置实例变量"""
        self.wrapped_functions = []
        self.extracted_functions = []
        self.dependencies = {}
        self.test_cases = []
    
    def wrap(
        self,
        code: str,
        module_name: str,
        output_dir: Optional[Path] = None,
        max_depth: int = 10,
    ) -> WrappedCode:
        """
        递归包装代码
        
        Args:
            code: 原始代码
            module_name: 模块名
            output_dir: 输出目录
            max_depth: 最大递归深度
            
        Returns:
            包装后的代码
        """
        self._reset()
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return WrappedCode(
                original_name=module_name,
                wrapped_code=code,
                extracted_functions=[],
                dependencies={},
                test_cases=[],
            )
        
        # 包装每个函数
        wrapped_parts = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                wrapped = self._wrap_function(node, code, max_depth)
                wrapped_parts.append(wrapped)
                self.extracted_functions.append(wrapped)
            
            elif isinstance(node, ast.ClassDef):
                wrapped = self._wrap_class(node, code)
                wrapped_parts.append(wrapped)
        
        # 生成包装后的代码
        wrapped_code = self._assemble_wrapped_code(module_name, wrapped_parts, code)
        
        # 生成测试用例
        self._generate_tests(wrapped_parts)
        
        return WrappedCode(
            original_name=module_name,
            wrapped_code=wrapped_code,
            extracted_functions=self.extracted_functions,
            dependencies=self.dependencies,
            test_cases=self.test_cases,
        )
    
    def _wrap_function(
        self,
        node: ast.FunctionDef,
        original_code: str,
        depth: int,
    ) -> str:
        """
        包装单个函数
        
        Args:
            node: 函数 AST 节点
            original_code: 原始代码
            depth: 当前递归深度
            
        Returns:
            包装后的代码字符串
        """
        func_name = node.name
        
        # 如果深度为0或函数很简单，直接返回原代码
        if depth <= 0 or self._is_simple_function(node):
            return self._extract_function_code(node, original_code)
        
        # 检测需要提取的嵌套逻辑
        needs_extraction = self._needs_extraction(node)
        
        if not needs_extraction:
            return self._extract_function_code(node, original_code)
        
        # 提取嵌套逻辑为独立函数
        extracted = self._extract_nested_logic(node, original_code, depth)
        
        # 包装后的函数
        wrapped = [
            f"def {func_name}_wrapped({', '.join([a.arg for a in node.args.args])}):",
            f'    """包装后的 {func_name}"""',
        ]
        
        # 添加原始函数调用
        wrapped.append(f"    return {func_name}({', '.join([a.arg for a in node.args.args])})")
        
        return "\n".join(wrapped)
    
    def _wrap_class(self, node: ast.ClassDef, original_code: str) -> str:
        """包装类"""
        class_name = node.name
        
        wrapped_parts = [f"class {class_name}_Wrapped:"]
        
        # 为每个方法创建包装
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith("_") or item.name == "__init__":
                    method_wrapped = self._wrap_function(item, original_code, depth=3)
                    wrapped_parts.append(f"\n    # {item.name} method")
                    wrapped_parts.append(method_wrapped)
        
        return "\n".join(wrapped_parts)
    
    def _extract_function_code(self, node: ast.FunctionDef, original_code: str) -> str:
        """提取函数代码"""
        lines = original_code.split("\n")
        start = node.lineno - 1
        end = node.end_lineno
        return "\n".join(lines[start:end])
    
    def _is_simple_function(self, node: ast.FunctionDef) -> bool:
        """判断是否为简单函数"""
        # 简单函数：10行以内，无嵌套，无复杂逻辑
        lines = (node.end_lineno or node.lineno) - node.lineno
        if lines > 20:
            return False
        
        # 检查嵌套深度
        max_depth = self._get_nesting_depth(node)
        if max_depth > 2:
            return False
        
        return True
    
    def _needs_extraction(self, node: ast.FunctionDef) -> bool:
        """判断是否需要提取嵌套逻辑"""
        # 需要提取的情况：
        # 1. 函数过长
        # 2. 嵌套过深
        # 3. 复杂条件
        
        lines = (node.end_lineno or node.lineno) - node.lineno
        if lines > 50:
            return True
        
        max_depth = self._get_nesting_depth(node)
        if max_depth > 3:
            return True
        
        # 计算复杂度
        complexity = self._calculate_complexity(node)
        if complexity > 10:
            return True
        
        return False
    
    def _extract_nested_logic(
        self,
        node: ast.FunctionDef,
        original_code: str,
        depth: int,
    ) -> List[str]:
        """提取嵌套逻辑"""
        extracted = []
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                # 提取条件分支为独立函数
                inner_func = self._create_inner_function(child, depth - 1)
                if inner_func:
                    extracted.append(inner_func)
        
        return extracted
    
    def _create_inner_function(self, node, depth: int) -> Optional[str]:
        """创建内部函数"""
        if depth <= 0:
            return None
        
        # 生成唯一函数名
        func_name = f"_inner_{hash(node) % 100000}"
        
        return f"""
def {func_name}(context):
    # 提取的嵌套逻辑
    # 需要根据具体节点分析
    pass
"""
    
    def _get_nesting_depth(self, node: ast.FunctionDef) -> int:
        """获取最大嵌套深度"""
        max_depth = [0]
        
        def check(node, depth=0):
            max_depth[0] = max(max_depth[0], depth)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                    check(child, depth + 1)
        
        check(node)
        return max_depth[0]
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _assemble_wrapped_code(
        self,
        module_name: str,
        parts: List[str],
        original_code: str,
    ) -> str:
        """组装包装后的代码"""
        lines = [
            f'"""',
            f"""Wrapped module: {module_name}_wrapped""",
            f'"""',
            "",
            "# ====== 导入区 ======",
            "import pytest",
            "",
            "# ====== 原始代码 ======",
            original_code,
            "",
            "# ====== 包装后的代码 ======",
        ]
        
        lines.extend(parts)
        
        lines.extend([
            "",
            "# ====== 包装完成 ======",
        ])
        
        return "\n".join(lines)
    
    def _generate_tests(self, wrapped_parts: List[str]) -> None:
        """生成测试用例"""
        for part in wrapped_parts[:5]:  # 限制数量
            if "def " in part:
                try:
                    test = self.llm.generate_test_cases(part, num_cases=3)
                    # 解析测试并创建 TestCase 对象
                    # (简化处理)
                    self.test_cases.append(TestCase(
                        function_name="inferred",
                        inputs={},
                        expected_output=None,
                        description=test[:100],
                    ))
                except Exception:
                    continue
