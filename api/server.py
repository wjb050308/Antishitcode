"""
Antishitcode API Server

基于 FastAPI 的 RESTful API
"""
import ast
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import tempfile
import uuid

from core import CodeArchaeologist
from core.types import (
    ExcavationResult,
    DecipherResult,
    AuthenticationResult,
    RefactorResult,
    CodeLayer,
)
from llm import OpenAIClient

# ============== API Models ==============

class AnalyzeRequest(BaseModel):
    """分析请求"""
    code: str = Field(..., description="Python 代码")
    use_llm: bool = Field(True, description="是否使用 LLM 分析")
    provider: str = Field("deepseek", description="LLM 提供商")
    model: Optional[str] = Field(None, description="指定模型")

class DecipherRequest(BaseModel):
    """解谜请求"""
    code: str = Field(..., description="函数/模块代码")
    context: str = Field("", description="上下文信息")
    function_name: str = Field("", description="函数名")
    language: str = Field("Chinese", description="解释语言")

class AuthenticateRequest(BaseModel):
    """安全审计请求"""
    code: str = Field(..., description="待审计代码")

class RefactorRequest(BaseModel):
    """重构请求"""
    code: str = Field(..., description="待重构代码")
    module_name: str = Field("anonymous", description="模块名")
    generate_report: bool = Field(True, description="是否生成报告")
    max_depth: int = Field(10, description="递归包装最大深度")

class ExcavateRequest(BaseModel):
    """发掘请求"""
    code: str = Field(..., description="待发掘代码")
    file_path: str = Field("<string>", description="文件路径")

class FullAnalysisRequest(BaseModel):
    """完整分析请求"""
    code: str = Field(..., description="待分析代码")
    provider: str = Field("deepseek", description="LLM 提供商")
    generate_tests: bool = Field(True, description="生成测试用例")
    generate_report: bool = Field(True, description="生成考古报告")

# ============== Response Models ==============

class QualityScore(BaseModel):
    """质量评分"""
    overall: float
    details: Dict[str, float]

class FunctionInfo(BaseModel):
    """函数信息"""
    name: str
    lineno: int
    end_lineno: int
    complexity: int
    layer: str
    pattern: str
    calls: List[str]

class ClassInfo(BaseModel):
    """类信息"""
    name: str
    lineno: int
    end_lineno: int
    methods: List[FunctionInfo]
    coupling_level: str

class ExcavationResponse(BaseModel):
    """发掘结果"""
    file_path: str
    quality_score: QualityScore
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    layers: Dict[str, List[str]]
    dead_code: List[str]

class SemanticUnderstanding(BaseModel):
    """语义理解"""
    purpose: str
    inputs: List[str]
    outputs: Optional[str]
    side_effects: List[str]
    business_context: str
    confidence: float
    suggested_name: str

class DecipherResponse(BaseModel):
    """解谜结果"""
    function_name: str
    semantic: SemanticUnderstanding
    original_code: str
    explained_code: str

class SecurityResult(BaseModel):
    """安全结果"""
    is_malicious: bool
    is_safe: bool
    malicious_patterns: List[str]
    warnings: List[str]
    security_issues: List[str]

class TestCase(BaseModel):
    """测试用例"""
    function_name: str
    inputs: Dict[str, Any]
    expected_output: Any
    description: str
    is_edge_case: bool

class RefactorResponse(BaseModel):
    """重构结果"""
    original_code: str
    refactored_code: str
    report: str
    dependency_graph: str
    test_cases: List[Dict[str, Any]]
    warnings: List[str]
    changes_summary: Dict[str, int]

# ============== API Application ==============

