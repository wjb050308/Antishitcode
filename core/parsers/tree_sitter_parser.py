# -*- coding: utf-8 -*-
"""
Tree-sitter based parser for multiple languages

Requires tree-sitter and language support:
    pip install tree-sitter-languages

Supports: JavaScript, TypeScript, Java, Go, Rust, C/C++, C#, PHP, Ruby, Swift, Kotlin, Scala
"""

from typing import List, Optional
from . import BaseParser, ParsedFile, ParsedFunction, ParsedClass, Language


class TreeSitterParser(BaseParser):
    """
    Multi-language parser using Tree-sitter
    
    When tree-sitter is not available, this parser will raise ImportError
    """
    
    # Language to tree-sitter grammar name mapping
    LANG_MAP = {
        Language.JAVASCRIPT: "javascript",
        Language.TYPESCRIPT: "typescript",
        Language.JAVA: "java",
        Language.GO: "go",
        Language.RUST: "rust",
        Language.CPP: "cpp",
        Language.C: "c",
        Language.CSHARP: "csharp",
        Language.PHP: "php",
        Language.RUBY: "ruby",
        Language.SWIFT: "swift",
        Language.KOTLIN: "kotlin",
        Language.SCALA: "scala",
    }
    
    def __init__(self, language: Language):
        self.language = language
        self.extensions = self._get_extensions(language)
        self._parser = None
        self._init_parser()
    
    def _get_extensions(self, lang: Language) -> List[str]:
        mapping = {
            Language.JAVASCRIPT: [".js", ".jsx", ".mjs"],
            Language.TYPESCRIPT: [".ts", ".tsx", ".mts"],
            Language.JAVA: [".java"],
            Language.GO: [".go"],
            Language.RUST: [".rs"],
            Language.CPP: [".cpp", ".cc", ".cxx", ".h", ".hpp"],
            Language.C: [".c"],
            Language.CSHARP: [".cs"],
            Language.PHP: [".php"],
            Language.RUBY: [".rb"],
            Language.SWIFT: [".swift"],
            Language.KOTLIN: [".kt", ".kts"],
            Language.SCALA: [".scala"],
        }
        return mapping.get(lang, [])
    
    def _init_parser(self):
        """Initialize tree-sitter parser"""
        try:
            from tree_sitter_languages import get_parser
            lang_name = self.LANG_MAP.get(self.language)
            if lang_name:
                self._parser = get_parser(lang_name)
        except ImportError:
            self._parser = None
    
    @property
    def is_available(self) -> bool:
        return self._parser is not None
    
    def parse(self, code: str, file_path: str = "<string>") -> ParsedFile:
        """Parse code"""
        if not self.is_available:
            raise ImportError(
                "tree-sitter for {} not installed. "
                "Install with: pip install tree-sitter-languages".format(self.language.value)
            )
        
        tree = self._parser.parse(bytes(code, "utf8"))
        
        return ParsedFile(
            language=self.language,
            file_path=file_path,
            functions=self.extract_functions(code),
            classes=self.extract_classes(code),
            imports=self.extract_imports(code),
            raw_code=code,
        )
    
    def extract_functions(self, code: str) -> List[ParsedFunction]:
        """Extract functions"""
        if not self.is_available:
            return []
        
        tree = self._parser.parse(bytes(code, "utf8"))
        functions = []
        func_types = ["function_declaration", "function_definition", 
                      "method_definition", "arrow_function"]
        
        for node in self._find_nodes(tree.root_node, func_types):
            func = self._parse_function_node(node, code)
            if func:
                functions.append(func)
        
        return functions
    
    def extract_classes(self, code: str) -> List[ParsedClass]:
        """Extract classes"""
        if not self.is_available:
            return []
        
        tree = self._parser.parse(bytes(code, "utf8"))
        classes = []
        
        for node in self._find_nodes(tree.root_node, ["class_declaration", "class_specifier"]):
            cls = self._parse_class_node(node, code)
            if cls:
                classes.append(cls)
        
        return classes
    
    def extract_imports(self, code: str) -> List[str]:
        """Extract imports"""
        if not self.is_available:
            return []
        
        imports = []
        tree = self._parser.parse(bytes(code, "utf8"))
        import_types = ["import_statement", "import_declaration", "require"]
        
        for node in self._find_nodes(tree.root_node, import_types):
            imports.append(self._get_node_text(node, code))
        
        return imports
    
    def calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        if not self.is_available:
            return 1
        
        tree = self._parser.parse(bytes(code, "utf8"))
        complexity = 1
        
        control_flow_types = ["if_statement", "for_statement", 
                             "while_statement", "case_clause", "catch_clause"]
        
        for node in self._find_nodes(tree.root_node, control_flow_types):
            complexity += 1
        
        return complexity
    
    def _find_nodes(self, root, types: List[str]) -> List:
        """Find nodes of specified types"""
        results = []
        
        def walk(node):
            if node.type in types:
                results.append(node)
            for child in node.children:
                walk(child)
        
        walk(root)
        return results
    
    def _parse_function_node(self, node, code: str) -> Optional[ParsedFunction]:
        """Parse function node"""
        try:
            name = self._get_identifier(node)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            
            args = self._get_function_args(node)
            complexity = self._calc_complexity(node)
            calls = self._get_function_calls(node)
            
            return ParsedFunction(
                name=name,
                lineno=start,
                end_lineno=end,
                args=args,
                returns=None,
                complexity=complexity,
                calls=calls,
                body=self._get_node_text(node, code),
            )
        except Exception:
            return None
    
    def _parse_class_node(self, node, code: str) -> Optional[ParsedClass]:
        """Parse class node"""
        try:
            name = self._get_identifier(node)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            
            methods = []
            func_types = ["function_declaration", "function_definition", 
                          "method_definition", "arrow_function"]
            
            for child in node.children:
                if child.type in func_types:
                    method = self._parse_function_node(child, code)
                    if method:
                        methods.append(method)
            
            return ParsedClass(
                name=name,
                lineno=start,
                end_lineno=end,
                methods=methods,
                base_classes=[],
            )
        except Exception:
            return None
    
    def _get_identifier(self, node) -> str:
        """Get identifier from node"""
        for child in node.children:
            if child.type in ["identifier", "field_identifier", "type_identifier"]:
                return self._get_node_text(child)
        return "anonymous"
    
    def _get_function_args(self, node) -> List[str]:
        """Get function arguments"""
        args = []
        for child in node.children:
            if child.type in ["formal_parameters", "parameter_list"]:
                for param in child.children:
                    if param.type == "identifier":
                        args.append(self._get_node_text(param))
                    elif param.type == "required_parameter":
                        for p in param.children:
                            if p.type == "identifier":
                                args.append(self._get_node_text(p))
        return args
    
    def _get_function_calls(self, node) -> List[str]:
        """Get function calls"""
        calls = []
        for child in node.children:
            if child.type == "call_expression":
                for c in child.children:
                    if c.type in ["identifier", "field_identifier"]:
                        calls.append(self._get_node_text(c))
        return list(set(calls))
    
    def _calc_complexity(self, node) -> int:
        """Calculate node complexity"""
        complexity = 1
        for child in node.children:
            if child.type in ["if_statement", "for_statement", 
                             "while_statement", "case_clause"]:
                complexity += 1
        return complexity
    
    def _get_node_text(self, node, code: str) -> str:
        """Get text content of node"""
        lines = code.split("\n")
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        
        if start_line == end_line:
            line = lines[start_line]
            start_col = node.start_point[1]
            end_col = node.end_point[1]
            return line[start_col:end_col]
        else:
            result = []
            for i in range(start_line, end_line + 1):
                line = lines[i]
                if i == start_line:
                    result.append(line[node.start_point[1]:])
                elif i == end_line:
                    result.append(line[:node.end_point[1]])
                else:
                    result.append(line)
            return "\n".join(result)
