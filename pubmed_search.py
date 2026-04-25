"""
PubMed 文献检索模块
使用 NCBI E-utilities API 进行文献检索
"""

import time
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from config import (
    NCBI_EMAIL, NCBI_API_KEY, NCBI_BASE_URL,
    REQUEST_DELAY, TIMEOUT, MAX_RETRIES, DEFAULT_RETMAX
)


class PubMedSearcher:
    """PubMed文献检索器"""

    def __init__(self):
        self.email = NCBI_EMAIL
        self.api_key = NCBI_API_KEY
        self.base_url = NCBI_BASE_URL
        self.delay = REQUEST_DELAY
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"PubMedResearchTool/1.0 ({self.email})"
        })

    def _make_request(self, url: str, params: Dict) -> Optional[str]:
        """发送请求并处理重试"""
        params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key

        for attempt in range(MAX_RETRIES):
            try:
                time.sleep(self.delay)
                response = self.session.get(
                    url,
                    params=params,
                    timeout=(10, TIMEOUT),  # (连接超时, 读取超时)
                    verify=True
                )
                response.raise_for_status()
                return response.text
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{MAX_RETRIES})，等待后重试...")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(5 * (attempt + 1))  # 增加等待时间
                else:
                    return None
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
        return None

    def search(
        self,
        query: str,
        retmax: int = DEFAULT_RETMAX,
        sort: str = "relevance",
        mindate: Optional[str] = None,
        maxdate: Optional[str] = None
    ) -> Dict:
        """
        检索PubMed文献

        Args:
            query: 检索词（支持PubMed高级检索语法）
            retmax: 返回最大数量
            sort: 排序方式 (relevance/pub_date)
            mindate: 起始日期 (YYYY/MM/DD 或 YYYY)
            maxdate: 结束日期 (YYYY/MM/DD 或 YYYY)

        Returns:
            包含 total_count, pmid_list, query_translation 的字典
        """
        url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": min(retmax, 10000),
            "retmode": "xml",
            "sort": sort,
            "usehistory": "y"
        }

        if mindate:
            params["mindate"] = mindate
        if maxdate:
            params["maxdate"] = maxdate

        print(f"正在检索: {query}")
        response_text = self._make_request(url, params)

        if not response_text:
            return {"total_count": 0, "pmid_list": [], "query_translation": ""}

        root = ET.fromstring(response_text)

        # 获取检索结果数量
        count_elem = root.find(".//Count")
        total_count = int(count_elem.text) if count_elem is not None else 0

        # 获取实际返回的PMID列表
        pmid_list = [
            elem.text for elem in root.findall(".//IdList/Id")
            if elem.text
        ]

        # 获取查询翻译（PubMed实际执行的检索式）
        translation_elem = root.find(".//QueryTranslation")
        query_translation = translation_elem.text if translation_elem is not None else ""

        # 获取WebEnv和QueryKey用于后续批量获取
        webenv_elem = root.find(".//WebEnv")
        querykey_elem = root.find(".//QueryKey")

        result = {
            "total_count": total_count,
            "pmid_list": pmid_list,
            "query_translation": query_translation,
            "webenv": webenv_elem.text if webenv_elem is not None else None,
            "query_key": querykey_elem.text if querykey_elem is not None else None
        }

        print(f"检索完成: 共找到 {total_count} 篇文献，本次获取 {len(pmid_list)} 篇")
        if query_translation:
            print(f"检索式转换: {query_translation}")

        return result

    def fetch_details(
        self,
        pmid_list: List[str],
        webenv: Optional[str] = None,
        query_key: Optional[str] = None
    ) -> List[Dict]:
        """
        获取文献详细信息

        Args:
            pmid_list: PMID列表
            webenv: ESearch返回的WebEnv (未使用，仅保留兼容性)
            query_key: ESearch返回的QueryKey (未使用，仅保留兼容性)

        Returns:
            文献详情列表
        """
        if not pmid_list:
            return []

        url = f"{self.base_url}/efetch.fcgi"
        all_articles = []

        # 分批获取，每批200篇
        batch_size = 200
        total_to_fetch = len(pmid_list)

        for i in range(0, total_to_fetch, batch_size):
            batch = pmid_list[i:i + batch_size]
            print(f"获取文献详情: {i + 1} - {min(i + len(batch), total_to_fetch)} / {total_to_fetch}")

            params = {
                "db": "pubmed",
                "retmode": "xml",
                "rettype": "medline",
                "id": ",".join(batch)
            }

            response_text = self._make_request(url, params)
            if response_text:
                articles = self._parse_articles(response_text)
                all_articles.extend(articles)

        return all_articles

    def _parse_articles(self, xml_text: str) -> List[Dict]:
        """解析PubMed XML返回的文献信息"""
        articles = []
        root = ET.fromstring(xml_text)

        for article_elem in root.findall(".//PubmedArticle"):
            article = self._extract_article_info(article_elem)
            if article:
                articles.append(article)

        return articles

    def _extract_article_info(self, article_elem) -> Optional[Dict]:
        """从XML元素中提取单篇文献信息"""
        try:
            medline = article_elem.find("MedlineCitation")
            if medline is None:
                return None

            pmid = self._get_text(medline, "PMID")
            if not pmid:
                return None

            article = medline.find("Article")
            if article is None:
                return None

            # 标题
            title = self._get_text(article, "ArticleTitle", "")

            # 摘要
            abstract_elem = article.find("Abstract")
            abstract = ""
            if abstract_elem is not None:
                abstract_parts = []
                for abs_text in abstract_elem.findall("AbstractText"):
                    label = abs_text.get("Label", "")
                    text = abs_text.text or ""
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                abstract = "\n".join(abstract_parts)

            # 作者列表
            authors = []
            author_list = article.find("AuthorList")
            if author_list is not None:
                for author in author_list.findall("Author"):
                    lastname = self._get_text(author, "LastName", "")
                    forename = self._get_text(author, "ForeName", "")
                    initials = self._get_text(author, "Initials", "")
                    if lastname:
                        if forename:
                            authors.append(f"{lastname} {forename}")
                        elif initials:
                            authors.append(f"{lastname} {initials}")
                        else:
                            authors.append(lastname)

            # 期刊信息
            journal = article.find("Journal")
            journal_title = ""
            pub_date = ""
            if journal is not None:
                journal_title = self._get_text(journal, "Title", "")
                pub_date = self._parse_pub_date(journal)

            # DOI
            doi = ""
            for id_elem in article_elem.findall(".//ArticleId"):
                if id_elem.get("IdType") == "doi":
                    doi = id_elem.text or ""
                    break

            # 关键词
            keywords = []
            keyword_list = medline.find("KeywordList")
            if keyword_list is not None:
                for kw in keyword_list.findall("Keyword"):
                    if kw.text:
                        keywords.append(kw.text)

            # MeSH主题词
            mesh_terms = []
            mesh_list = medline.find("MeshHeadingList")
            if mesh_list is not None:
                for mesh in mesh_list.findall("MeshHeading"):
                    desc = mesh.find("DescriptorName")
                    if desc is not None and desc.text:
                        mesh_terms.append(desc.text)

            # 发表类型
            pub_types = []
            for pt in article.findall("PublicationTypeList/PublicationType"):
                if pt.text:
                    pub_types.append(pt.text)

            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "first_author": authors[0] if authors else "",
                "journal": journal_title,
                "pub_date": pub_date,
                "year": pub_date[:4] if pub_date and len(pub_date) >= 4 else "",
                "doi": doi,
                "keywords": keywords,
                "mesh_terms": mesh_terms,
                "publication_types": pub_types,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }

        except Exception as e:
            print(f"解析文献时出错: {e}")
            return None

    def _get_text(self, parent, tag: str, default: str = "") -> str:
        """安全获取XML元素文本"""
        elem = parent.find(tag)
        return elem.text if elem is not None and elem.text else default

    def _parse_pub_date(self, journal_elem) -> str:
        """解析发表日期"""
        pub_date = ""
        journal_issue = journal_elem.find("JournalIssue")
        if journal_issue is not None:
            pub_date_elem = journal_issue.find("PubDate")
            if pub_date_elem is not None:
                year = self._get_text(pub_date_elem, "Year", "")
                month = self._get_text(pub_date_elem, "Month", "")
                day = self._get_text(pub_date_elem, "Day", "")

                # 处理MedlineDate格式 (如 "2023 Jan-Feb")
                medline_date = self._get_text(pub_date_elem, "MedlineDate", "")
                if medline_date:
                    pub_date = medline_date
                elif year:
                    pub_date = year
                    if month:
                        pub_date += f"-{month}"
                        if day:
                            pub_date += f"-{day}"

        return pub_date


def search_pubmed(
    query: str,
    max_results: int = 100,
    date_range: Optional[tuple] = None,
    sort_by: str = "relevance"
) -> List[Dict]:
    """
    便捷的PubMed检索函数

    Args:
        query: 检索词
        max_results: 最大结果数
        date_range: 日期范围 (起始年, 结束年) 如 ("2020", "2023")
        sort_by: 排序方式

    Returns:
        文献详情列表
    """
    searcher = PubMedSearcher()

    mindate = date_range[0] if date_range else None
    maxdate = date_range[1] if date_range else None

    search_result = searcher.search(
        query=query,
        retmax=max_results,
        sort=sort_by,
        mindate=mindate,
        maxdate=maxdate
    )

    if not search_result["pmid_list"]:
        return []

    articles = searcher.fetch_details(search_result["pmid_list"])

    return articles


if __name__ == "__main__":
    # 测试示例
    results = search_pubmed(
        query="diabetes mellitus treatment",
        max_results=5
    )
    for article in results:
        print(f"\n标题: {article['title']}")
        print(f"作者: {', '.join(article['authors'][:3])}")
        print(f"期刊: {article['journal']}")
        print(f"日期: {article['pub_date']}")
        print(f"PMID: {article['pmid']}")
