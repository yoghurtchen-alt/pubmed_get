"""
LLM 智能分析模块
使用大语言模型 API 生成文献综述、研究总结等
支持 DeepSeek、OpenAI 等 API
"""

import os
import re
import json
import time
from typing import List, Dict, Optional, Tuple
import requests


class LLMAnalyzer:
    """LLM 文献分析器"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: str = "deepseek-chat"
    ):
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY', '')
        self.api_base = api_base or "https://api.deepseek.com/v1"
        self.model = model
        self.timeout = 120

    def _call_api(self, messages: List[Dict], temperature: float = 0.1) -> Optional[str]:
        """调用 LLM API"""
        if not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"LLM API 调用失败: {e}")
            return None

    def _build_article_block(self, articles: List[Dict], max_abstract_len: int = 600) -> Tuple[str, List[Dict]]:
        """
        构建文献信息块，同时返回文献索引映射
        统一编号格式 [1], [2], ...
        """
        article_map = []
        lines = []
        for i, article in enumerate(articles, 1):
            info = {
                'index': i,
                'pmid': article.get('pmid', ''),
                'title': article.get('title', ''),
                'authors': article.get('authors', [])[:3],
                'journal': article.get('journal', ''),
                'year': article.get('year', ''),
                'doi': article.get('doi', '')
            }
            article_map.append(info)

            lines.append(f"\n[{i}] {article.get('title', '')}")
            authors_str = ', '.join(article.get('authors', [])[:3])
            if len(article.get('authors', [])) > 3:
                authors_str += " et al."
            lines.append(f"    Authors: {authors_str}")
            lines.append(f"    Journal: {article.get('journal', '')} ({article.get('year', '')})")
            if article.get('doi'):
                lines.append(f"    DOI: {article.get('doi', '')}")
            lines.append(f"    PMID: {article.get('pmid', '')}")

            abstract = article.get('abstract', '')
            if abstract:
                if len(abstract) > max_abstract_len:
                    abstract = abstract[:max_abstract_len] + "..."
                lines.append(f"    Abstract: {abstract}")

        return "\n".join(lines), article_map

    def _build_reference_list(self, article_map: List[Dict]) -> str:
        """构建标准参考文献列表"""
        lines = []
        for info in article_map:
            authors = ', '.join(info['authors'])
            if len(info['authors']) >= 3:
                first_author = info['authors'][0] if info['authors'] else ''
                authors = f"{first_author} et al."
            ref = f"[{info['index']}] {authors}. {info['title']}. {info['journal']}. {info['year']}."
            if info['doi']:
                ref += f" DOI: {info['doi']}"
            ref += f" PMID: {info['pmid']}."
            lines.append(ref)
        return "\n".join(lines)

    def _validate_citations(self, text: str, max_index: int) -> str:
        """
        验证并修正引用编号
        确保所有 [N] 引用都在合法范围内
        """
        def replace_citation(match):
            num = int(match.group(1))
            if 1 <= num <= max_index:
                return match.group(0)
            return f"[ref-error:{num}]"

        text = re.sub(r'\[(\d+)\]', replace_citation, text)
        return text

    def generate_literature_review(
        self,
        articles: List[Dict],
        query: str,
        max_articles: int = 20
    ) -> Dict:
        """生成文献综述"""
        selected = articles[:max_articles]
        article_block, article_map = self._build_article_block(selected, max_abstract_len=600)
        reference_list = self._build_reference_list(article_map)

        system_prompt = """你是一位严谨的医学文献综述撰写专家。你必须严格遵守以下规则：

