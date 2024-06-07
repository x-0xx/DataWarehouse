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























        page_info = {
            'id': get_snow_flake(),
            'category': '[category]',
            'url': '[url]',
            'brand': '[brand]',
            'batch_id': batch_id
        }
        item = initial_item(seed_table, page_info)
        # 数据入库
        yield item


if __name__ == "__main__":
    SeedSpider().start()
