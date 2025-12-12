# bookmarkget.py

import requests
from bs4 import BeautifulSoup
import headers


def get_book_details(isbn):
    # 尝试搜索ISBN
    result = search_isbn(isbn)

    # 如果是13位ISBN且未找到匹配的书籍，则尝试截取后10位再次搜索
    if len(isbn) == 13 and result == "未找到匹配的书籍":
        isbn_10 = isbn[3:]
        result = search_isbn(isbn_10)

    return result


def search_isbn(isbn):
    # 搜索页面的URL
    search_url = f"https://www.shukui.net/so/search.php"
    params = {'q': isbn}

    try:
        # 发送请求到搜索页面
        response = requests.get(search_url, params=params, headers=headers.get_shukui_headers(), timeout=10)

        if response.status_code != 200:
            return "无法访问，请稍后重试"

        response.encoding = 'utf-8'
        html = response.text

        # 解析搜索结果页面的HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 寻找第一个 cate-item 元素
        cate_item = soup.find('div', class_='cate-item')
        if not cate_item:
            return "未找到匹配的书籍"

        # 从 cate-item 中提取详情页面的相对链接
        link_tag = cate_item.find('a')
        if not link_tag:
            return "未找到详情链接"

        relative_link = link_tag['href']
        details_url = f"https://www.shukui.net{relative_link}"

        # 请求书籍详情页面
        details_response = requests.get(details_url, headers=headers.get_shukui_headers(), timeout=10)

        if details_response.status_code != 200:
            return "无法访问书籍详情页面，请稍后重试"

        details_response.encoding = 'utf-8'
        details_html = details_response.text

        # 解析书籍详情页面
        details_soup = BeautifulSoup(details_html, 'html.parser')

        # 提取 id="book-contents" 的内容
        book_contents = details_soup.find(id="book-contents")
        if not book_contents:
            return "无法找到书籍内容"

        return book_contents.text.strip()

    except Exception as e:
        return f"获取书签出错: {str(e)}"