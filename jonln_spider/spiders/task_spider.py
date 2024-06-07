# -*- coding: utf-8 -*-
"""
Created on 2024-06-03 09:45:07
---------
@summary:
---------
@author: xxiaojun
"""

import feapder
from setting import source_code_coll_name, task_table, seed_table
from utils.tools import save_source_code, get_proxies, query_task, initial_update_item, get_snow_flake, initial_item


class TaskSpider(feapder.AirSpider):
    def download_midware(self, request):
        request.proxies = get_proxies()
        return request

    def start_requests(self):
        tasks = query_task(
            table=seed_table, condition='[condition]')
        for task in tasks:
            url = task.get('url')
            yield feapder.Request(url, task=task)

    def parse(self, request, response):
        task = request.task
        seed_id = task.get("id")
        # task表id跟mongo源码存储id保持一致
        _id = get_snow_flake()
        # 保存源码
        yield save_source_code(_id, response, source_code_coll_name)
        # 保存详情页信息
        task_info = dict(
            seed_id=seed_id,
            id=_id,
            url=response.url,
            batch_id=task.get("batch_id")
        )
        item = initial_item(task_table, task_info)
        yield item

        # 更新seed表state
        update_item = initial_update_item(tab_name=seed_table, _id=seed_id)
        update_item.state = 1
        yield update_item


if __name__ == "__main__":
    TaskSpider().start()
