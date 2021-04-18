DEBUG = True

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'holdle',
    'charset': 'utf8'
}

ERROR_CODE_OK = '200000'

HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': '12.push2.eastmoney.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}
URL_INDEX = 'http://12.push2.eastmoney.com/api/qt/clist/get?cb=callback&pn=1&pz=50&fltt=2&invt=2&fid=&fs=b:MK0010&fields=f2,f3,f4,f12,f14'
