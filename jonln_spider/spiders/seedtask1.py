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
       yield feapder.Request("https://www.liankebio.com/products")

    def parse(self, request, response):
        i = 0
        for s1_node in response.xpath('.//li[@class="btn menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children current-menu-item current_page_item dropdown menu-item-777"]/ul[@class="sub-menu"]'):
            for s2_node in s1_node.xpath('./li'):
                for s3_node in s2_node.xpath('./a[@class="menu-link"]'):
                    mid1 = "".join(s3_node.xpath(".//text()").getall())
                    if mid1 is not None:
                        #print(mid1)
                        title1 = mid1
                        for s4_node in s2_node.xpath('.//ul[@class="sub-menu"]'):
                            for s5_node in s4_node.xpath('.//a[@class="menu-link"]'):
                                mid2 = "".join(s5_node.xpath(".//text()").getall())
                                #print(mid2)
                                if mid2 is not None:
                                    s = "产品中心"
                                    if title1 not in s:
                                        title2 = mid2.strip()
                                        url = "".join(s5_node.xpath(".//@href").getall())
                                        if url.find("https://www.liankebio.com")==-1:
                                            url = "https://www.liankebio.com"+url
                                        category = title1 + ">>" + title2
                                        if category:
                                            dbid = (f"id: {i}")
                                            i = i+1
                                            print(f"id: {i}")
                                            print(category)
                                            print(url)
                                            yield feapder.Request(url, callback=self.parse_detail, dbid=dbid,category=category)
    def parse_detail(self, request, response):
            box = response.xpath('.//ul[@class="page-numbers"]')
            text = box.xpath('.//li[position() = last() - 1]')
            page_text = text.xpath('.//text()').get()
            print(page_text)
            if page_text:
                page_number = int("".join(filter(str.isdigit, page_text)))
            else:
                page_number = None

            # 计数的元素是class为"pro_description"的元素
            front_items = response.xpath('.//ul[@class="products oceanwp-row clr grid tablet-col tablet-2-col"]')
            items = front_items.xpath('./li')
            items_count = len(items)
            print(items_count)
            print(f"最终页码: {page_number}")
            if page_number is None:
                category_count = items_count
            else:

                category_count = items_count * page_number
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
