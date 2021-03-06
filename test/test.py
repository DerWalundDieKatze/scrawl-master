import os
import re
import time

import bs4
import threadpool

cities = {
    'bj': '北京',
    'cd': '成都',
    'cq': '重庆',
    'cs': '长沙',
    'dg': '东莞',
    'dl': '大连',
    'fs': '佛山',
    'gz': '广州',
    'hz': '杭州',
    'hf': '合肥',
    'jn': '济南',
    'nj': '南京',
    'qd': '青岛',
    'sh': '上海',
    'sz': '深圳',
    'su': '苏州',
    'sy': '沈阳',
    'tj': '天津',
    'wh': '武汉',
    'xm': '厦门',
    'yt': '烟台',
    'wx': '无锡',
}

from bs4 import BeautifulSoup


def getDistrict():
    file = open('../1.html', 'rb')
    html = file.read()
    bs = BeautifulSoup(html, "html.parser")

    rs = bs.find_all('div', attrs={'data-role': 'ershoufang'})
    ll = rs.pop(0)
    print(dir(bs4.element.ResultSet))
    print(type(rs))
    print(ll)

    for i in rs:
        subRS = i.find_all("a")
        for i in subRS:
            print(i.get("href"))
            print(i.get_text())
            print(type(i))


def getHouseInfo():
    file = open('../1.html', 'rb')
    html = file.read()
    bs = BeautifulSoup(html, "html.parser")

    page_total = bs.find(class_='page-box house-lst-page-box')
    print(page_total)
    print(dir(type(page_total)))
    dictPage = page_total.get("page-data")
    print(type(dictPage), type(eval(dictPage)))
    print(eval(dictPage).get("totalPage"))
    print(page_total.get("page-url"))

    rs = bs.find_all("div", attrs={"class": "info clear"})
    print(rs)
    for unit in rs:
        houseInfo = unit.find('div', attrs={'class': 'houseInfo'})
        position = unit.find('div', attrs={'class': 'positionInfo'})
        priceinfo = unit.find('div', attrs={'class': 'totalPrice'})
        print(houseInfo.get_text())
        print(priceinfo.find("span").get_text())
        # print(type(position))
        # data-el="region"
        positionInfo = position.find('a', attrs={'data-el': 'region'})
        print(positionInfo.get("href"), positionInfo.get_text())
        print(dir(type(position)))
        # print(position, position.get_text())
        print("")


def isNumReg(str):
    regInt = '\d+'  # 能匹配123、123.63、123eabd、abc236等所有包含了数字的字符串
    regInt2 = '\d+$'  # 能匹配123、123.63、abc236等所有以数字结尾的字符串
    regInt2 = '^\d+$'  # 只能匹配1、12、123等只包含数字的字符串
    regFloat = '\d+\.\d+'  # 能12.36、efa56.63、wwe56.56abc等字符串
    regFloat2 = '^\d+\.\d+$'  # 能匹配2.36、0.36、00069.63、0.0、263.25等

    # 以下是整数和小数正确的正则表达式
    regInt = '^0$|^[1-9]\d*'  # 不接受09这样的为整数
    regFloat = '^\d+\.\d+|^[1-9]\d*\.\d+'
    # 接受0.00、0.360这样的为小数，不接受00.36，思路:若整数位为零,小数位可为任意整数，但小数位数至少为1位，若整数位为自然数打头，后面可添加任意多个整数，小数位至少1位

    regIntOrFloat = regFloat + '|' + regInt  # 整数或小数

    # patternIntOrFloat = re.compile(regIntOrFloat)  # 创建pattern对象，以便后续可以复用
    # if patternIntOrFloat.search(str):
    #     return True
    # if re.search(patternIntOrFloat, str):
    #     return True

    ret = re.search(regIntOrFloat, str)
    print(float(ret.group(0)))

    if re.search(regIntOrFloat, str):
        return True
    else:
        return False


def ThreadFun(arg1, arg2):
    pass


def main():
    device_list = [1, 2, 3, 4, 5, 6, 7, 8]  # 需要处理的设备个数
    task_pool = threadpool.ThreadPool(8)  # 8是线程池中线程的个数
    request_list = []  # 存放任务列表
    # 首先构造任务列表
    for device in device_list:
        request_list.append(threadpool.makeRequests(ThreadFun, [((device,), {})]))
    # 将每个任务放到线程池中，等待线程池中线程各自读取任务，然后进行处理，使用了map函数，不了解的可以去了解一下。
    map(task_pool.putRequest, request_list)
    # 等待所有任务处理完成，则返回，如果没有处理完，则一直阻塞
    task_pool.poll()


def sayhello(params):
    print("Hello ", params[0], params[1], params[2])
    strWrite = params[0] +"," + params[1] +"\n"
    params[2].write(strWrite)
    time.sleep(2)


def paramList(cn_cities, f):
    thread_param_list = []

    for k, v in cn_cities:
        group = [k, v, f]
        thread_param_list.append(group)

    return thread_param_list


def testThreadPool():
    with open("./1.csv", "w") as f:
        pl = paramList(cities.items(), f)
        print(type(pl))
        start_time = time.time()
        pool = threadpool.ThreadPool(len(pl))

        requests = threadpool.makeRequests(sayhello, pl)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        print('%d second' % (time.time() - start_time))


def testCsv():
    csv_file = os.getcwd() + "/{0}_{1}.csv".format(11, 88)
    with open(csv_file, "w") as f:
        l = "2" + "," + "444"
        f.write(l)


if __name__ == '__main__':
    testCsv()

    testThreadPool()

    print(isNumReg("10.098对象"))  # True
    print(isNumReg("345对象"))  # True

    # getHouseInfo()
