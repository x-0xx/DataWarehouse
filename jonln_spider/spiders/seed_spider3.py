# -*- coding: utf-8 -*-
"""
Created on 2024-06-03 09:44:54
---------
@summary:
---------
@author: uxding
"""

import feapder
from setting import seed_table
from utils.tools import batch_id, get_snow_flake, get_proxies, initial_item


class SeedSpider(feapder.AirSpider):

    def download_midware(self, request):
        request.proxies = get_proxies()
        return request

    def start_requests(self):
        yield feapder.Request("http://www.xn--zhq293d.com/list.php?catid=23&page=1")

    def parse(self, request, response):
        print('111111')
        print(response.xpath('.//div[@class="l-left-n"]/ul'))
        print(response.xpath('.//text()').getall())
        for s1_node in response.xpath('.//div[@class="l-left-n"]/ul'):
            for s2_node in s1_node.xpath('./li'):
                for s3_node in s2_node.xpath('./a'):
                    mid1 = "".join(s3_node.xpath(".//text()").getall())
                    if mid1 is not None:
                        print(mid1)
                        title1 = mid1

                        url = "".join(s3_node.xpath(".//@href").getall())
                        if url.find("http://www.xn--zhq293d.com/") == -1:
                            url = "http://www.xn--zhq293d.com/" + url
                        category = title1

                        print(category)
                        print(url)

                        page_info = {
                            'id': get_snow_flake(),
                            'category': category,
                            'url': url,
                            'brand': title1,
                            'batch_id': batch_id
                        }
                        item = initial_item(seed_table, page_info)
                        # 数据入库
                        yield item


if __name__ == "__main__":
    SeedSpider().start()
