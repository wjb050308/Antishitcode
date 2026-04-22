"""
Antishitcode Prompt Engineering

高级提示工程 - 让 AI 更深入地理解和"解密"代码
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PromptStrategy(Enum):
    """提示策略"""
    SEMANTIC_UNDERSTANDING = "semantic"      # 语义理解
    CONTROL_FLOW = "control_flow"           # 控制流分析
    DATA_FLOW = "data_flow"                 # 数据流分析
    PATTERN_RECOGNITION = "pattern"         # 模式识别
    HISTORICAL_RECONSTRUCTION = "historical" # 历史重建
    SECURITY_AUDIT = "security"             # 安全审计
    DECODING = "decoding"                   # 解码破解


@dataclass
class PromptTemplate:
    """提示模板"""
    strategy: PromptStrategy
    role: str
    task: str
    constraints: List[str]
    output_format: str
    examples: List[str]


# ============== 核心提示库 ==============

class PromptLibrary:
    """
    提示词库
    
    包含各种代码分析和"解密"场景的提示模板
    """
    
    # 角色定义
    ROLES = {
        "archaeologist": """你是一位代码考古学家，精通各种编程语言的演变历史。
你擅长从代码的风格、结构、命名中推断出：
1. 代码的原始编写时间和背景
2. 代码的原始业务意图
3. 代码经历了哪些修改和重构
4. 代码作者的水平和风格
5. 代码存在的问题和潜在风险""",
        
        "translator": """你是一位古文翻译专家，擅长将模糊、混乱的表达翻译成清晰准确的意思。
你对待代码就像对待古代文献：
1. 理解字面背后的真实含义
2. 识别各种隐喻和缩写
3. 还原被压缩的信息
4. 解释专业术语和缩写
5. 给出通俗易懂的解释""",
        
        "detective": """你是一位代码侦探，擅长破解各种代码谜题。
你能够：
1. 从蛛丝马迹中推断代码的真正目的
2. 发现隐藏的执行路径
3. 追踪敏感数据的流向
4. 识别伪装和混淆
5. 还原被加密或编码的信息""",
        
        "engineer": """你是一位资深软件工程师，擅长代码分析和重构。
你能够：
1. 理解复杂代码的业务逻辑
2. 识别代码模式和反模式
3. 设计重构方案
4. 生成测试用例
5. 写出清晰可维护的代码""",
        
        "psychologist": """你是一位 AI 心理分析师，专注于理解 AI 的"思维方式"。
