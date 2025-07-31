"""
中国网站访问配置
Configuration for accessing Chinese domestic websites
"""

# 中国主要搜索引擎
CHINESE_SEARCH_ENGINES = {
    "bing": "https://www.bing.com/search?q={query}&FORM=QBLH&hl=en",
    "baidu": "https://www.baidu.com/s?wd={query}&ie=utf-8",
    "sogou": "https://www.sogou.com/web?query={query}",
    "360": "https://www.so.com/s?q={query}",
    "bing_cn": "https://cn.bing.com/search?q={query}"
}

# 浏览器配置优化
BROWSER_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "accept_language": "zh-CN,zh;q=0.9,en;q=0.8",
    "timeout": 10000,  # 增加超时时间
    "wait_time": 5000   # 等待页面加载时间
}

# 代理配置（可选）
PROXY_CONFIG = {
    "enabled": False,
    "http_proxy": None,
    "https_proxy": None,
    "socks_proxy": None
}

def get_search_url(query: str, engine: str = "bing") -> str:
    """获取搜索引擎URL"""
    if engine in CHINESE_SEARCH_ENGINES:
        return CHINESE_SEARCH_ENGINES[engine].format(query=query)
    else:
        return CHINESE_SEARCH_ENGINES["bing"].format(query=query)

def optimize_for_chinese_sites(url: str) -> dict:
    """为中国网站优化浏览器配置"""
    # 简化逻辑：统一使用中文优化配置
    return {
        "user_agent": BROWSER_CONFIG["user_agent"],
        "accept_language": BROWSER_CONFIG["accept_language"],
        "timeout": BROWSER_CONFIG["timeout"],
        "wait_time": BROWSER_CONFIG["wait_time"]
    } 