1. **引用规则**：所有陈述必须引用来源文献，使用 [编号] 格式，如 [1]、[2,3]、[1,4,5]。编号必须与下方文献列表中的编号一一对应，绝不可编造不存在的编号。
2. **禁止编造**：只使用提供的文献信息，不得添加任何文献中没有的数据、结论或观点。
3. **格式规则**：严格使用 Markdown 格式，标题用 ##，正文段落不用特殊标记。
4. **语言**：使用中文撰写，专业术语保留英文原文。
5. **参考文献**：综述末尾必须包含"参考文献"章节，格式已在模板中给出，直接复制即可，不要修改。"""

        user_prompt = f"""请基于以下 {len(selected)} 篇文献，撰写关于"{query}"的文献综述。

## 文献列表

{article_block}

---

## 输出模板（严格按此格式填写）

## 一、引言

（介绍"{query}"的研究背景、临床意义、当前面临的挑战，引用相关文献 [编号]）

## 二、研究现状

（概述当前研究的主要方向和进展，每个方向引用对应文献 [编号]）

## 三、主要研究发现

### 3.1 （第一个主要发现的主题）
（详细阐述，引用文献 [编号]）

### 3.2 （第二个主要发现的主题）
（详细阐述，引用文献 [编号]）

### 3.3 （第三个主要发现的主题）
（详细阐述，引用文献 [编号]）

## 四、讨论

（分析不同研究之间的共性和差异，讨论存在的争议和未解决的问题，引用文献 [编号]）

## 五、研究局限与展望

（总结当前研究的局限性，提出未来研究方向，引用文献 [编号]）

## 六、结论

（总结全文核心观点，强调临床或研究意义）

## 参考文献

{reference_list}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        content = self._call_api(messages, temperature=0.1)

        if content:
            content = self._validate_citations(content, len(selected))
            return {
                'success': True,
                'review': content,
                'articles_used': len(selected),
                'query': query
            }
        else:
            return {
                'success': False,
                'review': self._generate_simple_review(selected, query),
                'articles_used': len(selected),
                'query': query,
                'note': 'LLM API 调用失败，使用基于规则的简单总结'
            }

    def generate_research_summary(
        self,
        articles: List[Dict],
        query: str
    ) -> Dict:
        """生成研究总结"""
        selected = articles[:15]
        article_block, article_map = self._build_article_block(selected, max_abstract_len=500)

        system_prompt = """你是一位医学研究专家。请严格基于提供的文献信息生成研究总结。

规则：
1. 每个观点必须标注来源文献编号，格式为 [编号]
2. 不得编造文献中没有的信息
3. 使用中文，专业术语保留英文
4. 控制在500字以内"""

        user_prompt = f"""基于以下文献，生成关于"{query}"的简洁研究总结。

## 文献列表

{article_block}

---

## 输出模板

**研究背景**：（1-2句话，引用 [编号]）

**主要发现**：
- （发现1，引用 [编号]）
- （发现2，引用 [编号]）
- （发现3，引用 [编号]）

**研究方法特点**：（1-2句话，引用 [编号]）

**局限性**：（1-2句话，引用 [编号]）

**未来方向**：（1-2句话，引用 [编号]）
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        content = self._call_api(messages, temperature=0.1)

        if content:
            content = self._validate_citations(content, len(selected))
        else:
            content = self._generate_simple_summary(selected, query)

        return {
            'success': content is not None,
            'summary': content,
            'articles_used': len(selected)
        }

    def extract_key_findings(self, articles: List[Dict]) -> Dict:
        """提取关键研究发现"""
        selected = articles[:10]
        article_block, article_map = self._build_article_block(selected, max_abstract_len=400)
        reference_list = self._build_reference_list(article_map)

        system_prompt = """你是一位医学研究分析师。请严格从提供的文献中提取关键发现。

规则：
1. 每条发现必须标注来源文献编号，格式为 [编号]
2. 只提取文献中明确提到的发现，不得推断或编造
3. 按重要性排序
4. 使用中文"""

        user_prompt = f"""从以下文献中提取关键研究发现。

## 文献列表

{article_block}

---

## 输出模板

1. **（发现标题）**：（具体描述，引用 [编号]）

2. **（发现标题）**：（具体描述，引用 [编号]）

