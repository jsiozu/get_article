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


def load_history(dir_name):
    """
    此方法加载历史访问信息
    :return:
    """

    try:
        page_visited = pickle.load(open("./" + dir_name + "/page_visited.p", "rb"))  # 记录该页面是否被访问过
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
    div_tag = soup.find('div', class_='listMidContent')  # 所有文章数据都存放在div标签中，从页面中找到此标签
    ul = div_tag.find('ul')  # 文章放在ul标签中，因此获取ul标签
    li_tags = ul.find_all('li')
    for li in li_tags:  # 遍历搜索到的ul中的li标签
        href = article_path + li.find('a').get('href')  # 文章链接存储在a标签的href属性中
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

    article_div = soup.find('div', class_='showLeft')  # 文章内容存储在此类div标签中
    # 获取标题
    title = article_div.find('div', class_='newsTitle').text
    # 获取文章正文内容
    text = article_div.find('div', class_='newsContent').text
    body_list = text.replace(u'\xa0', u'').replace('\t', '').replace('\r', '').split('\n')  # 存储文章每一段
    # 将获取的文章保存到txt文件中
    title = title.replace('-', '_').replace('\r', '').replace('*', '').replace(' ', '_').replace('>', '').replace('?', '').replace('#', '').replace(';', '').replace('_', '').replace('\'', '').replace('\"', '').replace(
        '/', ' ').replace('\n', '').strip()
    filename = './' + dir_name + '/' + title + '.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for text in body_list:
            if len(text) > 1:
                f.write(text)
                f.write('\n')
        f.flush()


dir_name = '国防科技信息网_军工电子_data'  # 爬取数据存储的文件夹，访问记录也从中加载
page_visited = load_history(dir_name)  # 加载访问历史

page = "http://www.dsti.net/Information/HyeList/electron/"  # 记录需要访问的页面链接
article_path = 'http://www.dsti.net'  # 文章链接的基本路径
TOTAL_PAGE = 696  # 该网站可访问的总页面数
page_num = page_visited  # 开始访问的页面
print(page_num)


# 开始访问页面
while page_num <= TOTAL_PAGE:  # 需要访问的页面还没有访问完

    # 获取页面内容
    html = get_response(page + str(page_num), 0)
    # 解析网页内容
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
        read_article(soup)
        # 防止爬虫检测，休眠1秒
        time.sleep(1)

    # 该页面文章访问完成，将该页面标记为已访问,并将访问记录保存
    pickle.dump(page_num, open("./" + dir_name + "/page_visited.p", "wb"))
    print(page + str(page_num))
    # 访问下一个页面
    page_num += 1
