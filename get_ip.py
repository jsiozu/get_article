import json
import time
import urllib.request
import pickle
import requests
from bs4 import BeautifulSoup


def get_response(url, i):
    """
    此方法获取url对应的页面的html数据
    :param url: 要访问的页面的链接
    :param i: 重复尝试访问次数，超过一定次数放弃此页面
    :return:
    """

    try:
        if i > 15:
            return None
        # define a header to address the error: 'HTTP Error 403: Forbidden'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 ' \
                     'Safari/537.36 '
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(url, None, headers)  # The assembled request
        response = urllib.request.urlopen(request, timeout=15)
        return response.read()
    except:
        get_response(url, i + 1)


def load_history():
    """
    此方法加载历史访问信息
    :return:
    """

    try:
        # load urls
        page_visited = int(pickle.load(open("./ip_history.p", "rb")))  # 记录该页面是否被访问过
    except:
        page_visited = 1
    return page_visited


def load_ip_list():
    try:
        # load urls
        with open('./ip_list.json', 'r', encoding='utf-8') as f:
            ip_list = json.load(f)
    except:
        ip_list = []
    return ip_list


def search_ip(soup, ip_list):
    """
    此方法搜索页面中可以访问的文章
    :param soup: html页面解析后的结果封装在soup里
    :return: 文章待访问列表
    """

    table = soup.find('table')  # 所有文章数据都存放在div标签中，从页面中找到此标签
    tr_tags = table.find_all('tr')
    for tr in tr_tags[1:]:
        xieyi = tr.find_all('td')[4].text
        ip = tr.find_all('td')[1].text
        port = tr.find_all('td')[2].text
        ip_list.append({xieyi: ip + ':' + port})  # 文章链接存储在a标签的href属性中


page = "http://ip.yqie.com/proxygaoni/index"  # 记录需要访问的页面链接
article_path = 'http://www.wuqibaike.com/'  # 文章基准链接

page_visited = load_history()  # 加载访问历史

TOTAL_PAGE = 3423  # 该网站可访问的总页面数
page_num = page_visited  # 开始访问的页面
print(page_num)

ip_list = load_ip_list()
# 开始访问页面
while page_num <= TOTAL_PAGE:  # 需要访问的页面还没有访问完

    # 获取页面内容
    if page_num == 1:
        html = get_response(page + '.htm', 0)
    else:
        html = get_response(page + '_' + str(page_num) + '.htm', 0)

    # 解析网页内容
    soup = BeautifulSoup(html, 'html.parser')
    # 获取要抓取的文章的链接
    search_ip(soup, ip_list)

    time.sleep(1)

    with open('./ip_list.json', 'w', encoding='utf-8') as f:
        json.dump(ip_list, f, ensure_ascii=False)
    # 该页面文章访问完成，将该页面标记为已访问,并将访问记录保存
    pickle.dump(page_num, open("./ip_history.p", "wb"))
    print(page + '_' + str(page_num) + '.htm')
    # 访问下一个页面
    page_num += 1
