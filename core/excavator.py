"""
地层分析器 - 识别代码层次

考古学原理：将代码按层次分类
- 核心层 (CORE): 原始架构，最早的逻辑
- 功能层 (FEATURE): 后期添加的功能
- 补丁层 (PATCH): 修 bug 的代码
- 技术债层 (DEBT): 临时解决方案
- 死代码层 (DEAD): 废弃代码
"""
import ast
from typing import Dict, List, Set
from .types import CodeLayer, FunctionInfo, ClassInfo, ExcavationResult


class Excavator:
    """
    代码地层发掘器
    
    通过 AST 分析识别代码的层次结构
    """
    
    def __init__(self):
        self.code = ""
        self.tree = None
        self.layers: Dict[CodeLayer, List] = {
            CodeLayer.CORE: [],
            CodeLayer.FEATURE: [],
            CodeLayer.PATCH: [],
            CodeLayer.DEBT: [],
            CodeLayer.DEAD: [],
        }
    
    def excavate(self, tree: ast.AST, code: str) -> ExcavationResult:
        """
        发掘代码地层
        
        Args:
            tree: AST 树
            code: 原始代码
            
        Returns:
            发掘结果
        """
        self.tree = tree
        self.code = code
        
        functions = []
        classes = []
        dead_code = []
        
        # 遍历 AST
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_info = self._analyze_function(node)
                functions.append(func_info)
                
                # 检测死代码
                if self._is_dead_code(node):
                    dead_code.append(func_info.name)
                    func_info.layer = CodeLayer.DEAD
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node)
                classes.append(class_info)
        
        # 计算整体质量评分
        quality_score = self._calculate_quality_score(functions, dead_code)
        
        # 更新层次
        self.layers[CodeLayer.CORE] = [f for f in functions if f.layer == CodeLayer.CORE]
        self.layers[CodeLayer.DEAD] = dead_code
        
        return ExcavationResult(
            file_path="",
            layers=self.layers,
            functions=functions,
            classes=classes,
            dead_code=dead_code,
            overall_quality_score=quality_score,
        )
    
    def _analyze_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """分析函数"""
        # 计算圈复杂度
        complexity = self._calculate_complexity(node)
        
        # 检测函数调用
        calls = self._get_function_calls(node)
        
        # 推断层次
        layer = self._infer_layer(node, calls)
        
        # 检测代码模式
        pattern = self._detect_pattern(node)
        
        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            args=[arg.arg for arg in node.args.args],
            returns=self._get_return_type(node),
            complexity=complexity,
            calls=calls,
            layer=layer,
            pattern=pattern,
        )
    
    def _analyze_class(self, node: ast.ClassDef) -> ClassInfo:
        """分析类"""
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith("_") or item.name == "__init__":
                    methods.append(self._analyze_function(item))
        
        base_classes = [b.attr if isinstance(b, ast.Attribute) else b.id for b in node.bases]
        
        return ClassInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            methods=methods,
            base_classes=base_classes,
        )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _get_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """获取函数调用列表"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return list(set(calls))
    
    def _infer_layer(self, node: ast.FunctionDef, calls: List[str]) -> CodeLayer:
        """推断代码层次"""
        name = node.name.lower()
        
        # 检测是否为死代码
        if self._is_dead_code(node):
            return CodeLayer.DEAD
        
        # 检测是否为补丁
        if "fix" in name or "bug" in name or "patch" in name:
            return CodeLayer.PATCH
        
        # 检测是否为技术债
        if "temp" in name or "tmp" in name or "hack" in name or "workaround" in name:
            return CodeLayer.DEBT
        
        # 检测是否为临时功能
        if "deprecated" in name or "old" in name or "legacy" in name:
            return CodeLayer.FEATURE
        
        # 默认为核心层
        return CodeLayer.CORE
    
    def _detect_pattern(self, node: ast.FunctionDef) -> str:
        """检测代码模式"""
        # 检测嵌套过深
        max_depth = self._get_nesting_depth(node)
        if max_depth > 5:
            return "anti"
        
        # 检测函数过长
        lines = node.end_lineno - node.lineno
        if lines > 100:
            return "shit"
        
        # 检测复杂度过高
        complexity = self._calculate_complexity(node)
        if complexity > 15:
            return "anti"
        
        return "normal"
    
    def _get_nesting_depth(self, node: ast.FunctionDef, current_depth: int = 0) -> int:
        """获取最大嵌套深度"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                depth = self._get_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _is_dead_code(self, node: ast.FunctionDef) -> bool:
        """检测死代码"""
        name = node.name.lower()
        
        # 明显是死代码的命名
        dead_patterns = ["unused", "dead", "obsolete", "deprecated", "old", "temp_old"]
        if any(p in name for p in dead_patterns):
            return True
        
        # 只被死代码调用
        # (简化检测，实际需要数据流分析)
        
        return False
    
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """推断返回类型"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                if isinstance(child.value, ast.Constant):
                    return type(child.value.value).__name__
                elif isinstance(child.value, ast.Name):
                    return child.value.id
                elif isinstance(child.value, ast.Attribute):
                    return child.value.attr
        return "unknown"
    
    def _calculate_quality_score(
        self,
        functions: List[FunctionInfo],
        dead_code: List[str],
    ) -> float:
        """计算代码质量评分"""
        if not functions:
            return 0.0
        
        # 基础分
        score = 80.0
        
        # 死代码扣分
        dead_ratio = len(dead_code) / len(functions)
        score -= dead_ratio * 30
        
        # 复杂度扣分
        high_complexity = sum(1 for f in functions if f.complexity > 10)
        score -= high_complexity * 2
        
        # 屎山代码扣分
        shit_code = sum(1 for f in functions if f.pattern == "shit")
        score -= shit_code * 5
        
        return max(0.0, min(100.0, score))
