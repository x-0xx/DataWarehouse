# -*- coding: utf-8 -*-
"""
Created on 2024-06-03 09:45:38
---------
@summary:
---------
@author: xxiaojun
"""

import json
import feapder
import pandas as pd
from utils.tools import text_clear, initial_update_item, query_task
from feapder import UpdateItem
from setting import coll_name, task_table, fast_query_api


class DetailParser(feapder.AirSpider):

    def start_requests(self):
        yield feapder.Request("http://www.jonln.com/cus_rat_ip_10_cxcl10/")
        # 这是测试用例, 真实情况以下面请求为准
        tasks = query_task(task_table, fields=(
            'id', 'url', 'category',), condition='state = 1 AND parse_state = 0')
        for task in tasks:
            yield feapder.Request(fast_query_api, task=task)

    def parse(self, request, response):
        soup = response.bs4()
        task = request.task
        response.text = text_clear.remove_tag(
            response.text, tags=['br', 'br ', 'br/'])
        page_info = {
            '_id': task.get('id'),
            'url': task.get('url'),
            'category': task.get('category'),
        }
        page_info |= self.extract_path(soup)
        page_info |= self.extract_normal_info(soup)
        page_info |= self.extract_order_info(soup)
        page_info |= self.extract_product_detail(soup)
        page_info = json.loads(text_clear.add_tag(
            json.dumps(page_info), ["br", "br /", "br/"]))

        # 解析结果入mongo
        mongo_item = UpdateItem(**page_info)
        mongo_item.table_name = coll_name
        yield mongo_item

        # 更新 task 表 parse_state 状态值
        update_item = initial_update_item(task_table, task.get('id'))
        update_item.parse_state = 1
        yield update_item

    @staticmethod
    def extract_path(soup):
        path = {}
        if ol_tag := soup.find('ol', class_="breadcrumb"):
            path |= {'path': '>>'.join([_.text.strip()
                                        for _ in ol_tag.find_all('a')])}
        return path

    @staticmethod
    def extract_normal_info(soup):
        container = {}
        if name_tag := soup.find('div', class_="product_desc"):
            container |= {'product_name': name_tag.h1.text.strip()}
        if cate_div_tag := soup.find('div', class_="cats_btn"):
            container |= {'product_category': cate_div_tag.a.text.strip()}
        if div_tag := soup.find('div', class_="pro_info_box"):
            for item in div_tag.find('div', class_="item"):
                if item.name and item.name == 'br':
                    continue
                split_text = item.text.strip().replace('\xa0', ' ').split('：')
                container |= {split_text[0].strip(): split_text[1].strip()}
        return container

    @staticmethod
    def extract_order_info(soup):
        container = {}
        fields_need_container = (
            'brand', 'catalog_no', 'size', 'package', 'price')
        tmp = []
        for tr_tag in soup.find('table', class_="table").find_all('tr'):
            td_text_list = [_.text.strip() for _ in tr_tag.find_all('td') if _]
            if _ := dict(zip(fields_need_container, td_text_list)):
                tmp.append(_)
        if tmp:
            container |= {'order_info': tmp}
        return container

    @staticmethod
    def extract_product_detail(soup):
        container = {}
        if div_tag := soup.find('div', class_="activeBox"):
            for h3_tag in div_tag.find_all('h3'):
                primary_key = h3_tag.text.replace('|', '').strip()
                value_list = []
                for siblings in h3_tag.next_siblings:
                    if not siblings.name:
                        continue
                    if siblings.name == 'h3':
                        break
                    if siblings.name == 'table':
                        data = pd.read_html(str(siblings))[0].to_dict('list')
                        value_list.append(data)
                    if img_tag := siblings.find('img'):
                        value_list.append({'img_info': img_tag.get('src')})
                    if siblings.name == 'p':
                        value_list.append(siblings.text.strip())
                value_list = [str(_).replace('\xa0', ' ')
                              for _ in value_list if _ != '']
                if value_list:
                    if primary_key in ('ELISA操作视频', 'ELISA操作前必读 / 下载'):
                        continue
                    container |= {primary_key: value_list[0] if len(
                        value_list) == 1 else value_list}
        return container


if __name__ == "__main__":
    DetailParser().start()
