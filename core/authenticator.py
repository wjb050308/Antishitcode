"""
鉴真模块 - 安全审计

考古学原理：鉴定文物真伪，识别伪造和隐藏
"""
import ast
import re
from typing import List, Set
from .types import AuthenticationResult


class Authenticator:
    """
    代码鉴真器
    
    检测恶意代码、死代码、隐藏逻辑
    """
    
    # 恶意代码模式
    MALICIOUS_PATTERNS = {
        "subprocess_popen": r"subprocess\.Popen",
        "eval_exec": r"\beval\s*\(|\bexec\s*\(",
        "os_system": r"os\.system",
        "os_popen": r"os\.popen",
        "builtins_exec": r"__builtins__.*exec",
        "import_subprocess": r"import\s+subprocess",
        "import_os": r"import\s+os",
        "base64_decode": r"base64\.b64decode",
        "requests_post": r"requests\.post",
        "urllib_request": r"urllib\.request",
        "socket_connection": r"socket\.connect",
        "hidden_file": r"\/\..*|\.bat|\.ps1",
        "password_hardcode": r"password\s*=\s*['\"][^'\"]{8,}['\"]",
        "api_key_hardcode": r"(api_key|apikey|secret)\s*=\s*['\"][^'\"]{16,}['\"]",
    }
    
    # 可疑函数名
    SUSPICIOUS_NAMES = {
        "backdoor", "shell", "exploit", "payload", "hijack",
        "steal", "bypass", "inject", "hook", "patch",
        "crack", "hack", "trojan", "virus", "malware",
    }
    
    # 警告模式
    WARNING_PATTERNS = {
        "print_debug": r"print\s*\(",
        "pass_implementation": r"pass\s*$",
        "todo_comment": r"#\s*TODO|#\s*FIXME|#\s*HACK",
        "broad_exception": r"except\s*:",
        "sleep_instead_of_wait": r"time\.sleep",
    }
    
    def __init__(self):
        self.code = ""
        self.tree = None
    
    def analyze(self, code: str) -> AuthenticationResult:
        """
        安全审计分析
        
        Args:
            code: 代码
            
        Returns:
            鉴真结果
        """
        self.code = code
        
        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            return AuthenticationResult(
                is_malicious=False,
                malicious_patterns=[],
                is_safe=False,
                warnings=["代码语法错误，无法分析"],
                security_issues=["语法错误"],
            )
        
        malicious_patterns = self._detect_malicious()
        security_issues = self._detect_security_issues()
        warnings = self._detect_warnings()
        
        is_malicious = len(malicious_patterns) > 0
        is_safe = not is_malicious and len(security_issues) == 0
        
        return AuthenticationResult(
            is_malicious=is_malicious,
            malicious_patterns=malicious_patterns,
            is_safe=is_safe,
            warnings=warnings,
            security_issues=security_issues,
        )
    
    def _detect_malicious(self) -> List[str]:
        """检测恶意代码模式"""
        findings = []
        
        for name, pattern in self.MALICIOUS_PATTERNS.items():
            if re.search(pattern, self.code):
                findings.append(name)
        
        # 检测可疑函数名
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name.lower()
                if any(susp in func_name for susp in self.SUSPICIOUS_NAMES):
                    findings.append(f"suspicious_function: {node.name}")
        
        return list(set(findings))
    
    def _detect_security_issues(self) -> List[str]:
        """检测安全问题"""
        issues = []
        
        # 检测硬编码密码
        if re.search(r"password\s*=\s*['\"][^'\"]{8,}['\"]", self.code):
            issues.append("发现硬编码密码")
        
        # 检测硬编码 API Key
        if re.search(r"(api_key|apikey|secret)\s*=\s*['\"][^'\"]{16,}['\"]", self.code):
            issues.append("发现硬编码 API Key")
        
        # 检测不安全的随机数
        if "random.random()" in self.code and "password" in self.code.lower():
            issues.append("使用不安全的随机数生成密码")
        
        # 检测明文传输
        if "http://" in self.code and ("password" in self.code or "token" in self.code):
            issues.append("明文 HTTP 传输敏感信息")
        
        return issues
    
    def _detect_warnings(self) -> List[str]:
        """检测警告"""
        warnings = []
        
        # 检测调试代码
        if re.search(r"print\s*\(", self.code):
            # 检查是否在生产代码中
            if "# DEBUG" not in self.code and "#debug" not in self.code.lower():
                warnings.append("发现 print 语句，可能是调试代码")
        
        # 检测 TODO/FIXME
        todos = re.findall(r"#\s*(TODO|FIXME|HACK)", self.code, re.IGNORECASE)
        if todos:
            warnings.append(f"发现 {len(todos)} 处未完成代码标记")
        
        # 检测 broad exception
        if re.search(r"except\s*:\s*$", self.code, re.MULTILINE):
            warnings.append("发现裸露的 except 语句，建议指定异常类型")
        
        # 检测过长的函数
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                length = (node.end_lineno or node.lineno) - node.lineno
                if length > 100:
                    warnings.append(f"函数 {node.name} 过长 ({length} 行)")
        
        return warnings
