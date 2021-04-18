import re
import json
import pymysql

from config import DB_CONFIG

# 解析JSONP字符串
def parse_jsonp(text):
    return json.loads(re.findall(r'^\w+\((.*)\).*', text)[0])


# 获取数据库连接
def get_db_conn_cur():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    return conn, cur


# 查询数据
def query_data(sql: str, params: list=[], fetchone=False):
    result = None
    conn, cur = get_db_conn_cur()
    cur.execute(sql, params)
    result = cur.fetchone() if fetchone else list(cur.fetchall())
    conn.close()
    return result
