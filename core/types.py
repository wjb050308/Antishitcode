"""
数据类型定义
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class CodeLayer(Enum):
    """代码地层类型"""
    CORE = "core"           # 核心业务逻辑
    FEATURE = "feature"     # 功能层
    PATCH = "patch"        # 补丁层
    DEBT = "debt"          # 技术债
    DEAD = "dead"          # 死代码


class CodePattern(Enum):
    """代码模式类型"""
    GOOD = "good"                    # 良好模式
    DESIGN_PATTERN = "design"         # 设计模式
    ANTI_PATTERN = "anti"            # 反模式
    SHIT_CODE = "shit"               # 屎山代码
    DEAD_CODE = "dead"               # 死代码
    OBFUSCATED = "obfuscated"        # 混淆代码


class CouplingLevel(Enum):
    """耦合度等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NestingPattern(Enum):
    """嵌套模式"""
    NORMAL = "normal"
    DEEP_NESTING = "deep_nesting"     # 深层嵌套
    CALLBACK_HELL = "callback_hell"  # 回调地狱
    CONDITIONAL_CHAIN = "conditional_chain"  # 条件链


class CodeQuality(Enum):
    """代码质量等级"""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"            # 70-89
    FAIR = "fair"            # 50-69
    POOR = "poor"            # 30-49
    CRITICAL = "critical"    # 0-29


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    lineno: int
    end_lineno: int
    args: List[str]
    returns: Optional[str]
    complexity: int
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)
    layer: CodeLayer = CodeLayer.CORE
    pattern: CodePattern = CodePattern.SHIT_CODE
    params: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    lineno: int
    end_lineno: int
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    layer: CodeLayer = CodeLayer.CORE
    coupling_level: CouplingLevel = CouplingLevel.MEDIUM


@dataclass
class SemanticUnderstanding:
    """AI 语义理解结果"""
    purpose: str                          # 函数目的
    inputs: List[str]                    # 输入参数说明
    outputs: Optional[str]               # 输出说明
    side_effects: List[str]              # 副作用
    business_context: str                # 业务上下文
    confidence: float                   # 置信度 0-1
    suggested_name: str                 # 建议的命名


@dataclass
class TestCase:
    """测试用例"""
    function_name: str
    inputs: Dict[str, Any]
    expected_output: Any
    description: str
    is_edge_case: bool = False


@dataclass
class ExcavationResult:
    """发掘结果"""
    file_path: str
    layers: Dict[CodeLayer, List[Any]] = field(default_factory=dict)
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    dead_code: List[str] = field(default_factory=list)
    overall_quality_score: float = 0.0


@dataclass
class DecipherResult:
    """解谜结果"""
    function_name: str
    semantic: SemanticUnderstanding
    original_code: str
    explained_code: str                   # AI 解释后的代码


@dataclass
class AuthenticationResult:
    """鉴真结果"""
    is_malicious: bool
    is_safe: bool
    malicious_patterns: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    risk_level: str = "medium"           # low, medium, high, critical


@dataclass
class WrappedCode:
    """包装后的代码"""
    original_name: str
    wrapped_code: str
    extracted_functions: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    test_cases: List[TestCase] = field(default_factory=list)


@dataclass
class RefactorResult:
    """重构结果"""
    original_code: str
    refactored_code: str
    report: str                           # 考古报告
    dependency_graph: str                 # 依赖图（DOT格式）
    test_cases: List[TestCase] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    changes_summary: Dict[str, int] = field(default_factory=dict)