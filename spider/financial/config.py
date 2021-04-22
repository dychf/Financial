import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 断点续爬配置文件
LOCATION_FILE_NAME = 'progress.json'
LOCATION_FILE_PATH = os.path.join(BASE_PATH, LOCATION_FILE_NAME)

# 间隔多少天重新爬数据
TASK_INTERVAL_DAY = 7
TASK_EXCEPTION_SLEEP_TIME = 10

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'holdle',
    'charset': 'utf8'
}

# 请求头
HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': 'quotes.money.163.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
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
URL_ZCFZB = 'http://quotes.money.163.com/service/zcfzb_{stock_code}.html'  # 资产负债表
URL_LRB = 'http://quotes.money.163.com/service/lrb_{stock_code}.html'  # 利润表
URL_XJLLB = 'http://quotes.money.163.com/service/xjllb_{stock_code}.html'  # 现金流量表

# 流行指数：上证50、沪深300、中证500、红利指数、科创50
URL_INDEX_SZ50 = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000016cons.xls'
URL_INDEX_HS300 = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000300cons.xls'
URL_INDEX_ZZ500 = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000905cons.xls'
URL_INDEX_HLZS = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000015cons.xls'
URL_INDEX_KC50 = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000688cons.xls'