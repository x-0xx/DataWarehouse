from pymongo import MongoClient
import re
import pandas as pd
import feapder
from feapder import Item
from feapder.db.mysqldb import MysqlDB
mysqldb = MysqlDB(
    ip='182.254.242.79',
    port=3306,
    user_name='zhongliangwei',
    user_pass='liangwei.zhong@2024',
    db='RawProduct2024'
)
sql = "SELECT `id`, `url` FROM DomesticProductTaskTable LIMIT 100"  # 替换 your_table_name 为你的表名，并可选地设置LIMIT

# 调用find方法执行查询
results = mysqldb.find(sql)

# 打印查询结果
for result in results:
    print(result)



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
            dbid = result['id']
            yield feapder.Request(result['url'], callback=self.before_parse,dbid = dbid)

        def before_parse(self, request, response):
            dbid = request.dbid
            for urlbox in response.xpath('.//div[@class="equ-list/ul"]'):
                _ = urlbox.xpath('.//li')
                url = "".join(_.xpath(".//@href").getall())

                if url.find("http://www.xn--zhq293d.com/") == -1:
                    url = "http://www.xn--zhq293d.com/" + url
                print(url)
                yield feapder.Request(url, callback=self.parse,dbid = dbid)

        def parse(self, request, response):
            dbid = request.dbid
            print(dbid)
            print(request.url)
            path = {}
            div_tag = response.xpath('//div[@class="current"]/p')
            if div_tag:
                # 获取所有<a>标签的文本内容，去除首尾空白，并用'>>'连接
                path['path'] = '>>'.join(["".join(a.xpath(".//text()").getall()) for a in div_tag.xpath(".//a")])
            print(path)

            # 解析通用信息1
            container1 = {}
            cate_div_tag = response.xpath('//div[@class="cats_btn"]')
            if cate_div_tag:
                container1['product_category'] = '>>'.join(["".join(cate_div_tag.xpath(".//text()").getall()).strip()])
            div_tag = response.xpath('//div[@class="pro_info_box"]')

            div_item = response.xpath('//div[@class="item"]')[0]
            text_content = div_item.get().strip().replace('<div class="item">', ' ').replace('<br>', ' ').replace(
                '</div>', ' ').strip()
            # print(text_content)
            if '：' in text_content:  # 确保文本中有'：'字符
                spc = re.split(r'：|\n', text_content)
                for i in range(0, len(spc), 2):  # 步长为2，确保两两分组
                    # 分别获取键和值
                    key = spc[i].strip()
                    value = spc[i + 1].strip() if i + 1 < len(spc) else None
                    # 检查是否每个键值对都有效
                    if value is not None:
                        container1[key] = value
            # 打印结果
            print(container1)

            # 解析商品详情2
            container2 = []
            fields_need_container2 = ('brand', 'catalog_no', 'size', 'package', 'price')
            table = response.xpath('.//table[@class="table"]')[0]
            # 如果找到了<table>元素，接着找到这个<table>元素下的所有<tr>元素
            if table is not None:
                tr_elements = table.xpath('.//tbody//tr')
                if tr_elements is not None:
                    td_texts = []
                    for tr in tr_elements:
                        td_text = [''.join(_.xpath('.//text()').getall()).strip() for _ in
                                   tr.xpath('.//td[position() < 8]') if _]
                        # 将提取的文本添加到列表中
                        if td_text is not None:
                            td_texts.append(td_text)

                        if fields_need_container2 and td_text:  # 确保两个列表都非空
                            container2.append(dict(zip(fields_need_container2, td_text)))
                print({'order_info': container2})

            # 解析商品详情3
            container3 = {}
            if div_tag := response.xpath('.//div[@class="activeBox"]'):
                for h3_tag in div_tag.xpath('.//h3'):
                    primary_key = "".join(h3_tag.xpath(".//text()").getall()).replace('|', '').strip()
                    value_list = []
                    following_siblings = h3_tag.xpath('following-sibling::*')
                    for siblings in following_siblings:
                        if not siblings.xpath('name()').get(): continue
                        if siblings.xpath('name()').get() == 'h3': break
                        if siblings.xpath('name()').get() == 'table':
                            data = pd.read_html(str(siblings.get()))[0].to_dict('list')
                            value_list.append(data)
                        if img_tag := siblings.xpath('.//img'):
                            value_list.append({'img_info': img_tag.get('src')})
                        if siblings.xpath('name()').get() == 'p':
                            value_list.append("".join(siblings.xpath(".//text()").getall()).strip())
                    value_list = [str(_).replace('\xa0', ' ') for _ in value_list if _ != '']
                    if value_list:
                        if primary_key in ('ELISA操作视频', 'ELISA操作前必读 / 下载'): continue
                        container3 |= {primary_key: value_list[0] if len(value_list) == 1 else value_list}
            print(container3)

            item = Item()  # 声明一个item
            item.table_name = "Detail"  # 指定存储的表名
            item.id = dbid
            item.url = request.url
            item.path = path
            item.container1 = container1
            item.container2 = container2
            item.container3 = container3

            yield item  # 返回item， item会自动批量入库


    if __name__ == "__main__":
        inMongo().start()
