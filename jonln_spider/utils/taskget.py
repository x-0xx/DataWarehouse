from feapder.db.mysqldb import MysqlDB
mysqldb = MysqlDB(
    ip='182.254.242.79',
    port=3306,
    user_name='zhongliangwei',
    user_pass='liangwei.zhong@2024',
    db='RawProduct2024'
)
sql = "SELECT * FROM TaskNeed LIMIT 10"  # 替换 your_table_name 为你的表名，并可选地设置LIMIT

# 调用find方法执行查询
result = mysqldb.find(sql)

# 打印查询结果
for item in result:
    print(item)