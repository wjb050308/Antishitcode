"""
OpenAI 兼容 LLM 客户端
支持 OpenAI / DeepSeek / Claude 等
"""
import os
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    usage: Dict[str, int]
    cost: float


class OpenAIClient:
    """LLM 客户端"""
    
    DEFAULT_MODELS = {
        "openai": "gpt-4",
        "deepseek": "deepseek-chat",
        "claude": "claude-3-sonnet",
        "zhipu": "glm-4",
    }
    
    def __init__(
        self,
        provider: str = "deepseek",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        初始化 LLM 客户端
        
        Args:
            provider: 提供商 (openai/deepseek/claude/zhipu)
            api_key: API Key (会从环境变量读取)
            base_url: 自定义 API 地址
            model: 指定模型
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_env_key()
        self.model = model or self.DEFAULT_MODELS.get(self.provider, "gpt-4")
        
        # 设置 base_url
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = self._get_default_base_url()
        
        self._client = None
    
    def _get_env_key(self) -> str:
        """从环境变量获取 API Key"""
        env_keys = {
            "openai": "OPENAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
        }
        key_name = env_keys.get(self.provider, "OPENAI_API_KEY")
        return os.environ.get(key_name, "")
    
    def _get_default_base_url(self) -> str:
        """获取默认 API 地址"""
        urls = {
            "openai": "https://api.openai.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "claude": "https://api.anthropic.com/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
        }
        return urls.get(self.provider, "https://api.deepseek.com/v1")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        
        if self.provider == "openai" or self.provider == "deepseek":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.provider == "claude":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
        
        return headers
    
    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        发送对话请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            LLMResponse
        """
        import requests
        
        if self.provider == "claude":
            # Claude API 格式
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            endpoint = f"{self.base_url}/messages"
        else:
            # OpenAI 兼容格式
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            endpoint = f"{self.base_url}/chat/completions"
        
        try:
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            
            if self.provider == "claude":
                content = data["content"][0]["text"]
                usage = data.get("usage", {})
            else:
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
            
            # 估算费用 (简化版)
            cost = self._estimate_cost(usage)
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage,
                cost=cost,
            )
            
        except requests.exceptions.RequestException as e:
            raise LLMError(f"API 请求失败: {e}")
    
    def _estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算费用"""
        # 简化估算
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        # DeepSeek 价格 (约)
        price_per_1k_input = 0.001
        price_per_1k_output = 0.002
        
        return (input_tokens * price_per_1k_input + output_tokens * price_per_1k_output) / 1000
    
    def understand_function(self, code: str, context: str = "") -> Dict[str, Any]:
        """
        理解函数意图
        
        Args:
            code: 函数代码
            context: 上下文信息
            
        Returns:
            语义理解结果字典
        """
        prompt = f"""你是代码考古学家，负责分析以下代码的功能和意图。

分析这个函数：
```python
{code}
```

{context}

请用 JSON 格式返回分析结果：
{{
    "purpose": "这个函数做什么",
    "inputs": ["参数1: 含义", "参数2: 含义"],
    "outputs": "返回值含义",
    "side_effects": ["可能的副作用1", "副作用2"],
    "business_context": "推测的业务场景",
    "confidence": 0.85,
    "suggested_name": "建议的更清晰的函数名"
}}
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.3)
        
        try:
            # 尝试解析 JSON
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # 如果不是 JSON，返回原文
            return {
                "purpose": response.content,
                "inputs": [],
                "outputs": None,
                "side_effects": [],
                "business_context": "",
                "confidence": 0.5,
                "suggested_name": "",
            }
    
    def explain_code(self, code: str, language: str = "Chinese") -> str:
        """
        解释代码逻辑
        
        Args:
            code: 代码
            language: 输出语言
            
        Returns:
            解释文本
        """
        prompt = f"""作为代码考古学家，请解释以下代码的实现逻辑。
用{language}回答，要清晰易懂。

```python
{code}
```

请逐步解释：
1. 这个函数/模块的总体目的
2. 核心算法或逻辑流程
3. 关键变量和它们的作用
4. 可能的边界情况
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.3)
        return response.content
    
    def generate_test_cases(self, code: str, num_cases: int = 5) -> str:
        """
        生成测试用例
        
        Args:
            code: 函数代码
            num_cases: 生成数量
            
        Returns:
            测试代码字符串
        """
        prompt = f"""为以下函数生成 {num_cases} 个测试用例。
返回 pytest 格式的测试代码。

```python
{code}
```

要求：
1. 覆盖正常输入
2. 覆盖边界情况
3. 包含参数说明
4. 直接可以运行
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.3)
        return response.content
    
    def suggest_refactor(self, code: str) -> str:
        """
        建议重构方案
        
        Args:
            code: 代码
            
        Returns:
            重构建议
        """
        prompt = f"""作为代码考古学家，请分析以下代码并给出重构建议。

```python
{code}
```

请分析：
1. 代码存在的问题
2. 重构的具体步骤
3. 重构后的代码
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        return response.content


class LLMError(Exception):
    """LLM 错误"""
    pass


# 全局默认客户端
_default_client: Optional[OpenAIClient] = None


def get_default_client() -> OpenAIClient:
    """获取默认 LLM 客户端"""
    global _default_client
    if _default_client is None:
        _default_client = OpenAIClient()
    return _default_client


def set_default_client(client: OpenAIClient) -> None:
    """设置默认 LLM 客户端"""
    global _default_client
    _default_client = client
