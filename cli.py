#!/usr/bin/env python3
"""
Antishitcode CLI

代码考古学家的命令行界面
"""
import argparse
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core import CodeArchaeologist
from core.types import ExcavationResult
from llm import OpenAIClient


def cmd_analyze(args):
    """分析文件"""
    archaeologist = CodeArchaeologist(
        llm_client=OpenAIClient() if args.llm else None
    )
    
    result = archaeologist.analyze_file(args.file)
    
    print(f"\n{'='*60}")
    print(f"📊 分析结果: {result['file']}")
    print(f"{'='*60}")
    print(f"代码质量评分: {result['quality_score']:.1f}/100")
    print(f"包装函数: {result['functions']}")
    print(f"生成测试: {result['tests']}")
    
    if result['warnings']:
        print(f"\n⚠️ 警告:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    if args.verbose and result.get('report'):
        print(f"\n{'='*60}")
        print("📜 考古报告")
        print(f"{'='*60}")
        print(result['report'])


def cmd_refactor(args):
    """重构文件"""
    archaeologist = CodeArchaeologist(
        llm_client=OpenAIClient() if args.llm else None
    )
    
    result = archaeologist.verify_and_refactor(args.file)
    
    # 输出重构后的代码
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(result.refactored_code)
        print(f"✅ 重构代码已保存到: {output_path}")
    else:
        print(f"\n{'='*60}")
        print("🔧 重构后的代码")
        print(f"{'='*60}")
        print(result.refactored_code)
    
    # 输出报告
    if args.report or args.verbose:
        print(f"\n{'='*60}")
        print("📜 考古报告")
        print(f"{'='*60}")
        print(result.report)
    
    # 输出依赖图
    if args.graph:
        print(f"\n{'='*60}")
        print("🔗 依赖关系图 (DOT 格式)")
        print(f"{'='*60}")
        print(result.dependency_graph)


def cmd_excavate(args):
    """完整发掘流程"""
    archaeologist = CodeArchaeologist(
        llm_client=OpenAIClient() if args.llm else None
    )
    
    result = archaeologist.excavate(args.file)
    
    print(f"\n{'='*60}")
    print(f"🏛️ 发掘结果: {result.file_path}")
    print(f"{'='*60}")
    print(f"代码质量评分: {result.overall_quality_score:.1f}/100")
    print(f"函数数量: {len(result.functions)}")
    print(f"类数量: {len(result.classes)}")
    print(f"死代码: {len(result.dead_code)}")
    
    print(f"\n📊 地层分布:")
    for layer, items in result.layers.items():
        if items:
            print(f"  {layer.value}: {len(items)} 个")
    
    if args.verbose:
        print(f"\n{'='*60}")
        print("🔍 函数详情")
        print(f"{'='*60}")
        for func in result.functions[:10]:
            print(f"  {func.name} (行 {func.lineno}-{func.end_lineno})")
            print(f"    - 复杂度: {func.complexity}")
            print(f"    - 模式: {func.pattern.value}")
            print(f"    - 调用: {', '.join(func.calls[:5]) if func.calls else '无'}")


def cmd_visualize(args):
    """生成依赖图"""
    archaeologist = CodeArchaeologist()
    
    result = archaeologist.excavate(args.file)
    dep_graph = archaeologist.dep_graph
    
    if args.format == "mermaid":
        output = dep_graph.generate_mermaid(result)
    else:
        output = dep_graph.generate_dot(result)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"✅ 依赖图已保存到: {args.output}")
    else:
        print(output)
    
    # 找出关键函数
    critical = dep_graph.find_critical_functions(result)
    if critical:
        print(f"\n🔴 关键函数 (被多次调用):")
        for func in critical[:5]:
            print(f"  - {func}")
    
    # 孤立函数
    isolated = dep_graph.find_isolated_functions(result)
    if isolated:
        print(f"\n🔵 孤立函数 (无依赖关系):")
        for func in isolated[:5]:
            print(f"  - {func}")


def main():
    parser = argparse.ArgumentParser(
        description="🧱 Antishitcode - 代码考古学家",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  antishitcode analyze main.py
  antishitcode refactor main.py -o refactored.py --report
  antishitcode excavate main.py --verbose
  antishitcode visualize main.py -o graph.dot
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析文件")
    analyze_parser.add_argument("file", help="Python 文件路径")
    analyze_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    analyze_parser.add_argument("--llm", action="store_true", help="启用 LLM 分析")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # refactor 命令
    refactor_parser = subparsers.add_parser("refactor", help="重构文件")
    refactor_parser.add_argument("file", help="Python 文件路径")
    refactor_parser.add_argument("-o", "--output", help="输出文件路径")
    refactor_parser.add_argument("--report", action="store_true", help="生成报告")
    refactor_parser.add_argument("--graph", action="store_true", help="显示依赖图")
    refactor_parser.add_argument("--llm", action="store_true", help="启用 LLM 分析")
    refactor_parser.set_defaults(func=cmd_refactor)
    
    # excavate 命令
    excavate_parser = subparsers.add_parser("excavate", help="完整发掘")
    excavate_parser.add_argument("file", help="Python 文件路径")
    excavate_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    excavate_parser.add_argument("--llm", action="store_true", help="启用 LLM 分析")
    excavate_parser.set_defaults(func=cmd_excavate)
    
    # visualize 命令
    visualize_parser = subparsers.add_parser("visualize", help="生成依赖图")
    visualize_parser.add_argument("file", help="Python 文件路径")
    visualize_parser.add_argument("-o", "--output", help="输出文件路径")
    visualize_parser.add_argument("-f", "--format", choices=["dot", "mermaid"], default="dot", help="输出格式")
    visualize_parser.set_defaults(func=cmd_visualize)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        if args.command in ["analyze", "refactor", "excavate"]:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
