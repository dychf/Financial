import uuid
import json
import random
import pymysql
import requests
import pandas as pd

from io import StringIO
from pypinyin import lazy_pinyin, Style
from financial.config import DB_CONFIG, HTTP_HEADERS

# 生成UUID
def generate_uuid() -> str:
    return str(uuid.uuid1()).replace('-', '')

# 读取网络文件
def read_net_file(url: str, file_type='CSV', encoding='GB18030') -> pd.DataFrame:
    headers = {
        'Accept': HTTP_HEADERS['Accept'],
        'User-Agent': random.choice(HTTP_HEADERS['User-Agent'])
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if file_type == 'CSV':
            data = StringIO(response.text)
            return pd.read_csv(data, encoding=encoding)
        elif file_type == 'EXCEL':
            return pd.read_excel(response.content)
    return None

# 拼音首字母
def pinyin(string: str) -> str:
    items = lazy_pinyin(string, style=Style.TONE3)
    result = ''
    for item in items:
        result += item[0]
    return result.lower()

# 修改垃圾数据
def change_text(value: str, default_value=None, to_type=float) -> object:

    def to(v):
        if to_type is str:
            return str(v)
        if to_type is float:
            return float(v)
        if to_type is int:
            return int(v)
        return v

    if value is None:
        return default_value
    if type(value) is str:
        value = value.strip()
        if value == '--' or value == '':
            return default_value  
        return to(value)
    return to(value)

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

# 插入/更新数据
def replace_db(sql: str, params=[], is_many=False, is_special_sql=False) -> int:
    conn, cur = get_db_conn_cur()
    result = 0
    if is_many:
        if is_special_sql:
            for i, args in enumerate(params):
                count = cur.execute(sql, args)
                result += count
        else:
            result = cur.executemany(sql, params)
    else:
        result = cur.execute(sql, params)
    conn.commit()
    return result

# 写文件
def write_file(file_path: str, content: object, is_dumps=True):
    if is_dumps:
        content = json.dumps(content)
    file = open(file_path, 'w')
    file.write(content)
    file.close()

# 读文件
def read_file(file_path: str, return_json=True):
    file = open(file_path, 'r')
    content = file.read()
    file.close()
    if return_json:
        content = json.loads(content)
    return content
