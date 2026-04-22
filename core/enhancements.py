"""
核心算法增强模块

包含：
1. 增强的死代码检测（数据流分析）
2. 增强的复杂度计算（Halstead 指标）
3. 嵌套模式识别
"""
import ast
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class NestingPattern(Enum):
    """嵌套模式类型"""
    NORMAL = "normal"
    CALLBACK_HELL = "callback_hell"
    PROMISE_CHAIN = "promise_chain"
    CONDITIONAL_CHAIN = "conditional_chain"
    DEEP_NESTING = "deep_nesting"


@dataclass
class DataFlowInfo:
    """数据流信息"""
    defined_vars: Set[str]          # 定义过的变量
    used_vars: Set[str]              # 使用过的变量
    returned_vars: Set[str]          # 返回的变量
    modified_vars: Set[str]           # 修改过的变量
    dead_vars: Set[str]              # 死变量（定义了但没使用）


@dataclass
class EnhancedComplexity:
    """增强的复杂度信息"""
    cyclomatic: int                  # 圈复杂度
    halstead_volume: float           # Halstead 容量
    halstead_difficulty: float       # Halstead 难度
    maintainability_index: float      # 可维护性指数
    nesting_pattern: NestingPattern   # 嵌套模式
    max_nesting_depth: int           # 最大嵌套深度
    cognitive_complexity: int         # 认知复杂度


