# !/usr/bin/env python
# coding=utf-8
# 此代码仅供学习与交流，请勿用于商业用途。
# 城市缩写和城市名的映射
# 想抓取其他已有城市的话，需要把相关城市信息放入下面的字典中
# 不过暂时只有下面这些城市在链家上是统一样式

from bs4 import BeautifulSoup
from utils.request import *
import re
from db.mysql import *
import threadpool

lock = threading.Lock()

class HouseInfo:
    def __init__(self, baseInfo, price, position):
        self.__base__ = baseInfo
        self.__price__ = price
        self.__position__ = position

    def getAveragePrice(self) -> int:
        # return 每平米价格，精确到元
        list = self.__base__.split("|")
        for item in list:

            regex_str = ".*平米.*"
            match_obj = re.match(regex_str, item)

            if match_obj is not None:
                # print(match_obj.string)
                strTrip = match_obj.string.strip(" ")

                # 以下是整数和小数正确的正则表达式
                regInt = '^0$|^[1-9]\d*'  # 不接受09这样的为整数
                regFloat = '^[1-9]\d*\.\d+|^[1-9]\d*\.\d+'  # 接受0.00、0.360这样的为小数，不接受00.36，思路:若整数位为零,小数位可为任意整数，但小数位数至少为1位，若整数位为自然数打头，后面可添加任意多个整数，小数位至少1位

                regIntOrFloat = regFloat + '|' + regInt  # 整数或小数

                housingArea = re.search(regIntOrFloat, strTrip)
                housingArea = housingArea.group(0)
                housingAreaInt = housingArea.split(".")[0]

                return 10000 * float(self.__price__) / float(housingAreaInt)

    def getVillageName(self):
        return self.__position__

class Village(object):
    def __init__(self):
        pass


    def update(self, city: str, area: str) -> (int, int):
        # return 总的出售房屋套数 ;map[xiaoqu]housinfo
        url = "https://{}.lianjia.com{}".format(city, area)
        html = reqPage(url)
        #soup = BeautifulSoup(html, "lxml")
        soup = BeautifulSoup(html, "html.parser")

        villageHouseInfo = {}

        css_class = soup.find(class_='total fl')
        area_total = css_class.find("span").get_text()

        # print(type(area_total))
        area_total = area_total.strip()

        if area_total == "0":
            return None, None

        page_box = soup.find(class_='page-box house-lst-page-box')
        page_data = page_box.get("page-data")
        totalPage = eval(page_data).get("totalPage")
        # page_box.get("page-url")


        for i in range(1, 1 + int(totalPage)):
            if i != 1:
                newPageUrl = url + "pg{}".format(i)
                html = reqPage(newPageUrl)
                #soup = BeautifulSoup(html, "lxml")

                soup = BeautifulSoup(html, "html.parser")

            rs = soup.find_all("div", attrs={"class": "info clear"})

            # print(len(rs))
            for unit in rs:
                baseInfo = unit.find('div', attrs={'class': 'houseInfo'})
                positionInfo = unit.find('div', attrs={'class': 'positionInfo'}).find('a', attrs={'data-el': 'region'})
                priceinfo = unit.find('div', attrs={'class': 'totalPrice'})

                titleInfo = unit.find('div', attrs={'class' : 'title'}).find("a")
                if titleInfo is None :
                    print("err::::::",unit.find('div', attrs={'class' : 'title'}))
                houseUrl = titleInfo.get('href').strip()


                # positionInfo = position.find('a', attrs={'data-el': 'region'})
                # print(positionInfo.get("href"), positionInfo.get_text())

                position = positionInfo.get_text().strip()
                price = priceinfo.find("span").get_text().strip()
                baseInfo = baseInfo.get_text().strip()

                #print(position,url,houseInfo,price)

                AddHouseInfo(baseInfo,houseUrl,price,position)

                # arrayHousinfo = []
                arrayHousinfo = villageHouseInfo.get(positionInfo.get("href"))
                if arrayHousinfo is not None:
                    arrayHousinfo.append(HouseInfo(baseInfo, price, position))
                else:
                    villageHouseInfo[positionInfo.get("href")] = [HouseInfo(baseInfo, price, position)]

                time.sleep(1)

        AddVillage(area, self.__average__(villageHouseInfo), area_total, url)
        return int(area_total), self.__average__(villageHouseInfo)


    def __average__(self, villageHouseInfo: dict) -> int:
        allVilageAverage = 0
        for (k, v) in villageHouseInfo.items():
            villageTotalAverage = 0

            #print("1111111111",v[0].getVillageName(), k)
            for item in v:
                villageTotalAverage += item.getAveragePrice()
            allVilageAverage += villageTotalAverage / len(v)
            #print("village average:",k, villageTotalAverage / len(v), "yuan/pingmi")

        return int(allVilageAverage / len(villageHouseInfo))

