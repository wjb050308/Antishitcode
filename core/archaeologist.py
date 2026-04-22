"""
代码考古学家 - 主类
"""
import ast
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from .types import (
    CodeLayer,
    CodePattern,
    FunctionInfo,
    ClassInfo,
    SemanticUnderstanding,
    TestCase,
    ExcavationResult,
    DecipherResult,
    AuthenticationResult,
    WrappedCode,
    RefactorResult,
)
from .excavator import Excavator
from .typology import TypologyAnalyzer
from .decipher import DecipherEngine
from .authenticator import Authenticator
from .wrapper import RecursiveWrapper
from .verifier import TestVerifier
from .dependency_graph import DependencyGraph

# Lazy imports for LLM client
_llm_client = None

def _get_llm_client():
    global _llm_client
    if _llm_client is None:
        try:
            from llm import OpenAIClient, get_default_client
            _llm_client = get_default_client()
        except ImportError:
            try:
                from ..llm import OpenAIClient, get_default_client
                _llm_client = get_default_client()
            except ImportError:
                _llm_client = None
    return _llm_client


class CodeArchaeologist:
    """
    代码考古学家
    
    主要功能：
    1. 发掘 (Excavation) - 识别代码层次
    2. 解谜 (Decipherment) - AI 理解意图
    3. 鉴真 (Authentication) - 安全审计
    4. 包装 (Wrapping) - 递归包装可测试
    5. 验证 (Verification) - 测试保正确性
    """
    
    def __init__(
        self,
        llm_client = None,
        max_depth: int = 10,
        generate_tests: bool = True,
    ):
        """
        初始化代码考古学家
        
        Args:
            llm_client: LLM 客户端
            max_depth: 递归包装最大深度
            generate_tests: 是否生成测试用例
        """
        if llm_client is not None:
            self.llm = llm_client
        else:
            self.llm = _get_llm_client()
        self.max_depth = max_depth
        self.generate_tests = generate_tests
        
        # 子模块
        self.excavator = Excavator()
        self.typology = TypologyAnalyzer()
        self.decipher = DecipherEngine(self.llm)
        self.authenticator = Authenticator()
        self.wrapper = RecursiveWrapper(self.llm)
        self.verifier = TestVerifier()
        self.dep_graph = DependencyGraph()
    
    def excavate(self, code_or_path: Union[str, Path]) -> ExcavationResult:
        """
        发掘代码地层
        
        Args:
            code_or_path: 代码字符串或文件路径
            
        Returns:
            发掘结果
        """
        if isinstance(code_or_path, Path) or os.path.exists(code_or_path):
            code = Path(code_or_path).read_text()
            file_path = str(code_or_path)
        else:
            code = code_or_path
            file_path = "<string>"
        
        # 解析 AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"代码语法错误: {e}")
        
        # 1. 发掘 - 识别地层
        excavation_result = self.excavator.excavate(tree, code)
        
        # 2. 类型分类
        for func in excavation_result.functions:
            func.pattern = self.typology.classify_function(func, tree)
        
        for cls in excavation_result.classes:
            cls.layer = self.typology.classify_class(cls, tree)
        
        excavation_result.file_path = file_path
        
        return excavation_result
    
    def decipher_function(
        self,
        code: str,
        context: str = "",
        function_name: str = "",
    ) -> DecipherResult:
        """
        解谜函数意图
        
        Args:
            code: 函数代码
            context: 上下文
            function_name: 函数名
            
        Returns:
            解谜结果
        """
        # AI 理解语义
        semantic_dict = self.llm.understand_function(code, context)
        
        semantic = SemanticUnderstanding(
            purpose=semantic_dict.get("purpose", ""),
            inputs=semantic_dict.get("inputs", []),
            outputs=semantic_dict.get("outputs", ""),
            side_effects=semantic_dict.get("side_effects", []),
            business_context=semantic_dict.get("business_context", ""),
            confidence=semantic_dict.get("confidence", 0.5),
            suggested_name=semantic_dict.get("suggested_name", function_name),
        )
        
        # AI 解释代码
        explained = self.llm.explain_code(code)
        
        return DecipherResult(
            function_name=function_name,
            semantic=semantic,
            original_code=code,
            explained_code=explained,
        )
    
    def authenticate(self, code: str) -> AuthenticationResult:
        """
        鉴真 - 安全审计
        
        Args:
            code: 代码
            
        Returns:
            鉴真结果
        """
        return self.authenticator.analyze(code)
    
    def wrap_recursively(
        self,
        code_or_path: Union[str, Path],
        output_dir: Optional[Path] = None,
    ) -> WrappedCode:
        """
        递归包装代码
        
        Args:
            code_or_path: 代码或文件路径
            output_dir: 输出目录
            
        Returns:
            包装后的代码
        """
        if isinstance(code_or_path, Path) or os.path.exists(code_or_path):
            code = Path(code_or_path).read_text()
            name = Path(code_or_path).stem
        else:
            code = code_or_path
            name = "anonymous"
        
        return self.wrapper.wrap(code, name, output_dir, self.max_depth)
    
    def verify_and_refactor(
        self,
        code_or_path: Union[str, Path],
        generate_report: bool = True,
    ) -> RefactorResult:
        """
        完整重构流程
        
        Args:
            code_or_path: 代码或文件路径
            generate_report: 是否生成报告
            
        Returns:
            重构结果
        """
        if isinstance(code_or_path, Path) or os.path.exists(code_or_path):
            code = Path(code_or_path).read_text()
            file_path = str(code_or_path)
        else:
            code = code_or_path
            file_path = "<string>"
        
        # 1. 发掘
        excavation = self.excavate(code)
        
        # 2. 解谜
        decipher_results = []
        for func in excavation.functions:
            try:
                result = self.decipher_function(
                    self._extract_function_code(code, func),
                    function_name=func.name,
                )
                decipher_results.append(result)
            except Exception:
                continue
        
        # 3. 鉴真
        auth_result = self.authenticate(code)
        
        # 4. 包装
        wrapped = self.wrapper.wrap(code, Path(file_path).stem if file_path != "<string>" else "output")
        
        # 5. 验证
        if wrapped.test_cases:
            verified = self.verifier.verify(wrapped.test_cases)
        else:
            verified = {"passed": True, "details": "No tests to verify"}
        
        # 6. 生成报告
        if generate_report:
            report = self._generate_report(excavation, auth_result, wrapped)
        else:
            report = ""
        
        # 7. 生成依赖图
        dep_graph = self.dep_graph.generate_dot(excavation)
        
        return RefactorResult(
            original_code=code,
            refactored_code=wrapped.wrapped_code,
            report=report,
            test_cases=wrapped.test_cases,
            dependency_graph=dep_graph,
            warnings=auth_result.warnings,
            changes_summary={
                "functions_wrapped": len(wrapped.extracted_functions),
                "test_cases_generated": len(wrapped.test_cases),
                "dead_code_removed": len(excavation.dead_code),
            },
        )
    
    def _extract_function_code(self, code: str, func: FunctionInfo) -> str:
        """提取函数代码"""
        lines = code.split("\n")
        return "\n".join(lines[func.lineno - 1:func.end_lineno])
    
    def _generate_report(
        self,
        excavation: ExcavationResult,
        auth: AuthenticationResult,
        wrapped: WrappedCode,
    ) -> str:
        """生成考古报告"""
        lines = [
            "# 🏛️ 代码考古报告",
            "",
            f"**分析文件**: {excavation.file_path}",
            f"**代码质量评分**: {excavation.overall_quality_score:.1f}/100",
            "",
            "## 📊 地层分析",
        ]
        
        for layer, items in excavation.layers.items():
            if items:
                lines.append(f"### {layer.value.upper()}")
                for item in items:
                    if isinstance(item, FunctionInfo):
                        lines.append(f"- `{item.name}` (行 {item.lineno})")
                    elif isinstance(item, str):
                        lines.append(f"- {item}")
        
        lines.extend([
            "",
            "## 🔍 解谜结果",
        ])
        
        for func in excavation.functions[:5]:  # 只显示前5个
            lines.append(f"### `{func.name}`")
            lines.append(f"- 复杂度: {func.complexity}")
            lines.append(f"- 模式: {func.pattern.value}")
            lines.append(f"- 调用: {', '.join(func.calls) if func.calls else '无'}")
        
        lines.extend([
            "",
            "## 🛡️ 鉴真结果",
            f"- 安全: {'✅' if auth.is_safe else '⚠️'}",
        ])
        
        if auth.warnings:
            lines.append("- 警告:")
            for warning in auth.warnings:
                lines.append(f"  - {warning}")
        
        lines.extend([
            "",
            "## 📦 重构摘要",
            f"- 包装函数: {len(wrapped.extracted_functions)}",
            f"- 生成测试: {len(wrapped.test_cases)}",
            f"- 移除死代码: {len(excavation.dead_code)}",
        ])
        
        return "\n".join(lines)
    
    def analyze_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果字典
        """
        result = self.verify_and_refactor(file_path)
        
        return {
            "file": str(file_path),
            "quality_score": result.refactored_code and 100 or 0,
            "functions": result.changes_summary.get("functions_wrapped", 0),
            "tests": result.changes_summary.get("test_cases_generated", 0),
            "warnings": result.warnings,
            "report": result.report,
        }
    
    def analyze_directory(self, dir_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        分析整个目录
        
        Args:
            dir_path: 目录路径
            
        Returns:
            每个文件的分析结果列表
        """
        path = Path(dir_path)
        if not path.is_dir():
            raise ValueError(f"不是目录: {dir_path}")
        
        results = []
        for py_file in path.rglob("*.py"):
            try:
                result = self.analyze_file(py_file)
                results.append(result)
            except Exception as e:
                results.append({
                    "file": str(py_file),
                    "error": str(e),
                })
        
        return results
