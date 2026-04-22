"""
解谜引擎 - AI 理解代码意图

考古学原理：破译古代文字，理解原始含义
"""


class DecipherEngine:
    """
    代码解谜引擎
    
    使用 AI 理解屎山代码的真实意图
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def understand(
        self,
        code: str,
        context: str = "",
        function_name: str = "",
    ) -> dict:
        """
        理解代码意图
        
        Args:
            code: 代码
            context: 上下文
            function_name: 函数名
            
        Returns:
            理解结果字典
        """
        return self.llm.understand_function(code, context)
    
    def explain(self, code: str, language: str = "Chinese") -> str:
        """
        解释代码逻辑
        
        Args:
            code: 代码
            language: 输出语言
            
        Returns:
            解释文本
        """
        return self.llm.explain_code(code, language)
    
    def understand_control_flow(self, code: str) -> dict:
        """
        理解控制流
        
        Args:
            code: 代码
            
        Returns:
            控制流描述
        """
        prompt = f"""分析以下代码的控制流，输出每个分支的作用。

```python
{code}
```

输出 JSON 格式：
{{
    "branches": [
        {{"condition": "条件", "action": "执行的动作", "lineno": 行号}},
        ...
    ],
    "loops": [
        {{"type": "for/while", "iterable": "迭代对象", "body": "循环体目的"}},
        ...
    ]
}}
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.llm.chat(messages, temperature=0.3)
        
        import json
        try:
            return json.loads(response.content)
        except:
            return {"error": "无法解析控制流"}
    
    def infer_data_flow(self, code: str) -> dict:
        """
        推断数据流
        
        Args:
            code: 代码
            
        Returns:
            数据流描述
        """
        prompt = f"""分析以下代码的数据流追踪每个变量的变化。

```python
{code}
```

输出每个变量的变化过程
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.llm.chat(messages, temperature=0.3)
        return {"data_flow": response.content}
