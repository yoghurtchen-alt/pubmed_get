# PubMed 文献自动检索与研究报告生成工具

从 PubMed 批量检索医学文献，自动生成 Word 研究报告和 Excel 文献汇总表，支持 LLM 智能分析综述。

> **分支说明**：
> - `master` — Web 界面版本（Flask）
> - `api` — AI Agent 版本（CLI + MCP Server，无 Web 依赖）

## 功能特性

- **批量文献检索** - 支持 PubMed 高级检索语法，可限制年份、排序方式
- **自动信息提取** - 获取标题、作者、摘要、期刊、DOI、MeSH 主题词等
- **报告自动生成** - Word 研究报告 + Excel 文献汇总表
- **文本分析** - 研究主题提取、趋势分析、知识缺口识别
- **LLM 智能综述** - 接入 DeepSeek/OpenAI API 生成文献综述、研究总结、关键发现、临床意义分析
- **CLI + JSON 输出** - 适合 AI Agent 调用
- **MCP Server** - 支持 Claude/Hermes/OpenClaw 等通过 MCP 协议直接调用

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置（可选）

编辑 `config.py`，填入你的邮箱：

```python
NCBI_EMAIL = "your_email@example.com"
```

### 3. 运行

**命令行模式：**

```bash
# 基本检索（人类可读输出）
python main.py -q "diabetes treatment" -n 50

# JSON 输出（适合 AI Agent 解析）
python main.py -q "diabetes treatment" -n 50 --json

# 一站式全流程（检索+分析+LLM综述+报告）
python main.py -q "diabetes" -n 20 --json --with-analysis --api-key YOUR_KEY

# 仅检索
python main.py -q "cancer" --json --mode search

# 仅分析（从 JSON 文件读取）
python main.py --json --mode analyze --input results.json

# 演示模式（无需网络）
python main.py --demo -q "diabetes" --json
```

**MCP Server 模式：**

```bash
# 启动 MCP Server
python mcp_server.py
```

在 Claude Desktop / Cursor 等工具中配置：

```json
{
    "mcpServers": {
        "pubmed": {
            "command": "python",
            "args": ["path/to/pubmed_get/mcp_server.py"],
            "env": {
                "DEEPSEEK_API_KEY": "your_key_here"
            }
        }
    }
}
```

**Python API 调用：**

```python
from pubmed_api import search, analyze, llm_review, search_and_analyze

# 检索
result = search("diabetes treatment", max_results=20)
articles = result["articles"]

# 分析
analysis = analyze(articles, "full")

# LLM 综述
review = llm_review(articles, "diabetes treatment", "summary", api_key="YOUR_KEY")

# 一站式
result = search_and_analyze("diabetes", api_key="YOUR_KEY")
```

## MCP 工具列表

| 工具名 | 功能 |
|--------|------|
| `pubmed_search` | 检索 PubMed 文献 |
| `pubmed_analyze` | 分析文献数据（主题/趋势/缺口） |
| `pubmed_llm_review` | LLM 生成综述/总结/发现/临床意义 |
| `pubmed_generate_report` | 生成 Word/Excel 报告 |
| `pubmed_search_and_analyze` | 一站式全流程 |

## 项目结构

```
pubmed_get/
├── config.py              # 配置文件
├── pubmed_search.py       # PubMed API 检索模块
├── pubmed_api.py          # API 接口层（AI Agent 调用入口）
├── mcp_server.py          # MCP Server
├── report_generator.py    # Word/Excel 报告生成
├── text_analyzer.py       # 文本分析模块
├── llm_analyzer.py        # LLM 智能分析模块
├── demo_data.py           # 演示数据
├── main.py                # CLI 主程序
├── requirements.txt       # Python 依赖
└── templates/
    └── index.html          # Web 前端页面（master 分支）
```

## PubMed 检索语法示例

| 需求 | 检索式 |
|------|--------|
| 糖尿病治疗 | `diabetes mellitus treatment` |
| 特定作者 | `Smith J[Author]` |
| 特定期刊 | `diabetes[journal]` |
| 标题检索 | `insulin[Title]` |
| 综述文献 | `diabetes AND review[Publication Type]` |

## 技术栈

- Python 3.8+
- MCP (Model Context Protocol)
- python-docx (Word 生成)
- pandas (数据处理)
- requests (HTTP 请求)

## License

MIT
