"""
测试用例
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import CodeArchaeologist
from core.types import CodeLayer, CodePattern


class TestExcavator:
    """测试地层分析"""
    
    def test_simple_function(self):
        """测试简单函数分析"""
        from core.excavator import Excavator
        import ast
        
        code = """
def hello():
    print("Hello")
"""
        tree = ast.parse(code)
        excavator = Excavator()
        result = excavator.excavate(tree, code)
        
        assert len(result.functions) == 1
        assert result.functions[0].name == "hello"
        assert result.overall_quality_score > 50
    
    def test_complexity_calculation(self):
        """测试复杂度计算"""
        from core.excavator import Excavator
        import ast
        
        code = """
def complex_function(x):
    if x > 0:
        for i in range(10):
            if i > 5:
                return i
    return 0
"""
        tree = ast.parse(code)
        excavator = Excavator()
        result = excavator.excavate(tree, code)
        
        assert len(result.functions) == 1
        assert result.functions[0].complexity > 1


class TestTypology:
    """测试类型分析"""
    
    def test_shit_code_detection(self):
        """测试屎山代码检测"""
        from core.typology import TypologyAnalyzer
        from core.types import FunctionInfo
        
        analyzer = TypologyAnalyzer()
        
        # 模拟屎山函数
        func = FunctionInfo(
            name="shit_function",
            lineno=1,
            end_lineno=250,
            args=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"],
            returns="int",
            complexity=25,
        )
        
        pattern = analyzer.classify_function(func, None)
        
        assert pattern == CodePattern.SHIT_CODE


class TestAuthenticator:
    """测试安全审计"""
    
    def test_safe_code(self):
        """测试安全代码"""
        from core.authenticator import Authenticator
        
        code = """
def add(a, b):
    return a + b
"""
        auth = Authenticator()
        result = auth.analyze(code)
        
        assert result.is_safe
        assert len(result.malicious_patterns) == 0
    
    def test_malicious_detection(self):
        """测试恶意代码检测"""
        from core.authenticator import Authenticator
        
        code = """
import subprocess
def backdoor():
    subprocess.Popen(['bash', '-c', 'rm -rf /'])
"""
        auth = Authenticator()
        result = auth.analyze(code)
        
        assert not result.is_safe or len(result.warnings) > 0


class TestDependencyGraph:
    """测试依赖图"""
    
    def test_dot_generation(self):
        """测试 DOT 图生成"""
        from core.dependency_graph import DependencyGraph
        from core.types import ExcavationResult, FunctionInfo
        
        graph = DependencyGraph()
        
        # 创建模拟数据
        func1 = FunctionInfo("a", 1, 10, [], None, 1, ["b", "c"])
        func2 = FunctionInfo("b", 11, 20, [], None, 1, ["c"])
        func3 = FunctionInfo("c", 21, 30, [], None, 1, [])
        
        excavation = ExcavationResult(
            file_path="test.py",
            layers={},
            functions=[func1, func2, func3],
            classes=[],
            dead_code=[],
            overall_quality_score=80,
        )
        
        dot = graph.generate_dot(excavation)
        
        assert "digraph" in dot
        assert "a" in dot
        assert "b" in dot
        assert "c" in dot


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