app = FastAPI(
    title="🧱 Antishitcode API",
    description="代码考古学家 API - 让 AI 帮你理解、测试、重构屎山代码",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局考古学家实例
archaeologists: Dict[str, CodeArchaeologist] = {}

def get_archaeologist(provider: str = "deepseek") -> CodeArchaeologist:
    """获取或创建考古学家实例"""
    if provider not in archaeologists:
        llm_client = OpenAIClient(provider=provider)
        archaeologists[provider] = CodeArchaeologist(llm_client=llm_client)
    return archaeologists[provider]

# ============== API Endpoints ==============

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "Antishitcode API",
        "version": "0.1.0",
        "description": "代码考古学家 API",
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

# ----- 分析类 API -----

@app.post("/api/v1/excavate", response_model=ExcavationResponse)
async def excavate_api(request: ExcavateRequest):
    """
    发掘代码地层
    
    识别代码的层次结构（核心层/补丁层/技术债等）
    """
    try:
        archaeologist = get_archaeologist()
        result = archaeologist.excavate(request.code)
        
        return ExcavationResponse(
            file_path=result.file_path or request.file_path,
            quality_score=QualityScore(
                overall=result.overall_quality_score,
                details={
                    "complexity": sum(f.complexity for f in result.functions) / max(len(result.functions), 1),
                    "dead_code_ratio": len(result.dead_code) / max(len(result.functions), 1),
                }
            ),
            functions=[
                FunctionInfo(
                    name=f.name,
                    lineno=f.lineno,
                    end_lineno=f.end_lineno,
                    complexity=f.complexity,
                    layer=f.layer.value,
                    pattern=f.pattern.value,
                    calls=f.calls,
                )
                for f in result.functions
            ],
            classes=[
                ClassInfo(
                    name=c.name,
                    lineno=c.lineno,
                    end_lineno=c.end_lineno,
                    methods=[
                        FunctionInfo(
                            name=m.name,
                            lineno=m.lineno,
                            end_lineno=m.end_lineno,
                            complexity=m.complexity,
                            layer=m.layer.value,
                            pattern=m.pattern.value,
                            calls=m.calls,
                        )
                        for m in c.methods
                    ],
                    coupling_level=c.coupling_level.value,
                )
                for c in result.classes
            ],
            layers={
                layer.value: [str(item) if isinstance(item, str) else getattr(item, 'name', str(item)) 
                              for item in items]
                for layer, items in result.layers.items()
            },
            dead_code=result.dead_code,
        )
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"代码语法错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/decipher", response_model=DecipherResponse)
async def decipher_api(request: DecipherRequest):
    """
    AI 解谜函数意图
    
    使用 LLM 理解代码的真实意图
    """
    try:
        archaeologist = get_archaeologist()
        
        result = archaeologist.decipher_function(
            code=request.code,
            context=request.context,
            function_name=request.function_name,
        )
        
        return DecipherResponse(
            function_name=result.function_name,
            semantic=SemanticUnderstanding(
                purpose=result.semantic.purpose,
                inputs=result.semantic.inputs,
                outputs=result.semantic.outputs,
                side_effects=result.semantic.side_effects,
                business_context=result.semantic.business_context,
                confidence=result.semantic.confidence,
                suggested_name=result.semantic.suggested_name,
            ),
            original_code=result.original_code,
            explained_code=result.explained_code,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/authenticate", response_model=SecurityResult)
async def authenticate_api(request: AuthenticateRequest):
    """
    安全审计
    
    检测恶意代码、死代码、安全问题
    """
    try:
        archaeologist = get_archaeologist()
        result = archaeologist.authenticate(request.code)
        
        return SecurityResult(
            is_malicious=result.is_malicious,
            is_safe=result.is_safe,
            malicious_patterns=result.malicious_patterns,
            warnings=result.warnings,
            security_issues=result.security_issues,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/refactor", response_model=RefactorResponse)
async def refactor_api(request: RefactorRequest):
    """
    递归包装重构
    
    将屎山代码包装成可测试单元
    """
    try:
        archaeologist = get_archaeologist()
        
        result = archaeologist.verify_and_refactor(
            code_or_path=request.code,
            generate_report=request.generate_report,
        )
        
        return RefactorResponse(
            original_code=result.original_code,
            refactored_code=result.refactored_code,
            report=result.report,
            dependency_graph=result.dependency_graph,
            test_cases=[
                {
                    "function_name": tc.function_name,
                    "inputs": tc.inputs,
                    "expected_output": str(tc.expected_output),
                    "description": tc.description,
                    "is_edge_case": tc.is_edge_case,
                }
                for tc in result.test_cases
            ],
            warnings=result.warnings,
            changes_summary=result.changes_summary,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze")
async def analyze_api(request: FullAnalysisRequest):
    """
    完整分析
    
    包含发掘 + 解谜 + 鉴真 + 重构
    """
    try:
        archaeologist = get_archaeologist(request.provider)
        
        result = archaeologist.verify_and_refactor(
            code_or_path=request.code,
            generate_report=request.generate_report,
        )
        
        return {
            "success": True,
            "quality_score": archaeologist.excavate(request.code).overall_quality_score,
            "refactored_code": result.refactored_code,
            "report": result.report,
            "dependency_graph": result.dependency_graph,
            "test_cases_count": len(result.test_cases),
            "warnings": result.warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----- 文件上传 API -----

@app.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    use_llm: bool = Form(True),
    provider: str = Form("deepseek"),
):
    """
    上传文件分析
    
    接收 Python 文件并进行分析
    """
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="只支持 .py 文件")
    
    try:
        content = await file.read()
        code = content.decode("utf-8")
        
        archaeologist = get_archaeologist(provider)
        result = archaeologist.verify_and_refactor(
            code_or_path=code,
            generate_report=True,
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "quality_score": archaeologist.excavate(code).overall_quality_score,
            "refactored_code": result.refactored_code,
            "report": result.report,
            "warnings": result.warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----- 批量处理 API -----

class BatchAnalyzeRequest(BaseModel):
    """批量分析请求"""
    codes: List[Dict[str, str]]  # [{"name": "file1.py", "code": "..."}, ...]
    provider: str = "deepseek"

class BatchAnalyzeResponse(BaseModel):
    """批量分析响应"""
    total: int
    results: List[Dict[str, Any]]

@app.post("/api/v1/batch", response_model=BatchAnalyzeResponse)
async def batch_analyze_api(request: BatchAnalyzeRequest):
    """
    批量分析
    
    一次提交多个代码片段进行分析
    """
    results = []
    
    for item in request.codes:
        try:
            archaeologist = get_archaeologist(request.provider)
            result = archaeologist.excavate(item["code"])
            
            results.append({
                "name": item.get("name", "unknown"),
                "success": True,
                "quality_score": result.overall_quality_score,
                "functions": len(result.functions),
                "classes": len(result.classes),
                "dead_code": len(result.dead_code),
            })
        except Exception as e:
            results.append({
                "name": item.get("name", "unknown"),
                "success": False,
                "error": str(e),
            })
    
    return BatchAnalyzeResponse(
        total=len(request.codes),
        results=results,
    )

# ----- 依赖图 API -----

@app.post("/api/v1/dependency-graph")
async def dependency_graph_api(request: ExcavateRequest):
    """
    生成依赖关系图
    
    返回 DOT 和 Mermaid 格式
    """
    try:
        archaeologist = get_archaeologist()
        result = archaeologist.excavate(request.code)
        
        dot_graph = archaeologist.dep_graph.generate_dot(result)
        mermaid_graph = archaeologist.dep_graph.generate_mermaid(result)
        
        # 关键函数和孤立函数
        critical = archaeologist.dep_graph.find_critical_functions(result)
        isolated = archaeologist.dep_graph.find_isolated_functions(result)
        
        return {
            "dot": dot_graph,
            "mermaid": mermaid_graph,
            "critical_functions": critical,
            "isolated_functions": isolated,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== Main ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
