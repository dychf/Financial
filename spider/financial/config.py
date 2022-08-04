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
    'password': 'sergserg',
    'database': 'financial',
    'charset': 'utf8'
}

# 请求头
HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': {
        'eastmoney': '12.push2.eastmoney.com',
        '163': 'quotes.money.163.com'
    },
    'Referer': {
        '163': 'http://quotes.money.163.com/old/'
    },
    'User-Agent': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:65.0) Gecko/20100101 Firefox/65.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/31.0.1650.18 Mobile/11B554a Safari/8536.25',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4',
        'Mozilla/5.0 (Linux; Android 4.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.59 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; M351 Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
    ]
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
