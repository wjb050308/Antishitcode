"""
统一解析器接口

自动检测语言并分派到对应解析器
"""
import os
from pathlib import Path
from typing import Dict, Optional, Union

from . import Language, ParsedFile, BaseParser
from .python_parser import PythonParser

# 尝试导入 Tree-sitter 解析器（可选）
try:
    from .tree_sitter_parser import TreeSitterParser
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False
    TreeSitterParser = None


class UniversalParser:
    """
    统一解析器
    
    自动检测语言，支持：
    - Python: 使用原生 ast
    - 其他语言: 使用 Tree-sitter（如果可用）
    """
    
    # 语言到解析器的映射
    _parsers: Dict[Language, BaseParser] = {
        Language.PYTHON: PythonParser(),
    }
    
    # 文件扩展名到语言的映射
    EXTENSION_MAP = {
        '.py': Language.PYTHON,
        '.pyw': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.jsx': Language.JAVASCRIPT,
        '.ts': Language.TYPESCRIPT,
        '.tsx': Language.TYPESCRIPT,
        '.java': Language.JAVA,
        '.go': Language.GO,
        '.rs': Language.RUST,
        '.c': Language.C,
        '.cpp': Language.CPP,
        '.cc': Language.CPP,
        '.cxx': Language.CPP,
        '.h': Language.CPP,
        '.hpp': Language.CPP,
        '.cs': Language.CSHARP,
        '.php': Language.PHP,
        '.rb': Language.RUBY,
        '.swift': Language.SWIFT,
        '.kt': Language.KOTLIN,
        '.scala': Language.SCALA,
    }
    
    def __init__(self, use_tree_sitter: bool = True):
        """
        初始化统一解析器
        
        Args:
            use_tree_sitter: 是否使用 Tree-sitter（如果可用）
        """
        self.use_tree_sitter = use_tree_sitter and HAS_TREE_SITTER
        
        if self.use_tree_sitter and TreeSitterParser:
            # 注册 Tree-sitter 支持的语言
            for lang in [
                Language.JAVASCRIPT,
                Language.TYPESCRIPT,
                Language.JAVA,
                Language.GO,
                Language.RUST,
                Language.CPP,
                Language.CSHARP,
                Language.PHP,
                Language.RUBY,
                Language.SWIFT,
                Language.KOTLIN,
                Language.SCALA,
            ]:
                self._parsers[lang] = TreeSitterParser(lang)
    
    def parse(self, code: str, file_path: str = "<string>") -> ParsedFile:
        """
        解析代码
        
        Args:
            code: 代码字符串
            file_path: 文件路径（用于检测语言）<string>
            
        Returns:
            ParsedFile
        """
        language = self.detect_language(file_path, code)
        parser = self.get_parser(language)
        
        if parser:
            return parser.parse(code, file_path)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def detect_language(self, file_path: str = "", code: str = "") -> Language:
        """
        检测编程语言
        
        Args:
            file_path: 文件路径
            code: 代码内容
            
        Returns:
            Language
        """
        # 1. 通过文件扩展名检测
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext in self.EXTENSION_MAP:
                return self.EXTENSION_MAP[ext]
        
        # 2. 通过代码内容检测（shebang）
        if code:
            first_line = code.strip().split('\n')[0]
            if '#!' in first_line:
                if 'python' in first_line.lower():
                    return Language.PYTHON
                elif 'node' in first_line.lower():
                    return Language.JAVASCRIPT
                elif 'ruby' in first_line.lower():
                    return Language.RUBY
            
            # 3. 通过代码特征检测
            if self._looks_like_python(code):
                return Language.PYTHON
            elif self._looks_like_javascript(code):
                return Language.JAVASCRIPT
            elif self._looks_like_java(code):
                return Language.JAVA
            elif self._looks_like_go(code):
                return Language.GO
        
        # 默认返回 Python
        return Language.PYTHON
    
    def get_parser(self, language: Language) -> Optional[BaseParser]:
        """获取对应语言的解析器"""
        return self._parsers.get(language)
    
    def is_supported(self, file_path: str = "", code: str = "") -> bool:
        """检查是否支持该语言"""
        lang = self.detect_language(file_path, code)
        return lang in self._parsers
    
    def _looks_like_python(self, code: str) -> bool:
        """检测是否像 Python 代码"""
        indicators = [
            'import ',
            'from ',
            'def ',
            'class ',
            'if __name__',
            'print(',
            'self.',
            '    ',  # 缩进
        ]
        return sum(1 for i in indicators if i in code) >= 2
    
    def _looks_like_javascript(self, code: str) -> bool:
        """检测是否像 JavaScript 代码"""
        indicators = [
            'const ',
            'let ',
            'var ',
            'function ',
            '=> {',
            'require(',
            'import ',
            'export ',
            'console.log',
            'undefined',
        ]
        return sum(1 for i in indicators if i in code) >= 2
    
    def _looks_like_java(self, code: str) -> bool:
        """检测是否像 Java 代码"""
        indicators = [
            'public class',
            'private ',
            'protected ',
            'System.out.println',
            'void main',
            'import java.',
            'public static void',
            '@Override',
        ]
        return sum(1 for i in indicators if i in code) >= 2
    
    def _looks_like_go(self, code: str) -> bool:
        """检测是否像 Go 代码"""
        indicators = [
            'package ',
            'func ',
            'import (',
            'import "',
            'fmt.',
            'go func',
            ':= ',
            'nil',
        ]
        return sum(1 for i in indicators if i in code) >= 2


class LanguageRegistry:
    """
    语言注册表
    
    用于注册新的语言解析器
    """
    
    _parsers: Dict[Language, type] = {
        Language.PYTHON: PythonParser,
    }
    
    @classmethod
    def register(cls, language: Language, parser_class: type):
        """注册解析器"""
        if not issubclass(parser_class, BaseParser):
            raise ValueError(f"{parser_class} must be a subclass of BaseParser")
        cls._parsers[language] = parser_class
    
    @classmethod
    def get_parser_class(cls, language: Language) -> Optional[type]:
        """获取解析器类"""
        return cls._parsers.get(language)
    
    @classmethod
    def supported_languages(cls) -> list:
        """列出支持的语言"""
        return list(cls._parsers.keys())
