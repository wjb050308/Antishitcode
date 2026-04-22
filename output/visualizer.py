"""
可视化工具
"""
from typing import List, Dict, Any


class Visualizer:
    """
    可视化工具
    
    生成各种格式的依赖关系图
    """
    
    def __init__(self):
        self.graph = None
    
    def visualize_ast(self, tree, max_depth: int = 3) -> str:
        """
        可视化 AST 结构
        
        Args:
            tree: AST 树
            max_depth: 最大深度
            
        Returns:
            ASCII 树形图
        """
        lines = ["AST 结构:", ""]
        
        def render_node(node, depth=0, prefix=""):
            if depth > max_depth:
                return
            
            node_name = type(node).__name__
            indent = "  " * depth
            lines.append(f"{indent}{prefix}{node_name}")
            
            for i, child in enumerate(node.__dict__.get("body", [])):
                is_last = i == len(node.__dict__.get("body", [])) - 1
                new_prefix = "└── " if is_last else "├── "
                render_node(child, depth + 1, new_prefix)
        
        if hasattr(tree, "body"):
            for i, node in enumerate(tree.body):
                is_last = i == len(tree.body) - 1
                prefix = "└── " if is_last else "├── "
                render_node(node, 0, prefix)
        
        return "\n".join(lines)
    
    def visualize_complexity(
        self,
        functions: List[Any],
    ) -> str:
        """
        可视化复杂度分布
        
        Args:
            functions: 函数列表
            
        Returns:
            ASCII 柱状图
        """
        lines = ["函数复杂度分布:", ""]
        
        # 排序
        sorted_funcs = sorted(
            functions,
            key=lambda f: f.complexity,
            reverse=True,
        )[:10]  # 前10
        
        max_complexity = max(f.complexity for f in sorted_funcs) if sorted_funcs else 1
        
        for func in sorted_funcs:
            bar_length = int(func.complexity / max_complexity * 40)
            bar = "█" * bar_length
            lines.append(f"{func.name:20} {bar} ({func.complexity})")
        
        return "\n".join(lines)
    
    def visualize_layers(
        self,
        layers: Dict[str, List[Any]],
    ) -> str:
        """
        可视化代码层次
        
        Args:
            layers: 层次字典
            
        Returns:
            ASCII 图
        """
        lines = ["代码地层结构:", "", "     层次     数量"]
        lines.append("   " + "─" * 30)
        
        layer_names = {
            "core": "🟢 核心层",
            "feature": "🔵 功能层",
            "patch": "🟡 补丁层",
            "debt": "🟠 技术债",
            "dead": "⚫ 死代码",
        }
        
        for layer, items in layers.items():
            name = layer_names.get(layer, layer)
            count = len(items)
            bar = "█" * min(count, 50)
            lines.append(f"{name:12} {count:4} {bar}")
        
        return "\n".join(lines)
    
    def visualize_coupling(
        self,
        dependencies: Dict[str, List[str]],
    ) -> str:
        """
        可视化耦合度
        
        Args:
            dependencies: 依赖关系
            
        Returns:
            耦合度矩阵
        """
        lines = ["函数耦合度:", "", "函数调用关系:"]
        
        for func, calls in dependencies.items():
            if calls:
                calls_str = ", ".join(calls[:5])
                if len(calls) > 5:
                    calls_str += "..."
                lines.append(f"  {func} → {calls_str}")
        
        return "\n".join(lines)
