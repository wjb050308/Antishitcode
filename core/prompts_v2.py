"""
增强的 AI 解谜引擎 - Chain-of-Thought 推理

让 AI 逐步推理，深入理解代码意图
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ReasoningStep(Enum):
    """推理步骤类型"""
    IDENTIFY = "identify"           # 识别
    ANALYZE = "analyze"           # 分析
    INFER = "infer"               # 推断
    VERIFY = "verify"             # 验证
    SYNTHESIZE = "synthesize"     # 综合


@dataclass
class ReasoningChain:
    """推理链"""
    steps: List[Dict[str, str]]   # 每一步的推理
    conclusion: str                 # 最终结论
    confidence: float              # 置信度
    alternative_interpretations: List[str]  # 其他可能的解释


@dataclass
class StepResult:
    """步骤结果"""
    step_type: ReasoningStep
    observation: str        # 观察到什么
    inference: str         # 推断出什么
    evidence: List[str]   # 证据
    confidence: float     # 置信度


class ChainOfThoughtDecipher:
    """
    Chain-of-Thought 解谜引擎
    
    通过多步骤推理深入理解代码
    """
    
    # 预定义的推理提示模板
    REASONING_PROMPTS = {
        ReasoningStep.IDENTIFY: """
## 步骤 1: 识别 (Identify)

**目标**: 从代码中提取关键元素

**任务**: 仔细阅读代码，识别以下元素：

1. **输入**: 函数接收什么参数？参数的类型和用途？
2. **输出**: 函数返回什么？返回值的含义？
3. **变量**: 函数使用了哪些变量？它们的作用是什么？
4. **调用**: 函数调用了哪些其他函数？
5. **控制流**: 函数的执行路径是怎样的？

**输出格式**:
```
观察:
- 输入: ...
- 输出: ...
- 关键变量: [v1, v2, ...]
- 函数调用: [f1, f2, ...]
- 执行路径: ...
```
""",
        
        ReasoningStep.ANALYZE: """
## 步骤 2: 分析 (Analyze)

**目标**: 理解代码的深层逻辑和结构

**任务**: 基于识别出的元素，深入分析：

1. **数据变换**: 输入是如何变成输出的？经历了哪些变换？
2. **条件判断**: 条件分支的逻辑是什么？每条分支的目的是什么？
3. **循环模式**: 循环的目的是什么？迭代的是什么？
4. **异常处理**: 代码如何处理错误和边界情况？
5. **副作用**: 代码是否有副作用（修改全局状态、IO等）？

**输出格式**:
```
分析:
- 数据变换链: ...
- 条件逻辑: ...
- 循环目的: ...
- 错误处理: ...
- 副作用: ...
```
""",
        
        ReasoningStep.INFER: """
## 步骤 3: 推断 (Infer)

**目标**: 推断代码的业务意图和设计意图

**任务**: 基于前两步的分析，推断：

1. **业务目的**: 这段代码想要完成什么业务任务？
2. **设计模式**: 代码使用了什么设计模式或惯用法？
3. **原始作者**: 作者可能是什么样的开发者？水平如何？
4. **历史演变**: 代码可能经历了哪些修改？
5. **上下文**: 这段代码可能用在什么场景中？

**输出格式**:
```
推断:
- 业务目的: ...
- 设计模式: ...
- 作者画像: ...
- 历史演变: [阶段1: ..., 阶段2: ...]
- 可能场景: ...
```
""",
        
        ReasoningStep.VERIFY: """
## 步骤 4: 验证 (Verify)

**目标**: 验证推断的正确性

**任务**: 检查之前的推断是否正确：

1. **一致性检查**: 推断与代码实际行为是否一致？
2. **边界情况**: 代码对边界情况的处理是否支持推断？
3. **矛盾检测**: 是否有矛盾的逻辑？
4. **遗漏检测**: 是否有重要的逻辑被遗漏？
5. **置信度评估**: 综合以上，对推断的置信度是多少？

**输出格式**:
```
验证结果:
- 一致性: [一致/不一致]
- 边界支持: [是/否]
- 矛盾: [有/无]
- 遗漏: [有/无]
- 置信度: 0.0-1.0
- 需要修正的地方: ...
```
""",
        
        ReasoningStep.SYNTHESIZE: """
## 步骤 5: 综合 (Synthesize)

**目标**: 生成最终的语义理解和解释

**任务**: 综合所有推理步骤，生成：

1. **一句话总结**: 用一句话概括代码的功能
2. **详细说明**: 详细的语义描述
3. **建议的函数名**: 更清晰的函数名
4. **重构建议**: 如何让代码更清晰
5. **其他可能的解释**: 如果推断不确定，列出其他可能

