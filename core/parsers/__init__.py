"""
Antishitcode 多语言解析器架构

提供统一的接口支持多种编程语言
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class Language(Enum):
    """支持的语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"


@dataclass
class ParsedFunction:
    """解析后的函数信息"""
    name: str
    lineno: int
    end_lineno: int
    args: List[str]
    returns: Optional[str]
    complexity: int
    calls: List[str]
    body: str  # 原始代码片段


@dataclass
class ParsedClass:
    """解析后的类信息"""
    name: str
    lineno: int
    end_lineno: int
    methods: List[ParsedFunction]
    base_classes: List[str]


@dataclass
class ParsedFile:
    """解析后的文件信息"""
    language: Language
    file_path: str
    functions: List[ParsedFunction]
    classes: List[ParsedClass]
    imports: List[str]
    raw_code: str


class BaseParser(ABC):
    """解析器基类"""
    
    language: Language
    extensions: List[str]  # 文件扩展名
    
    @abstractmethod
    def parse(self, code: str, file_path: str = "<string>") -> ParsedFile:
        """解析代码"""
        pass
    
    @abstractmethod
    def extract_functions(self, code: str) -> List[ParsedFunction]:
        """提取函数"""
        pass
    
    @abstractmethod
    def extract_classes(self, code: str) -> List[ParsedClass]:
        """提取类"""
        pass
    
    @abstractmethod
    def extract_imports(self, code: str) -> List[str]:
        """提取导入语句"""
        pass
    
    @abstractmethod
    def calculate_complexity(self, code: str) -> int:
        """计算复杂度"""
        pass
    
    def get_code_slice(self, code: str, start: int, end: int) -> str:
        """提取代码片段"""
        lines = code.split('\n')
        return '\n'.join(lines[start-1:end])


# 导出
from .python_parser import PythonParser
from .universal_parser import UniversalParser, LanguageRegistry
from .tree_sitter_parser import TreeSitterParser

__all__ = [
    "Language",
    "ParsedFunction",
    "ParsedClass", 
    "ParsedFile",
    "BaseParser",
    "PythonParser",
    "UniversalParser",
    "LanguageRegistry",
    "TreeSitterParser",
]
