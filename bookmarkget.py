# bookmarkget.py

import urllib.request

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
    search_url = f"https://www.shukui.net/so/search.php?q={isbn}"

    try:
        req = urllib.request.Request(search_url, headers=headers.get_shukui_headers())

        # 发送请求到搜索页面
        with urllib.request.urlopen(req) as response:
            if response.getcode() != 200:
                return "无法访问，请稍后重试"
            html = response.read().decode('utf-8')

        # 解析搜索结果页面的HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 寻找第一个 cate-item 元素
        cate_item = soup.find('div', class_='cate-item')
        if not cate_item:
            return "未找到匹配的书籍"

        # 从 cate-item 中提取详情页面的相对链接
        relative_link = cate_item.find('a')['href']

        # 拼接得到完整的书籍详情页面URL
        details_url = f"https://www.shukui.net{relative_link}"

        # 创建详情页面请求对象，再次使用headers模块中的get_headers函数
        details_req = urllib.request.Request(details_url, headers=headers.get_shukui_headers())

        # 请求书籍详情页面
        with urllib.request.urlopen(details_req) as details_response:
            if details_response.getcode() != 200:
                return "无法访问书籍详情页面，请稍后重试"
            details_html = details_response.read().decode('utf-8')

        # 解析书籍详情页面
        details_soup = BeautifulSoup(details_html, 'html.parser')

        # 提取 id="book-contents" 的内容
        book_contents = details_soup.find(id="book-contents")
        if not book_contents:
            return "无法找到书籍内容"

        return book_contents.text

    except Exception as e:
        return str(e)


# 测试函数
# isbn = "9787111532414"
# print(get_book_details(isbn))
