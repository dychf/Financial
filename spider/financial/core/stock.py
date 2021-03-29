import pandas as pd
import requests
import lxml

from lxml import etree
from financial.config import URL_GSZL, URL_FHPX, URL_ZCFZB, URL_LRB, URL_XJLLB
from financial.utils import pinyin, change_text, replace_db

class Stock:

    def __init__(self, code: str, category: None):
        self.code = code
        self.category = category
        self.__url_gszl = URL_GSZL.format(stock_code=self.code)
        self.__url_zcfzb = URL_ZCFZB.format(stock_code=self.code)
        self.__url_lrb = URL_LRB.format(stock_code=self.code)
        self.__url_xjllb = URL_XJLLB.format(stock_code=self.code)
        self.__url_fhpx = URL_FHPX.format(stock_code=self.code)
        self.encoding = 'GB18030'
        self.__get_data()

    # 更新数据库
    def into_db(self):
        # 基础信息
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

        # 营业活动现金流量、投资活动现金流量、筹资活动现金流量
        xjllb_sql = """
            INSERT INTO financial(code, year, yyhdxjll, tzhdxjll, czhdxjll)
            VALUES(%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE code = %s, year = %s, yyhdxjll = %s, tzhdxjll = %s, czhdxjll = %s
        """
        xjllb_sql_params = [
            [self.code, year, self.xjllb_yyhdxjll[i], self.xjllb_tzhdxjll[i], self.xjllb_czhdxjll[i]] * 2
            for i, year in enumerate(self.years)
        ]
        replace_db(xjllb_sql, xjllb_sql_params, is_many=True, is_special_sql=True)

        # 分红派息
        # 分红率：(每十股分红金额 * 总股本) / 10 / 归属于母公司所有者的净利润
        fhl_sql = """
            INSERT INTO dividend(code, year, sg, zz, px, cqcxr, fhl)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE code = %s, year = %s, sg = %s, zz = %s, px = %s, cqcxr = %s, fhl = %s
        """
        fhl_sql_params = []
        for i, year in enumerate(self.fhpx_years):
            temp = [self.code, year, self.fhpx_sg[i], self.fhpx_zz[i], self.fhpx_px[i], self.fhpx_cqcxr[i]]
            if year in self.years:
                index = self.years.index(year)
                fhl = self.fhpx_px[i] * self.zcfzb_zgb[index] / 10 / self.lrb_jlr[index]
                temp.append(fhl)
            else:
                temp.append(None)
            fhl_sql_params.append(temp * 2)
        replace_db(fhl_sql, fhl_sql_params, is_many=True, is_special_sql=True)

        # 资产负债比率（占总资产%）
        # 现金与约当现金、应收账款、存货、流动资产、应付账款、流动负债
        zcfzbl_sql = """
            UPDATE financial
            SET
                xjyydxj_zzc_bl = %s,
                yszk_zzc_bl = %s,
                ch_zzc_bl = %s,
                ldzc_zzc_bl = %s,
                yfzk_zzc_bl = %s,
                ldfz_zzc_bl = %s
            WHERE code = %s AND year = %s
        """
        zcfzbl_sql_params = []
        for i, year in enumerate(self.years):
            zcfzb_zzc = self.zcfzb_zzc[i]  # 总资产
            temp = [
                self.zcfzb_xjyydxj[i] / zcfzb_zzc,  # 现金与约当现金
                self.zcfzb_yszk[i] / zcfzb_zzc,  # 应收账款
                self.zcfzb_ch[i] / zcfzb_zzc,  # 存货
                self.zcfzb_ldzc[i] / zcfzb_zzc,  # 流动资产
                self.zcfzb_yfzk[i] / zcfzb_zzc,  # 应付账款
                self.zcfzb_ldfz[i] / zcfzb_zzc,  # 流动负债
                self.code, year
            ]
            zcfzbl_sql_params.append(temp)
        replace_db(zcfzbl_sql, zcfzbl_sql_params, is_many=True)

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
        self.__get_data_fhpx()

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

    # 分红派息
    def __get_data_fhpx(self):
        response = requests.get(self.__url_fhpx)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            nodes = html.cssselect('body > div.area > div:nth-child(5) > table > tr')
            self.fhpx_years = []  # 分红派息年份
            self.fhpx_sg = []  # 送股
            self.fhpx_zz = []  # 转增
            self.fhpx_px = []  # 派息
            self.fhpx_cqcxr = []  # 除权除息日
            for i, node in enumerate(nodes):
                all_td = node.findall('td')
                self.fhpx_years.append(all_td[1].text)
                self.fhpx_sg.append(int(change_text(all_td[2].text, 0)))
                self.fhpx_zz.append(int(change_text(all_td[3].text, 0)))
                self.fhpx_px.append(float(change_text(all_td[4].text, 0)))
                self.fhpx_cqcxr.append(change_text(all_td[6].text))

    # 资产负债表
    def __get_data_zcfzb(self):
        df = pd.read_csv(self.__url_zcfzb, encoding=self.encoding)
        self.zcfzb_zgb = []  # 总股本  CSV_LINE:96  DF_INDEX:94
        self.zcfzb_xjyydxj = []  # 现金与约当现金  CSV_LINE:2+3+4+5+6  DF_INDEX:0+1+2+3+4
        self.zcfzb_yszk = []  # 应收账款  CSV_LINE:8  DF_INDEX:6
        self.zcfzb_ch = []  # 存货 CSV_LINE:21  DF_INDEX:19
        self.zcfzb_ldzc = []  # 流动资产 CSV_LINE:26  DF_INDEX:24
        self.zcfzb_yfzk = []  # 应付账款 CSV_LINE:61  DF_INDEX:59
        self.zcfzb_ldfz = []  # 流动负债 CSV_LINE:85  DF_INDEX:83
        self.zcfzb_zzc = []  # 总资产 CSV_LINE:53  DF_INDEX:51
        for year in self.years:
            data = df[f'{year}-12-31']
            # 总股本
            self.zcfzb_zgb.append(float(change_text(data[94], 0)))
            # 现金与约当现金
            v_csv_2 = float(change_text(data[0], 0))
            v_csv_3 = float(change_text(data[1], 0))
            v_csv_4 = float(change_text(data[2], 0))
            v_csv_5 = float(change_text(data[3], 0))
            v_csv_6 = float(change_text(data[4], 0))
            self.zcfzb_xjyydxj.append(v_csv_2 + v_csv_3 + v_csv_4 + v_csv_5 + v_csv_6)
            # 应收账款
            self.zcfzb_yszk.append(float(change_text(data[6], 0)))
            # 存货
            self.zcfzb_ch.append(float(change_text(data[19], 0)))
            # 流动资产
            self.zcfzb_ldzc.append(float(change_text(data[24], 0)))
            # 应付账款
            self.zcfzb_yfzk.append(float(change_text(data[59], 0)))
            # 流动负债
            self.zcfzb_ldfz.append(float(change_text(data[83], 0)))
            # 总资产
            self.zcfzb_zzc.append(float(change_text(data[51], 0)))

    # 利润表
    def __get_data_lrb(self):
        df = pd.read_csv(self.__url_lrb, encoding=self.encoding)
        self.lrb_jlr = []  # 归属于母公司所有者的净利润  CSV_LINE:42  DF_INDEX:40
        for year in self.years:
            data = df[f'{year}-12-31']
            self.lrb_jlr.append(float(data[40]))

    # 现金流量表
    def __get_data_xjllb(self):
        df = pd.read_csv(self.__url_xjllb, encoding=self.encoding)
        self.years = [ymd[:4] for ymd in df.columns.to_list()[1:] if ymd.strip() != '' and ymd[:4].isdigit()]
        self.xjllb_yyhdxjll = []  # 营业活动现金流量  CSV_LINE:26  DF_INDEX:24
        self.xjllb_tzhdxjll = []  # 投资活动现金流量  CSV_LINE:41  DF_INDEX:39
        self.xjllb_czhdxjll = []  # 筹资活动现金流量  CSV_LINE:53  DF_INDEX:51
        for year in self.years:
            data = df[f'{year}-12-31']
            self.xjllb_yyhdxjll.append(data[24])
            self.xjllb_tzhdxjll.append(data[39])
            self.xjllb_czhdxjll.append(data[51])
