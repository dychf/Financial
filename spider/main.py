import os
import json
import time

from financial.core import Stock, Category
from financial.config import LOCATION_FILE_PATH, TASK_INTERVAL_DAY, TASK_EXCEPTION_SLEEP_TIME
from financial.utils import read_file, write_file

def start_up():
    # 读取进度
    config = {'done': False, 'category': None, 'stock': None}
    if os.path.exists(LOCATION_FILE_PATH):
        config = read_file(LOCATION_FILE_PATH)
    else:
        write_file(LOCATION_FILE_PATH, config)

    if config['done']:  # 如果上次任务完成了
        # 检查文件最后一次修改时间是否大于间隔天数，如果是则重新刷全盘数据
        file_stat = os.stat(LOCATION_FILE_PATH)
        now = int(time.time())
        if (now - file_stat.st_mtime) < TASK_INTERVAL_DAY * 24 * 3600:
            return
        config = {'done': False, 'category': None, 'stock': None}

    start_category_id = config['category']
    start_stock_id = config['stock']

    categorys = Category.get_all_category()
    all_category_id = [category.id for category in categorys]
    if start_category_id in all_category_id:
        categorys = categorys[all_category_id.index(start_category_id):]

    for category in categorys:
        category.into_db()
        for stock_code in category.get_stock_codes():
            if category.id == config['category'] and config['stock'] is not None and stock_code <= config['stock']:
                continue
            stock = Stock(stock_code, category)
            stock.into_db()
            config['category'] = category.id
            config['stock'] = stock.code
            write_file(LOCATION_FILE_PATH, config)
            print('DONE:', category.id, category.name, stock.code, stock.zwjc)
    
    config['done'] = True
    config['category'] = category.id
    config['stock'] = stock.code
    write_file(LOCATION_FILE_PATH, config)

    return True

if __name__ == '__main__':
    while True:
        try:
            result = start_up()
            if result:
                break
        except:
            print(f'出错了，休息{TASK_EXCEPTION_SLEEP_TIME}秒')
            time.sleep(TASK_EXCEPTION_SLEEP_TIME)
