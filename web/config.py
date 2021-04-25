DEBUG = True

SECRET = 'zpJIL73894'

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'holdle',
    'charset': 'utf8'
}

ERROR_CODE_OK = '200'
ERROR_CODE_NO_AUTH = '400'
ERROR_CODE_ERROR = '500'

HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': {
        'eastmoney': '12.push2.eastmoney.com'
    },
    'Referer': {
        '163': 'http://quotes.money.163.com/old/'
    },
    'User-Agent': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46'
    ]
}
# 指数
URL_INDEX = 'http://12.push2.eastmoney.com/api/qt/clist/get?cb=callback&pn=1&pz=50&fltt=2&invt=2&fid=&fs=b:MK0010&fields=f2,f3,f4,f12,f14'
# 热门分类
URL_CATEGORY = 'http://quotes.money.163.com/hs/realtimedata/service/plate.php?page=0&query=TYPE:HANGYE&fields=NAME,PERCENT,PLATE_ID,UPNUM,DOWNNUM&sort=PERCENT&order=desc&count=1000'