class EnhancedExcavator:
    """
    增强的发掘器
    
    在原有基础上增加：
    - 数据流分析的死代码检测
    - Halstead 指标计算
    - 嵌套模式识别
    """
    
    def __init__(self):
        self.current_function: Optional[str] = None
        self.data_flow: Dict[str, DataFlowInfo] = {}
    
    def analyze_data_flow(self, node: ast.AST, function_name: str) -> DataFlowInfo:
        """
        分析函数的数据流
        
        Args:
            node: 函数 AST 节点
            function_name: 函数名
            
        Returns:
            数据流信息
        """
        self.current_function = function_name
        self.data_flow[function_name] = DataFlowInfo(
            defined_vars=set(),
            used_vars=set(),
            returned_vars=set(),
            modified_vars=set(),
            dead_vars=set(),
        )
        
        # 分析函数体
        for stmt in ast.walk(node):
            self._analyze_statement(stmt)
        
        # 计算死变量
        info = self.data_flow[function_name]
        info.dead_vars = info.defined_vars - info.used_vars
        
        return info
    
    def _analyze_statement(self, node: ast.AST):
        """分析语句的数据流"""
        info = self.data_flow.get(self.current_function)
        if info is None:
            return
        
        if isinstance(node, ast.Assign):
            # 赋值语句：左边是定义
            for target in node.targets:
                if isinstance(target, ast.Name):
                    info.defined_vars.add(target.id)
            # 分析右边的使用
            self._analyze_expr(node.value, info)
            
        elif isinstance(node, ast.AugAssign):
            # 增量赋值
            if isinstance(node.target, ast.Name):
                info.defined_vars.add(target.id)
                info.modified_vars.add(target.id)
            self._analyze_expr(node.value, info)
            
        elif isinstance(node, ast.Return):
            # 返回语句
            if node.value:
                self._analyze_expr(node.value, info)
                # 尝试确定返回的变量
                if isinstance(node.value, ast.Name):
                    info.returned_vars.add(node.value.id)
                elif isinstance(node.value, ast.BinOp):
                    # 二元运算可能涉及多个变量
                    self._extract_vars_from_expr(node.value, info.returned_vars)
                    
        elif isinstance(node, ast.Name):
            # 变量引用
            info.used_vars.add(node.id)
            
        elif isinstance(node, ast.Call):
            # 函数调用
            if isinstance(node.func, ast.Name):
                info.used_vars.add(node.func.id)
            for arg in node.args:
                self._analyze_expr(arg, info)
                
        elif isinstance(node, ast.If):
            # 条件判断
            self._analyze_expr(node.test, info)
            
        elif isinstance(node, ast.For):
            # for 循环
            if isinstance(node.target, ast.Name):
                info.defined_vars.add(node.target.id)
            self._analyze_expr(node.iter, info)
            for stmt in node.body:
                self._analyze_statement(stmt)
                
        elif isinstance(node, ast.While):
            self._analyze_expr(node.test, info)
            
        elif isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.optional_vars, ast.Name):
                    info.defined_vars.add(item.optional_vars.id)
    
    def _analyze_expr(self, node: ast.AST, info: DataFlowInfo):
        """分析表达式中的变量使用"""
        if node is None:
            return
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                info.used_vars.add(child.id)
    
    def _extract_vars_from_expr(self, node: ast.AST, var_set: Set[str]):
        """从表达式中提取变量名"""
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                var_set.add(child.id)
    
    def detect_dead_code_flow(self, node: ast.FunctionDef, info: DataFlowInfo) -> bool:
        """
        基于数据流分析检测是否为死代码
        
        Args:
            node: 函数 AST 节点
            info: 数据流信息
            
        Returns:
            是否是死代码
        """
        # 死代码的判断标准：
        # 1. 函数定义了变量但从未返回
        # 2. 函数返回的值从未被使用（需要调用者分析）
        # 3. 函数内部有永不执行的代码
        
        # 如果函数没有 return，则可能是死代码
        has_return = False
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                has_return = True
                break
        
        if not has_return:
            return True
        
        # 如果有返回，但返回的是从未定义的变量，也是死代码
        if info.returned_vars:
            if info.returned_vars.issubset(info.defined_vars - info.used_vars):
                # 返回的变量都是死变量
                return True
        
        return False
    
    def calculate_halstead(
        self,
        operators: List[str],
        operands: List[str],
    ) -> Tuple[float, float]:
        """
        计算 Halstead 指标
        
        Args:
            operators: 操作符列表
            operands: 操作数列表
            
        Returns:
            (容量, 难度)
        """
        import math
        
        # 去重
        n1 = len(set(operators))  # 不同操作符数
        n2 = len(set(operands))  # 不同操作数数
        N1 = len(operators)        # 总操作符数
        N2 = len(operands)        # 总操作数数
        
        # 容量 V = N * log2(n)
        N = N1 + N2
        n = n1 + n2
        
        if n == 0:
            volume = 0.0
        else:
            volume = N * math.log2(n) if n > 0 else 0.0
        
        # 难度 D = (n1/2) * (N2/n2)
        difficulty = 0.0
        if n2 > 0 and n1 > 0:
            difficulty = (n1 / 2) * (N2 / n2)
        
        return volume, difficulty
    
    def extract_operators_operands(self, node: ast.AST) -> Tuple[List[str], List[str]]:
        """
        提取操作符和操作数
        
        Returns:
            (operators, operands)
        """
        operators = []
        operands = []
        
        for child in ast.walk(node):
            # 操作符
            if isinstance(child, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                operators.append("arithmetic")
            elif isinstance(child, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                operators.append("comparison")
            elif isinstance(child, (ast.And, ast.Or, ast.Not)):
                operators.append("logical")
            elif isinstance(child, ast.Call):
                operators.append("call")
            elif isinstance(child, ast.If):
                operators.append("if")
            elif isinstance(child, (ast.For, ast.While)):
                operators.append("loop")
            elif isinstance(child, ast.Assign):
                operators.append("assign")
            
            # 操作数
            if isinstance(child, ast.Name):
                operands.append(child.id)
            elif isinstance(child, ast.Constant):
                operands.append(str(type(child.value).__name__))
            elif isinstance(child, ast.Attribute):
                operands.append(child.attr)
        
        return operators, operands
    
    def calculate_maintainability_index(
        self,
        lines: int,
        complexity: int,
        halstead_volume: float,
    ) -> float:
        """
        计算可维护性指数
        
        MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        
        Args:
            lines: 代码行数
            complexity: 圈复杂度
            halstead_volume: Halstead 容量
            
        Returns:
            可维护性指数 (0-100)
        """
        import math
        
        if lines <= 0 or halstead_volume <= 0:
            return 100.0
        
        mi = 171.0
        mi -= 5.2 * math.log(halstead_volume) if halstead_volume > 0 else 0
        mi -= 0.23 * complexity
        mi -= 16.2 * math.log(lines)
        mi = mi * 100 / 171
        
        return max(0.0, min(100.0, mi))
    
    def detect_nesting_pattern(self, node: ast.AST) -> Tuple[NestingPattern, int]:
        """
        检测嵌套模式
        
        Args:
            node: 函数 AST 节点
            
        Returns:
            (嵌套模式, 最大深度)
        """
        max_depth = 0
        callback_count = 0
        conditional_count = 0
        
        def walk(node, depth=0):
            nonlocal max_depth, callback_count, conditional_count
            
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                depth += 1
                max_depth = max(max_depth, depth)
                if isinstance(node, ast.If):
                    conditional_count += 1
            elif isinstance(node, ast.Call):
                for arg in node.args:
                    if isinstance(arg, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef)):
                        callback_count += 1
            elif isinstance(node, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef)):
                callback_count += 1
            
            for child in ast.iter_child_nodes(node):
                walk(child, depth)
        
        walk(node)
        
        # 判断嵌套模式
        if max_depth >= 6:
            pattern = NestingPattern.DEEP_NESTING
        elif callback_count >= 3:
            pattern = NestingPattern.CALLBACK_HELL
        elif conditional_count >= 5:
            pattern = NestingPattern.CONDITIONAL_CHAIN
        else:
            pattern = NestingPattern.NORMAL
        
        return pattern, max_depth
    
    def calculate_cognitive_complexity(self, node: ast.AST) -> int:
        """
        计算认知复杂度
        
        基于 SonarSource 的算法
        """
        class CognitiveVisitor(ast.NodeVisitor):
            def __init__(self):
                self.score = 0
                self.structural_increment = 0
                self.nesting_level = 0
            
            def visit_FunctionDef(self, node):
                self.structural_increment = 1
                for child in node.body:
                    self._visit_stmt(child, 0)
                self.structural_increment = 0
            
            def _visit_stmt(self, node, level):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    self.score += 1 + level
                    self.nesting_level += 1
                    for child in node.body:
                        self._visit_stmt(child, level + 1)
                    if isinstance(node, ast.If):
                        for child in node.orelse:
                            self._visit_stmt(child, level + 1)
                    self.nesting_level -= 1
                elif isinstance(node, (ast.BoolOp,)):
                    self.score += level
                    for child in node.values:
                        if isinstance(child, (ast.BoolOp,)):
                            self._visit_stmt(child, level + 1)
                elif isinstance(node, (ast.While,)):
                    self.score += 1 + level
                    self.nesting_level += 1
                    for child in node.body:
                        self._visit_stmt(child, level + 1)
                    self.nesting_level -= 1
                elif isinstance(node, (ast.With,)):
                    self.score += 1 + level
                    self.nesting_level += 1
                    for child in node.body:
                        self._visit_stmt(child, level + 1)
                    self.nesting_level -= 1
                else:
                    for child in ast.iter_child_nodes(node):
                        if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp)):
                            self._visit_stmt(child, level)
                        elif isinstance(child, ast.NodeVisitor):
                            child.accept(self)
            
            def visit_Call(self, node):
                # 递归调用增加复杂度
                if isinstance(node.func, ast.Name):
                    if node.func.id == self.parent_func_name:
                        self.score += 1 + self.nesting_level
                self.generic_visit(node)
        
        visitor = CognitiveVisitor()
        visitor.visit(node)
        return visitor.score
    
    def enhanced_analyze(self, code: str) -> Dict:
        """
        增强的代码分析
        
        Returns:
            包含所有增强指标的字典
        """
        tree = ast.parse(code)
        results = {
            "functions": [],
            "overall_metrics": {
                "total_cyclomatic": 0,
                "avg_maintainability": 0,
                "nesting_patterns": {},
            }
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    continue
                    
                func_info = {
                    "name": node.name,
                    "lines": node.end_lineno - node.lineno,
                }
                
                # 数据流分析
                data_flow = self.analyze_data_flow(node, node.name)
                func_info["dead_vars"] = list(data_flow.dead_vars)
                func_info["is_dead_code"] = self.detect_dead_code_flow(node, data_flow)
                
                # Halstead 指标
                operators, operands = self.extract_operators_operands(node)
                volume, difficulty = self.calculate_halstead(operators, operands)
                func_info["halstead_volume"] = volume
                func_info["halstead_difficulty"] = difficulty
                
                # 圈复杂度
                complexity = self._calc_complexity(node)
                func_info["cyclomatic_complexity"] = complexity
                
                # 可维护性指数
                mi = self.calculate_maintainability_index(
                    func_info["lines"],
                    complexity,
                    volume,
                )
                func_info["maintainability_index"] = mi
                
                # 嵌套模式
                pattern, max_depth = self.detect_nesting_pattern(node)
                func_info["nesting_pattern"] = pattern.value
                func_info["max_nesting_depth"] = max_depth
                
                # 认知复杂度
                func_info["cognitive_complexity"] = self.calculate_cognitive_complexity(node)
                
                results["functions"].append(func_info)
                
                # 汇总
                results["overall_metrics"]["total_cyclomatic"] += complexity
        
        # 计算平均可维护性
        if results["functions"]:
            total_mi = sum(f["maintainability_index"] for f in results["functions"])
            results["overall_metrics"]["avg_maintainability"] = total_mi / len(results["functions"])
        
        return results
    
    def _calc_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler,)):
                complexity += 1
        
        return complexity
