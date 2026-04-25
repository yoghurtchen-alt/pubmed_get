"""
PubMed 文献检索工具配置文件
建议到 NCBI 注册邮箱以获取更高访问频率：
https://www.ncbi.nlm.nih.gov/account/
"""

# NCBI API 配置
NCBI_EMAIL = "chenmingyaodr@outlook.com"  # 请替换为你的邮箱
NCBI_API_KEY = "2a5b8ff6ea8fc5d53e8637ac412b3a891a09"  # 可选，申请后填入可提高访问频率
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# 请求配置
REQUEST_DELAY = 0.5  # 无API Key时建议间隔0.5秒
TIMEOUT = 60  # 增加超时时间
MAX_RETRIES = 3

# 检索配置
DEFAULT_RETMAX = 100  # 默认返回文献数量
MAX_RETMAX = 10000   # 单次最大返回数量

# 输出配置
OUTPUT_DIR = "output"
DEFAULT_REPORT_NAME = "文献研究报告"
