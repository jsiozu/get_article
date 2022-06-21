import json
import time
import urllib.request
import pickle
import requests
from bs4 import BeautifulSoup

with open('./ip_list.json', 'r', encoding='utf-8') as f:
    proxy_list = json.load(f)
print(len(proxy_list))
# define a header to address the error: 'HTTP Error 403: Forbidden'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 ' \
             'Safari/537.36 '
headers = {'User-Agent': user_agent, }


def get_ip():
    i = 0
    for proxy_ip in proxy_list:
        yield proxy_ip
        i += 1
        print(i)


ip_literator = get_ip()


def get_response(url, i):
    """
    此方法获取url对应的页面的html数据
    :param url: 要访问的页面的链接
    :param i: 重复尝试访问次数，超过一定次数放弃此页面
    :return:
    """

    try:
        if i > 15:
            i = 0
            proxy_ip = next(ip_literator)
            proxy_handler = urllib.request.ProxyHandler(proxy_ip)
            opener = urllib.request.build_opener(proxy_handler)
            request = urllib.request.Request(url, None, headers)
            response = opener.open(request, timeout=15)
            return response.read()
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
        page_visited = int(pickle.load(open("武器百科_陆军装备_data/page_visited.p", "rb")))  # 记录该页面是否被访问过
    except:
        page_visited = 1
    return page_visited


def search_article(soup):
    """
    此方法搜索页面中可以访问的文章
    :param soup: html页面解析后的结果封装在soup里
    :return: 文章待访问列表
    """

    article_list = []  # 存储当前页要访问的文章的链接
    div_tag = soup.find('div', class_='r group1 bor-ccc cate_show')  # 所有文章数据都存放在div标签中，从页面中找到此标签
    dl_tags = div_tag.find_all('dl')  # 文章放在ul标签中，因此获取ul标签
    for dl in dl_tags:  # 遍历搜索到的ul中的li标签
        href = article_path + dl.find('dt', class_='h2').find('a').get('href')  # 文章链接存储在a标签的href属性中
        if href not in article_list:
            article_list.append(href)
    return article_list


def read_article(soup):
    """
    此方法获取文章内容
    :param soup: html解析后的数据存放在soup里
    :param article_visited: 文章访问记录
    :return: 返回文章访问记录，此方法对其进行了更新
    """
    try:
        article = soup.find('article', class_='bor-ccc')  # 文章内容存储在此类article标签中
        # 获取标题
        title = article.find('div', class_='title_thema').find('h1').text
        # 获取文章正文内容
        summary = article.find('div', id='summary').find('div', class_='des').text
        content = article.find('div', class_='content_1 clearfix').find('div', class_='content_topp').text.replace(
            u'\xa0', u'').replace('\t', '').replace('\r', '')
        # 将获取的文章保存到json文件中
        title = title.replace('-', '_').replace(' ', '_').replace('|', '').replace('?', '').replace('#', '').replace(
            ';', '').replace('_', '').replace('\'', '').replace('\"', '').replace(
            '/', ' ').replace('\n', '').strip()
        filename = './武器百科_陆军装备_data/' + title + '.txt'
        to_save = {'title': title, 'summary': summary, 'content': content}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(to_save, f, ensure_ascii=False)
    except:
        return False


page = "http://www.wuqibaike.com/index.php?category-view-1-"  # 记录需要访问的页面链接
article_path = 'http://www.wuqibaike.com/'  # 文章基准链接

page_visited = load_history()  # 加载访问历史

TOTAL_PAGE = 792  # 该网站可访问的总页面数
page_num = page_visited  # 开始访问的页面
print(page_num)

# 开始访问页面
while page_num <= TOTAL_PAGE:  # 需要访问的页面还没有访问完

    # 获取页面内容
    html = get_response(page + str(page_num), 0)
    # 解析网页内容
    soup = BeautifulSoup(html, 'html.parser')
    while "该IP地址被禁止访问" in soup.text:
        html = get_response(page + str(page_num), 16)
        soup = BeautifulSoup(html, 'html.parser')
    # 获取要抓取的文章的链接
    article_list = search_article(soup)

    # 遍历当前页面的每一篇文章
    for article in article_list:
        # 获取页面内容
        html = get_response(article, 0)
        if html is None:
            continue
        # 解析网页内容
        soup = BeautifulSoup(html, 'html.parser')
        # 获取文章内容并保存，以文章题目问保存的文件名称
        flag = read_article(soup)
        if flag is False:
            exit(0)
        # 防止爬虫检测，休眠1秒
        time.sleep(1)

    # 该页面文章访问完成，将该页面标记为已访问,并将访问记录保存
    pickle.dump(page_num, open("武器百科_陆军装备_data/page_visited.p", "wb"))
    print(page + str(page_num) + '.html')
    # 访问下一个页面
    page_num += 1
