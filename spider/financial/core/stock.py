import pandas as pd
import requests
import lxml

from lxml import etree
from financial.config import URL_GSZL, URL_ZCFZB, URL_LRB, URL_XJLLB
from financial.utils import pinyin, change_text, replace_db

class Stock:

    def __init__(self, code: str, category: None):
        self.code = code
        self.category = category
        self.__url_gszl = URL_GSZL.format(stock_code=self.code)
        self.__url_zcfzb = URL_ZCFZB.format(stock_code=self.code)
        self.__url_lrb = URL_LRB.format(stock_code=self.code)
        self.__url_xjllb = URL_XJLLB.format(stock_code=self.code)
        self.encoding = 'GB18030'
        self.__get_data()

    # 更新数据库
    def into_db(self):
        # 更新基础信息
        gszl_sql = """
            REPLACE INTO stock(
                code, zwjc, zwjc_py, gsqc, dy, zzxs, gswz, zyyw, jyfw,
                clrq, ssrq, sssc, zcxs, ssbjr, kjssws,
                category_id
            )
            VALUES({params})
        """.format(params=','.join(['%s' for i in range(16)]))
        gszl_sql_params = [
            self.code, self.zwjc, self.zwjc_py, self.gsqc, self.dy, self.zzxs, self.gswz, self.zyyw, self.jyfw,
            self.clrq, self.ssrq, self.sssc, self.zcxs, self.ssbjr, self.kjssws,
            self.category.id
        ]
        replace_db(gszl_sql, gszl_sql_params)

        # 插入现金流量表数据
        xjllb_sql = """
            INSERT INTO financial(code, year, yyhdxjll, tzhdxjll, czhdxjll)
            VALUES(%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE code = %s, year = %s, yyhdxjll = %s, tzhdxjll = %s, czhdxjll = %s
        """
        xjllb_sql_params = [
            [self.code, year, self.yyhdxjll[i], self.tzhdxjll[i], self.czhdxjll[i]] * 2
            for i, year in enumerate(self.years)
        ]
        replace_db(xjllb_sql, xjllb_sql_params, is_many=True, is_special_sql=True)

    # 市场
    def market(self):
        kv = {'6': '上海', '0': '深圳', '3': '深圳'}
        return kv[self.code[0]]
    
    # 抓取数据
    def __get_data(self):
        self.__get_data_gszl()
        self.__get_data_xjllb()
        self.__get_data_zcfzb()
        self.__get_data_lrb()

    # 基本信息
    def __get_data_gszl(self):
        response = requests.get(self.__url_gszl)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            self.zzxs = change_text(html.xpath('/html/body/div[2]/div[4]/table/tr[1]/td[2]')[0].text)  # 组织形式
            self.dy = html.xpath('/html/body/div[2]/div[4]/table/tr[1]/td[4]')[0].text  # 地域
            self.zwjc = html.xpath('/html/body/div[2]/div[4]/table/tr[2]/td[2]')[0].text  # 中文简称
            self.zwjc_py = pinyin(self.zwjc)  # 中文简称_拼音首字母
            self.gsqc = html.xpath('/html/body/div[2]/div[4]/table/tr[3]/td[2]')[0].text  # 公司全称

            comment = html.xpath('/html/body/div[2]/div[4]/table/comment()')[0]
            comment = etree.fromstring(comment.text)
            self.gswz = change_text(comment.xpath('/tr/td[2]')[0].text)  # 公司网站

            self.zyyw = html.xpath('/html/body/div[2]/div[4]/table/tr[10]/td[2]')[0].text.strip()  # 主营业务
            self.jyfw = html.xpath('/html/body/div[2]/div[4]/table/tr[11]/td[2]')[0].text.strip()  # 经营范围
            self.clrq = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[1]/td[2]')[0].text)  # 成立日期
            self.ssrq = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[2]/td[2]')[0].text)  # 上市日期
            self.sssc = self.market()  # 上市市场
            self.zcxs = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[16]/td[2]')[0].text)  # 主承销商
            self.ssbjr = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[17]/td[2]')[0].text)  # 上市保荐人
            self.kjssws = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[18]/td[2]')[0].text)  # 会计师事务所

    # 资产负债表
    def __get_data_zcfzb(self):
        # df = pd.read_csv(self.__url_zcfzb, encoding=self.encoding)
        # print(df)
        pass

    # 利润表
    def __get_data_lrb(self):
        pass

    # 现金流量表
    def __get_data_xjllb(self):
        df = pd.read_csv(self.__url_xjllb, encoding=self.encoding)
        self.years = [ymd[:4] for ymd in df.columns.to_list()[1:] if ymd.strip() != '']
        self.yyhdxjll = []  # CSV_LINE:26  DF_INDEX:24
        self.tzhdxjll = []  # CSV_LINE:41  DF_INDEX:39
        self.czhdxjll = []  # CSV_LINE:53  DF_INDEX:51
        for year in self.years:
            data = df[f'{year}-12-31']
            self.yyhdxjll.append(data[24])
            self.tzhdxjll.append(data[39])
            self.czhdxjll.append(data[51])
