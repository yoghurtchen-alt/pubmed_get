"""
PubMed 文献检索 API 模块
为 AI Agent (Hermes/OpenClaw/MCP) 提供结构化调用接口

所有函数均：
- 无交互式输入
- 返回 dict（可直接 JSON 序列化）
- 包含 success/error 字段
"""

from typing import List, Dict, Optional
from pubmed_search import search_pubmed as _search_pubmed
from text_analyzer import TextAnalyzer
from llm_analyzer import LLMAnalyzer
from report_generator import ReportGenerator


def search(
    query: str,
    max_results: int = 100,
    start_year: Optional[str] = None,
    end_year: Optional[str] = None,
    sort_by: str = "relevance"
) -> Dict:
    """
    检索 PubMed 文献

    Args:
        query: 检索词（支持 PubMed 高级检索语法）
        max_results: 最大返回数量 (1-10000)
        start_year: 起始年份 (如 "2020")
        end_year: 结束年份 (如 "2024")
        sort_by: 排序方式 "relevance" 或 "pub_date"

    Returns:
        {
            "success": bool,
            "query": str,
            "total": int,
            "articles": [...],
            "error": str  # 仅失败时
        }
    """
    try:
        date_range = None
        if start_year and end_year:
            date_range = (start_year, end_year)

        articles = _search_pubmed(
            query=query,
            max_results=max_results,
            date_range=date_range,
            sort_by=sort_by
        )

        return {
            "success": True,
            "query": query,
            "total": len(articles),
            "articles": articles
        }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "total": 0,
            "articles": [],
            "error": str(e)
        }


def analyze(
    articles: List[Dict],
    analysis_type: str = "full"
) -> Dict:
    """
    分析文献数据

    Args:
        articles: search() 返回的 articles 列表
        analysis_type: 分析类型
            - "full": 完整分析
            - "topics": 研究主题
            - "trends": 研究趋势
            - "gaps": 知识缺口
            - "summary": 研究概况

    Returns:
        {
            "success": bool,
            "analysis_type": str,
            "result": {...},
            "error": str  # 仅失败时
        }
    """
    try:
        if not articles:
            return {"success": False, "analysis_type": analysis_type, "result": {}, "error": "没有文献数据"}

        analyzer = TextAnalyzer()

        if analysis_type == "topics":
            result = analyzer.analyze_research_topics(articles)
        elif analysis_type == "trends":
            result = analyzer.analyze_research_trends(articles)
        elif analysis_type == "gaps":
            result = analyzer.find_knowledge_gaps(articles)
        elif analysis_type == "summary":
            result = analyzer.generate_research_summary(articles)
        else:
            result = analyzer.generate_full_analysis(articles)

        return {
            "success": True,
            "analysis_type": analysis_type,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "analysis_type": analysis_type,
            "result": {},
            "error": str(e)
        }


def llm_review(
    articles: List[Dict],
    query: str,
    review_type: str = "review",
    api_key: Optional[str] = None
) -> Dict:
    """
    使用 LLM 生成智能分析

    Args:
        articles: search() 返回的 articles 列表
        query: 检索词
        review_type: 综述类型
            - "review": 完整文献综述
            - "summary": 研究总结
            - "findings": 关键发现
            - "clinical": 临床意义
        api_key: DeepSeek/OpenAI API Key

    Returns:
        {
            "success": bool,
            "review_type": str,
            "content": str,
            "articles_used": int,
            "error": str  # 仅失败时
        }
    """
    try:
        if not articles:
            return {"success": False, "review_type": review_type, "content": "", "articles_used": 0, "error": "没有文献数据"}

        analyzer = LLMAnalyzer(api_key=api_key)

        if review_type == "summary":
            result = analyzer.generate_research_summary(articles, query)
            content = result.get("summary", "")
        elif review_type == "findings":
            result = analyzer.extract_key_findings(articles)
            content = result.get("findings", "")
        elif review_type == "clinical":
            result = analyzer.analyze_clinical_significance(articles)
            content = result.get("clinical_analysis", "")
        else:
            result = analyzer.generate_literature_review(articles, query)
            content = result.get("review", "")

        return {
            "success": result.get("success", False),
            "review_type": review_type,
            "content": content,
            "articles_used": result.get("articles_used", 0)
        }
    except Exception as e:
        return {
            "success": False,
            "review_type": review_type,
            "content": "",
            "articles_used": 0,
            "error": str(e)
        }


def generate_report(
    articles: List[Dict],
    query: str,
    output_format: str = "both",
    report_title: Optional[str] = None
) -> Dict:
    """
    生成报告文件

    Args:
        articles: search() 返回的 articles 列表
        query: 检索词
        output_format: 输出格式 "word" / "excel" / "both"
        report_title: 报告标题

    Returns:
        {
            "success": bool,
            "files": [str, ...],  # 文件路径列表
            "error": str  # 仅失败时
        }
    """
    try:
        if not articles:
            return {"success": False, "files": [], "error": "没有文献数据"}

        generator = ReportGenerator()
        paths = generator.generate_both(
            articles=articles,
            query=query,
            report_title=report_title
        )

        return {
            "success": True,
            "files": paths
        }
    except Exception as e:
        return {
            "success": False,
            "files": [],
            "error": str(e)
        }


def search_and_analyze(
    query: str,
    max_results: int = 50,
    start_year: Optional[str] = None,
    end_year: Optional[str] = None,
    api_key: Optional[str] = None,
    review_type: str = "summary"
) -> Dict:
    """
    一站式检索 + 分析 + LLM综述

    适合 AI Agent 一次性完成全流程调用

    Args:
        query: 检索词
        max_results: 最大检索数量
        start_year: 起始年份
        end_year: 结束年份
        api_key: LLM API Key（可选，不提供则跳过LLM分析）
        review_type: LLM综述类型

    Returns:
        {
            "success": bool,
            "query": str,
            "total": int,
            "articles": [...],
            "analysis": {...},
            "llm_review": {...},  # 仅提供 api_key 时
            "report_files": [str, ...],
            "error": str  # 仅失败时
        }
    """
    # 1. 检索
    search_result = search(query, max_results, start_year, end_year)
    if not search_result["success"]:
        return search_result

    articles = search_result["articles"]

    # 2. 文本分析
    analysis_result = analyze(articles, "full")

    # 3. LLM 综述（可选）
    llm_result = None
    if api_key:
        llm_result = llm_review(articles, query, review_type, api_key)

    # 4. 生成报告
    report_result = generate_report(articles, query)

    return {
        "success": True,
        "query": query,
        "total": len(articles),
        "articles": articles,
        "analysis": analysis_result.get("result", {}),
        "llm_review": llm_result if llm_result else None,
        "report_files": report_result.get("files", [])
    }
