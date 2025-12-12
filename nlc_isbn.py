# nlc_isbn.py

import re
import requests
from bs4 import BeautifulSoup
from headers import get_opacnlc_headers

BASE_URL = "http://opac.nlc.cn/F"


def get_dynamic_url(update_status):
    try:
        # 使用 Session 保持会话状态
        session = requests.Session()
        session.headers.update(get_opacnlc_headers())

        # 获取初始页面以获得动态URL
        response = session.get(BASE_URL, timeout=10)
        response.encoding = 'utf-8'

        dynamic_url_match = re.search(r"http://opac.nlc.cn:80/F/[^\s?]*", response.text)
        if dynamic_url_match:
            dynamic_url = dynamic_url_match.group(0)
            update_status(f"动态URL: {dynamic_url}")
            return dynamic_url, session
        else:
            raise ValueError("无法找到动态URL")
    except Exception as e:
        update_status(f"获取动态URL时出错: {e}")
        return None, None


def isbn2meta(isbn, update_status):
    if not isinstance(isbn, str):
        update_status("ISBN必须是字符串")
        return None

    try:
        isbn_match = re.match(r"\d{10,}", isbn).group()
    except AttributeError:
        update_status(f"无效的ISBN代码: {isbn}")
        return None

    if isbn_match != isbn:
        update_status(f"无效的ISBN代码: {isbn}")
        return None

    dynamic_url, session = get_dynamic_url(update_status)
    if not dynamic_url:
        return None

    # 构建查询参数
    params = {
        "func": "find-b",
        "find_code": "ISB",
        "request": isbn,
        "local_base": "NLC01",
        "filter_code_1": "WLN",
        "filter_request_1": "",
        "filter_code_2": "WYR",
        "filter_request_2": "",
        "filter_code_3": "WYR",
        "filter_request_3": "",
        "filter_code_4": "WFM",
        "filter_request_4": "",
        "filter_code_5": "WSL",
        "filter_request_5": ""
    }

    try:
        # 使用获取到的 session 和 dynamic_url 发起查询
        response = session.get(dynamic_url, params=params, timeout=15)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        return parse_metadata(soup, isbn, update_status)
    except Exception as e:
        update_status(f"获取元数据时出错: {e}")
        return None


def parse_metadata(soup, isbn, update_status):
    data = {}
    prev_td1 = ''
    prev_td2 = ''

    try:
        table = soup.find("table", attrs={"id": "td"})
        if not table:
            # 有时候没有直接结果，可能是列表页，这里暂保留原逻辑，若无 table 则视为未找到
            return None
    except Exception as e:
        update_status(f"解析元数据时出错: {e}")
        return None

    tr_elements = table.find_all('tr')

    for tr in tr_elements:
        td_elements = tr.find_all('td', class_='td1')
        if len(td_elements) == 2:
            td1 = td_elements[0].get_text(strip=True).replace('\n', '').replace('\xa0', ' ')
            td2 = td_elements[1].get_text(strip=True).replace('\n', '').replace('\xa0', ' ')
            if td1 == '' and td2 == '':
                continue
            if td1:
                data.update({td1: td2.strip()})
            else:
                data.update({prev_td1: '\n'.join([prev_td2, td2]).strip()})
            prev_td1 = td1.strip()
            prev_td2 = td2.strip()

    pubdate_match = re.search(r',\s*(\d{4})', data.get("出版项", ""))
    pubdate = pubdate_match.group(1) if pubdate_match else ""

    publisher_match = re.search(r':\s*(.+),\s', data.get("出版项", ""))
    publisher = publisher_match.group(1) if publisher_match else ""

    tags = data.get("主题", "").replace('--', '&')
    tags += f' & {data.get("中图分类号", "")}'
    tags += f' & {publisher}'
    tags += f' & {pubdate}'
    tags = tags.split(' & ')

    metadata = {
        "title": data.get("题名与责任", f"{isbn}"),
        "tags": tags,
        "comments": data.get("内容提要", ""),
        'publisher': publisher,
        'pubdate': pubdate,
        'authors': data.get("著者", "").split(' & '),
        "isbn": isbn,
        "vector morphological term": data.get("载体形态项", ""),
    }

    return metadata