import random
import requests
import re

# 支持的图片后缀
IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


def is_url(s):
    return isinstance(s, str) and s.strip().startswith(('http://', 'https://'))


def is_image_url(url):
    return url.lower().endswith(IMG_EXTS)


def get_urls_from_text(text):
    """从文本中提取所有图片URL"""
    urls = re.findall(r'https?://[^\s,\"]+', text)
    return [u for u in urls if is_image_url(u)]


def get_network_image_url(config_value):
    """
    根据配置值自动识别并返回一个可用的图片URL。
    支持：
    - 单个图片直链
    - 多个图片直链（逗号分隔）
    - 直接返回图片的API
    - 返回json/txt的API（自动提取图片URL）
    """
    if not config_value:
        return None
    # 逗号分隔多个URL
    if ',' in config_value:
        candidates = [u.strip() for u in config_value.split(',') if u.strip()]
        candidates = [u for u in candidates if is_url(u)]
        if candidates:
            return random.choice(candidates)
    # 单个URL
    url = config_value.strip()
    if not is_url(url):
        return None
    # 1. 直链图片
    if is_image_url(url):
        return url
    # 2. 直接返回图片内容或302跳转的API，直接用作图片src
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        ct = resp.headers.get('Content-Type', '')
        if ct.startswith('image/'):
            return resp.url  # 直链或跳转后的图片
    except Exception:
        pass
    # 3. 尝试GET请求，解析json/txt
    try:
        resp = requests.get(url, timeout=5)
        ct = resp.headers.get('Content-Type', '')
        if ct.startswith('image/'):
            return resp.url
        # json格式
        if 'json' in ct:
            data = resp.json()
            # 常见格式：{"url": "..."} 或 list
            if isinstance(data, dict):
                for k in ['url', 'image', 'img', 'src']:
                    if k in data and is_image_url(data[k]):
                        return data[k]
            elif isinstance(data, list):
                imgs = [x for x in data if isinstance(x, str) and is_image_url(x)]
                if imgs:
                    return random.choice(imgs)
        # txt格式
        if 'text' in ct:
            urls = get_urls_from_text(resp.text)
            if urls:
                return random.choice(urls)
    except Exception:
        pass
    # 兜底：直接返回原始url（如API每次都返回图片）
    return url


def count_network_images(config_value):
    """
    统计网络图片数量（全部显示未知）
    """
    if not config_value:
        return 0
    return None

def _count_from_url(url):
    try:
        resp = requests.get(url, timeout=5)
        ct = resp.headers.get('Content-Type', '')
        if ct.startswith('image/'):
            return 1
        if 'json' in ct:
            data = resp.json()
            if isinstance(data, dict):
                for k in ['url', 'image', 'img', 'src', 'images', 'imgs']:
                    v = data.get(k)
                    if isinstance(v, str) and is_image_url(v):
                        return 1
                    if isinstance(v, list):
                        return len([x for x in v if isinstance(x, str) and is_image_url(x)])
                return len(get_urls_from_text(str(data)))
            elif isinstance(data, list):
                return len([x for x in data if isinstance(x, str) and is_image_url(x)])
        if 'text' in ct:
            urls = get_urls_from_text(resp.text)
            return len(urls)
    except Exception:
        pass
    return None 