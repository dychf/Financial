import json
import requests
import pymysql

from lxml import etree
from financial.config import URL_CATEGORY, CATEGORY_STOCK_PAGE_SIZE, URL_CATEGORY_STOCK
from financial.utils import replace_db

class Category:

    def __init__(self, id, name='', parent=None, order=None):
        self.id = id
        self.name = name
        self.parent = parent
        self.order = order
    
    def __str__(self):
        return f'{self.id} {self.name} {self.parent}'

    # 抓取数据
    @staticmethod
    def get_all_category():
        categorys = []
        response = requests.get(URL_CATEGORY)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            for i, parent_node in enumerate(html.xpath('//*[@id="f0-f7"]/ul/li')):
                parent_id = parent_node.get('qquery').split(':')[-1]
                parent_name = parent_node.find('a').get('title')
                categorys.append(Category(parent_id, parent_name, order=i + 1))
                for j, sub_node in enumerate(parent_node.findall('ul/li')):
                    sub_id = sub_node.get('qid')
                    sub_name = sub_node.find('a').get('title')
                    categorys.append(Category(sub_id, sub_name, parent_id, j + 1))
        return categorys

    # 获取分类下的所有股票代码
    def get_stock_codes(self):
        codes = []
        if self.parent is None:
            return codes

        page_no = 0
        while True:
            url = URL_CATEGORY_STOCK.format(page_no = page_no, page_size = CATEGORY_STOCK_PAGE_SIZE, category_id = self.id)
            response = requests.get(url)
            if response.status_code == 200:
                result = json.loads(response.text)
                if not result['list']:
                    break
                for item in result['list']:
                    code = item['SYMBOL']
                    if code[0] not in ['9', '2', '1', '5']:  # 排除B股、场内基金
                        codes.append(item['SYMBOL'])
            page_no += 1
        
        return codes

    # 更新数据库
    def into_db(self):
        sql = 'REPLACE INTO category(id, name, display, parent_id) VALUES(%s, %s, %s, %s)'
        params = [self.id, self.name, self.order, self.parent]
        replace_db(sql, params)
