# nlc_isbn.py

import re
import urllib.request

from bs4 import BeautifulSoup

from headers import get_opacnlc_headers

BASE_URL = "http://opac.nlc.cn/F"
SEARCH_URL_TEMPLATE = BASE_URL + "?func=find-b&find_code=ISB&request={isbn}&local_base=NLC01" + \
                      "&filter_code_1=WLN&filter_request_1=&filter_code_2=WYR&filter_request_2=" + \
                      ("&filter_code_3=WYR&filter_request_3=&filter_code_4=WFM&filter_request_4=&filter_code_5=WSL"
                       "&filter_request_5=")


def get_dynamic_url(update_status):
    try:
        response = urllib.request.urlopen(urllib.request.Request(BASE_URL, headers=get_opacnlc_headers()), timeout=10)
        response_text = response.read().decode('utf-8')
        dynamic_url_match = re.search(r"http://opac.nlc.cn:80/F/[^\s?]*", response_text)
        if dynamic_url_match:
            update_status(f"动态URL: {dynamic_url_match.group(0)}")
            return dynamic_url_match.group(0)
        else:
            raise ValueError("无法找到动态URL")
    except Exception as e:
        update_status(f"获取动态URL时出错: {e}")
        return None


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

    dynamic_url = get_dynamic_url(update_status)
    if not dynamic_url:
        return None

    search_url = SEARCH_URL_TEMPLATE.format(isbn=isbn)
    try:
        response = urllib.request.urlopen(urllib.request.Request(search_url, headers=get_opacnlc_headers()), timeout=10)
        response_text = response.read().decode('utf-8')
        soup = BeautifulSoup(response_text, "html.parser")
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
