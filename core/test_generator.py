"""
增强的测试用例生成器

包含：
- 边界值分析
- 等价类划分
- 参数类型推断
- 约束生成
"""
import ast
import re
from typing import List, Dict, Tuple, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class TestCategory(Enum):
    """测试类别"""
    NORMAL = "normal"           # 正常输入
    BOUNDARY = "boundary"        # 边界值
    EQUIVALENCE = "equivalence" # 等价类
    EDGE_CASE = "edge_case"     # 极端情况
    ERROR = "error"             # 错误处理


@dataclass
class ParameterInfo:
    """参数信息"""
    name: str
    inferred_type: str
    default_value: Any
    constraints: List[str]
    possible_values: List[Any]
    is_optional: bool


@dataclass
class EnhancedTestCase:
    """增强的测试用例"""
    function_name: str
    inputs: Dict[str, Any]
    expected_output: Any
    category: TestCategory
    description: str
    edge_case_reason: str      # 为什么这是边界情况
    coverage_rationale: str    # 这个用例覆盖了什么


class EnhancedTestGenerator:
    """
    增强的测试用例生成器
    
    基于代码分析生成高质量测试用例
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def analyze_parameters(self, code: str) -> List[ParameterInfo]:
        """
        分析函数参数
        
        Args:
            code: 函数代码
            
        Returns:
            参数信息列表
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        params = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in node.args.args:
                    param = ParameterInfo(
                        name=arg.arg,
                        inferred_type=self._infer_type(arg),
                        default_value=None,
                        constraints=[],
                        possible_values=[],
                        is_optional=arg.arg in [a.arg for a in node.args.defaults] if node.args.defaults else False,
                    )
                    
                    # 从函数体推断约束
                    constraints = self._infer_constraints(node, arg.arg)
                    param.constraints = constraints
                    
                    params.append(param)
        
        return params
    
    def _infer_type(self, arg: ast.arg) -> str:
        """推断参数类型"""
        # 简化实现：基于变量名推断
        name = arg.arg.lower()
        
        type_hints = {
            "str": ["str", "string", "name", "text", "msg", "content"],
            "int": ["num", "count", "id", "index", "size", "len", "age", "x", "y", "z"],
            "float": ["rate", "price", "salary", "percent", "ratio"],
            "bool": ["is_", "has_", "can_", "should_", "flag", "enabled", "flag"],
            "list": ["list", "arr", "array", "items", "values", "data"],
            "dict": ["dict", "map", "obj", "object", "config"],
        }
        
        for ptype, keywords in type_hints.items():
            if any(kw in name for kw in keywords):
                return ptype
        
        return "Any"
    
    def _infer_constraints(self, func_node: ast.FunctionDef, param_name: str) -> List[str]:
        """推断参数约束"""
        constraints = []
        
        for node in ast.walk(func_node):
            # 比较操作
            if isinstance(node, ast.Compare):
                # 检测 >, <, >=, <=, ==, !=
                for op in node.ops:
                    if isinstance(op, (ast.Gt, ast.Lt, ast.GtE, ast.LtE)):
                        constraints.append(f"需要比较操作")
                    elif isinstance(op, (ast.Eq, ast.NotEq)):
                        constraints.append(f"需要相等判断")
            
            # 检测除法
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                constraints.append("可能被除数")
            
            # 检测索引操作
            if isinstance(node, ast.Subscript):
                constraints.append("可能被索引")
        
        return list(set(constraints))
    
    def generate_boundary_cases(self, param: ParameterInfo) -> List[Dict[str, Any]]:
        """
        生成边界值测试用例
        
        Args:
            param: 参数信息
            
        Returns:
            边界值测试用例
        """
        cases = []
        ptype = param.inferred_type
        
        if ptype == "int":
            cases = [
                {"name": param.name, "value": 0, "reason": "最小整数"},
                {"name": param.name, "value": 1, "reason": "最小正整数"},
                {"name": param.name, "value": -1, "reason": "负数边界"},
                {"name": param.name, "value": 127, "reason": "单字节边界"},
                {"name": param.name, "value": 128, "reason": "单字节溢出"},
                {"name": param.name, "value": 255, "reason": "字节边界"},
                {"name": param.name, "value": 32767, "reason": "16位正数边界"},
                {"name": param.name, "value": -32768, "reason": "16位负数边界"},
            ]
        elif ptype == "float":
            cases = [
                {"name": param.name, "value": 0.0, "reason": "零"},
                {"name": param.name, "value": -0.0, "reason": "负零"},
                {"name": param.name, "value": float('inf'), "reason": "正无穷"},
                {"name": param.name, "value": float('-inf'), "reason": "负无穷"},
                {"name": param.name, "value": float('nan'), "reason": "非数"},
            ]
        elif ptype == "str":
            cases = [
                {"name": param.name, "value": "", "reason": "空字符串"},
                {"name": param.name, "value": " ", "reason": "空格"},
                {"name": param.name, "value": "\\n", "reason": "换行符"},
                {"name": param.name, "value": "\\t", "reason": "制表符"},
                {"name": param.name, "value": "a", "reason": "单字符"},
                {"name": param.name, "value": "a" * 255, "reason": "长字符串"},
                {"name": param.name, "value": "a" * 1000, "reason": "超长字符串"},
            ]
        elif ptype == "list":
            cases = [
                {"name": param.name, "value": [], "reason": "空列表"},
                {"name": param.name, "value": [None], "reason": "单元素列表"},
                {"name": param.name, "value": [1, 2, 3], "reason": "正常列表"},
            ]
        
        return cases
    
    def generate_equivalence_classes(self, param: ParameterInfo) -> List[Dict[str, Any]]:
        """
        生成等价类测试用例
        
        Args:
            param: 参数信息
            
        Returns:
            等价类测试用例
        """
        classes = []
        ptype = param.inferred_type
        
        if ptype == "int":
            classes = [
                {"name": param.name, "value": 0, "class": "零"},
                {"name": param.name, "value": 1, "class": "正小整数"},
                {"name": param.name, "value": 100, "class": "正大整数"},
                {"name": param.name, "value": -1, "class": "负整数"},
                {"name": param.name, "value": -100, "class": "负大整数"},
            ]
        elif ptype == "str":
            classes = [
                {"name": param.name, "value": "", "class": "空字符串"},
                {"name": param.name, "value": "abc", "class": "正常字符串"},
                {"name": param.name, "value": "123", "class": "数字字符串"},
                {"name": param.name, "value": "ABC", "class": "大写字符串"},
                {"name": param.name, "value": "abc123", "class": "混合字符串"},
            ]
        elif ptype == "list":
            classes = [
                {"name": param.name, "value": [], "class": "空列表"},
                {"name": param.name, "value": [1], "class": "单元素"},
                {"name": param.name, "value": [1, 2, 3], "class": "少量元素"},
                {"name": param.name, "value": list(range(100)), "class": "大量元素"},
            ]
        
        return classes
    
    def generate_all_tests(
        self,
        code: str,
        num_boundary: int = 5,
        num_equivalence: int = 4,
    ) -> List[EnhancedTestCase]:
        """
        生成完整测试用例集
        
        Args:
            code: 函数代码
            num_boundary: 边界值用例数量
            num_equivalence: 等价类用例数量
            
        Returns:
            测试用例列表
        """
        test_cases = []
        
        # 分析参数
        params = self.analyze_parameters(code)
        if not params:
            return test_cases
        
        func_name = self._extract_function_name(code)
        
        # 为每个参数生成测试用例
        for param in params:
            # 边界值
            boundary_cases = self.generate_boundary_cases(param)
            for case in boundary_cases[:num_boundary]:
                test_cases.append(EnhancedTestCase(
                    function_name=func_name,
                    inputs={param.name: case["value"]},
                    expected_output=None,  # 需要实际运行
                    category=TestCategory.BOUNDARY,
                    description=f"边界值: {case['reason']}",
                    edge_case_reason=case["reason"],
                    coverage_rationale=f"覆盖 {param.name} 的{case['reason']}",
                ))
            
            # 等价类
            equiv_cases = self.generate_equivalence_classes(param)
            for case in equiv_cases[:num_equivalence]:
                test_cases.append(EnhancedTestCase(
                    function_name=func_name,
                    inputs={param.name: case["value"]},
                    expected_output=None,
                    category=TestCategory.EQUIVALENCE,
                    description=f"等价类: {case['class']}",
                    edge_case_reason=case["class"],
                    coverage_rationale=f"覆盖 {param.name} 的等价类 {case['class']}",
                ))
        
        # 生成正常用例
        normal_inputs = {}
        for param in params:
            if param.inferred_type == "int":
                normal_inputs[param.name] = 10
            elif param.inferred_type == "str":
                normal_inputs[param.name] = "test"
            elif param.inferred_type == "float":
                normal_inputs[param.name] = 1.5
            elif param.inferred_type == "list":
                normal_inputs[param.name] = [1, 2, 3]
            elif param.inferred_type == "bool":
                normal_inputs[param.name] = True
            else:
                normal_inputs[param.name] = None
        
        test_cases.append(EnhancedTestCase(
            function_name=func_name,
            inputs=normal_inputs,
            expected_output=None,
            category=TestCategory.NORMAL,
            description="正常输入",
            edge_case_reason="",
            coverage_rationale="验证函数基本功能",
        ))
        
        # 极端情况
        test_cases.append(EnhancedTestCase(
            function_name=func_name,
            inputs={param.name: None for param in params},
            expected_output=None,
            category=TestCategory.EDGE_CASE,
            description="所有参数为 None",
            edge_case_reason="None 处理",
            coverage_rationale="验证 None 输入的处理",
        ))
        
        return test_cases
    
    def _extract_function_name(self, code: str) -> str:
        """提取函数名"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return node.name
        except:
            pass
        return "unknown"
    
    def generate_pytest_code(self, test_cases: List[EnhancedTestCase]) -> str:
        """
        生成 pytest 测试代码
        
        Args:
            test_cases: 测试用例列表
            
        Returns:
            pytest 代码字符串
        """
        if not test_cases:
            return "# No test cases generated"
        
        func_name = test_cases[0].function_name
        lines = [
            '"""',
            f"测试模块: {func_name}",
            '"""',
            "import pytest",
            "import sys",
            "sys.path.insert(0, '.')",
            "",
            f"# 导入待测试的模块",
            "# from your_module import your_function",
            "",
        ]
        
        # 按类别分组
        by_category = {}
        for tc in test_cases:
            cat = tc.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tc)
        
        # 生成测试函数
        for category, cases in by_category.items():
            lines.append(f"# {'='*60}")
            lines.append(f"# {category.upper()} 测试用例")
            lines.append(f"# {'='*60}")
            
            for i, tc in enumerate(cases):
                test_name = f"test_{tc.function_name}_{category}_{i}"
                lines.append(f"\ndef {test_name}():")
                lines.append(f'    """{tc.description}"""')
                lines.append(f'    # Coverage: {tc.coverage_rationale}')
                
                if tc.edge_case_reason:
                    lines.append(f'    # Edge case: {tc.edge_case_reason}')
                
                lines.append(f"    inputs = {tc.inputs}")
                lines.append(f"    # expected = your_function(**inputs)  # TODO: 运行实际代码获取预期输出")
                lines.append(f"    # assert expected == expected_output")
                lines.append("    pass")
        
        return "\n".join(lines)
    
    def generate_llm_prompt(self, code: str, num_cases: int = 10) -> str:
        """
        生成 LLM 测试用例提示
        
        Args:
            code: 函数代码
            num_cases: 生成数量
            
        Returns:
            提示词
        """
        return f"""作为测试工程师，请为以下函数生成 {num_cases} 个高质量测试用例。

## 函数
```python
{code}
```

## 要求

1. **覆盖正常输入**: 基本功能测试
2. **覆盖边界值**: 0, 负数, 最大值, 空值等
3. **覆盖等价类**: 不同类型的有效输入
4. **覆盖错误处理**: None, 非法输入等
5. **每个用例说明**: 覆盖了什么，为什么这样选

## 输出格式

```json
[
    {{
        "description": "测试描述",
        "inputs": {{"param1": value1, "param2": value2}},
        "expected": "预期输出",
        "category": "normal/boundary/equivalence/edge_case/error",
        "coverage": "覆盖了什么"
    }}
]
```
"""
