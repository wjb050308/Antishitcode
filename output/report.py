"""
报告生成器
"""
from typing import Dict, Any
from pathlib import Path


class ReportGenerator:
    """
    考古报告生成器
    """
    
    def __init__(self, template: str = "markdown"):
        self.template = template
    
    def generate(
        self,
        excavation_result,
        auth_result,
        refactor_result,
    ) -> str:
        """
        生成完整报告
        
        Args:
            excavation_result: 发掘结果
            auth_result: 鉴真结果
            refactor_result: 重构结果
            
        Returns:
            报告字符串
        """
        if self.template == "markdown":
            return self._generate_markdown(
                excavation_result,
                auth_result,
                refactor_result,
            )
        elif self.template == "html":
            return self._generate_html(
                excavation_result,
                auth_result,
                refactor_result,
            )
        else:
            return self._generate_text(
                excavation_result,
                auth_result,
                refactor_result,
            )
    
    def _generate_markdown(
        self,
        excavation_result,
        auth_result,
        refactor_result,
    ) -> str:
        """生成 Markdown 报告"""
        lines = [
            "# 🏛️ 代码考古报告",
            "",
            f"**分析文件**: {excavation_result.file_path}",
            f"**生成时间**: {self._get_timestamp()}",
            "",
            "---",
            "",
            "## 📊 概览",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 代码质量评分 | {excavation_result.overall_quality_score:.1f}/100 |",
            f"| 函数数量 | {len(excavation_result.functions)} |",
            f"| 类数量 | {len(excavation_result.classes)} |",
            f"| 死代码 | {len(excavation_result.dead_code)} |",
            f"| 安全状态 | {'✅ 安全' if auth_result.is_safe else '⚠️ 存在风险'} |",
            "",
            "---",
            "",
            "## 📜 地层分析",
        ]
        
        for layer, items in excavation_result.layers.items():
            if items:
                lines.append(f"\n### {layer.value.upper()}")
                for item in items:
                    if hasattr(item, 'name'):
                        lines.append(f"- `{item.name}` (行 {item.lineno})")
                    elif isinstance(item, str):
                        lines.append(f"- {item}")
        
        if auth_result.warnings:
            lines.extend([
                "",
                "---",
                "",
                "## ⚠️ 警告",
            ])
            for warning in auth_result.warnings:
                lines.append(f"- {warning}")
        
        if auth_result.security_issues:
            lines.extend([
                "",
                "---",
                "",
                "## 🔒 安全问题",
            ])
            for issue in auth_result.security_issues:
                lines.append(f"- {issue}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 📦 重构摘要",
            "",
            f"- 包装函数: {refactor_result.changes_summary.get('functions_wrapped', 0)}",
            f"- 生成测试: {refactor_result.changes_summary.get('test_cases_generated', 0)}",
            f"- 移除死代码: {refactor_result.changes_summary.get('dead_code_removed', 0)}",
        ])
        
        return "\n".join(lines)
    
    def _generate_html(
        self,
        excavation_result,
        auth_result,
        refactor_result,
    ) -> str:
        """生成 HTML 报告"""
        md = self._generate_markdown(
            excavation_result,
            auth_result,
            refactor_result,
        )
        
        # 简单的 Markdown -> HTML 转换
        html = md.replace("# ", "<h1>").replace("## ", "<h2>").replace("### ", "<h3>")
        html = html.replace("**", "<strong>").replace("`", "<code>")
        html = html.replace("\n\n", "</p><p>")
        html = f"<html><body><p>{html}</p></body></html>"
        
        return html
    
    def _generate_text(
        self,
        excavation_result,
        auth_result,
        refactor_result,
    ) -> str:
        """生成纯文本报告"""
        return self._generate_markdown(
            excavation_result,
            auth_result,
            refactor_result,
        )
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save(self, content: str, output_path: Path) -> None:
        """保存报告到文件"""
        output_path.write_text(content)
