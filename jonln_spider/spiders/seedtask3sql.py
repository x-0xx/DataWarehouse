import feapder
from feapder import Item
import pymongo



class inMongo(feapder.AirSpider):
    __custom_setting__ = dict(
        ITEM_PIPELINES=["feapder.pipelines.mongo_pipeline.MongoPipeline"],
        MONGO_IP="182.254.242.79",
        MONGO_PORT=27017,
        MONGO_DB="SourceCode",
        MONGO_USER_NAME="zhongliangwei",
        MONGO_USER_PASS="liangwei.zhong@2024",
    )

    def start_requests(self):
       yield feapder.Request("http://www.xn--zhq293d.com/list.php?catid=23&page=1")

    def parse(self, request, response):
        i = 0
        for s1_node in response.xpath('.//div[@class="l-left-n"]/ul'):
            for s2_node in s1_node.xpath('./li'):
                for s3_node in s2_node.xpath('./a'):
                    mid1 = "".join(s3_node.xpath(".//text()").getall())
                    if mid1 is not None:
                        #print(mid1)
                        title1 = mid1

                        url = "".join(s3_node.xpath(".//@href").getall())
                        if url.find("http://www.xn--zhq293d.com/")==-1:
                            url = "http://www.xn--zhq293d.com/"+url
                        category = title1
                        if category:
                            dbid = (f"id: {i}")
                            i = i+1
                            print(f"id: {i}")
                            print(category)
                            print(url)
                            category_count = 0
                            yield feapder.Request(url, callback=self.parse_detail, dbid=dbid,category=category,category_count = category_count)
    def parse_detail(self, request, response):
            dbid = request.dbid
            category = request.category
            box = response.xpath('.//div[@class="page"]')
            text = box.xpath('./a[2]')
            page_text = text.xpath('.//@href').get()
            print(page_text)
            # 计数
            front_items = response.xpath('.//div[@class="equ-list"]/ul')
            items = front_items.xpath('./li')
            items_count = len(items)
            print(items_count)
            category_count = request.category_count
            print(category_count)
            category_count = items_count + category_count
            if page_text != 'javascript:;':
                url = page_text
                yield feapder.Request(url, callback=self.parse_detail, category_count = category_count,dbid=dbid,category=category)

            print(f"元素个数: {category_count}")

            item = Item()  # 声明一个item
            item.table_name = "DomesticProductTaskTable"  # 指定存储的表名
            item.id = request.dbid
            item.seed_id = request.dbid
            item.url = request.url
            item.category = request.category  # 给item属性赋值
            item.category_count = category_count
            yield item

            item = Item()  # 声明一个item
            item.table_name = "DomesticProductSeedTable"  # 指定存储的表名
            item.id = request.dbid
            item.url = request.url
            yield item  # 返回item， item会自动批量入库

if __name__ == "__main__":
    inMongo().start()