你能够：
1. 分析 AI 在代码中表现出的"思维模式"
2. 识别 AI 的"情绪"和"态度"
3. 理解 AI 的决策逻辑
4. 预测 AI 的"下一步"
5. 诊断 AI 的"心理问题\"""",
    }
    
    # ============== 语义理解提示 ==============
    
    SEMANTIC_UNDERSTANDING = """
## 任务：理解代码的深层语义

你需要深入分析以下代码，理解它的**真正目的**，而不仅仅是字面意思。

### 代码
```{language}
{code}
```

### 分析要求

1. **表面目的**：这段代码表面上在做什么？
2. **深层目的**：这段代码**真正**想要完成什么任务？
3. **业务上下文**：这段代码可能用在什么业务场景中？
4. **设计意图**：如果这是你写的，你会如何设计这个功能？
5. **隐含假设**：代码中隐含了哪些假设？

### 输出格式

```json
{{
    "surface_purpose": "表面目的描述",
    "deep_purpose": "深层目的描述",
    "business_context": "业务上下文",
    "design_intent": "设计意图",
    "implicit_assumptions": ["假设1", "假设2"],
    "confidence": 0.0-1.0,
    "uncertain_aspects": ["不确定的方面"]
}}
```

### 注意事项
- 不要只看表面，要思考"为什么要这样写"
- 考虑代码可能的历史演变
- 识别可能的代码异味和补救措施
"""

    # ============== 控制流解密提示 ==============
    
    CONTROL_FLOW_DECODING = """
## 任务：解密复杂控制流

分析这段代码的控制流，理解它的**真实执行逻辑**。

### 代码
```{language}
{code}
```

### 分析步骤

1. **画出执行路径图**：用文字描述每个分支的执行路径
2. **识别关键节点**：哪些条件判断最关键？
3. **发现隐藏逻辑**：是否有隐藏的执行路径？
4. **理解循环模式**：循环的真正目的是什么？
5. **追踪状态变化**：关键变量的状态如何变化？

### 输出格式

```json
{{
    "execution_paths": [
        {{
            "path_id": 1,
            "condition": "条件描述",
            "actions": ["动作1", "动作2"],
            "result": "执行结果"
        }}
    ],
    "hidden_paths": ["隐藏路径描述"],
    "key_decision_points": ["关键决策点"],
    "state_changes": [
        {{
            "variable": "变量名",
            "changes": ["变化1", "变化2"]
        }}
    ],
    "deobfuscated_logic": "用清晰语言描述的真实逻辑"
}}
```

### 解密技巧
- 如果看到奇怪的变量名，尝试推断它们的真实含义
- 追踪return语句，理解函数的真实输出
- 注意边界条件和异常处理
- 识别递归的真实终止条件
"""

    # ============== 数据流解密提示 ==============
    
    DATA_FLOW_DECODING = """
## 任务：追踪数据流动

分析数据如何在这段代码中流动，找出数据的**完整生命周期**。

### 代码
```{language}
{code}
```

### 分析要求

1. **输入识别**：数据从哪些地方进入？
2. **转换追踪**：数据经过哪些转换？
3. **存储分析**：数据存储在哪里？何时存储？
4. **输出终点**：数据最终流向哪里？
5. **副作用检测**：是否有意外的数据修改？

### 输出格式

```json
{{
    "data_sources": ["数据源1", "数据源2"],
    "transformations": [
        {{
            "step": 1,
            "input": "输入",
            "operation": "操作",
            "output": "输出"
        }}
    ],
    "storage": ["存储点1", "存储点2"],
    "data_sinks": ["终点1", "终点2"],
    "side_effects": ["副作用描述"],
    "data_lifecycle": "用时间线描述数据的完整生命周期"
}}
```

### 注意事项
- 特别注意全局变量和共享状态
- 追踪函数参数和返回值
- 识别数据类型的隐式转换
"""

    # ============== 模式识别提示 ==============
    
    PATTERN_RECOGNITION = """
## 任务：识别代码模式

分析这段代码，识别其中包含的设计模式、反模式和其他代码特征。

### 代码
```{language}
{code}
```

### 识别清单

**设计模式**：
- [ ] Singleton / 单例模式
- [ ] Factory / 工厂模式
- [ ] Observer / 观察者模式
- [ ] Strategy / 策略模式
- [ ] Decorator / 装饰器模式
- [ ] Adapter / 适配器模式
- [ ] Proxy / 代理模式
- [ ] 其他：___________

**反模式**：
- [ ] God Class / 上帝类
- [ ] Magic Numbers / 魔法数字
- [ ] Long Method / 过长方法
- [ ] Deep Nesting / 深层嵌套
- [ ] Spaghetti Code / 意面代码
- [ ] Lava Flow / 熔岩流
- [ ] Shotgun Surgery / 散弹手术
- [ ] 其他：___________

### 输出格式

```json
{{
    "design_patterns": [
        {{
            "pattern": "模式名称",
            "confidence": 0.0-1.0,
            "evidence": "证据",
            "location": "位置"
        }}
    ],
    "anti_patterns": [
        {{
            "pattern": "反模式名称",
            "severity": "high/medium/low",
            "evidence": "证据",
            "location": "位置",
            "refactor_suggestion": "重构建议"
        }}
    ],
    "overall_assessment": "整体评估"
}}
```
"""

    # ============== 历史重建提示 ==============
    
    HISTORICAL_RECONSTRUCTION = """
## 任务：重建代码的历史

根据代码的特征，推断它的**编写历史和演变过程**。

### 代码
```{language}
{code}
```

### 考古分析维度

1. **年代鉴定**：这段代码可能写于什么年代？
2. **作者画像**：作者是什么样的开发者？（水平/风格/习惯）
3. **修改痕迹**：代码经历了哪些修改？
4. **技术债务**：留下了哪些技术债？
5. **历史背景**：代码可能受到什么技术趋势影响？

### 代码特征提取

请分析以下特征：
- 命名风格（驼峰/下划线/拼音/缩写）
- 代码结构（顺序/嵌套/模块化）
- 注释风格（有/无/过时）
- 技术栈痕迹（框架/库/API）
- 格式风格（缩进/空格/换行）

### 输出格式

```json
{{
    "estimated_era": "年代估计",
    "author_profile": {{
        "skill_level": "初/中/高级",
        "style_characteristics": ["特征1", "特征2"],
        "惯用写法": ["写法1", "写法2"]
    }},
    "modification_history": [
        {{
            "layer": "层次",
            "description": "描述",
            "confidence": 0.0-1.0
        }}
    ],
    "technical_debts": [
        {{
            "issue": "问题",
            "severity": "high/medium/low",
            "origin": "起源"
        }}
    ],
    "historical_context": "历史背景推测"
}}
```
"""

    # ============== 安全审计提示 ==============
    
    SECURITY_AUDIT = """
## 任务：安全审计

仔细检查这段代码，识别潜在的安全问题。

### 代码
```{language}
{code}
```

### 安全检查清单

**高危风险**：
- [ ] 命令注入 (subprocess/os.system)
- [ ] 代码注入 (eval/exec)
- [ ] SQL 注入
- [ ] 路径遍历
- [ ] 反序列化漏洞
- [ ] 硬编码凭证
- [ ] 不安全的随机数
- [ ] 敏感信息泄露

**中危风险**：
- [ ] 输入验证不完整
- [ ] 错误处理不当
- [ ] 日志泄露信息
- [ ] 资源未释放
- [ ] 竞态条件

**低危风险**：
- [ ] 调试代码残留
- [ ] 冗余代码
- [ ] 注释中的敏感信息

### 输出格式

```json
{{
    "risk_level": "high/medium/low",
    "vulnerabilities": [
        {{
            "type": "漏洞类型",
            "severity": "critical/high/medium/low",
            "location": "位置",
            "description": "描述",
            "exploit_scenario": "利用场景",
            "remediation": "修复建议"
        }}
    ],
    "compliance_issues": ["合规问题"],
    "overall_assessment": "整体评估"
}}
```
"""

    # ============== 混淆代码解密提示 ==============
    
    OBFUSCATION_DECODING = """
## 任务：解密混淆代码

这是一段被混淆的代码，你的任务是**还原它的真实面目**。

### 代码
```{language}
{code}
```

### 解密策略

1. **变量名还原**：a/b/c → 有意义的名称
2. **函数还原**：func_0x123 → 真实功能
3. **字符串解码**：base64/rot13/其他编码
4. **控制流还原**：还原被扭曲的执行顺序
5. **常量展开**：魔法数字 → 有意义的常量

### 解密步骤

```
第一步：识别混淆类型
- 变量名混淆：单字母/无意义名称
- 字符串加密：编码后的字符串
- 控制流平坦化：switch-case 结构
- API 隐藏：间接调用

第二步：提取线索
- 字符串常量中的关键词
- 注释中的提示
- 代码的结构特征

第三步：逐层还原
- 还原变量名
- 解码字符串
- 还原控制流
- 重构函数逻辑

第四步：验证正确性
- 理解重构后的代码
- 对比原始行为
```

### 输出格式

```json
{{
    "obfuscation_types": ["混淆类型1", "混淆类型2"],
    "decoding_steps": [
        {{
            "step": 1,
            "original": "原始片段",
            "decoded": "解密后",
            "technique": "使用的技术"
        }}
    ],
    "deobfuscated_code": "完整的解密后代码",
    "confidence": 0.0-1.0,
    "remaining_mysteries": ["未解之谜"]
}}
```

### 提示
- 从字符串常量开始，往往能找到线索
- 追踪数据的使用位置
- 注意加密算法可能留下的痕迹
"""


