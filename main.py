"""
PubMed 文献自动检索与研究报告生成工具
主程序入口

使用方法:
    1. 直接运行: python main.py
    2. 命令行参数: python main.py -q "diabetes treatment" -n 50
"""

import argparse
import sys
from typing import Optional

from pubmed_search import search_pubmed
from report_generator import generate_report
from demo_data import get_demo_articles


def print_banner():
    """打印程序横幅"""
    banner = """
    +============================================================+
    |          PubMed 文献自动检索与研究报告生成工具             |
    |                                                            |
    |  功能: 从PubMed批量检索医学文献，自动生成汇总报告          |
    |  支持: Word研究报告 + Excel文献汇总表                      |
    +============================================================+
    """
    print(banner)


def get_user_input() -> tuple:
    """交互式获取用户输入"""
    print("\n【文献检索设置】")
    print("-" * 50)

    # 选择模式
    print("\n运行模式:")
    print("  1. 真实PubMed检索 (需要网络连接)")
    print("  2. 演示模式 (使用模拟数据，无需网络)")
    mode_input = input("请选择 [1]: ").strip()
    use_demo = mode_input == "2"

    # 检索词
    query = input("请输入检索词 (支持PubMed高级检索语法): ").strip()
    while not query:
        print("检索词不能为空，请重新输入!")
        query = input("请输入检索词: ").strip()

    # 检索数量
    max_results_input = input("请输入最大检索数量 [默认100]: ").strip()
    try:
        max_results = int(max_results_input) if max_results_input else 100
    except ValueError:
        print("输入无效，使用默认值 100")
        max_results = 100

    # 日期范围
    date_range = None
    date_input = input("是否限制发表年份? (y/n) [默认n]: ").strip().lower()
    if date_input == 'y':
        start_year = input("  起始年份 (如 2020): ").strip()
        end_year = input("  结束年份 (如 2024): ").strip()
        if start_year and end_year:
            date_range = (start_year, end_year)

    # 排序方式
    sort_options = {
        "1": "relevance",
        "2": "pub_date"
    }
    print("\n排序方式:")
    print("  1. 相关度 (默认)")
    print("  2. 发表日期")
    sort_input = input("请选择 [1]: ").strip()
    sort_by = sort_options.get(sort_input, "relevance")

    # 输出格式
    print("\n输出格式:")
    print("  1. Word研究报告 + Excel汇总表 (默认)")
    print("  2. 仅Word研究报告")
    print("  3. 仅Excel汇总表")
    format_input = input("请选择 [1]: ").strip()
    format_options = {
        "1": "both",
        "2": "word",
        "3": "excel"
    }
    output_format = format_options.get(format_input, "both")

    # 报告标题
    report_title = input("\n请输入报告标题 (直接回车使用默认): ").strip()

    return query, max_results, date_range, sort_by, output_format, report_title, use_demo


def run_search(
    query: str,
    max_results: int = 100,
    date_range: Optional[tuple] = None,
    sort_by: str = "relevance",
    output_format: str = "both",
    report_title: Optional[str] = None,
    use_demo: bool = False
):
    """
    执行检索和报告生成

    Args:
        query: 检索词
        max_results: 最大结果数
        date_range: 日期范围
        sort_by: 排序方式
        output_format: 输出格式
        report_title: 报告标题
        use_demo: 是否使用演示数据
    """
    print(f"\n{'='*60}")
    if use_demo:
        print("演示模式: 使用模拟数据生成报告")
    else:
        print("开始执行检索...")
    print(f"{'='*60}")

    # 1. 检索文献
    if use_demo:
        articles = get_demo_articles(query)[:max_results]
        print(f"\n[演示模式] 加载 {len(articles)} 篇模拟文献")
    else:
        articles = search_pubmed(
            query=query,
            max_results=max_results,
            date_range=date_range,
            sort_by=sort_by
        )

    if not articles:
        print("\n[!] 未找到相关文献，请尝试调整检索词。")
        return

    print(f"\n[OK] 成功获取 {len(articles)} 篇文献详情")

    # 2. 生成报告
    print(f"\n{'='*60}")
    print("正在生成报告...")
    print(f"{'='*60}")

    paths = generate_report(
        articles=articles,
        query=query,
        output_format=output_format,
        report_title=report_title if report_title else None
    )

    # 3. 输出结果
    print(f"\n{'='*60}")
    print("[OK] 任务完成!")
    print(f"{'='*60}")
    print("\n生成文件:")
    for path in paths:
        print(f"  -> {path}")

    print("\n文献统计:")
    print(f"  - 总文献数: {len(articles)}")

    # 统计年份分布
    years = [a.get("year", "") for a in articles if a.get("year")]
    if years:
        from collections import Counter
        year_counts = Counter(years)
        print(f"  - 年份范围: {min(years)} - {max(years)}")
        print(f"  - 最新文献: {year_counts.most_common(1)[0][0]}年 ({year_counts.most_common(1)[0][1]}篇)")

    # 统计期刊
    journals = [a.get("journal", "") for a in articles if a.get("journal")]
    if journals:
        from collections import Counter
        journal_counts = Counter(journals)
        print(f"  - 主要期刊: {journal_counts.most_common(1)[0][0]}")

    print(f"\n提示:")
    print(f"  - 报告文件保存在 output/ 目录下")
    print(f"  - 建议到 NCBI 注册邮箱以提高API访问频率")
    print(f"  - 可在 config.py 中配置默认参数")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="PubMed文献自动检索与研究报告生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                                    # 交互式模式
  python main.py -q "diabetes treatment"            # 简单检索
  python main.py -q "diabetes" -n 200               # 检索200篇
  python main.py -q "cancer" --start 2020 --end 2024 # 限制年份
  python main.py -q "COVID-19" -f excel             # 仅生成Excel
  python main.py --demo                             # 演示模式 (无需网络)
        """
    )

    parser.add_argument(
        "-q", "--query",
        help="检索词 (支持PubMed高级检索语法)"
    )
    parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=100,
        help="最大检索数量 (默认: 100)"
    )
    parser.add_argument(
        "--start",
        help="起始年份 (如: 2020)"
    )
    parser.add_argument(
        "--end",
        help="结束年份 (如: 2024)"
    )
    parser.add_argument(
        "-s", "--sort",
        choices=["relevance", "pub_date"],
        default="relevance",
        help="排序方式 (默认: relevance)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["word", "excel", "both"],
        default="both",
        help="输出格式 (默认: both)"
    )
    parser.add_argument(
        "-t", "--title",
        help="报告标题"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="使用演示模式 (模拟数据，无需网络)"
    )

    args = parser.parse_args()

    print_banner()

    # 如果没有提供检索词，进入交互模式
    if not args.query:
        query, max_results, date_range, sort_by, output_format, report_title, use_demo = get_user_input()
    else:
        query = args.query
        max_results = args.max_results
        date_range = (args.start, args.end) if args.start and args.end else None
        sort_by = args.sort
        output_format = args.format
        report_title = args.title
        use_demo = args.demo

    # 执行检索
    try:
        run_search(
            query=query,
            max_results=max_results,
            date_range=date_range,
            sort_by=sort_by,
            output_format=output_format,
            report_title=report_title,
            use_demo=use_demo
        )
    except KeyboardInterrupt:
        print("\n\n[!] 用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
