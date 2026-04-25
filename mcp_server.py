"""
MCP (Model Context Protocol) Server
让 AI Agent (Claude/Hermes/OpenClaw) 可以直接调用 PubMed 检索工具

启动方式:
    python mcp_server.py

在 Claude Desktop / Cursor 等工具中配置:
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
"""

import json
import sys
import os
from typing import Any

from pubmed_api import search, analyze, llm_review, generate_report, search_and_analyze

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")


def handle_request(request: dict) -> dict:
    """处理 MCP 请求"""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "pubmed-research",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "pubmed_search",
                        "description": "检索 PubMed 文献。支持高级检索语法，如 diabetes[Title]、Smith J[Author]、review[Publication Type]。返回文献的标题、作者、摘要、期刊、年份、DOI等信息。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "检索词，支持 PubMed 高级检索语法"
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "最大返回数量，默认100",
                                    "default": 100
                                },
                                "start_year": {
                                    "type": "string",
                                    "description": "起始年份，如 2020"
                                },
                                "end_year": {
                                    "type": "string",
                                    "description": "结束年份，如 2024"
                                },
                                "sort_by": {
                                    "type": "string",
                                    "enum": ["relevance", "pub_date"],
                                    "description": "排序方式，默认 relevance",
                                    "default": "relevance"
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "pubmed_analyze",
                        "description": "分析已检索的文献数据，提取研究主题、趋势、知识缺口等。需要先调用 pubmed_search 获取文献列表。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "articles": {
                                    "type": "array",
                                    "description": "pubmed_search 返回的 articles 列表"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["full", "topics", "trends", "gaps", "summary"],
                                    "description": "分析类型：full=完整分析, topics=研究主题, trends=研究趋势, gaps=知识缺口, summary=研究概况",
                                    "default": "full"
                                }
                            },
                            "required": ["articles"]
                        }
                    },
                    {
                        "name": "pubmed_llm_review",
                        "description": "使用大语言模型生成文献综述、研究总结、关键发现或临床意义分析。需要 DEEPSEEK_API_KEY 环境变量或在参数中提供 api_key。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "articles": {
                                    "type": "array",
                                    "description": "pubmed_search 返回的 articles 列表"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "检索词"
                                },
                                "review_type": {
                                    "type": "string",
                                    "enum": ["review", "summary", "findings", "clinical"],
                                    "description": "综述类型：review=文献综述, summary=研究总结, findings=关键发现, clinical=临床意义",
                                    "default": "summary"
                                },
                                "api_key": {
                                    "type": "string",
                                    "description": "DeepSeek/OpenAI API Key（可选，默认使用环境变量）"
                                }
                            },
                            "required": ["articles", "query"]
                        }
                    },
                    {
                        "name": "pubmed_generate_report",
                        "description": "生成 Word/Excel 研究报告文件，保存到 output 目录。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "articles": {
                                    "type": "array",
                                    "description": "pubmed_search 返回的 articles 列表"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "检索词"
                                },
                                "output_format": {
                                    "type": "string",
                                    "enum": ["word", "excel", "both"],
                                    "description": "输出格式，默认 both",
                                    "default": "both"
                                },
                                "report_title": {
                                    "type": "string",
                                    "description": "报告标题（可选）"
                                }
                            },
                            "required": ["articles", "query"]
                        }
                    },
                    {
                        "name": "pubmed_search_and_analyze",
                        "description": "一站式检索+分析+LLM综述+报告生成。适合一次性完成全流程。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "检索词"
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "最大检索数量，默认50",
                                    "default": 50
                                },
                                "start_year": {
                                    "type": "string",
                                    "description": "起始年份"
                                },
                                "end_year": {
                                    "type": "string",
                                    "description": "结束年份"
                                },
                                "api_key": {
                                    "type": "string",
                                    "description": "LLM API Key（可选）"
                                },
                                "review_type": {
                                    "type": "string",
                                    "enum": ["review", "summary", "findings", "clinical"],
                                    "description": "LLM综述类型，默认 summary",
                                    "default": "summary"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            result_data = _dispatch_tool(tool_name, arguments)

            # 截断过长的文章列表以避免响应过大
            result_str = json.dumps(result_data, ensure_ascii=False)
            if len(result_str) > 50000:
                result_data = _truncate_result(result_data)
                result_str = json.dumps(result_data, ensure_ascii=False)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_str
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
                        }
                    ],
                    "isError": True
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"}
    }


def _dispatch_tool(tool_name: str, arguments: dict) -> dict:
    """分发工具调用"""
    if tool_name == "pubmed_search":
        return search(
            query=arguments["query"],
            max_results=arguments.get("max_results", 100),
            start_year=arguments.get("start_year"),
            end_year=arguments.get("end_year"),
            sort_by=arguments.get("sort_by", "relevance")
        )

    elif tool_name == "pubmed_analyze":
        return analyze(
            articles=arguments["articles"],
            analysis_type=arguments.get("analysis_type", "full")
        )

    elif tool_name == "pubmed_llm_review":
        api_key = arguments.get("api_key") or DEEPSEEK_API_KEY
        return llm_review(
            articles=arguments["articles"],
            query=arguments["query"],
            review_type=arguments.get("review_type", "summary"),
            api_key=api_key
        )

    elif tool_name == "pubmed_generate_report":
        return generate_report(
            articles=arguments["articles"],
            query=arguments["query"],
            output_format=arguments.get("output_format", "both"),
            report_title=arguments.get("report_title")
        )

    elif tool_name == "pubmed_search_and_analyze":
        api_key = arguments.get("api_key") or DEEPSEEK_API_KEY
        return search_and_analyze(
            query=arguments["query"],
            max_results=arguments.get("max_results", 50),
            start_year=arguments.get("start_year"),
            end_year=arguments.get("end_year"),
            api_key=api_key if api_key else None,
            review_type=arguments.get("review_type", "summary")
        )

    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}


def _truncate_result(data: dict) -> dict:
    """截断过长的结果，保留摘要信息"""
    if "articles" in data and isinstance(data["articles"], list):
        total = len(data["articles"])
        data["articles"] = data["articles"][:10]
        data["_truncated"] = f"仅显示前10篇，共{total}篇"
    return data


def main():
    """MCP Server 主循环 - 通过 stdin/stdout 通信"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = handle_request(request)
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
