import uuid
import json
import pymysql

from pypinyin import lazy_pinyin, Style
from financial.config import DB_CONFIG

# 生成UUID
def generate_uuid() -> str:
    return str(uuid.uuid1()).replace('-', '')

# 拼音首字母
def pinyin(string: str) -> str:
    items = lazy_pinyin(string, style=Style.TONE3)
    result = ''
    for item in items:
        result += item[0]
    return result.lower()

# 修改垃圾数据
def change_text(string: str) -> object:
    if string is None:
        return None
    string = string.strip()
    if string == '--' or string == '':
        return None
    return string

# 获取数据库连接
def get_db_conn_cur():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    return conn, cur

# 插入/更新数据
def replace_db(sql: str, params=[]) -> int:
    conn, cur = get_db_conn_cur()
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
