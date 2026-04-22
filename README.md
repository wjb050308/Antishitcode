# 🧱 Antishitcode - 赤石科技

> 让 AI 成为你的代码考古学家

用考古学原理理解、测试、重构屎山代码。基于 Chain-of-Thought 推理、递归包装、Halstead 复杂度分析。

---

## 🔮 多语言支持

| 语言 | 状态 | 解析器 | 说明 |
|------|------|--------|------|
| 🐍 Python | ✅ 已支持 | ast | 原生 AST 解析 |
| 📜 JavaScript | 🔜 规划中 | Tree-sitter | 前端/全栈项目 |
| 📘 TypeScript | 🔜 规划中 | Tree-sitter | 类型安全 JS |
| ☕ Java | 🔜 规划中 | Tree-sitter | 企业级项目 |
| 🔷 Go | 🔜 规划中 | Tree-sitter | 云原生/后端 |
| 🦀 Rust | 🔜 规划中 | Tree-sitter | 系统编程 |
| ⚙️ C/C++ | 🔜 规划中 | Tree-sitter | 底层开发 |

**欢迎提交 PR 扩展其他语言！**

---

## ⚡ 快速开始

### 安装

```bash
pip install antishitcode
```

### Python 代码分析

```bash
# 分析单个文件
antishitcode analyze app.py

# 启用深度分析
antishitcode analyze app.py --deep

# 生成测试用例
antishitcode test app.py --generate
```

### API 服务

```bash
# 启动 API 服务器
antishitcode serve

# 分析代码
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo(x): return x * 2"}'
```

---

## 🧱 核心概念

### 考古学原理

| 考古学 | 代码世界 | 功能 |
|--------|----------|------|
| 地层学 | 代码层次 | 分析代码演变历史 |
| 类型学 | 代码模式 | 识别代码分类 |
| 语义学 | 代码意图 | 理解业务含义 |
| 鉴真术 | 代码审计 | 发现隐藏问题 |

---

## ✨ 核心功能

### 📨 代码考古 (Excavator)
- 识别代码地层：核心层、补丁层、技术债层
- 计算圈复杂度、Halstead 指标
- 检测嵌套模式（callback hell, deep nesting）

### 🧩 递归解谜 (Wrapper)
- 自动包装深层嵌套代码
- 生成可测试的包装函数
- 递归处理多层回调

### 🧪 智能测试 (TestGenerator)
- 边界值分析
- 等价类划分
- LLM 生成测试用例

### 📊 复杂度分析 (Enhanced)
- 认知复杂度
- 可维护性指数
- 数据流依赖

### 🔗 依赖图谱 (DependencyGraph)
- 调用关系可视化
- 循环依赖检测
- 关键函数识别

### 🛡️ 安全鉴真 (Authenticator)
- 恶意代码检测
- 死代码发现
- 安全漏洞扫描

---

## 🛠️ 技术栈

- **Python AST** - 代码解析
- **LLM** - OpenAI / DeepSeek / Claude
- **FastAPI** - API 服务
- **Tree-sitter** - 多语言解析（规划中）

---

## 📁 项目结构

```
antishitcode/
├── core/
│   ├── archaeologist.py      # 主类
│   ├── excavator.py           # 地层分析
│   ├── wrapper.py             # 递归包装
│   ├── authenticator.py       # 安全审计
│   ├── verifier.py            # 测试验证
│   ├── dependency_graph.py   # 依赖图
│   ├── prompts_v2.py          # CoT 推理
│   ├── enhancements.py       # 增强算法
│   ├── test_generator.py      # 测试生成
│   ├── parsers/              # 多语言解析器
│   │   ├── __init__.py       # 基类定义
│   │   ├── python_parser.py  # Python 解析器
│   │   ├── universal_parser.py # 统一入口
│   │   └── tree_sitter_parser.py # Tree-sitter 解析器
│   └── graph_enhanced.py      # 增强依赖图
├── api/
│   └── server.py             # FastAPI 服务
├── cli.py                    # 命令行入口
└── requirements.txt
```

---

## 🔌 API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/excavate` | POST | 代码挖掘 |
| `/api/v1/decipher` | POST | AI 解谜 |
| `/api/v1/authenticate` | POST | 安全审计 |
| `/api/v1/refactor` | POST | 代码重构 |
| `/api/v1/analyze` | POST | 综合分析 |
| `/api/v1/batch` | POST | 批量处理 |
| `/api/v1/dependency-graph` | POST | 依赖图 |

---

## 📦 扩展多语言

安装 Tree-sitter 语言支持：

```bash
pip install tree-sitter-languages

# 可选：单独安装特定语言
npm install -g tree-sitter-cli
```

---

## ⚠️ 免责声明

**本项目仅提供思路和方法论，所有代码由 AI 生成。**

- 不对代码分析结果的准确性做保证
- 不对因使用本工具造成的任何损失负责
- 建议结合人工审查使用

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License

---

**用 AI 考古学破解屎山代码，让交接不再痛苦！** 🧱