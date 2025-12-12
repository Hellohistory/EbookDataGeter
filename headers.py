# headers.py

import random


def generate_user_agents(num_agents):
    user_agents = []

    for _ in range(num_agents):
        user_agent = (
            f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            f'Chrome/{random.randint(1, 200)}.0.0.0 Safari/537.36 Edg/{random.randint(1, 200)}.0.0.0'
        )
        user_agents.append(user_agent)

    return user_agents


user_agents = generate_user_agents(20)

Accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8, ' \
          'application/signed-exchange;v=b3;q=0.7'


def get_opacnlc_headers():
    return {
        'Accept': Accept,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Host': 'opac.nlc.cn',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': random.choice(user_agents)
    }


def get_shukui_headers():
    return {
        'Accept': Accept,
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Host': 'www.shukui.net',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': random.choice(user_agents),
        'Referer': 'https://www.shukui.net/'
    }