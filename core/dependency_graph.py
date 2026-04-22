"""
依赖关系图生成器

考古学原理：绘制文物出土位置关系图
"""
import ast
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class DependencyGraph:
    """
    依赖关系图生成器
    
    生成函数/模块调用关系图 (DOT 格式)
    """
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.functions: Dict[str, Tuple[int, int]] = {}  # name -> (start, end)
    
    def generate_dot(self, excavation_result) -> str:
        """
        生成 DOT 格式依赖图
        
        Args:
            excavation_result: 发掘结果
            
        Returns:
            DOT 格式字符串
        """
        self.graph.clear()
        self.reverse_graph.clear()
        self.functions.clear()
        
        # 构建图
        for func in excavation_result.functions:
            self.functions[func.name] = (func.lineno, func.end_lineno)
            
            for call in func.calls:
                self.graph[func.name].add(call)
                self.reverse_graph[call].add(func.name)
        
        # 生成 DOT
        lines = [
            "digraph CodeDependencies {",
            '    rankdir=TB;',
            '    node [shape=box, style=rounded];',
            '    edge [color=gray];',
            "",
        ]
        
        # 添加节点
        for func_name in self.functions:
            coupling = self._calculate_coupling(func_name)
            color = self._get_color_by_coupling(coupling)
            
            lines.append(
                f'    "{func_name}" [label="{func_name}\\n({coupling})" '
                f'color={color}];'
            )
        
        lines.append("")
        
        # 添加边
        for func, calls in self.graph.items():
            for call in calls:
                if call in self.functions:  # 只显示我们关心的函数
                    lines.append(f'    "{func}" -> "{call}";')
        
        lines.extend([
            "",
            "}",
        ])
        
        return "\n".join(lines)
    
    def _calculate_coupling(self, func_name: str) -> str:
        """计算耦合度"""
        incoming = len(self.reverse_graph.get(func_name, []))
        outgoing = len(self.graph.get(func_name, []))
        
        total = incoming + outgoing
        
        if total <= 2:
            return "low"
        elif total <= 5:
            return "medium"
        else:
            return "high"
    
    def _get_color_by_coupling(self, coupling: str) -> str:
        """根据耦合度返回颜色"""
        colors = {
            "low": "green",
            "medium": "orange",
            "high": "red",
        }
        return colors.get(coupling, "gray")
    
    def generate_mermaid(self, excavation_result) -> str:
        """
        生成 Mermaid 格式依赖图
        
        Args:
            excavation_result: 发掘结果
            
        Returns:
            Mermaid 格式字符串
        """
        self.graph.clear()
        self.reverse_graph.clear()
        self.functions.clear()
        
        # 构建图
        for func in excavation_result.functions:
            self.functions[func.name] = (func.lineno, func.end_lineno)
            
            for call in func.calls:
                self.graph[func.name].add(call)
                self.reverse_graph[call].add(func.name)
        
        lines = ["flowchart TD", ""]
        
        # 添加节点
        for func_name in self.functions:
            coupling = self._calculate_coupling(func_name)
            
            if coupling == "high":
                shape = "{"
            elif coupling == "medium":
                shape = "["
            else:
                shape = "("
            
            end_shape = "}" if coupling == "high" else ("]" if coupling == "medium" else ")")
            
            lines.append(f'    {func_name}{shape}{func_name}{end_shape}')
        
        lines.append("")
        
        # 添加边
        for func, calls in self.graph.items():
            for call in calls:
                if call in self.functions:
                    lines.append(f"    {func} --> {call}")
        
        return "\n".join(lines)
    
    def find_critical_functions(self, excavation_result) -> List[str]:
        """
        找出关键函数（被很多函数调用）
        
        Args:
            excavation_result: 发掘结果
            
        Returns:
            关键函数列表
        """
        self.graph.clear()
        self.reverse_graph.clear()
        
        for func in excavation_result.functions:
            for call in func.calls:
                self.graph[func.name].add(call)
                self.reverse_graph[call].add(func.name)
        
        critical = []
        for func, callers in self.reverse_graph.items():
            if len(callers) >= 5:  # 被5个以上函数调用
                critical.append(func)
        
        return sorted(critical, key=lambda x: len(self.reverse_graph[x]), reverse=True)
    
    def find_isolated_functions(self, excavation_result) -> List[str]:
        """
        找出孤立函数（不调用其他函数，也不被调用）
        
        Args:
            excavation_result: 发掘结果
            
        Returns:
            孤立函数列表
        """
        self.graph.clear()
        self.reverse_graph.clear()
        
        for func in excavation_result.functions:
            for call in func.calls:
                self.graph[func.name].add(call)
                self.reverse_graph[call].add(func.name)
        
        isolated = []
        for func in excavation_result.functions:
            has_calls = len(self.graph.get(func.name, [])) > 0
            is_called = len(self.reverse_graph.get(func.name, [])) > 0
            
            if not has_calls and not is_called:
                isolated.append(func.name)
        
        return isolated
