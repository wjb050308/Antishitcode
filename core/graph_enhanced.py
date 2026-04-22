"""
增强的依赖图模块

包含：
- 数据流依赖
- 类型依赖
- 时间依赖
- 语义依赖
"""
import ast
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class DependencyType(Enum):
    """依赖类型"""
    CALL = "call"                 # 函数调用
    DATA_READ = "data_read"       # 数据读取
    DATA_WRITE = "data_write"     # 数据写入
    TYPE = "type"                # 类型依赖
    TEMPORAL = "temporal"        # 时间依赖
    SEMANTIC = "semantic"        # 语义依赖


@dataclass
class EnhancedDependency:
    """增强的依赖信息"""
    source: str
    target: str
    dep_type: DependencyType
    weight: float                # 依赖强度
    description: str            # 依赖描述


@dataclass
class NodeMetrics:
    """节点指标"""
    fan_in: int                  # 传入依赖
    fan_out: int                 # 传出依赖
    coupling: float              # 耦合度
    stability: float             # 稳定性
    responsibility: float         # 职责度


class EnhancedDependencyGraph:
    """
    增强的依赖图生成器
    
    支持多种依赖类型的分析和可视化
    """
    
    def __init__(self):
        # 基础依赖图
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_call_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # 数据流依赖
        self.data_reads: Dict[str, Set[str]] = defaultdict(set)   # func -> vars read
        self.data_writes: Dict[str, Set[str]] = defaultdict(set)  # func -> vars written
        
        # 类型依赖
        self.type_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # 函数信息
        self.functions: Dict[str, Tuple[int, int]] = {}  # name -> (start, end)
        self.return_types: Dict[str, str] = {}
        
        # 所有依赖
        self.all_dependencies: List[EnhancedDependency] = []
    
    def analyze(self, tree: ast.AST) -> 'EnhancedDependencyGraph':
        """
        分析依赖关系
        
        Args:
            tree: AST 树
            
        Returns:
            self
        """
        # 第一遍：收集所有函数定义
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[node.name] = (node.lineno, node.end_lineno or node.lineno)
        
        # 第二遍：分析依赖
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._analyze_function(node)
        
        return self
    
    def _analyze_function(self, func_node: ast.FunctionDef):
        """分析单个函数的依赖"""
        func_name = func_node.name
        
        # 分析函数调用
        for child in ast.walk(func_node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    callee = child.func.id
                    if callee in self.functions:
                        self.call_graph[func_name].add(callee)
                        self.reverse_call_graph[callee].add(func_name)
                        
                        self.all_dependencies.append(EnhancedDependency(
                            source=func_name,
                            target=callee,
                            dep_type=DependencyType.CALL,
                            weight=1.0,
                            description=f"{func_name} calls {callee}",
                        ))
        
        # 分析数据流
        defined_vars = set()
        used_vars = set()
        
        class DataFlowVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_func = func_name
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_vars.add(target.id)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # 记录函数调用时使用的变量
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        used_vars.add(arg.id)
                self.generic_visit(node)
        
        visitor = DataFlowVisitor()
        visitor.visit(func_node)
        
        self.data_reads[func_name] = used_vars - defined_vars
        self.data_writes[func_name] = defined_vars
        
        # 数据读取依赖
        for var in self.data_reads[func_name]:
            self.all_dependencies.append(EnhancedDependency(
                source=func_name,
                target=var,
                dep_type=DependencyType.DATA_READ,
                weight=0.5,
                description=f"{func_name} reads {var}",
            ))
        
        # 数据写入依赖
        for var in self.data_writes[func_name]:
            self.all_dependencies.append(EnhancedDependency(
                source=func_name,
                target=var,
                dep_type=DependencyType.DATA_WRITE,
                weight=0.5,
                description=f"{func_name} writes {var}",
            ))
    
    def calculate_metrics(self, func_name: str) -> NodeMetrics:
        """
        计算节点的度量
        
        Args:
            func_name: 函数名
            
        Returns:
            节点度量
        """
        fan_in = len(self.reverse_call_graph.get(func_name, set()))
        fan_out = len(self.call_graph.get(func_name, set()))
        
        # 耦合度 = fan_in + fan_out
        coupling = fan_in + fan_out
        
        # 稳定性 = fan_in / (fan_in + fan_out + 1)
        stability = fan_in / (fan_in + fan_out + 1)
        
        # 职责度 = fan_out (调用越多，责任越多)
        responsibility = fan_out
        
        return NodeMetrics(
            fan_in=fan_in,
            fan_out=fan_out,
            coupling=coupling,
            stability=stability,
            responsibility=responsibility,
        )
    
    def find_critical_functions(self, threshold: int = 3) -> List[Tuple[str, NodeMetrics]]:
        """
        找出关键函数（高扇入）
        
        Args:
            threshold: 扇入阈值
            
        Returns:
            关键函数列表
        """
        critical = []
        for func in self.functions:
            metrics = self.calculate_metrics(func)
            if metrics.fan_in >= threshold:
                critical.append((func, metrics))
        
        return sorted(critical, key=lambda x: x[1].fan_in, reverse=True)
    
    def find_unstable_functions(self, threshold: float = 0.3) -> List[Tuple[str, NodeMetrics]]:
        """
        找出不稳定函数（低稳定性）
        
        Args:
            threshold: 稳定性阈值
            
        Returns:
            不稳定函数列表
        """
        unstable = []
        for func in self.functions:
            metrics = self.calculate_metrics(func)
            if metrics.stability < threshold:
                unstable.append((func, metrics))
        
        return sorted(unstable, key=lambda x: x[1].stability)
    
    def find_isolated_functions(self) -> List[str]:
        """找出孤立函数（无依赖）"""
        isolated = []
        for func in self.functions:
            metrics = self.calculate_metrics(func)
            if metrics.coupling == 0:
                isolated.append(func)
        return isolated
    
    def find_layer_violations(self) -> List[Tuple[str, str]]:
        """
        找出层次违规（应该单向依赖）
        
        Returns:
            违规对列表
        """
        # 检测循环依赖
        violations = []
        visited = set()
        rec_stack = set()
        
        def has_cycle(func, path):
            if func in rec_stack:
                return True
            if func in visited:
                return False
            
            visited.add(func)
            rec_stack.add(func)
            
            for callee in self.call_graph.get(func, set()):
                if has_cycle(callee, path + [func]):
                    violations.append((func, callee))
                    return True
            
            rec_stack.remove(func)
            return False
        
        for func in self.functions:
            has_cycle(func, [])
        
        return violations
    
    def generate_enhanced_dot(
        self,
        highlight_critical: bool = True,
        highlight_cycles: bool = True,
    ) -> str:
        """
        生成增强的 DOT 图
        
        Args:
            highlight_critical: 高亮关键函数
            highlight_cycles: 高亮循环依赖
            
        Returns:
            DOT 格式字符串
        """
        lines = [
            "digraph CodeDependencies {",
            '    rankdir=TB;',
            '    node [shape=box, style=rounded];',
            '    edge [color=gray];',
            "",
        ]
        
        # 添加节点
        critical_funcs = {f[0] for f in self.find_critical_functions()}
        unstable_funcs = {f[0] for f in self.find_unstable_functions()}
        cycle_violations = set(self.find_layer_violations())
        
        for func in self.functions:
            metrics = self.calculate_metrics(func)
            
            # 节点属性
            attrs = [f'label="{func}\\n(in:{metrics.fan_in}, out:{metrics.fan_out})"']
            
            if func in critical_funcs and highlight_critical:
                attrs.append('color=red')
                attrs.append('style=filled')
                attrs.append('fillcolor=lightpink')
            elif func in unstable_funcs:
                attrs.append('color=orange')
            
            if (func, "") in cycle_violations and highlight_cycles:
                attrs.append('color=red')
                attrs.append('penwidth=3')
            
            lines.append(f'    "{func}" [{", ".join(attrs)}];')
        
        lines.append("")
        
        # 添加边（按类型着色）
        dep_colors = {
            DependencyType.CALL: "black",
            DependencyType.DATA_READ: "blue",
            DependencyType.DATA_WRITE: "green",
            DependencyType.TYPE: "purple",
            DependencyType.TEMPORAL: "gray",
            DependencyType.SEMANTIC: "orange",
        }
        
        for dep in self.all_dependencies:
            if dep.dep_type == DependencyType.CALL:
                color = dep_colors.get(dep.dep_type, "gray")
                weight = int(dep.weight * 10)
                lines.append(f'    "{dep.source}" -> "{dep.target}" [color={color}, weight={weight}];')
        
        # 添加数据流边（虚线）
        for func, vars in self.data_reads.items():
            for var in vars:
                lines.append(f'    "{func}" -> "VAR:{var}" [style=dashed, color=blue, constraint=false];')
        
        lines.extend(["}", ""])
        
        return "\n".join(lines)
    
    def generate_mermaid(
        self,
        show_dataflow: bool = False,
    ) -> str:
        """
        生成 Mermaid 格式依赖图
        
        Args:
            show_dataflow: 是否显示数据流
            
        Returns:
            Mermaid 格式字符串
        """
        lines = ["flowchart TD", ""]
        
        critical_funcs = {f[0] for f in self.find_critical_functions()}
        unstable_funcs = {f[0] for f in self.find_unstable_functions()}
        
        # 添加节点
        for func in self.functions:
            metrics = self.calculate_metrics(func)
            
            # 形状
            if func in critical_funcs:
                shape = "{"
            elif func in unstable_funcs:
                shape = "["
            else:
                shape = "("
            
            end_shape = "}" if func in critical_funcs else ("]" if func in unstable_funcs else ")")
            
            label = f"{func}\\n(in:{metrics.fan_in}, out:{metrics.fan_out})"
            lines.append(f'    {func}{shape}{label}{end_shape}')
        
        if show_dataflow:
            lines.append("")
            # 数据流
            for func, vars in self.data_reads.items():
                for var in vars:
                    lines.append(f'    VAR:{var} --> {func}')
        
        lines.append("")
        
        # 添加边
        for func, callees in self.call_graph.items():
            for callee in callees:
                lines.append(f"    {func} --> {callee}")
        
        return "\n".join(lines)
    
    def generate_dependency_report(self) -> str:
        """
        生成依赖分析报告
        
        Returns:
            Markdown 格式报告
        """
        lines = [
            "# 📊 依赖分析报告",
            "",
        ]
        
        # 关键函数
        critical = self.find_critical_functions()
        if critical:
            lines.extend([
                "## 🔴 关键函数 (高扇入)",
                "",
                "| 函数 | 扇入 | 扇出 | 耦合度 |",
                "|------|------|------|--------|",
            ])
            for func, metrics in critical:
                lines.append(f"| `{func}` | {metrics.fan_in} | {metrics.fan_out} | {metrics.coupling} |")
            lines.append("")
        
        # 不稳定函数
        unstable = self.find_unstable_functions()
        if unstable:
            lines.extend([
                "## 🟠 不稳定函数 (低稳定性)",
                "",
                "| 函数 | 扇入 | 扇出 | 稳定性 |",
                "|------|------|------|---------|",
            ])
            for func, metrics in unstable:
                lines.append(f"| `{func}` | {metrics.fan_in} | {metrics.fan_out} | {metrics.stability:.2f} |")
            lines.append("")
        
        # 孤立函数
        isolated = self.find_isolated_functions()
        if isolated:
            lines.extend([
                "## 🔵 孤立函数 (无依赖)",
                "",
                f"- {', '.join(f'`{f}`' for f in isolated)}",
                "",
            ])
        
        # 循环依赖
        violations = self.find_layer_violations()
        if violations:
            lines.extend([
                "## ⚠️ 循环依赖警告",
                "",
            ])
            for source, target in violations:
                lines.append(f"- `{source}` → `{target}`")
            lines.append("")
        
        # 统计
        lines.extend([
            "## 📈 统计",
            "",
            f"- 总函数数: {len(self.functions)}",
            f"- 总依赖数: {len(self.all_dependencies)}",
            f"- 关键函数数: {len(critical)}",
            f"- 不稳定函数数: {len(unstable)}",
            f"- 孤立函数数: {len(isolated)}",
            f"- 循环依赖数: {len(violations)}",
        ])
        
        return "\n".join(lines)
