"""
Python 解析器

使用 Python AST 解析 Python 代码
"""
import ast
from typing import List, Optional
from . import BaseParser, ParsedFile, ParsedFunction, ParsedClass, Language


class PythonParser(BaseParser):
    """Python 代码解析器"""
    
    language = Language.PYTHON
    extensions = ['.py', '.pyw']
    
    def parse(self, code: str, file_path: str = "<string>") -> ParsedFile:
        """
        解析 Python 代码
        
        Args:
            code: Python 代码
            file_path: 文件路径
            
        Returns:
            ParsedFile
        """
        tree = ast.parse(code)
        
        return ParsedFile(
            language=self.language,
            file_path=file_path,
            functions=self.extract_functions(code),
            classes=self.extract_classes(code),
            imports=self.extract_imports(code),
            raw_code=code,
        )
    
    def extract_functions(self, code: str) -> List[ParsedFunction]:
        """提取所有函数"""
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = self._parse_function(node, code)
                functions.append(func)
        
        return functions
    
    def extract_classes(self, code: str) -> List[ParsedClass]:
        """提取所有类"""
        tree = ast.parse(code)
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls = self._parse_class(node, code)
                classes.append(cls)
        
        return classes
    
    def extract_imports(self, code: str) -> List[str]:
        """提取导入语句"""
        tree = ast.parse(code)
        imports = []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(self._format_import(node))
        
        return imports
    
    def calculate_complexity(self, code: str) -> int:
        """计算圈复杂度"""
        tree = ast.parse(code)
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _parse_function(self, node, code: str) -> ParsedFunction:
        """解析单个函数"""
        # 提取参数
        args = [arg.arg for arg in node.args.args]
        
        # 提取调用
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        # 计算复杂度
        complexity = self._calc_function_complexity(node)
        
        # 提取返回类型
        returns = self._get_return_type(node)
        
        # 获取函数体代码
        body = self.get_code_slice(code, node.lineno, node.end_lineno)
        
        return ParsedFunction(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            args=args,
            returns=returns,
            complexity=complexity,
            calls=list(set(calls)),
            body=body,
        )
    
    def _parse_class(self, node: ast.ClassDef, code: str) -> ParsedClass:
        """解析单个类"""
        methods = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith('_') or item.name in ['__init__', '__str__']:
                    methods.append(self._parse_function(item, code))
        
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._format_attribute(base))
        
        return ParsedClass(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            methods=methods,
            base_classes=base_classes,
        )
    
    def _format_import(self, node) -> str:
        """格式化导入语句"""
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            return f"import {', '.join(names)}"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            names = [alias.name for alias in node.names]
            return f"from {module} import {', '.join(names)}"
        return ''
    
    def _get_return_type(self, node) -> Optional[str]:
        """获取返回类型"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                return self._get_type_hint(child.value)
        return None
    
    def _get_type_hint(self, node) -> str:
        """从节点获取类型提示"""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return 'unknown'
    
    def _calc_function_complexity(self, node) -> int:
        """计算函数复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _format_attribute(self, node: ast.Attribute) -> str:
        """格式化属性访问"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
