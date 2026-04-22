"""
Antishitcode - 代码考古学家
让 AI 帮你理解、测试、重构屎山代码
"""

__version__ = "0.1.0"
__author__ = "wjb+openclaw"

from .archaeologist import CodeArchaeologist
from .types import ExcavationResult, DecipherResult, AuthenticationResult, WrappedCode

__all__ = [
    "CodeArchaeologist",
    "ExcavationResult",
    "DecipherResult", 
    "AuthenticationResult",
    "WrappedCode",
]
