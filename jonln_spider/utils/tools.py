# -*- encoding: utf-8 -*-
import json
import random
import zlib

from feapder import Item, UpdateItem
from feapder.db.mongodb import MongoDB
from feapder.db.mysqldb import MysqlDB
from feapder.utils.tools import get_current_date
from utils.generator import Generator
mysqldb = MysqlDB()
mongodb = MongoDB()


# 雪花id全局生成对象
g = Generator(random.randint(0, 999999))
# 全局唯一批次id
batch_id = g.snow_flake()


def get_snow_flake():
    return g.snow_flake()


# 源码保存
def byte_to_str(value):  # sourcery skip: raise-specific-error
    if isinstance(value, bytes):
        return str(value, encoding="utf-8")
    raise Exception("Type Error: Not bytes")


def str_to_byte(value):  # sourcery skip: raise-specific-error
    if isinstance(value, str):
        return bytes(value, encoding="utf-8")
    raise Exception("Type Error: Not str")


def compress_content(content):  # sourcery skip: raise-specific-error
    if isinstance(content, str):
        byte_content = str_to_byte(content)
        return zlib.compress(byte_content, 9)
    raise Exception("Type Error: Not str")


def decompress_content(content):  # sourcery skip: raise-specific-error
    if isinstance(content, bytes):
        byte_content = zlib.decompress(content)
        return byte_to_str(byte_content)
    raise Exception("Type Error: Not bytes")


# 代理
def get_proxies():
    port = random.choice(list(range(24000, 24401)))
    params = {'user': 13564157050,
              'pwd': 'deepbio2021'}

    params |= {'port': port}
    return {'http': 'http://{user}:{pwd}@haproxy.iinti.cn:{port}'.format(**params),
            'https': 'http://{user}:{pwd}@haproxy.iinti.cn:{port}'.format(**params)}


# 数据库操作
def query_task(table: str, condition: str = None, fields: tuple = ('id', 'url', 'batch_id')) -> list:
    """
    mysql_db : 数据库连接对象
    table : 指定mysql中的表名字
    condition : 加上WHERE后面的条件 （调试时使用）
    fields : 筛选字段
    return : list
    """
    sql = f"SELECT {','.join(fields)} FROM {table} "
    if condition:
        sql += f' WHERE {condition}'
    if result := mysqldb.find(sql=sql):
        return [dict(zip(fields, _)) for _ in result]
    raise Exception(f'【{table}】中未查询到相关数据')


def initial_update_item(tab_name: str, _id: int):
    update_item = UpdateItem()
    update_item.table_name = tab_name
    update_item.id = _id
    return update_item


def initial_item(tab_name: str, data: dict):
    item = Item(**data)
    item.table_name = tab_name
    return item


def save_source_code(_id: int, response, coll_name: str, async_json: dict = None):
    content = compress_content(response.text)
    async_content = compress_content(json.dumps(async_json))
    source_code = {
        "_id": _id,
        "url": response.url,
        "html": content,
        "create_date": get_current_date()
    }
    if async_json:
        source_code["async"] = async_content
        source_code["html"] = None
    item = UpdateItem(**source_code)
    item.table_name = coll_name
    return item


# 标签操作
class TextCleaner:
    @classmethod
    def remove_tag(cls, string: str, tags: list = None):
        _tags = ['sup', 'sub']
        if tags:
            _tags.extend(tags)
        for tag in _tags:
            meta_open_tag = '[{tag}]'.format(tag=tag)
            meta_close_tag = '[/{tag}]'.format(tag=tag)
            open_tag = '<{tag}>'.format(tag=tag)
            close_tag = '</{tag}>'.format(tag=tag)

            string = string.replace(open_tag, meta_open_tag)
            string = string.replace(close_tag, meta_close_tag)
        return string

    @classmethod
    def add_tag(cls, text: str, tags: list = None):
        _tags = ['sup', 'sub']
        if tags:
            _tags.extend(tags)
        for tag in _tags:
            meta_open_tag = '<{tag}>'.format(tag=tag)
            meta_close_tag = '</{tag}>'.format(tag=tag)
            open_tag = '[{tag}]'.format(tag=tag)
            close_tag = '[/{tag}]'.format(tag=tag)

            text = text.replace(open_tag, meta_open_tag)
            text = text.replace(close_tag, meta_close_tag)
        return text

    def dict_add_tag(self, data: dict):
        """

        :param data: dict
        :return: add tag dict
        """

        return json.loads(self.add_tag(json.dumps(data, indent=4, ensure_ascii=False)))


text_clear = TextCleaner()


if __name__ == '__main__':
    # 测试 snowflake
    print(get_snow_flake())
    print(batch_id)

    # 测试 compress_content
    string = '<p>测试</p>'
    print(compress_content(string))

    # 测试 tag 去除
    html_text = '''
    <div><sub>1</sub></div>
    <p><sup>2</sup></p>
    <div>节点1<br>节点2<br/></div>
    '''
    # 去除
    html_text = text_clear.remove_tag(html_text, tags=['br', 'br/', 'br '])
    print(html_text)  # Notice: 需要解析, 此处为测试
    # 添加
    print(text_clear.add_tag(html_text, tags=['br', 'br/', 'br ']))
