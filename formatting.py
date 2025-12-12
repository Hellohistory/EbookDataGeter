# formatting.py

def format_metadata(metadata):
    formatted_str = ""

    # 标题
    title = metadata.get('title', '无标题').split('/')[0].strip()
    formatted_str += f"标题: {title}\n"

    # 作者
    authors = metadata.get('authors', [])
    if authors:
        # 保持原始作者信息的完整性
        authors_formatted = '; '.join(authors)
    else:
        authors_formatted = '未知作者'
    formatted_str += f"作者: {authors_formatted}\n"

    # 出版信息
    publisher = metadata.get('publisher', '未知出版社')
    pubdate = metadata.get('pubdate', '未知日期')
    formatted_str += f"出版社: {publisher}\n"
    formatted_str += f"出版年份: {pubdate}\n"

    # ISBN
    isbn = metadata.get('isbn', '未知ISBN')
    formatted_str += f"ISBN: {isbn}\n"

    # 标签处理
    tags = metadata.get('tags', [])
    formatted_str += f"标签: {', '.join(tags)}\n"

    # 内容摘要
    comments = metadata.get('comments', '无内容摘要')
    formatted_str += f"\n内容摘要:\n{comments}\n"

    # 其他信息
    vector_term = metadata.get('vector morphological term', '')
    if vector_term:
        formatted_str += f"\n其他信息: {vector_term}\n"

    return formatted_str