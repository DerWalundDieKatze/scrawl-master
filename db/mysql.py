import threading
import time
import pymysql

lock = threading.Lock()


def db_init():
    '''初始化数据库'''
    global db
    try:
        lock.acquire()
        # 连接数据库
        db = pymysql.connect("127.0.0.1", "root", "123", "houseDB", charset='utf8')
        print("connect mysql ok")
        lock.release()
    except:
        lock.release()
        print("connect to mysql err")
        exit(-1)  # 如果错误，结束程序


def AddCity(cityName, averagePrice, totalNumber, url):
    '''写入数据'''
    cursor = db.cursor()  # 调用数据库游标
    # sql语句，插入数据
    sql = "INSERT INTO cities(cityName,averagePrice,count,url,timeNow) values(%s,%s,%s,%s,%s)"
    try:
        lock.acquire()  # 代码块锁定
        # 执行数据库插入操作
        cursor.execute(sql, (cityName, averagePrice, totalNumber, url, time.strftime("%Y-%m-%d"))),
        db.commit()  # 提交，只有改动了数据库才需要提交操作
        lock.release()
    except  Exception as e:
        lock.release()
        print("add city:", e)
        db.rollback()  # 数据回滚


def AddCountryTown(countyTownname, averagePrice, totalNumber, url):
    cursor = db.cursor()

    sql = "INSERT INTO countyTowns(countyTownname,averagePrice,totalNumber,url,timeNow) values(%s,%s,%s,%s,%s)"
    try:
        lock.acquire()
        cursor.execute(sql, (countyTownname, averagePrice, totalNumber, url, time.strftime("%Y-%m-%d"))),
        db.commit()
        lock.release()
    except  Exception as e:
        lock.release()
        print("add country:", e)
        db.rollback()


def AddVillage(villageName, averagePrice, totalNumber, url):
    cursor = db.cursor()

    sql = "INSERT INTO villages(villageName,averagePrice,count,url,timeNow) values(%s,%s,%s,%s,%s)"
    try:
        lock.acquire()
        cursor.execute(sql, (villageName, averagePrice, totalNumber, url, time.strftime("%Y-%m-%d")))
        db.commit()
        lock.release()
    except Exception as e:
        print("vaillage:", e)

        db.rollback()
        lock.release()


def AddHouseInfo(baseInfo, url, priceInfo, positionInfo):
    cursor = db.cursor()

    sql = "INSERT INTO houseInfo(baseInfo,url,priceInfo,positionInfo,timeNow) values(%s,%s,%s,%s,%s)"
    try:
        lock.acquire()
        cursor.execute(sql, (baseInfo, url, priceInfo, positionInfo, time.strftime("%Y-%m-%d")))
        db.commit()
        lock.release()
    except Exception as e:
        print("exception1:", e)
        print("exception2:", url, "baseinfo:", baseInfo, "priceInfo:", priceInfo, "pi:", positionInfo)
        db.rollback()
        lock.release()


def AddDistrict(districtName, averagePrice, totalNumber, url):
    cursor = db.cursor()

    sql = "INSERT INTO districts(districtName,averagePrice,count ,url,timeNow) values(%s,%s,%s,%s,%s)"
    try:
        lock.acquire()
        cursor.execute(sql, (districtName, averagePrice, totalNumber, url, time.strftime("%Y-%m-%d")))
        db.commit()
        lock.release()
    except Exception as e:
        print("AddDistict:", e)
        db.rollback()
        lock.release()

'''
# def ReadDB(name):
#     sql = "SELECT * FROM  values(%s)"
#    cursor = db.cursor()
#
#    try:
#      cursor.execute(sql, (name))
#      data = cursor.fetchone()
#
#       while data:
#         print(data)
#         data = cursor.fetchone()
#     except:
#          print("Error!")

'''


if __name__ == '__main__':
    db_init()
    AddDistrict("111", "23", "555555", "http:2333")
