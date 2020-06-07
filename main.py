import city
from db.mysql import *

def update():

    db_init()  # db
    print("------完成数据库初始化-----")
    city.City().update()
    print("------完成数据爬取-----")

#city --> area  --->distict --> village

if __name__ == "__main__":
    update()