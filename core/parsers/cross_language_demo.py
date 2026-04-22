"""
多语言分析演示

展示如何使用 UniversalParser 分析不同语言的代码
"""

# 示例代码片段
PYTHON_CODE = '''
def calculate(x, y):
    result = 0
    if x > 0:
        for i in range(y):
            if i % 2 == 0:
                result += i * 2
            else:
                result -= i
    return result

class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b
'''

JAVASCRIPT_CODE = '''
function calculate(x, y) {
    let result = 0;
    if (x > 0) {
        for (let i = 0; i < y; i++) {
            if (i % 2 === 0) {
                result += i * 2;
            } else {
                result -= i;
            }
        }
    }
    return result;
}

class MathUtils {
    static add(a, b) {
        return a + b;
    }
}
'''

JAVA_CODE = '''
public class Calculator {
    public int calculate(int x, int y) {
        int result = 0;
        if (x > 0) {
            for (int i = 0; i < y; i++) {
                if (i % 2 == 0) {
                    result += i * 2;
                } else {
                    result -= i;
            }
        }
        return result;
    }
    
    public static int add(int a, int b) {
        return a + b;
    }
}
'''

GO_CODE = '''
func calculate(x, y int) int {
    result := 0
    if x > 0 {
        for i := 0; i < y; i++ {
            if i%2 == 0 {
                result += i * 2
            } else {
                result -= i
            }
        }
    }
    return result
}

func add(a, b int) int {
    return a + b
}
'''


def demo_universal_parser():
    """演示统一解析器"""
    print("=" * 60)
    print("多语言解析器演示")
    print("=" * 60)
    
    try:
        from core.parsers import UniversalParser, Language
        
        parser = UniversalParser(use_tree_sitter=False)
        
        print("\n1️⃣ Python 代码分析")
        print("-" * 40)
        result = parser.parse(PYTHON_CODE, "demo.py")
        print(f"   语言: {result.language.value}")
        print(f"   函数数: {len(result.functions)}")
        print(f"   类数: {len(result.classes)}")
        for func in result.functions[:3]:
            print(f"   - {func.name}({', '.join(func.args)})")
        
        print("\n2️⃣ JavaScript 代码分析")
        print("-" * 40)
        result = parser.parse(JAVASCRIPT_CODE, "demo.js")
        print(f"   语言: {result.language.value}")
        print(f"   函数数: {len(result.functions)}")
        print(f"   类数: {len(result.classes)}")
        
        print("\n3️⃣ Java 代码分析")
        print("-" * 40)
        result = parser.parse(JAVA_CODE, "demo.java")
        print(f"   语言: {result.language.value}")
        print(f"   函数数: {len(result.functions)}")
        print(f"   类数: {len(result.classes)}")
        
        print("\n4️⃣ Go 代码分析")
        print("-" * 40)
        result = parser.parse(GO_CODE, "demo.go")
        print(f"   语言: {result.language.value}")
        print(f"   函数数: {len(result.functions)}")
        print(f"   类数: {len(result.classes)}")
        
        print("\n5️⃣ 语言自动检测")
        print("-" * 40)
        tests = [
            ("print('hello')", "<unknown>"),
            ("def foo(): pass", "<unknown>"),
            ("const x = 1", "<unknown>"),
            ("function foo() {}", "<unknown>"),
            ("public class A {}", "<unknown>"),
        ]
        for code, _ in tests:
            lang = parser.detect_language("", code)
            print(f"   '{code[:20]}...' -> {lang.value}")
        
    except ImportError as e:
        print(f"\n⚠️ 需要安装额外依赖: {e}")
        print("当前只支持 Python")


def demo_parser_registry():
    """演示语言注册表"""
    print("\n" + "=" * 60)
    print("语言注册表")
    print("=" * 60)
    
    from core.parsers import LanguageRegistry
    
    print("\n已支持的语言:")
    for lang in LanguageRegistry.supported_languages():
        print(f"   ✅ {lang.value}")
    
    print("\n规划支持的语言:")
    future_langs = [
        Language.JAVASCRIPT,
        Language.TYPESCRIPT,
        Language.JAVA,
        Language.GO,
        Language.RUST,
    ]
    for lang in future_langs:
        if lang not in LanguageRegistry.supported_languages():
            print(f"   🔜 {lang.value}")


if __name__ == "__main__":
    demo_universal_parser()
    demo_parser_registry()
