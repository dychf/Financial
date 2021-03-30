import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 断点续爬配置文件
LOCATION_FILE_NAME = 'progress.json'
LOCATION_FILE_PATH = os.path.join(BASE_PATH, LOCATION_FILE_NAME)

# 间隔多少天重新爬数据
TASK_INTERVAL_DAY = 7

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'holdle',
    'charset': 'utf8'
}

# 行业分类
URL_CATEGORY = 'http://quotes.money.163.com/old'
CATEGORY_STOCK_PAGE_SIZE = 50
URL_CATEGORY_STOCK = 'http://quotes.money.163.com/hs/service/diyrank.php?query=PLATE_IDS:{category_id}&fields=SYMBOL&sort=SYMBOL&order=asc&page={page_no}&count={page_size}'

# 基本信息
URL_GSZL = 'http://quotes.money.163.com/f10/gszl_{stock_code}.html'

# 分红派息
URL_FHPX = 'http://quotes.money.163.com/f10/fhpg_{stock_code}.html'

# 三表数据源
URL_ZCFZB = 'http://quotes.money.163.com/service/zcfzb_{stock_code}.html?type=year'  # 资产负债表
URL_LRB = 'http://quotes.money.163.com/service/lrb_{stock_code}.html?type=year'  # 利润表
URL_XJLLB = 'http://quotes.money.163.com/service/xjllb_{stock_code}.html?type=year'  # 现金流量表
