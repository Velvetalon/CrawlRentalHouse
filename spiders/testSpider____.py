import scrapy
from fake_useragent import UserAgent
from scrapy_splash import SplashRequest
import bs4
import zufang.items
import json
import time
import js2py
from ..Proxy import ProxyAPI
import requests

from twisted.internet.ssl import AcceptableCiphers
from scrapy.core.downloader import contextfactory
# contextfactory.DEFAULT_CIPHERS = AcceptableCiphers.fromOpenSSLCipherString('DEFAULT:!DH')

class testSpider(scrapy.Spider):
    name = "mainSpider"
    #关闭ssl验证
    ua = UserAgent(verify_ssl=False)
    urls = ["https://gz.zu.anjuke.com/fangyuan/p1/",]
    phone_template = "https://gz.zu.anjuke.com/v3/ajax/getBrokerPhone/?broker_id={broker_id}&token={token}&prop_id={prop_id}&prop_city_id={prop_city_id}&house_type={house_type}"
    proxy = ProxyAPI.ProxyAPI()

    def start_requests(self):
        for url in self.urls :
            yield scrapy.Request(url = url,
                                 headers={"user-agent":self.ua.random},
                                 callback=self.parse_house_list,
                                dont_filter=True)

    def parse_house_list(self, response):
        #解析网页。提取并请求其中所有的房源信息页。
        soup = bs4.BeautifulSoup(response.body.decode("utf8"), "lxml")
        info_list = soup.find_all(class_="zu-itemmod")
        url_list = [url.a["href"] for url in info_list]
        for url in url_list:
            #使用代理访问子页面
            yield SplashRequest(url = url,
                                 headers={"user-agent":self.ua.random},
                                 callback=self.parse_house,
                                dont_filter=True)

        #请求下一页。
        next_url = soup.find(class_="aNxt")
        if next_url != None :
            yield SplashRequest(url=next_url["href"],
                                headers={"user-agent": self.ua.random},
                                callback=self.parse_house_list,
                                dont_filter=True)

    def parse_house(self,response):
        cookie = response.headers["Set-Cookie"].decode("utf8")
        item = zufang.items.ZufangItem()
        soup = bs4.BeautifulSoup(response.body.decode("utf8"),"lxml")
        try :
            #房屋链接
            item["house_url"] = response.url
            #房源名字
            item["house_name"] = soup.find(class_="house-title").get_text()
            #租金
            item["price"] = soup.find(class_="price").em.get_text()
            #房屋类型
            item["house_type"] = soup.find_all(class_="house-info-item l-width")[0].find_all(name="span")[-1].get_text()
            #房屋面积
            item["house_area"] = soup.find(class_="info-tag no-line").em.get_text()
            #出租方式
            item["rental_method"] = soup.find(class_="full-line cf").find_all(name="span")[1].get_text()
            #所在小区
            item["community"] = soup.find_all(class_="house-info-item l-width")[2].a.get_text()
            #性别要求
            gender = soup.find_all(class_="house-info-item")[-1].find_all("span")[-1].get_text()
            if "小区" in gender :
                gender = "暂无"
            item["gender"] = gender
            #押金方式
            item["deposit"] = soup.find(class_="full-line cf").find_all("span")[1].get_text()
            #联系人
            item["contact"] = soup.find(class_="broker-name").get_text()
            #联系手机
            js = soup.find_all(name="script")
            context = js2py.EvalJs()
            for i in js :
                if "brokerPhone" in i.get_text() :
                    context.execute(i.get_text())
                    data_dict = getattr(context,"__Json4fe")

                    broker_id = data_dict["getPhoneParam"]["broker_id"]
                    token = data_dict["token"]
                    prop_id = data_dict["prop_id"]
                    prop_city_id = data_dict["prop_city_id"]
                    house_type = data_dict["house_type"]


                    yield scrapy.Request(url = self.phone_template.format(
                        broker_id=broker_id,
                        token=token,
                        prop_id = prop_id,
                        prop_city_id = prop_city_id,
                        house_type = house_type,
                    ),headers={"user-agent":self.ua.random,"cookie" : cookie},
                    meta = {"item":item,"url" :response.url,},
                    callback=self.parse_phone,dont_filter=True)
                    break

        # 重新爬取出错url
        except Exception as e:
            print("检测到错误，重新爬取")
            print("错误信息：", e)
            yield SplashRequest(url=response.url,
                                headers={"user-agent": self.ua.random},
                                callback=self.parse_house_list,
                                dont_filter=True)

    def parse_phone(self,response):
        item = response.meta["item"]
        js = json.loads(response.text)
        item["phone"] = "".join(js["val"].split())
        item["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        yield item

























