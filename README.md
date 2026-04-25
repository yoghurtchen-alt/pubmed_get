# PubMed 文献自动检索与研究报告生成工具

从 PubMed 批量检索医学文献，自动生成 Word 研究报告和 Excel 文献汇总表，支持 LLM 智能分析综述。

## 功能特性

- **批量文献检索** - 支持 PubMed 高级检索语法，可限制年份、排序方式
- **自动信息提取** - 获取标题、作者、摘要、期刊、DOI、MeSH 主题词等
- **报告自动生成** - Word 研究报告 + Excel 文献汇总表
- **文本分析** - 研究主题提取、趋势分析、知识缺口识别
- **LLM 智能综述** - 接入 DeepSeek/OpenAI API 生成文献综述、研究总结、关键发现、临床意义分析
- **Web 界面** - 基于 Flask 的可视化操作界面
- **命令行模式** - 支持命令行参数快速检索

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

**Web 模式（推荐）：**

```bash
python web_app.py
# 打开浏览器访问 http://127.0.0.1:5000
```

**命令行模式：**

```bash
# 交互式
python main.py

# 快速检索
python main.py -q "diabetes treatment" -n 50

# 限制年份
python main.py -q "cancer" --start 2020 --end 2024

# 演示模式（无需网络）
python main.py --demo -q "any topic"
```

## LLM 智能分析配置

在 Web 界面中输入 DeepSeek API Key 即可使用智能分析功能。

获取 API Key：[DeepSeek 开放平台](https://platform.deepseek.com/)

也可以设置环境变量：

```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key

# Linux/Mac
export DEEPSEEK_API_KEY=your_api_key
```

## 项目结构

```
pubmed_get/
├── config.py              # 配置文件
├── pubmed_search.py       # PubMed API 检索模块
├── report_generator.py    # Word/Excel 报告生成
├── text_analyzer.py       # 文本分析模块
├── llm_analyzer.py        # LLM 智能分析模块
├── demo_data.py           # 演示数据
├── main.py                # 命令行主程序
├── web_app.py             # Flask Web 应用
├── requirements.txt       # Python 依赖
└── templates/
    └── index.html          # Web 前端页面
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
- Flask (Web 框架)
- python-docx (Word 生成)
- pandas (数据处理)
- requests (HTTP 请求)

## 注意事项

- 无 API Key 时，NCBI 建议每秒不超过 3 次请求
- 注册 NCBI 邮箱可提高访问频率
- LLM 智能分析功能需要配置 API Key

## License

MIT