# ============== Prompt Builder ==============

class PromptBuilder:
    """
    提示构建器
    
    动态组合提示模板，生成针对特定代码的分析提示
    """
    
    def __init__(self):
        self.library = PromptLibrary()
    
    def build_semantic_prompt(
        self,
        code: str,
        language: str = "python",
        context: str = "",
    ) -> Tuple[str, Dict]:
        """
        构建语义理解提示
        
        Returns:
            (prompt, metadata)
        """
        prompt = self.library.SEMANTIC_UNDERSTANDING.format(
            language=language,
            code=code,
        )
        
        if context:
            prompt += f"\n\n### 额外上下文\n{context}"
        
        metadata = {
            "strategy": PromptStrategy.SEMANTIC_UNDERSTANDING,
            "role": "archaeologist",
            "language": language,
        }
        
        return prompt, metadata
    
    def build_control_flow_prompt(
        self,
        code: str,
        language: str = "python",
    ) -> Tuple[str, Dict]:
        """构建控制流分析提示"""
        prompt = self.library.CONTROL_FLOW_DECODING.format(
            language=language,
            code=code,
        )
        
        return prompt, {
            "strategy": PromptStrategy.CONTROL_FLOW,
            "role": "detective",
            "language": language,
        }
    
    def build_data_flow_prompt(
        self,
        code: str,
        language: str = "python",
    ) -> Tuple[str, Dict]:
        """构建数据流分析提示"""
        prompt = self.library.DATA_FLOW_DECODING.format(
            language=language,
            code=code,
        )
        
        return prompt, {
            "strategy": PromptStrategy.DATA_FLOW,
            "role": "detective",
            "language": language,
        }
    
    def build_pattern_prompt(
        self,
        code: str,
        language: str = "python",
    ) -> Tuple[str, Dict]:
        """构建模式识别提示"""
        prompt = self.library.PATTERN_RECOGNITION.format(
            language=language,
            code=code,
        )
        
        return prompt, {
            "strategy": PromptStrategy.PATTERN_RECOGNITION,
            "role": "engineer",
            "language": language,
        }
    
    def build_historical_prompt(
        self,
        code: str,
        language: str = "python",
    ) -> Tuple[str, Dict]:
        """构建历史重建提示"""
        prompt = self.library.HISTORICAL_RECONSTRUCTION.format(
            language=language,
            code=code,
        )
        
        return prompt, {
            "strategy": PromptStrategy.HISTORICAL_RECONSTRUCTION,
            "role": "archaeologist",
            "language": language,
        }
    
    def build_security_prompt(
        self,
        code: str,
        language: str = "python",
    ) -> Tuple[str, Dict]:
        """构建安全审计提示"""
        prompt = self.library.SECURITY_AUDIT.format(
            language=language,
            code=code,
        )
        
        return prompt, {
            "strategy": PromptStrategy.SECURITY_AUDIT,
            "role": "detective",
            "language": language,
        }
    
    def build_decoding_prompt(
        self,
        code: str,
        language: str = "python",
        obfuscation_type: Optional[str] = None,
    ) -> Tuple[str, Dict]:
        """
        构建混淆解密提示
        
        Args:
            code: 混淆代码
            language: 编程语言
            obfuscation_type: 已知的混淆类型（可选）
        """
        prompt = self.library.OBFUSCATION_DECODING.format(
            language=language,
            code=code,
        )
        
        if obfuscation_type:
            prompt += f"\n\n已知混淆类型：{obfuscation_type}"
        
        return prompt, {
            "strategy": PromptStrategy.DECODING,
            "role": "detective",
            "language": language,
            "obfuscation_type": obfuscation_type,
        }
    
    def build_comprehensive_prompt(
        self,
        code: str,
        language: str = "python",
        context: str = "",
    ) -> Tuple[str, Dict]:
        """
        构建综合分析提示
        
        组合多个策略的完整分析
        """
        prompts = []
        
        # 1. 语义理解
        semantic, meta1 = self.build_semantic_prompt(code, language, context)
        prompts.append(("语义理解", semantic))
        
        # 2. 控制流
        control, meta2 = self.build_control_flow_prompt(code, language)
        prompts.append(("控制流分析", control))
        
        # 3. 数据流
        data, meta3 = self.build_data_flow_prompt(code, language)
        prompts.append(("数据流分析", data))
        
        # 4. 模式识别
        pattern, meta4 = self.build_pattern_prompt(code, language)
        prompts.append(("模式识别", pattern))
        
        # 5. 历史重建
        historical, meta5 = self.build_historical_prompt(code, language)
        prompts.append(("历史重建", historical))
        
        # 组合
        combined = f"""# 代码综合分析任务

你需要从多个维度分析以下代码。

## 代码
```{language}
{code}
```

{f"## 上下文\n{context}\n" if context else ""}

## 分析维度

对以下每个维度进行深入分析：

### 1. 语义理解
{semantic.split('### 代码')[2].split('### 输出格式')[0]}

### 2. 控制流分析
{control.split('### 代码')[2].split('### 解密技巧')[0]}

### 3. 数据流追踪
{data.split('### 代码')[2].split('### 注意事项')[0]}

### 4. 模式识别
{pattern.split('### 代码')[2].split('### 输出格式')[0]}

### 5. 历史重建
{historical.split('### 代码')[2].split('### 代码特征提取')[0]}

## 输出要求

请以 JSON 格式返回综合分析结果，包含所有维度的分析。
"""
        
        return combined, {
            "strategy": "comprehensive",
            "role": "archaeologist",
            "language": language,
            "dimensions": ["semantic", "control_flow", "data_flow", "pattern", "historical"],
        }