class District(object):
    def __init__(self):
        pass

    def update(self, city, disctrict) -> (int, int):
        url = "https://{}.lianjia.com/{}".format(city, disctrict)

        html = reqPage(url)
        soup = BeautifulSoup(html, "html.parser")
        list = soup.find_all('div', attrs={'data-role': 'ershoufang'})

        cn_areas = []
        pinyin_areas = []
        i = list[0]

        list = i.find_all("div")
        if len(list) != 2:
            return None, None, None, None

        areasList = list[1]

        disctrictTotal = 0
        disctrictAverage = 0

        filename = disctrict
        filename = filename.replace("/", "_")
        for i in areasList.find_all("a"):
            href = i.get("href")
            area_totalnum, area_average = Village().update(city, href)
            if area_totalnum is not None:
                pinyin_areas.append(href)

                disctrictTotal += int(area_totalnum)
                disctrictAverage += int(area_average) * area_totalnum
                cn_areas.append(i.get_text())

                AddDistrict(filename,area_average,area_totalnum,href)


        if disctrictTotal != 0 :
            print("in {0} have {1} houses, average {2} yuan/pingmi".format(disctrict, disctrictTotal,
                                                                       int(disctrictAverage / disctrictTotal)))
            return disctrictTotal, int(disctrictAverage / disctrictTotal)
        else :
            print("err:",url)
            return  0,0

class CountryTown(object):
    def __init__(self):
        self.houseTotalOfCity = 0
        self.cityAverage = 0.0

    # 城市数据更新
    def update(self, city) -> (int, int):
        lock = threading.Lock()


        url = "https://{}.lianjia.com/ershoufang".format(city)
        html = reqPage(url)
        soup = BeautifulSoup(html, "html.parser")
        list = soup.find_all('div', attrs={'data-role': 'ershoufang'})

        ch_countryTowns = []
        pinyin_countryTowns = []
        paramList = []

        for i in list:
            list = i.find_all("a")
            for i in list:
                href = i.get("href")
                if len(re.findall(r".*zhoubian", href)) == 0:  # not zhoubian
                    pinyin_countryTowns.append(href)
                    ch_countryTowns.append(i.get_text())
                    group = [city, href, i.get_text()]
                    paramList.append(group)
                    # (target=run, args=("t1",)
                    # t =  threading.Thread(target=req, args=(city,href,i.get_text(),))
                    # t.start()
                    # t.join()

                    # threads.append(t)

        pool = threadpool.ThreadPool(len(paramList))
        requests = threadpool.makeRequests(self.reqCountryTown, paramList)
        [pool.putRequest(req) for req in requests]
        pool.wait()

        if self.houseTotalOfCity is not None and self.houseTotalOfCity != 0:
            AddCity(city, self.cityAverage / self.houseTotalOfCity, self.houseTotalOfCity, url)
            return self.houseTotalOfCity, self.cityAverage / self.houseTotalOfCity
        else:
            print("err contry town:", self.houseTotalOfCity, self.cityAverage)
            return 0, 0

    #
    def reqCountryTown(self, params):

        global lock

        city = params[0]
        href = params[1]
        contryTownName = params[2]

        try:
            # 每户信息
            totalNumOfHouse, areaAverage = District().update(city, href)
            if totalNumOfHouse is None or totalNumOfHouse == 0:
                print(href, city, totalNumOfHouse, areaAverage)
                return
        except Exception as e:
            print("district update exception:", e, "city:", city, "href:", href)
            return

        print("country town:", href, contryTownName, "total house:", totalNumOfHouse, "areaAverage:", areaAverage)

        lock.acquire()
        self.houseTotalOfCity += totalNumOfHouse
        self.cityAverage += areaAverage * totalNumOfHouse
        lock.release()
        AddCountryTown(contryTownName, areaAverage, totalNumOfHouse, href)

'''
# from utils.log import *

# cities = {
#     'bj': '北京',
#     'cd': '成都',
#     'cq': '重庆',
#     'cs': '长沙',
#     'dg': '东莞',
#     'dl': '大连',
#     'fs': '佛山',
#     'gz': '广州',
#     'hz': '杭州',
#     'hf': '合肥',
#     'jn': '济南',
#     'nj': '南京',
#     'qd': '青岛',
#     'sh': '上海',
#     'sz': '深圳',
#     'su': '苏州',
#     'sy': '沈阳',
#     'tj': '天津',
#     'wh': '武汉',
#     'xm': '厦门',
#     'yt': '烟台',
#     'wx': '无锡',
# }
'''


class City(object):
    def __init__(self):
        self.cities = {
            'sh': '上海',
            'su': '苏州'
        }
        self.lianjia_cities = self.cities
        self.beike_cities = self.cities



    def create_prompt_text(self, cities):
        """
        根据已有城市中英文对照表拼接选择提示信息
        :return: 拼接好的字串
        """
        s = ""
        count = 0
        for en_name, ch_name in cities.items():
            count += 1
            s = s + en_name + ":" + ch_name
            if count % 4 == 0:
                s = s + "\n"
            else:
                s = s + ", "
        return f'Which city do you want to crawl?\n{s}'

    # 获取  er手房信息
    def get_city_ershou_info(self, params):
        totalHouse, average = CountryTown().update(params[0])
        if totalHouse is None or average is None:
            return

    def paramList(self, cn_cities):
        thread_param_list = []
        for k, v in cn_cities:
            group = [k, v]
            thread_param_list.append(group)

        return thread_param_list

    # 更新数据
    def update(self):
        # csv_file = os.getcwd() + "/result/{0}.csv".format("all_cities")
        # with open(csv_file, "w") as f:

        start_time = time.time()
        pool = threadpool.ThreadPool(len(self.cities.items()))
        # get_city_ershou_info 获取 二手房
        requests = threadpool.makeRequests(self.get_city_ershou_info, self.paramList(self.cities.items()))
        [pool.putRequest(req) for req in requests]
        pool.wait()
        print('%d second' % (time.time() - start_time))


if __name__ == '__main__':
    # print(cities.get("sh", None))
    # print(create_prompt_text(cities))
    # print(get_city_ershou_info("sh"))
    pass