**输出格式**:
```json
{
    "summary": "一句话总结",
    "detailed_explanation": "详细说明...",
    "suggested_name": "建议的函数名",
    "refactor_suggestions": ["建议1", "建议2"],
    "alternative_interpretations": ["其他解释1", "其他解释2"],
    "confidence": 0.0-1.0
}
```
""",
    }
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def reason(self, code: str, context: str = "") -> ReasoningChain:
        """
        执行 Chain-of-Thought 推理
        
        Args:
            code: 待分析的代码
            context: 上下文信息
            
        Returns:
            推理链结果
        """
        steps = []
        current_state = {"code": code, "observations": "", "analysis": ""}
        
        # 逐步执行推理
        for step_type in ReasoningStep:
            prompt = self._build_step_prompt(step_type, current_state, context)
            response = self._call_llm(prompt)
            
            step_result = self._parse_step_response(step_type, response)
            steps.append({
                "type": step_type.value,
                "observation": step_result.observation,
                "inference": step_result.inference,
                "evidence": step_result.evidence,
                "confidence": step_result.confidence,
            })
            
            # 更新状态
            current_state["observations"] += step_result.observation + "\n"
            current_state["analysis"] += step_result.inference + "\n"
        
        # 最终综合
        final_prompt = self._build_final_prompt(current_state, context)
        final_response = self._call_llm(final_prompt)
        
        conclusion, confidence, alternatives = self._parse_final_response(final_response)
        
        return ReasoningChain(
            steps=steps,
            conclusion=conclusion,
            confidence=confidence,
            alternative_interpretations=alternatives,
        )
    
    def _build_step_prompt(
        self,
        step_type: ReasoningStep,
        state: Dict,
        context: str,
    ) -> str:
        """构建步骤提示"""
        template = self.REASONING_PROMPTS[step_type]
        
        prompt = f"""你是一位代码考古学家，负责分析以下代码。

## 代码
```{state['code']}```

{context}

{template}

请仔细分析并输出结构化的结果。
"""
        
        return prompt
    
    def _build_final_prompt(self, state: Dict, context: str) -> str:
        """构建最终综合提示"""
        return f"""你是一位代码考古学家。基于之前的分析步骤，综合推理出代码的最终语义理解。

## 代码
```{state['code']}```

## 之前的观察和分析
{state['observations']}

{state['analysis']}

{self.REASONING_PROMPTS[ReasoningStep.SYNTHESIZE]}

请综合所有信息，生成最终的理解结果。
"""
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        messages = [
            {
                "role": "system",
                "content": """你是一位专业的代码考古学家。你擅长通过逐步推理深入理解代码的真正意图。
回答要结构化、清晰、有逻辑性。"""
            },
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat(messages, temperature=0.3)
        return response.content
    
    def _parse_step_response(
        self,
        step_type: ReasoningStep,
        response: str,
    ) -> StepResult:
        """解析步骤响应"""
        # 简化解析，实际应用中可能需要更复杂的解析逻辑
        lines = response.strip().split("\n")
        
        observation = ""
        inference = ""
        evidence = []
        confidence = 0.5
        
        # 简单提取
        current_section = None
        for line in lines:
            line = line.strip()
            if "观察:" in line or "Observation:" in line:
                current_section = "observation"
            elif "推断:" in line or "Inference:" in line or "分析:" in line:
                current_section = "inference"
            elif "证据:" in line or "Evidence:" in line:
                current_section = "evidence"
            elif "置信度:" in line or "Confidence:" in line:
                current_section = "confidence"
            elif current_section == "observation" and line:
                observation += line + "\n"
            elif current_section == "inference" and line:
                inference += line + "\n"
            elif current_section == "evidence" and line:
                evidence.append(line)
            elif current_section == "confidence" and line:
                try:
                    # 尝试提取数字
                    import re
                    match = re.search(r'0?\.\d+|1\.0', line)
                    if match:
                        confidence = float(match.group())
                except:
                    pass
        
        return StepResult(
            step_type=step_type,
            observation=observation.strip(),
            inference=inference.strip(),
            evidence=evidence,
            confidence=confidence,
        )
    
    def _parse_final_response(self, response: str) -> Tuple[str, float, List[str]]:
        """解析最终响应"""
        conclusion = ""
        confidence = 0.5
        alternatives = []
        
        try:
            import json
            
            # 尝试提取 JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            data = json.loads(json_str)
            conclusion = data.get("summary", data.get("detailed_explanation", ""))
            confidence = data.get("confidence", 0.5)
            alternatives = data.get("alternative_interpretations", [])
            
        except (json.JSONDecodeError, IndexError):
            # 降级处理
            conclusion = response.strip()
        
        return conclusion, confidence, alternatives
    
    def quick_understand(self, code: str) -> Dict[str, Any]:
        """
        快速理解（单次调用，但使用优化提示）
        
        Args:
            code: 代码
            
        Returns:
            理解结果字典
        """
        prompt = f"""作为代码考古学家，请深入分析以下代码。

## 代码
```python
{code}
```

## 分析要求

请从以下维度进行分析（不需要逐步推理，但要全面）：

1. **表面功能**: 代码做什么？
2. **深层意图**: 代码真正想完成什么？
3. **实现方式**: 关键算法和数据结构是什么？
4. **质量评估**: 代码有什么问题（可维护性、性能、安全）？
5. **重构建议**: 如何让代码更清晰？

请用中文回答，结构清晰。
"""
        
        messages = [
            {
                "role": "system",
                "content": """你是一位代码考古学家。你能透过混乱的代码表面，理解其真正的意图。"""
            },
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat(messages, temperature=0.3)
        
        return {
            "analysis": response.content,
            "code": code,
            "length": len(code),
        }
