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
                fhl = round(self.fhpx_px[i] * self.zcfzb_zgb[index] / 10 / self.lrb_jlr_gm[index] * 100, 2)
                temp.append(fhl)
            else:
                temp.append(None)
            fhl_sql_params.append(temp * 2)
        replace_db(fhl_sql, fhl_sql_params, is_many=True, is_special_sql=True)

        # ----- 资产负债比率（占总资产%）-----
        # 现金与约当现金、应收账款、存货、流动资产、应付账款、流动负债、长期负债、股东权益
        # ----- 财务结构 -----
        # 负债占资产比率、长期资金占不动产/厂房及设备比率
        # ----- 偿债能力 -----
        # 流动比率、速动比率
        # ----- 经营能力 -----
        # 应收账款周转率(次)、平均收现日数、存货周转率(次)、平均销货日数(在库天数)、不动产/厂房及设备周转率、总资产周转率(次)
        # ----- 获利能力 -----
        # 股东权益报酬率(ROE)、总资产报酬率(ROA)、营业毛利率、营业利益率
        zcfzbl_sql = """
            UPDATE financial
            SET
                xjyydxj_zzc_bl = %s,
                yszk_zzc_bl = %s,
                ch_zzc_bl = %s,
                ldzc_zzc_bl = %s,
                yfzk_zzc_bl = %s,
                ldfz_zzc_bl = %s,
                cqfz_zzc_bl = %s,
                gdqy_zzc_bl = %s,

                fz_zzc_bl = %s,
                cqzj_bdc_bl = %s,

                ldbl = %s,
                sdbl = %s,

                yszkzzl = %s,
                pjsxrs = %s,
                chzzl = %s,
                pjxhrs = %s,
                gdzczzl = %s,
                zzczzl = %s,

                gdqybcl = %s,
                zzcbcl = %s,
                yymll = %s,
                yylyl = %s
            WHERE code = %s AND year = %s
        """
        zcfzbl_sql_params = []
        for i, year in enumerate(self.years):
            zcfzb_zzc = self.zcfzb_zzc[i]  # 总资产
            temp = [
                round(self.zcfzb_xjyydxj[i] / zcfzb_zzc * 100, 2),  # 现金与约当现金
                round(self.zcfzb_yszk[i] / zcfzb_zzc * 100, 2),  # 应收账款
                round(self.zcfzb_ch[i] / zcfzb_zzc * 100, 2),  # 存货
                round(self.zcfzb_ldzc[i] / zcfzb_zzc * 100, 2),  # 流动资产
                round(self.zcfzb_yfzk[i] / zcfzb_zzc * 100, 2),  # 应付账款
                round(self.zcfzb_ldfz[i] / zcfzb_zzc * 100, 2),  # 流动负债
                round(self.zcfzb_cqfz[i] / zcfzb_zzc * 100, 2),  # 长期负债
                round(self.zcfzb_gdqy[i] / zcfzb_zzc * 100, 2),  # 股东权益

                round(self.zcfzb_zfz[i] / zcfzb_zzc * 100, 2),  # 负债占资产比率
                # 长期资金占不动产/厂房及设备比率：(长期负债 + 股东权益) / (固定资产 + 在建工程 + 工程物资)
                round((self.zcfzb_cqfz[i] + self.zcfzb_gdqy[i]) / (self.zcfzb_gdzc[i] + self.zcfzb_zjgc[i] + self.zcfzb_gcwz[i]) * 100, 2),

                round(self.zcfzb_ldzc[i] / self.zcfzb_ldfz[i] * 100, 2),  # 流动比率：流动资产 / 流动负债
                # 速动比率：(流动资产 - 存货 - 预付款项) / 流动负债
                round((self.zcfzb_ldzc[i] - self.zcfzb_ch[i] - self.zcfzb_yfkx[i]) / self.zcfzb_ldfz[i] * 100, 2),

                # 应收账款周转率(次)：营业收入 / 应收账款
                round(self.lrb_yysr[i] / self.zcfzb_yszk[i], 2),
                round(360 / round(self.lrb_yysr[i] / self.zcfzb_yszk[i], 2), 2),  # 平均收现日数：360 / 应收账款周转率(次)
                round(self.lrb_yycb[i] / self.zcfzb_ch[i], 2),  # 存货周转率(次)：营业成本 / 存货
                round(360 / round(self.lrb_yycb[i] / self.zcfzb_ch[i], 2), 2),  # 平均销货日数(在库天数)
                # 不动产/厂房及设备周转率(固定资产周转率)：营业收入 / (固定资产 + 在建工程 + 工程物资)
                round(self.lrb_yysr[i] / (self.zcfzb_gdzc[i] + self.zcfzb_zjgc[i] + self.zcfzb_gcwz[i]), 2),
                round(self.lrb_yysr[i] / self.zcfzb_zzc[i], 2),  # 总资产周转率(次)：营业收入 / 总资产

                round(self.lrb_jlr_gm[i] / self.zcfzb_gdqy_gm[i] * 100, 2),  # 股东权益报酬率(ROE)
                round(self.lrb_jlr_gm[i] / self.zcfzb_zzc[i] * 100, 2),  # 总资产报酬率(ROA)
                # 营业毛利率：(营业收入合计 - 营业成本合计) /  营业收入合计
                round((self.lrb_yysr_hj[i] - self.lrb_yycb_hj[i]) / self.lrb_yysr_hj[i] * 100, 2),
                round(self.lrb_yylr[i] / self.lrb_yysr[i] * 100, 2),  # 营业利益率：营业利润 / 营业收入

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
            self.zzxs = change_text(html.xpath('/html/body/div[2]/div[4]/table/tr[1]/td[2]')[0].text, to_type=str)  # 组织形式
            self.dy = html.xpath('/html/body/div[2]/div[4]/table/tr[1]/td[4]')[0].text  # 地域
            self.zwjc = html.xpath('/html/body/div[2]/div[4]/table/tr[2]/td[2]')[0].text  # 中文简称
            self.zwjc_py = pinyin(self.zwjc)  # 中文简称_拼音首字母
            self.gsqc = html.xpath('/html/body/div[2]/div[4]/table/tr[3]/td[2]')[0].text  # 公司全称

            comment = html.xpath('/html/body/div[2]/div[4]/table/comment()')[0]
            comment = etree.fromstring(comment.text)
            self.gswz = change_text(comment.xpath('/tr/td[2]')[0].text, to_type=str)  # 公司网站

            self.zyyw = html.xpath('/html/body/div[2]/div[4]/table/tr[10]/td[2]')[0].text.strip()  # 主营业务
            self.jyfw = html.xpath('/html/body/div[2]/div[4]/table/tr[11]/td[2]')[0].text.strip()  # 经营范围
            self.clrq = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[1]/td[2]')[0].text, to_type=str)  # 成立日期
            self.ssrq = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[2]/td[2]')[0].text, to_type=str)  # 上市日期
            self.sssc = self.market()  # 上市市场
            self.zcxs = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[16]/td[2]')[0].text, to_type=str)  # 主承销商
            self.ssbjr = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[17]/td[2]')[0].text, to_type=str)  # 上市保荐人
            self.kjssws = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[18]/td[2]')[0].text, to_type=str)  # 会计师事务所

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
                self.fhpx_sg.append(change_text(all_td[2].text, 0))
                self.fhpx_zz.append(change_text(all_td[3].text, 0))
                self.fhpx_px.append(change_text(all_td[4].text, 0))
                self.fhpx_cqcxr.append(change_text(all_td[6].text, to_type=str))

    # 资产负债表
    def __get_data_zcfzb(self):
        df = pd.read_csv(self.__url_zcfzb, encoding=self.encoding)
        self.zcfzb_zgb = []  # 总股本  CSV_LINE:96  DF_INDEX:94
        self.zcfzb_xjyydxj = []  # 现金与约当现金  CSV_LINE:2+3+4+5+6  DF_INDEX:0+1+2+3+4
        self.zcfzb_yszk = []  # 应收账款  CSV_LINE:8  DF_INDEX:6
        self.zcfzb_ch = []  # 存货 CSV_LINE:21  DF_INDEX:19
        self.zcfzb_ldzc = []  # 流动资产 CSV_LINE:26  DF_INDEX:24
        self.zcfzb_yfzk = []  # 应付账款 CSV_LINE:61  DF_INDEX:59
        self.zcfzb_yfkx = []  # 预付款项 CSV_LINE:9  DF_INDEX:7
        self.zcfzb_ldfz = []  # 流动负债 CSV_LINE:85  DF_INDEX:83
        self.zcfzb_cqfz = []  # 长期负债 CSV_LINE:94  DF_INDEX:92
        self.zcfzb_gdqy = []  # 股东权益 CSV_LINE:108  DF_INDEX:106
        self.zcfzb_gdqy_gm = []  # 归属母公司股东权益 CSV_LINE:106  DF_INDEX:104
        self.zcfzb_gdzc = []  # 固定资产 CSV_LINE:38  DF_INDEX:36
        self.zcfzb_zjgc = []  # 在建工程 CSV_LINE:39  DF_INDEX:37
        self.zcfzb_gcwz = []  # 工程物资 CSV_LINE:40  DF_INDEX:38
        self.zcfzb_zfz = []  # 总负债 CSV_LINE:95  DF_INDEX:93
        self.zcfzb_zzc = []  # 总资产 CSV_LINE:53  DF_INDEX:51
        for year in self.years:
            data = df[f'{year}-12-31']
            # 总股本
            self.zcfzb_zgb.append(change_text(data[94], 0))
            # 现金与约当现金
            v_csv_2 = change_text(data[0], 0)
            v_csv_3 = change_text(data[1], 0)
            v_csv_4 = change_text(data[2], 0)
            v_csv_5 = change_text(data[3], 0)
            v_csv_6 = change_text(data[4], 0)
            self.zcfzb_xjyydxj.append(v_csv_2 + v_csv_3 + v_csv_4 + v_csv_5 + v_csv_6)
            # 应收账款
            self.zcfzb_yszk.append(change_text(data[6], 0))
            # 预付款项
            self.zcfzb_yfkx.append(change_text(data[7], 0))
            # 存货
            self.zcfzb_ch.append(change_text(data[19], 0))
            # 流动资产
            self.zcfzb_ldzc.append(change_text(data[24], 0))
            # 应付账款
            self.zcfzb_yfzk.append(change_text(data[59], 0))
            # 流动负债
            self.zcfzb_ldfz.append(change_text(data[83], 0))
            # 长期负债
            self.zcfzb_cqfz.append(change_text(data[92], 0))
            # 股东权益
            self.zcfzb_gdqy.append(change_text(data[106], 0))
            # 归属母公司股东权益
            self.zcfzb_gdqy_gm.append(change_text(data[104], 0))
            # 总负债
            self.zcfzb_zfz.append(change_text(data[93], 0))
            # 固定资产
            self.zcfzb_gdzc.append(change_text(data[36], 0))
            # 在建工程
            self.zcfzb_zjgc.append(change_text(data[37], 0))
            # 工程物资
            self.zcfzb_gcwz.append(change_text(data[38], 0))
            # 总资产
            self.zcfzb_zzc.append(change_text(data[51], 0))

    # 利润表
    def __get_data_lrb(self):
        df = pd.read_csv(self.__url_lrb, encoding=self.encoding)
        self.lrb_jlr_gm = []  # 归属于母公司所有者的净利润  CSV_LINE:42  DF_INDEX:40
        self.lrb_yysr = []  # 营业收入  CSV_LINE:2  DF_INDEX:0
        self.lrb_yysr_hj = []  # 营业收入合计  CSV_LINE:3+4+5+6+7+8  DF_INDEX:1+2+3+4+5+6
        self.lrb_yycb = []  # 营业成本  CSV_LINE:10  DF_INDEX:8
        self.lrb_yycb_hj = []  # 营业成本合计  CSV_LINE:10~21  DF_INDEX:8~19
        self.lrb_yylr = []  # 营业利润  CSV_LINE:34  DF_INDEX:32
        for year in self.years:
            data = df[f'{year}-12-31']
            self.lrb_jlr_gm.append(change_text(data[40], 0))
            self.lrb_yysr.append(change_text(data[0], 0))
            self.lrb_yysr_hj.append(sum([change_text(v, 0) for v in data[1:7]]))
            self.lrb_yycb.append(change_text(data[8], 0))
            self.lrb_yycb_hj.append(sum([change_text(v, 0) for v in data[8:20]]))
            self.lrb_yylr.append(change_text(data[32], 0))

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
