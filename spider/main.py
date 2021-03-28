import os
import json
import time

from financial.core import Stock, Category
from financial.config import LOCATION_FILE_PATH, TASK_INTERVAL_DAY
from financial.utils import read_file, write_file

def start_up():
    # 读取进度
    config = {'location': None}
    if os.path.exists(LOCATION_FILE_PATH):
        config = read_file(LOCATION_FILE_PATH)
    else:
        write_file(LOCATION_FILE_PATH, json.dumps(config))

    # 检查文件最后一次修改时间是否大于间隔天数，如果是则重新刷全盘数据
    file_stat = os.stat(LOCATION_FILE_PATH)
    now = int(time.time())
    if (now - file_stat.st_mtime) >= TASK_INTERVAL_DAY * 24 * 3600:
        config['location'] = None
    start_category_id = config['location']

    categorys = Category.get_all_category()
    all_category_id = [category.id for category in categorys]
    if start_category_id in all_category_id:
        categorys = categorys[all_category_id.index(start_category_id) + 1:]

    for category in categorys:
        category.into_db()
        for stock_code in category.get_stock_codes():
            stock = Stock(stock_code, category)
            stock.into_db()
        config['location'] = category.id
        write_file(LOCATION_FILE_PATH, config)

if __name__ == '__main__':
    start_up()
