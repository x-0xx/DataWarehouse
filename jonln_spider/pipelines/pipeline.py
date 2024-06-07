from typing import Dict, List, Tuple

from feapder.utils import tools
from feapder.pipelines import BasePipeline
from feapder.utils.log import log

from utils.tools import mongodb, mysqldb


class Pipeline(BasePipeline):

    def __init__(self):
        self.mysqldb = mysqldb
        self.mongodb = mongodb

    def save_items(self, table, items: List[Dict]) -> bool:
        if table in ("DomesticProductSeedTable", "DomesticProductTaskTable"):
            sql, datas = tools.make_batch_sql(table, items)
            add_count = self.mysqldb.add_batch(sql, datas)
            datas_size = len(datas)
            if add_count:
                log.info(
                    f"共导出 {datas_size} 条数据到 {table}, 重复 {datas_size - add_count} 条")
            return add_count is not None
        else:
            try:
                add_count = self.mongodb.add_batch(
                    coll_name=table, datas=items)
                datas_size = len(items)
                log.info(
                    f"共导出 {datas_size} 条数据到 {table}, 新增 {add_count}条, 重复 {datas_size - add_count} 条")

                return True
            except Exception as e:
                log.exception(e)
                return False

    def update_items(self, table, items: List[Dict], update_keys=Tuple) -> bool:
        if table in ("DomesticProductSeedTable", "DomesticProductTaskTable"):
            sql, datas = tools.make_batch_sql(
                table, items, update_columns=update_keys or list(
                    items[0].keys())
            )
            update_count = self.mysqldb.add_batch(sql, datas)
            if update_count:
                msg = f"共更新 {update_count // 2} 条数据到 {table}"
                if update_keys:
                    msg += f" 更新字段为 {update_keys}"
                log.info(msg)

            return update_count is not None
        else:
            try:
                add_count = self.mongodb.add_batch(
                    coll_name=table,
                    datas=items,
                    update_columns=update_keys or list(items[0].keys()),
                )
                datas_size = len(items)
                update_count = datas_size - add_count
                msg = f"共导出 {datas_size} 条数据到 {table}, 新增 {add_count} 条, 更新 {update_count} 条"
                if update_keys:
                    msg += f" 更新字段为 {update_keys}"
                log.info(msg)

                return True
            except Exception as e:
                log.exception(e)
                return False

    def close(self):
        pass
