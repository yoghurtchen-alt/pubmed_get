"""
PubMed 文献检索 Web 应用
基于 Flask 的网页版前端
"""

import os
import sys
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional
from flask import Flask, render_template, request, jsonify, send_file

from pubmed_search import search_pubmed
from report_generator import ReportGenerator
from demo_data import get_demo_articles
from text_analyzer import TextAnalyzer
from llm_analyzer import LLMAnalyzer
from config import OUTPUT_DIR

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 存储进行中的任务状态
task_status = {}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def api_search():
    """API: 执行文献检索"""
    data = request.get_json()

    query = data.get('query', '').strip()
    max_results = int(data.get('max_results', 100))
    start_year = data.get('start_year', '').strip()
    end_year = data.get('end_year', '').strip()
    sort_by = data.get('sort_by', 'relevance')
    use_demo = data.get('use_demo', False)

    if not query:
        return jsonify({'success': False, 'error': '检索词不能为空'}), 400

    # 日期范围
    date_range = None
    if start_year and end_year:
        date_range = (start_year, end_year)

    try:
        if use_demo:
            articles = get_demo_articles(query)[:max_results]
        else:
            articles = search_pubmed(
                query=query,
                max_results=max_results,
                date_range=date_range,
                sort_by=sort_by
            )

        # 统计信息
        stats = generate_statistics(articles)

        return jsonify({
            'success': True,
            'articles': articles,
            'total': len(articles),
            'stats': stats,
            'query': query
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API: 执行文献分析"""
    data = request.get_json()

    articles = data.get('articles', [])
    query = data.get('query', '')
    analysis_type = data.get('analysis_type', 'full')

    if not articles:
        return jsonify({'success': False, 'error': '没有文献数据'}), 400

    try:
        analyzer = TextAnalyzer()

        if analysis_type == 'topics':
            result = analyzer.analyze_research_topics(articles)
            return jsonify({'success': True, 'topics': result})

        elif analysis_type == 'summary':
            result = analyzer.generate_research_summary(articles)
            return jsonify({'success': True, 'summary': result})

        elif analysis_type == 'trends':
            result = analyzer.analyze_research_trends(articles)
            return jsonify({'success': True, 'trends': result})

        elif analysis_type == 'gaps':
            result = analyzer.find_knowledge_gaps(articles)
            return jsonify({'success': True, 'gaps': result})

        else:  # full analysis
            result = analyzer.generate_full_analysis(articles)
            return jsonify({'success': True, 'analysis': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/llm_review', methods=['POST'])
def api_llm_review():
    """API: 使用 LLM 生成文献综述"""
    data = request.get_json()

    articles = data.get('articles', [])
    query = data.get('query', '')
    review_type = data.get('review_type', 'review')
    api_key = data.get('api_key', '')

    if not articles:
        return jsonify({'success': False, 'error': '没有文献数据'}), 400

    try:
        analyzer = LLMAnalyzer(api_key=api_key if api_key else None)

        if review_type == 'review':
            result = analyzer.generate_literature_review(articles, query)
        elif review_type == 'summary':
            result = analyzer.generate_research_summary(articles, query)
        elif review_type == 'findings':
            result = analyzer.extract_key_findings(articles)
        elif review_type == 'clinical':
            result = analyzer.analyze_clinical_significance(articles)
        else:
            result = analyzer.generate_literature_review(articles, query)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """API: 生成报告文件"""
    data = request.get_json()

    articles = data.get('articles', [])
    query = data.get('query', '')
    output_format = data.get('output_format', 'both')
    report_title = data.get('report_title', '').strip()

    if not articles:
        return jsonify({'success': False, 'error': '没有文献数据'}), 400

    try:
        generator = ReportGenerator()
        paths = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if output_format in ['excel', 'both']:
            excel_path = generator.generate_excel(
                articles,
                f"文献汇总_{timestamp}.xlsx"
            )
            paths.append(excel_path)

        if output_format in ['word', 'both']:
            word_path = generator.generate_word_report(
                articles,
                query,
                f"研究报告_{timestamp}.docx",
                report_title if report_title else None
            )
            paths.append(word_path)

        # 返回文件名（不含路径）
        filenames = [os.path.basename(p) for p in paths]

        return jsonify({
            'success': True,
            'files': filenames,
            'paths': paths
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<filename>')
def api_download(filename):
    """下载生成的文件"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'success': False, 'error': '文件不存在'}), 404


def generate_statistics(articles: List[Dict]) -> Dict:
    """生成文献统计信息"""
    if not articles:
        return {}

    from collections import Counter

    # 年份统计
    years = [a.get('year', '') for a in articles if a.get('year')]
    year_counts = Counter(years)
    year_distribution = dict(sorted(year_counts.items()))

    # 期刊统计
    journals = [a.get('journal', '') for a in articles if a.get('journal')]
    journal_counts = Counter(journals)
    top_journals = journal_counts.most_common(10)

    # 作者统计
    all_authors = []
    for article in articles:
        all_authors.extend(article.get('authors', []))
    author_counts = Counter(all_authors)
    top_authors = author_counts.most_common(10)

    # 关键词统计
    all_keywords = []
    for article in articles:
        all_keywords.extend(article.get('keywords', []))
        all_keywords.extend(article.get('mesh_terms', []))
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(15)

    return {
        'year_range': f"{min(years)} - {max(years)}" if years else '',
        'year_distribution': year_distribution,
        'top_journals': top_journals,
        'top_authors': top_authors,
        'top_keywords': top_keywords
    }


if __name__ == '__main__':
    print("=" * 60)
    print("PubMed 文献检索 Web 应用")
    print("=" * 60)
    print("请打开浏览器访问: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
