"""
文献文本分析模块
提供关键词提取、主题聚类、摘要整合等功能
"""

import re
import json
from collections import Counter
from typing import List, Dict, Tuple, Optional
import math


class TextAnalyzer:
    """文献文本分析器"""

    def __init__(self):
        # 英文停用词
        self.stopwords = set([
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can',
            'need', 'dare', 'ought', 'used', 'this', 'that', 'these', 'those',
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'just', 'also', 'both', 'either', 'neither', 'one', 'two', 'first',
            'second', 'study', 'studies', 'research', 'analysis', 'data',
            'results', 'method', 'methods', 'using', 'based', 'showed',
            'found', 'observed', 'reported', 'published', 'et', 'al',
            'however', 'therefore', 'thus', 'furthermore', 'moreover',
            'although', 'while', 'whereas', 'despite', 'including',
            'among', 'between', 'within', 'during', 'after', 'before',
            'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
            'will', 'just', 'should', 'now'
        ])

    def extract_keywords_from_text(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """从文本中提取关键词（基于词频）"""
        if not text:
            return []

        # 清理文本
        text = text.lower()
        # 保留字母、数字、空格和连字符
        text = re.sub(r'[^a-z0-9\s\-]', ' ', text)

        # 分词（简单按空格分割，同时处理连字符词组）
        words = text.split()

        # 过滤停用词和短词
        filtered = []
        for word in words:
            word = word.strip('-')
            if len(word) >= 3 and word not in self.stopwords:
                filtered.append(word)

        # 统计词频
        word_counts = Counter(filtered)
        return word_counts.most_common(top_n)

    def analyze_research_topics(self, articles: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        分析研究主题
        基于标题和摘要提取高频主题词
        """
        # 合并所有标题和摘要
        all_text = ""
        for article in articles:
            all_text += " " + (article.get('title', '') or '')
            all_text += " " + (article.get('abstract', '') or '')

        # 提取关键词
        keywords = self.extract_keywords_from_text(all_text, top_n * 2)

        # 为每篇文献匹配主题
        topics = []
        for keyword, count in keywords[:top_n]:
            # 找出包含该关键词的文献
            related_articles = []
            for idx, article in enumerate(articles):
                text = (article.get('title', '') + " " + article.get('abstract', '')).lower()
                if keyword in text:
                    related_articles.append(idx)

            topics.append({
                'keyword': keyword,
                'count': count,
                'article_count': len(related_articles),
                'article_indices': related_articles[:5]  # 只保存前5篇的索引
            })

        return topics

    def generate_research_summary(self, articles: List[Dict]) -> Dict:
        """
        生成研究综述摘要
        整合所有文献的摘要，提取核心内容
        """
        if not articles:
            return {}

        # 1. 研究背景统计
        backgrounds = []
        objectives = []
        methods_list = []
        results_list = []
        conclusions = []

        for article in articles:
            abstract = article.get('abstract', '')
            if not abstract:
                continue

            # 尝试提取结构化摘要的各个部分
            sections = self._parse_structured_abstract(abstract)
            if sections.get('background'):
                backgrounds.append(sections['background'])
            if sections.get('objective'):
                objectives.append(sections['objective'])
            if sections.get('methods'):
                methods_list.append(sections['methods'])
            if sections.get('results'):
                results_list.append(sections['results'])
            if sections.get('conclusion'):
                conclusions.append(sections['conclusion'])

        # 2. 提取高频研究对象/疾病
        disease_keywords = self._extract_disease_keywords(articles)

        # 3. 提取高频干预措施/治疗方法
        intervention_keywords = self._extract_intervention_keywords(articles)

        return {
            'total_articles': len(articles),
            'structured_count': len(backgrounds),
            'diseases': disease_keywords[:10],
            'interventions': intervention_keywords[:10],
            'sample_backgrounds': backgrounds[:3] if backgrounds else [],
            'sample_objectives': objectives[:3] if objectives else [],
            'sample_conclusions': conclusions[:3] if conclusions else []
        }

    def _parse_structured_abstract(self, abstract: str) -> Dict[str, str]:
        """解析结构化摘要"""
        sections = {}

        # 常见的结构化摘要标签
        patterns = [
            (r'(?:Background|BACKGROUND|背景)\s*:?\s*(.*?)(?=(?:Objective|OBJECTIVE|目的|Methods|METHODS|方法)|$)', 'background'),
            (r'(?:Objective|OBJECTIVE|Aim|AIM|Purpose|PURPOSE|目的)\s*:?\s*(.*?)(?=(?:Methods|METHODS|方法|Background|BACKGROUND|背景)|$)', 'objective'),
            (r'(?:Methods|METHODS|Method|METHOD|方法)\s*:?\s*(.*?)(?=(?:Results|RESULTS|结果|Conclusion|CONCLUSION|结论)|$)', 'methods'),
            (r'(?:Results|RESULTS|Result|RESULT|结果)\s*:?\s*(.*?)(?=(?:Conclusion|CONCLUSION|结论|Discussion|DISCUSSION|讨论)|$)', 'results'),
            (r'(?:Conclusion|CONCLUSIONS|Conclusions|结论)\s*:?\s*(.*?)(?=(?:Keywords|KEYWORDS|关键词|Copyright|COPYRIGHT)|$)', 'conclusion'),
        ]

        for pattern, key in patterns:
            match = re.search(pattern, abstract, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                # 清理多余空白
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 10:  # 过滤过短的匹配
                    sections[key] = text

        # 如果不是结构化摘要，尝试按句子分割
        if not sections and abstract:
            sentences = re.split(r'(?<=[.!?])\s+', abstract)
            if len(sentences) >= 3:
                sections['background'] = sentences[0]
                sections['objective'] = sentences[1] if len(sentences) > 1 else ""
                sections['conclusion'] = sentences[-1]

        return sections

    def _extract_disease_keywords(self, articles: List[Dict]) -> List[Tuple[str, int]]:
        """提取疾病相关关键词"""
        disease_indicators = [
            'disease', 'disorder', 'syndrome', 'cancer', 'tumor', 'carcinoma',
            'diabetes', 'hypertension', 'infection', 'inflammation', 'failure',
            'dementia', 'asthma', 'arthritis', 'hepatitis', 'nephropathy',
            'cardiovascular', 'stroke', 'infarction', 'pneumonia', 'sepsis'
        ]

        all_text = ""
        for article in articles:
            all_text += " " + (article.get('title', '') or '')
            all_text += " " + (article.get('abstract', '') or '')
            all_text += " " + " ".join(article.get('mesh_terms', []))

        words = self.extract_keywords_from_text(all_text, 50)

        # 筛选疾病相关词
        diseases = []
        for word, count in words:
            if any(indicator in word for indicator in disease_indicators) or word.endswith('itis') or word.endswith('osis') or word.endswith('emia'):
                diseases.append((word, count))

        return diseases

    def _extract_intervention_keywords(self, articles: List[Dict]) -> List[Tuple[str, int]]:
        """提取干预措施关键词"""
        intervention_indicators = [
            'treatment', 'therapy', 'therapeutic', 'surgery', 'surgical',
            'medication', 'drug', 'agent', 'inhibitor', 'antibody',
            'vaccine', 'transplantation', 'intervention', 'rehabilitation',
            'exercise', 'diet', 'nutrition', 'radiation', 'chemotherapy'
        ]

        all_text = ""
        for article in articles:
            all_text += " " + (article.get('title', '') or '')
            all_text += " " + (article.get('abstract', '') or '')

        words = self.extract_keywords_from_text(all_text, 50)

        interventions = []
        for word, count in words:
            if any(indicator in word for indicator in intervention_indicators):
                interventions.append((word, count))

        return interventions

    def analyze_research_trends(self, articles: List[Dict]) -> Dict:
        """
        分析研究趋势
        """
        if not articles:
            return {}

        from collections import defaultdict

        # 按年份分组
        year_articles = defaultdict(list)
        for article in articles:
            year = article.get('year', '')
            if year:
                year_articles[year].append(article)

        # 每年的研究热点
        yearly_trends = {}
        for year in sorted(year_articles.keys()):
            year_text = ""
            for article in year_articles[year]:
                year_text += " " + (article.get('title', '') or '')

            keywords = self.extract_keywords_from_text(year_text, 5)
            yearly_trends[year] = [k[0] for k in keywords]

        return {
            'yearly_trends': yearly_trends,
            'year_counts': {year: len(arts) for year, arts in year_articles.items()}
        }

    def find_knowledge_gaps(self, articles: List[Dict]) -> List[str]:
        """
        识别知识空白/研究缺口
        基于文献中的局限性声明和未来研究方向
        """
        gaps = []

        gap_indicators = [
            r'(?:further|future|more)\s+(?:research|study|investigation|work)',
            r'(?:limited|limitation|limitations)\s+(?:by|of|in|to)',
            r'(?:not|no|lack|lacking|insufficient)\s+(?:data|evidence|study|research)',
            r'(?:unclear|unknown|uncertain|remains?\s+to\s+be)',
            r'(?:warrant|warrants|needed|required|necessary)',
        ]

        for article in articles:
            abstract = article.get('abstract', '')
            if not abstract:
                continue

            # 查找局限性/未来研究方向相关的句子
            sentences = re.split(r'(?<=[.!?])\s+', abstract)
            for sentence in sentences:
                sentence_lower = sentence.lower()
                for indicator in gap_indicators:
                    if re.search(indicator, sentence_lower):
                        # 清理并保存
                        clean = sentence.strip()
                        if len(clean) > 20 and len(clean) < 300:
                            gaps.append(clean)
                        break

        # 去重并返回前10条
        unique_gaps = list(dict.fromkeys(gaps))
        return unique_gaps[:10]

    def generate_full_analysis(self, articles: List[Dict]) -> Dict:
        """
        生成完整的文献分析报告
        """
        return {
            'research_topics': self.analyze_research_topics(articles),
            'research_summary': self.generate_research_summary(articles),
            'research_trends': self.analyze_research_trends(articles),
            'knowledge_gaps': self.find_knowledge_gaps(articles),
            'keyword_stats': self.extract_keywords_from_text(
                " ".join([
                    (a.get('title', '') or '') + " " + (a.get('abstract', '') or '')
                    for a in articles
                ]),
                top_n=30
            )
        }


# 便捷函数
def analyze_articles(articles: List[Dict]) -> Dict:
    """便捷的文献分析函数"""
    analyzer = TextAnalyzer()
    return analyzer.generate_full_analysis(articles)
