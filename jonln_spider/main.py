# -*- coding: utf-8 -*-
"""
Created on 2024-06-03 09:44:34
---------
@summary: 爬虫入口
---------
@author: xxiaojun
"""

from feapder import ArgumentParser
from spiders.seed_spider import SeedSpider
from spiders.task_spider import TaskSpider


def crawl_seed():
    spider = SeedSpider()
    spider.start()


def crawl_task():
    spider = TaskSpider()
    spider.start()


if __name__ == "__main__":
    parser = ArgumentParser(description="product 爬虫")

    parser.add_argument(
        "--crawl_seed", action="store_true", help="seed 爬虫", function=crawl_seed
    )
    parser.add_argument(
        "--crawl_task", action="store_true", help="task 爬虫", function=crawl_task
    )
    parser.start()