# ============== Prompt Executor ==============

class PromptExecutor:
    """
    提示执行器
    
    封装 LLM 调用，执行提示并解析结果
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.builder = PromptBuilder()
    
    def execute(
        self,
        code: str,
        strategy: PromptStrategy,
        language: str = "python",
        context: str = "",
        **kwargs,
    ) -> Dict:
        """
        执行提示
        
        Args:
            code: 代码
            strategy: 提示策略
            language: 编程语言
            context: 上下文
            **kwargs: 其他参数
            
        Returns:
            解析后的结果字典
        """
        import json
        
        # 构建提示
        if strategy == PromptStrategy.SEMANTIC_UNDERSTANDING:
            prompt, metadata = self.builder.build_semantic_prompt(code, language, context)
        elif strategy == PromptStrategy.CONTROL_FLOW:
            prompt, metadata = self.builder.build_control_flow_prompt(code, language)
        elif strategy == PromptStrategy.DATA_FLOW:
            prompt, metadata = self.builder.build_data_flow_prompt(code, language)
        elif strategy == PromptStrategy.PATTERN_RECOGNITION:
            prompt, metadata = self.builder.build_pattern_prompt(code, language)
        elif strategy == PromptStrategy.HISTORICAL_RECONSTRUCTION:
            prompt, metadata = self.builder.build_historical_prompt(code, language)
        elif strategy == PromptStrategy.SECURITY_AUDIT:
            prompt, metadata = self.builder.build_security_prompt(code, language)
        elif strategy == PromptStrategy.DECODING:
            prompt, metadata = self.builder.build_decoding_prompt(
                code, language, kwargs.get("obfuscation_type")
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # 调用 LLM
        messages = [
            {"role": "system", "content": self.builder.library.ROLES.get(metadata["role"], "")},
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat(messages, temperature=0.3)
        
        # 解析 JSON
        try:
            # 尝试提取 JSON
            content = response.content
            
            # 处理可能的 markdown 代码块
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            result["_metadata"] = metadata
            result["_raw_response"] = response.content
            
            return result
            
        except (json.JSONDecodeError, IndexError) as e:
            # 返回原始内容
            return {
                "error": f"Failed to parse JSON: {e}",
                "raw": response.content,
                "_metadata": metadata,
            }
    
    def execute_comprehensive(self, code: str, language: str = "python") -> Dict:
        """执行综合分析"""
        prompt, metadata = self.builder.build_comprehensive_prompt(code, language)
        
        messages = [
            {"role": "system", "content": self.builder.library.ROLES["archaeologist"]},
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat(messages, temperature=0.3)
        
        import json
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            
            result = json.loads(content.strip())
            result["_metadata"] = metadata
            
            return result
        except:
            return {
                "error": "Failed to parse comprehensive analysis",
                "raw": response.content,
            }