3. **（发现标题）**：（具体描述，引用 [编号]）

4. **（发现标题）**：（具体描述，引用 [编号]）

5. **（发现标题）**：（具体描述，引用 [编号]）

---

## 参考文献

{reference_list}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        content = self._call_api(messages, temperature=0.1)

        if content:
            content = self._validate_citations(content, len(selected))
        else:
            content = "API 调用失败，无法提取关键发现"

        return {
            'success': content is not None and content != "API 调用失败，无法提取关键发现",
            'findings': content,
            'articles_used': len(selected)
        }

    def analyze_clinical_significance(self, articles: List[Dict]) -> Dict:
        """分析临床意义"""
        selected = articles[:10]
        article_block, article_map = self._build_article_block(selected, max_abstract_len=400)
        reference_list = self._build_reference_list(article_map)

        system_prompt = """你是一位临床医学专家。请严格基于提供的文献信息分析临床意义。

规则：
1. 每个观点必须标注来源文献编号，格式为 [编号]
2. 不得编造文献中没有的结论
3. 使用中文，专业术语保留英文"""

        user_prompt = f"""分析以下文献的临床意义。

## 文献列表

{article_block}

---

## 输出模板

### 对临床实践的影响
（分析，引用 [编号]）

### 对指南制定的潜在贡献
（分析，引用 [编号]）

### 对患者预后的改善
（分析，引用 [编号]）

### 临床应用前景
（分析，引用 [编号]）

### 需要进一步验证的方向
（分析，引用 [编号]）

---

## 参考文献

{reference_list}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        content = self._call_api(messages, temperature=0.1)

        if content:
            content = self._validate_citations(content, len(selected))
        else:
            content = "API 调用失败"

        return {
            'success': content is not None and content != "API 调用失败",
            'clinical_analysis': content,
            'articles_used': len(selected)
        }

    def _generate_simple_review(self, articles: List[Dict], query: str) -> str:
        """生成简单的基于规则的综述（备用）"""
        if not articles:
            return "无文献数据"

        years = [a.get('year', '') for a in articles if a.get('year')]
        journals = [a.get('journal', '') for a in articles if a.get('journal')]

        from collections import Counter
        journal_counts = Counter(journals)

        review = f"## 文献综述：{query}\n\n"
        review += f"## 一、概述\n\n"
        review += f"本次检索共获取 {len(articles)} 篇相关文献。\n"
        if years:
            review += f"发表年份范围：{min(years)} - {max(years)}\n"

        review += f"\n## 二、主要来源期刊\n\n"
        for journal, count in journal_counts.most_common(5):
            review += f"- {journal}：{count} 篇\n"

        review += f"\n## 三、文献列表\n\n"
        for i, article in enumerate(articles[:10], 1):
            authors = ', '.join(article.get('authors', [])[:3])
            review += f"[{i}] {article.get('title', '')}\n"
            review += f"    {authors}. {article.get('journal', '')} ({article.get('year', '')}). PMID: {article.get('pmid', '')}\n\n"

        if len(articles) > 10:
            review += f"... 等共 {len(articles)} 篇文献\n"

        review += "\n> 注：此为基于规则的自动生成综述。配置 LLM API 密钥可获得更深入的分析。\n"
        return review

    def _generate_simple_summary(self, articles: List[Dict], query: str) -> str:
        """生成简单总结（备用）"""
        if not articles:
            return "无文献数据"

        summary = f'关于"{query}"的检索共找到 {len(articles)} 篇文献。\n\n'
        summary += "主要研究包括：\n"

        for i, article in enumerate(articles[:5], 1):
            summary += f"[{i}] {article.get('title', '')}\n"

        return summary


def generate_llm_review(
    articles: List[Dict],
    query: str,
    api_key: Optional[str] = None
) -> Dict:
    """便捷的 LLM 综述生成函数"""
    analyzer = LLMAnalyzer(api_key=api_key)
    return analyzer.generate_literature_review(articles, query)
