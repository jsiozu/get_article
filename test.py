import pickle
dir_name = '国防科技信息网_兵器工业_data'
def load_history():
    """
    此方法加载历史访问信息
    :return:
    """

    try:
        print("./" + dir_name + "/page_visited.p")
        page_visited = pickle.load(open("./" + dir_name + "/page_visited.p", "rb"))  # 记录该页面是否被访问过
    except:
        page_visited = 1
    return page_visited
page_visited = load_history()
print(page_visited)