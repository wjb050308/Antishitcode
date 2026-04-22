"""
类型学分析器 - 代码模式分类

考古学原理：将代码按形态分类
- 设计模式: 良好的架构
- 反模式: 不良实践
- 屎山代码: 需要重构的混乱代码
"""
import ast
from typing import List, Set
from .types import CodePattern, FunctionInfo, ClassInfo


class TypologyAnalyzer:
    """
    代码类型学分析器
    
    识别代码中的各种模式
    """
    
    # 反模式特征
    ANTI_PATTERNS = {
        "long_method": {"threshold": 100, "metric": "lines"},
        "high_complexity": {"threshold": 15, "metric": "cyclomatic"},
        "deep_nesting": {"threshold": 5, "metric": "depth"},
        "magic_numbers": {"threshold": 3, "metric": "count"},
        "global_variables": {"threshold": 0, "metric": "count"},
    }
    
    def classify_function(self, func: FunctionInfo, tree: ast.AST) -> CodePattern:
        """
        分类函数代码模式
        
        Args:
            func: 函数信息
            tree: AST 树
            
        Returns:
            代码模式
        """
        # 检测屎山代码
        if self._is_shit_code(func):
            return CodePattern.SHIT_CODE
        
        # 检测反模式
        if self._is_anti_pattern(func):
            return CodePattern.ANTI_PATTERN
        
        # 检测设计模式
        if self._is_design_pattern(func):
            return CodePattern.DESIGN_PATTERN
        
        # 检测死代码
        if func.layer.value == "dead":
            return CodePattern.DEAD_CODE
        
        return CodePattern.GOOD
    
    def classify_class(self, cls: ClassInfo, tree: ast.AST) -> CodePattern:
        """
        分类类代码模式
        """
        # God Class 检测
        if len(cls.methods) > 20:
            return CodePattern.ANTI_PATTERN
        
        # 继承层级过深
        if len(cls.base_classes) > 3:
            return CodePattern.ANTI_PATTERN
        
        return CodePattern.GOOD
    
    def _is_shit_code(self, func: FunctionInfo) -> bool:
        """检测是否为屎山代码"""
        # 函数过长
        func_length = func.end_lineno - func.lineno
        if func_length > 200:
            return True
        
        # 复杂度过高
        if func.complexity > 20:
            return True
        
        # 参数过多
        if len(func.args) > 10:
            return True
        
        return False
    
    def _is_anti_pattern(self, func: FunctionInfo) -> bool:
        """检测反模式"""
        # 复杂度过高
        if func.complexity > 15:
            return True
        
        # 函数名包含反模式特征
        anti_keywords = ["hack", "fix", "tmp", "temp", "bug"]
        if any(k in func.name.lower() for k in anti_keywords):
            return True
        
        return False
    
    def _is_design_pattern(self, func: FunctionInfo) -> bool:
        """检测设计模式"""
        # 工厂模式
        if func.name.startswith("create_") or func.name.startswith("make_"):
            return True
        
        # 单例模式
        if "_instance" in func.name or "get_instance" in func.name:
            return True
        
        # 策略模式
        if "strategy" in func.name.lower() or "policy" in func.name.lower():
            return True
        
        # 观察者模式
        if "notify" in func.name or "subscribe" in func.name or "update" in func.name:
            return True
        
        return False
    
    def detect_common_issues(self, tree: ast.AST) -> List[str]:
        """
        检测常见问题
        
        Returns:
            问题列表
        """
        issues = []
        
        # 检测全局变量
        globals = self._find_global_variables(tree)
        if globals:
            issues.append(f"发现 {len(globals)} 个全局变量: {', '.join(globals[:5])}")
        
        # 检测循环嵌套
        deep_loops = self._find_deep_loops(tree)
        if deep_loops:
            issues.append(f"发现 {len(deep_loops)} 处深层循环嵌套")
        
        # 检测重复代码 (简化检测)
        issues.append("建议运行静态分析工具进行深度检测")
        
        return issues
    
    def _find_global_variables(self, tree: ast.AST) -> List[str]:
        """查找全局变量"""
        globals = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals.append(target.id)
        return globals
    
    def _find_deep_loops(self, tree: ast.AST, max_depth: int = 3) -> List[tuple]:
        """查找深层循环"""
        deep_loops = []
        
        def check_nesting(node, depth=0):
            if isinstance(node, (ast.For, ast.While)):
                if depth >= max_depth:
                    deep_loops.append((node.lineno, depth))
                for child in ast.iter_child_nodes(node):
                    check_nesting(child, depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    check_nesting(child, depth)
        
        check_nesting(tree)
        return deep_loops
