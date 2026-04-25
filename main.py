"""
PubMed 文献自动检索与研究报告生成工具
主程序入口 - API 分支（面向 AI Agent）

使用方法:
    # 人类使用（可读输出）
    python main.py -q "diabetes treatment" -n 50

    # AI Agent 使用（JSON 输出）
    python main.py -q "diabetes treatment" -n 50 --json

    # 一站式全流程
    python main.py -q "diabetes" -n 20 --json --with-analysis --api-key YOUR_KEY

    # 仅检索
    python main.py -q "cancer" --json --mode search

    # 仅分析（从文件读取）
    python main.py --json --mode analyze --input results.json

    # 仅生成报告
    python main.py --json --mode report --input results.json
"""

import argparse
import json
import sys
from typing import Optional

from pubmed_api import search, analyze, llm_review, generate_report, search_and_analyze
from demo_data import get_demo_articles


def main():
    parser = argparse.ArgumentParser(
        description="PubMed文献自动检索与研究报告生成工具 (API分支)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本检索
  python main.py -q "diabetes treatment" -n 50

  # JSON 输出（适合 AI Agent 解析）
  python main.py -q "diabetes treatment" -n 50 --json

  # 一站式全流程（检索+分析+LLM综述+报告）
  python main.py -q "diabetes" -n 20 --json --with-analysis --api-key YOUR_KEY

  # 仅检索模式
  python main.py -q "cancer" --json --mode search

  # 仅分析模式（从 JSON 文件读取）
  python main.py --json --mode analyze --input search_results.json

  # 仅生成报告
  python main.py --json --mode report --input search_results.json

  # 演示模式
  python main.py --demo -q "diabetes" --json
        """
    )

    # 基本参数
    parser.add_argument("-q", "--query", help="检索词")
    parser.add_argument("-n", "--max-results", type=int, default=100, help="最大检索数量 (默认: 100)")
    parser.add_argument("--start", help="起始年份")
    parser.add_argument("--end", help="结束年份")
    parser.add_argument("-s", "--sort", choices=["relevance", "pub_date"], default="relevance", help="排序方式")
    parser.add_argument("--demo", action="store_true", help="演示模式")

    # 输出控制
    parser.add_argument("--json", dest="json_output", action="store_true", help="JSON 格式输出（适合 AI Agent）")
    parser.add_argument("--mode", choices=["search", "analyze", "report", "full"], default="full",
                        help="运行模式: search=仅检索, analyze=仅分析, report=仅报告, full=全流程")
    parser.add_argument("--input", help="输入 JSON 文件路径（analyze/report 模式使用）")

    # 分析选项
    parser.add_argument("--with-analysis", action="store_true", help="包含文本分析")
    parser.add_argument("--analysis-type", choices=["full", "topics", "trends", "gaps", "summary"],
                        default="full", help="分析类型 (默认: full)")

    # LLM 选项
    parser.add_argument("--api-key", help="DeepSeek/OpenAI API Key")
    parser.add_argument("--review-type", choices=["review", "summary", "findings", "clinical"],
                        default="summary", help="LLM 综述类型 (默认: summary)")

    # 报告选项
    parser.add_argument("-f", "--format", choices=["word", "excel", "both"], default="both", help="报告格式")
    parser.add_argument("-t", "--title", help="报告标题")

    args = parser.parse_args()

    # 根据模式执行
    if args.mode == "search":
        result = _do_search(args)
    elif args.mode == "analyze":
        result = _do_analyze(args)
    elif args.mode == "report":
        result = _do_report(args)
    else:
        result = _do_full(args)

    # 输出结果
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human_readable(result, args.mode)


def _do_search(args) -> dict:
    """仅检索模式"""
    if not args.query:
        return {"success": False, "error": "检索词不能为空，请使用 -q 参数指定"}

    if args.demo:
        articles = get_demo_articles(args.query)[:args.max_results]
        return {"success": True, "query": args.query, "total": len(articles), "articles": articles}

    return search(
        query=args.query,
        max_results=args.max_results,
        start_year=args.start,
        end_year=args.end,
        sort_by=args.sort
    )


def _do_analyze(args) -> dict:
    """仅分析模式"""
    articles = _load_articles(args)
    if articles is None:
        return {"success": False, "error": "无法加载文献数据，请使用 --input 指定文件或使用 -q 检索"}

    return analyze(articles, args.analysis_type)


def _do_report(args) -> dict:
    """仅报告模式"""
    data = _load_input_file(args)
    if data is None:
        return {"success": False, "error": "无法加载数据，请使用 --input 指定文件"}

    articles = data.get("articles", [])
    query = data.get("query", args.query or "unknown")

    return generate_report(articles, query, args.format, args.title)


def _do_full(args) -> dict:
    """全流程模式"""
    if not args.query:
        return {"success": False, "error": "检索词不能为空，请使用 -q 参数指定"}

    # 演示模式
    if args.demo:
        articles = get_demo_articles(args.query)[:args.max_results]
        search_result = {"success": True, "query": args.query, "total": len(articles), "articles": articles}
    else:
        search_result = search(
            query=args.query,
            max_results=args.max_results,
            start_year=args.start,
            end_year=args.end,
            sort_by=args.sort
        )

    if not search_result["success"]:
        return search_result

    articles = search_result["articles"]
    result = {
        "success": True,
        "query": args.query,
        "total": len(articles),
        "articles": articles
    }

    # 文本分析
    if args.with_analysis or not args.json_output:
        result["analysis"] = analyze(articles, args.analysis_type).get("result", {})

    # LLM 综述
    if args.api_key:
        result["llm_review"] = llm_review(articles, args.query, args.review_type, args.api_key)

    # 生成报告
    if args.format:
        result["report"] = generate_report(articles, args.query, args.format, args.title)

    return result


def _load_articles(args) -> Optional[list]:
    """从文件或检索加载文献数据"""
    if args.input:
        data = _load_input_file(args)
        return data.get("articles") if data else None

    if args.query:
        if args.demo:
            return get_demo_articles(args.query)[:args.max_results]
        result = search(args.query, args.max_results, args.start, args.end, args.sort)
        return result.get("articles") if result["success"] else None

    return None


def _load_input_file(args) -> Optional[dict]:
    """从 JSON 文件加载数据"""
    if not args.input:
        return None
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None


def _print_human_readable(result: dict, mode: str):
    """人类可读的输出格式"""
    if not result.get("success"):
        print(f"[错误] {result.get('error', '未知错误')}")
        return

    if mode == "search":
        print(f"\n检索完成: 共 {result.get('total', 0)} 篇文献")
        for i, article in enumerate(result.get("articles", [])[:10], 1):
            print(f"\n  {i}. {article.get('title', '')}")
            print(f"     {article.get('journal', '')} ({article.get('year', '')})")
            print(f"     PMID: {article.get('pmid', '')}")
        if result.get("total", 0) > 10:
            print(f"\n  ... 等共 {result['total']} 篇")

    elif mode == "analyze":
        analysis = result.get("result", {})
        topics = analysis.get("research_topics", [])
        if topics:
            print("\n研究主题:")
            for t in topics[:8]:
                print(f"  - {t.get('keyword', '')} (频次: {t.get('count', 0)})")

    elif mode == "report":
        files = result.get("files", [])
        if files:
            print("\n报告已生成:")
            for f in files:
                print(f"  -> {f}")

    else:  # full
        print(f"\n{'='*60}")
        print(f"检索完成: 共 {result.get('total', 0)} 篇文献")
        print(f"{'='*60}")

        if result.get("analysis"):
            print("\n[分析完成]")

        if result.get("llm_review"):
            print("\n[LLM 综述完成]")

        if result.get("report", {}).get("files"):
            print("\n报告文件:")
            for f in result["report"]["files"]:
                print(f"  -> {f}")

        if not result.get("analysis") and not result.get("llm_review"):
            for i, article in enumerate(result.get("articles", [])[:5], 1):
                print(f"\n  {i}. {article.get('title', '')}")
                print(f"     {article.get('journal', '')} ({article.get('year', '')})")


if __name__ == "__main__":
    main()
