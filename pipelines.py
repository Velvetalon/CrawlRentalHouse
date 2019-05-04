# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import zufang.settings as settings

class SaveDataPipeline(object):
    insert_template = """
        INSERT INTO house_table VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool("pymysql",
                                      host=settings.sqlsetting["HOST"],
                                      port=settings.sqlsetting["PORT"],
                                      db=settings.sqlsetting["DB"],
                                      user=settings.sqlsetting["USER"],
                                      password=settings.sqlsetting["PASSWORD"],
                                      charset=settings.sqlsetting["CHARSET"],
                                      cp_reconnect=True)                        #自动检测失效连接并重连。

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.insert_data,item)
        query.addErrback(self.error_hander,item)
        return item

    def insert_data(self,cursor,item):
        house_id = item["house_url"].split("/")[-1].split("?")[0]
        cursor.execute(self.insert_template,[house_id,item["house_url"],item["house_name"],
                                            item["price"],item["house_type"],item["house_area"],
                                             item["rental_method"],item["community"],item["gender"],
                                             item["deposit"],item["contact"],item["phone"],item["time"]])
        print("已提交数据库插入请求")
    def error_hander(self,failure,item):
        if "for key 'PRIMARY'" in str(failure) :
            print("主键重复：",item["house_url"].split("/")[-1])
        else :
            query = self.dbpool.runInteraction(self.insert_data, item)
            query.addErrback(self.error_hander, item)
            print("已重新提交数据库插入申请，ID：",item["house_url"].split("=")[-1])