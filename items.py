# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ZufangItem(scrapy.Item):
    house_url = scrapy.Field()      #房屋链接
    house_name = scrapy.Field()     #房源名字
    price = scrapy.Field()          #房源租金
    house_type = scrapy.Field()     #房屋类型
    house_area = scrapy.Field()     #房屋面积
    rental_method = scrapy.Field()  #出租方式
    community = scrapy.Field()      #所在小区
    gender = scrapy.Field()         #性别要求
    deposit = scrapy.Field()        #押金方式
    contact = scrapy.Field()        #联系人
    phone = scrapy.Field()          #联系手机
    time = scrapy.Field()           #爬取时间
