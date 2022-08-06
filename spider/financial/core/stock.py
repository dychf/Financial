import pandas as pd
import requests
import gc

from lxml import etree
from financial.config import URL_GSZL, URL_FHPX, URL_ZCFZB, URL_LRB, URL_XJLLB
from financial.config import URL_INDEX_SZ50, URL_INDEX_HS300, URL_INDEX_ZZ500, URL_INDEX_HLZS, URL_INDEX_KC50
from financial.utils import pinyin, change_text, replace_db, read_net_file


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
        # self.is_sz50 = 1 if code in Stock.SZ50 else 0
        # self.is_hs300 = 1 if code in Stock.HS300 else 0
        # self.is_zz500 = 1 if code in Stock.ZZ500 else 0
        # self.is_hlzs = 1 if code in Stock.HLZS else 0
        # self.is_kc50 = 1 if code in Stock.KC50 else 0
        self.is_sz50 = 0
        self.is_hs300 = 0
        self.is_zz500 = 0
        self.is_hlzs = 0
        self.is_kc50 = 0

    # 更新数据库
    def into_db(self):
        # 基础信息
        gszl_sql = """
            REPLACE INTO stock(
                code, zwjc, zwjc_py, gsqc, dy, zzxs, gswz, zyyw, jyfw,
                clrq, ssrq, sssc, zcxs, ssbjr, kjssws,
                sz50, hs300, zz500, hlzs, kc50,
                category_id
            )
            VALUES({params})
        """.format(params=','.join(['%s' for i in range(21)]))
        gszl_sql_params = [
            self.code, self.zwjc, self.zwjc_py, self.gsqc, self.dy, self.zzxs, self.gswz, self.zyyw, self.jyfw,
            self.clrq, self.ssrq, self.sssc, self.zcxs, self.ssbjr, self.kjssws,
            self.is_sz50, self.is_hs300, self.is_zz500, self.is_hlzs, self.is_kc50,
            self.category.id
        ]
        replace_db(gszl_sql, gszl_sql_params)

        # 分红派息
        # 分红率：(每十股分红金额 * 总股本) / 10 / 归属于母公司所有者的净利润
        fhl_sql = """
            INSERT INTO dividend(code, year, sg, zz, px, ggrq, cqcxr, fhl)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE code = %s, year = %s, sg = %s, zz = %s, px = %s, ggrq = %s, cqcxr = %s, fhl = %s
        """
        fhl_sql_params = []
        for i, year in enumerate(self.fhpx_years):
            temp = [self.code, year, self.fhpx_sg[i], self.fhpx_zz[i], self.fhpx_px[i], self.fhpx_ggrq[i],
                    self.fhpx_cqcxr[i]]
            if f'{year}-12-31' not in self.zcfzb_dates or f'{year}-12-31' not in self.lrb_dates:
                temp.append(None)
            else:
                try:
                    zcfzb_zgb_index = self.zcfzb_dates.index(f'{year}-12-31')
                    lrb_jlr_gm_index = self.lrb_dates.index(f'{year}-12-31')
                    fhl = round(self.fhpx_px[i] * self.zcfzb_zgb[zcfzb_zgb_index] / 10 / self.lrb_jlr_gm[
                        lrb_jlr_gm_index] * 100, 2)
                    temp.append(fhl)
                except:
                    temp.append(None)
            fhl_sql_params.append(temp * 2)
        replace_db(fhl_sql, fhl_sql_params, is_many=True, is_special_sql=True)

        self.dates = list(set(self.zcfzb_dates) | set(self.lrb_dates) | set(self.xjllb_dates))
        self.dates = [date for date in self.dates if date[5:7] in ['03', '06', '09', '12']]

        # 返回季报期
        def return_report(date: str):
            y, m, d = date.split('-')
            map_dict = {'03': 'Q1', '06': 'Q2', '09': 'Q3', '12': 'Q4'}
            return map_dict[m]

        # 初始化
        init_sql = """
            INSERT INTO financial(code, year, report) VALUES(%s, %s, %s)
            ON DUPLICATE KEY UPDATE code = %s, year = %s, report = %s
        """
        init_sql_params = [[self.code, date[:4], return_report(date)] * 2 for date in self.dates]
        replace_db(init_sql, init_sql_params, is_many=True, is_special_sql=True)

        # 营业活动现金流量、投资活动现金流量、筹资活动现金流量
        xjllb_sql = """
            UPDATE financial SET yyhdxjll = %s, tzhdxjll = %s, czhdxjll = %s
            WHERE code = %s AND year = %s AND report = %s
        """
        xjllb_sql_params = [
            [self.xjllb_yyhdxjll[i], self.xjllb_tzhdxjll[i], self.xjllb_czhdxjll[i], self.code, date[:4],
             return_report(date)]
            for i, date in enumerate(self.xjllb_dates) if date[5:7] in ['03', '06', '09', '12']
        ]
        replace_db(xjllb_sql, xjllb_sql_params, is_many=True)

        # ----- 资产负债比率（占总资产%）-----
        # 现金与约当现金、应收账款、存货、流动资产、应付账款、流动负债、长期负债、股东权益
        # ----- 财务结构 -----
        # 负债占资产比率、长期资金占不动产/厂房及设备比率
        # ----- 偿债能力 -----
        # 流动比率、速动比率
        # ----- 经营能力 -----
        # 应收账款周转率(次)、平均收现日数、存货周转率(次)、平均销货日数(在库天数)、不动产/厂房及设备周转率、总资产周转率(次)
        # ----- 获利能力 -----
        # 股东权益报酬率(ROE)、总资产报酬率(ROA)、营业毛利率、营业利益率、经营安全边际率、净利率、每股盈余、税后净利
        # ----- 现金流量 -----
        # 现金流量比率、现金流量允当比率、现金再投资比例
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
                yylyl = %s,
                jyaqbjl = %s,
                jll = %s,
                mgyy = %s,
                shjl = %s,

                xjllbl = %s,
                xjllydbl = %s,
                xjztzbl = %s
            WHERE code = %s AND year = %s AND report = %s
        """
        zcfzbl_sql_params = []

        def calc_xjllydbl(date: str):  # 计算：现金流量允当比率
            # 没当年数据
            if date not in self.xjllb_dates:
                return None

            # 截取五年年份
            end_dates = [date for date in self.xjllb_dates if date.endswith('-12-31')]
            index = end_dates.index(date)
            dates = end_dates[index: index + 5]

            # 未满五年，或者五年之间差数据
            if len(dates) < 5:
                return None
            end_year = int(date[:4])
            start_year = end_year - 4
            if start_year != int(dates[-1][:4]):
                return None

            # 近5年营业活动现金流量 / 近5年(资本支出 + 存货增加额 + 现金股利)
            # 存货增加额 = -(存货减少额)  注：存货减少额中负数表示增加
            xjllb_yyhdxjll = [self.xjllb_yyhdxjll[self.xjllb_dates.index(date)] for date in dates]
            xjllb_zbzc = [self.xjllb_zbzc[self.xjllb_dates.index(date)] for date in dates]
            xjllb_chjse = [self.xjllb_chjse[self.xjllb_dates.index(date)] for date in dates]
            xjllb_xjgl = [self.xjllb_xjgl[self.xjllb_dates.index(date)] for date in dates]
            return sum(xjllb_yyhdxjll) / (sum(xjllb_zbzc) - sum(xjllb_chjse) + sum(xjllb_xjgl))

        def calc_xjyydxj(date: str):  # 计算：现金与约当现金
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_xjyydxj[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_yszk(date: str):  # 计算：应收账款
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_yszk[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_ch(date: str):  # 计算：存货
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_ch[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_ldzc(date: str):  # 计算：流动资产
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_ldzc[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_yfzk(date: str):  # 计算：应付账款
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_yfzk[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_ldfz(date: str):  # 计算：流动负债
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_ldfz[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_cqfz(date: str):  # 计算：长期负债
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_cqfz[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_gdqy(date: str):  # 计算：股东权益
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_gdqy[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_fzzzcbl(date: str):  # 计算：负债占资产比率
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_zfz[i] / self.zcfzb_zzc[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        # 计算：长期资金占不动产/厂房及设备比率：(长期负债 + 股东权益) / (固定资产 + 在建工程 + 工程物资)
        def calc_cqzjzbdcbl(date: str):
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round((self.zcfzb_cqfz[i] + self.zcfzb_gdqy[i]) / (
                        self.zcfzb_gdzc[i] + self.zcfzb_zjgc[i] + self.zcfzb_gcwz[i]) * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_ldbl(date: str):  # 计算：流动比率：流动资产 / 流动负债
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round(self.zcfzb_ldzc[i] / self.zcfzb_ldfz[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_sdbl(date: str):  # 计算：速动比率：(流动资产 - 存货 - 预付款项) / 流动负债
            if date not in self.zcfzb_dates:
                return None
            try:
                i = self.zcfzb_dates.index(date)
                return round((self.zcfzb_ldzc[i] - self.zcfzb_ch[i] - self.zcfzb_yfkx[i]) / self.zcfzb_ldfz[i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_yszkzzl(date: str):  # 计算：应收账款周转率(次)：营业收入 / 应收账款
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.lrb_yysr[lrb_i] / self.zcfzb_yszk[zcfzb_i], 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_pjsxrs(date: str):  # 计算：平均收现日数：360 / 应收账款周转率(次)
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(360 / round(self.lrb_yysr[lrb_i] / self.zcfzb_yszk[zcfzb_i], 2), 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_chzzl(date: str):  # 计算：存货周转率(次)：营业成本 / 存货
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.lrb_yycb[lrb_i] / self.zcfzb_ch[zcfzb_i], 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_pjxhrs(date: str):  # 计算：平均销货日数(在库天数)：360 / 存货周转率(次)
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(360 / round(self.lrb_yycb[lrb_i] / self.zcfzb_ch[zcfzb_i], 2), 2)
            except(ValueError, ZeroDivisionError):
                return None

        # 不动产/厂房及设备周转率(固定资产周转率)：营业收入 / (固定资产 + 在建工程 + 工程物资)
        def calc_gdzczzl(date: str):
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.lrb_yysr[lrb_i] / (
                        self.zcfzb_gdzc[zcfzb_i] + self.zcfzb_zjgc[zcfzb_i] + self.zcfzb_gcwz[zcfzb_i]), 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_zzczzl(date: str):  # 总资产周转率(次)：营业收入 / 总资产
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.lrb_yysr[lrb_i] / self.zcfzb_zzc[zcfzb_i], 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_roe(date: str):  # 股东权益报酬率(ROE)
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.lrb_jlr_gm[lrb_i] / self.zcfzb_gdqy_gm[zcfzb_i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_roa(date: str):  # 总资产报酬率(ROA)
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.lrb_jlr_gm[lrb_i] / self.zcfzb_zzc[zcfzb_i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_yymll(date: str):  # 营业毛利率：(营业收入合计 - 营业成本合计) / 营业收入合计
            if date not in self.lrb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                return round((self.lrb_yysr_hj[lrb_i] - self.lrb_yycb_hj[lrb_i]) / self.lrb_yysr_hj[lrb_i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_yylyl(date: str):  # # 营业利益率：营业利润 / 营业收入
            if date not in self.lrb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                return round(self.lrb_yylr[lrb_i] / self.lrb_yysr[lrb_i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_jyaqbjl(date: str):  # 经营安全边际率：营业利益率 / 营业毛利率
            if date not in self.lrb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                return round(round(self.lrb_yylr[lrb_i] / self.lrb_yysr[lrb_i] * 100, 2) / round(
                    (self.lrb_yysr_hj[lrb_i] - self.lrb_yycb_hj[lrb_i]) / self.lrb_yysr_hj[lrb_i] * 100, 2) * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_jll(date: str):  # 净利率：净利润 / 营业收入
            if date not in self.lrb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                return round(self.lrb_jlr[lrb_i] / self.lrb_yysr[lrb_i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        def calc_mgyy(date: str):  # 每股盈余
            if date not in self.lrb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                return self.lrb_mgyy[lrb_i]
            except ValueError:
                return None

        def calc_shjl(date: str):  # 税后净利
            if date not in self.lrb_dates:
                return None
            try:
                lrb_i = self.lrb_dates.index(date)
                return self.lrb_jlr[lrb_i]
            except ValueError:
                return None

        def calc_xjllbl(date: str):  # 现金流量比率：营业活动现金流量 / 流动负债
            if date not in self.xjllb_dates or date not in self.zcfzb_dates:
                return None
            try:
                xjllb_i = self.xjllb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round(self.xjllb_yyhdxjll[xjllb_i] / self.zcfzb_ldfz[zcfzb_i] * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        # 现金再投资比例：(营业活动现金流量 - 现金股利) / (固定资产毛额 + 长期投资 + 其他资产 + 营运资金) 分母等同于 (资产总额 - 流动负债)
        def calc_xjztzbl(date: str):
            if date not in self.lrb_dates or date not in self.zcfzb_dates:
                return None
            try:
                xjllb_i = self.xjllb_dates.index(date)
                zcfzb_i = self.zcfzb_dates.index(date)
                return round((self.xjllb_yyhdxjll[xjllb_i] - self.xjllb_xjgl[xjllb_i]) / (
                        self.zcfzb_zzc[zcfzb_i] - self.zcfzb_ldfz[zcfzb_i]) * 100, 2)
            except(ValueError, ZeroDivisionError):
                return None

        for i, date in enumerate(self.dates):
            # 现金流量允当比率
            if date.endswith('-12-31'):
                try:
                    xjllydbl = calc_xjllydbl(date)
                    xjllydbl = round(xjllydbl * 100, 2)
                except:
                    xjllydbl = None
            else:
                xjllydbl = None
            temp = [
                calc_xjyydxj(date),  # 现金与约当现金
                calc_yszk(date),  # 应收账款
                calc_ch(date),  # 存货
                calc_ldzc(date),  # 流动资产
                calc_yfzk(date),  # 应付账款
                calc_ldfz(date),  # 流动负债
                calc_cqfz(date),  # 长期负债
                calc_gdqy(date),  # 股东权益

                calc_fzzzcbl(date),  # 负债占资产比率
                calc_cqzjzbdcbl(date),  # 长期资金占不动产/厂房及设备比率：(长期负债 + 股东权益) / (固定资产 + 在建工程 + 工程物资)

                calc_ldbl(date),  # 流动比率：流动资产 / 流动负债
                calc_sdbl(date),  # 速动比率：(流动资产 - 存货 - 预付款项) / 流动负债

                calc_yszkzzl(date),  # 应收账款周转率(次)：营业收入 / 应收账款
                calc_pjsxrs(date),  # 平均收现日数：360 / 应收账款周转率(次)
                calc_chzzl(date),  # 存货周转率(次)：营业成本 / 存货
                calc_pjxhrs(date),  # 平均销货日数(在库天数)：360 / 存货周转率(次)
                calc_gdzczzl(date),  # 不动产/厂房及设备周转率(固定资产周转率)：营业收入 / (固定资产 + 在建工程 + 工程物资)
                calc_zzczzl(date),  # 总资产周转率(次)：营业收入 / 总资产

                calc_roe(date),  # 股东权益报酬率(ROE)
                calc_roa(date),  # 总资产报酬率(ROA)
                calc_yymll(date),  # 营业毛利率：(营业收入合计 - 营业成本合计) / 营业收入合计
                calc_yylyl(date),  # 营业利益率：营业利润 / 营业收入
                calc_jyaqbjl(date),  # 经营安全边际率：营业利益率 / 营业毛利率
                calc_jll(date),  # 净利率：净利润 / 营业收入
                calc_mgyy(date),  # 每股盈余
                calc_shjl(date),  # 税后净利

                calc_xjllbl(date),  # 现金流量比率：营业活动现金流量 / 流动负债
                xjllydbl,  # 现金流量允当比率：近5年营业活动现金流量 /  近5年(资本支出 + 存货减少额 + 现金股利)
                # 现金再投资比例：(营业活动现金流量 - 现金股利) / (固定资产毛额 + 长期投资 + 其他资产 + 营运资金) 分母等同于 (资产总额 - 流动负债)
                calc_xjztzbl(date),

                self.code, date[:4], return_report(date)
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

        self.zzxs = ''  # 组织形式
        self.dy = ''  # 地域
        self.zwjc = ''  # 中文简称
        self.zwjc_py = ''  # 中文简称_拼音首字母
        self.gsqc = ''  # 公司全称
        self.gswz = ''  # 公司网站
        self.zyyw = ''  # 主营业务
        self.jyfw = ''  # 经营范围
        self.clrq = None  # 成立日期
        self.ssrq = None  # 上市日期
        self.sssc = ''  # 上市市场
        self.zcxs = ''  # 主承销商
        self.ssbjr = ''  # 上市保荐人
        self.kjssws = ''  # 会计师事务所

        response = requests.get(self.__url_gszl)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            self.zzxs = change_text(html.xpath('/html/body/div[2]/div[4]/table/tr[1]/td[2]')[0].text,
                                    to_type=str)  # 组织形式
            self.dy = html.xpath('/html/body/div[2]/div[4]/table/tr[1]/td[4]')[0].text  # 地域
            self.zwjc = html.xpath('/html/body/div[2]/div[4]/table/tr[2]/td[2]')[0].text  # 中文简称
            self.zwjc_py = pinyin(self.zwjc)  # 中文简称_拼音首字母
            self.gsqc = html.xpath('/html/body/div[2]/div[4]/table/tr[3]/td[2]')[0].text  # 公司全称

            comment = html.xpath('/html/body/div[2]/div[4]/table/comment()')[0]
            comment = etree.fromstring(comment.text)
            self.gswz = change_text(comment.xpath('/tr/td[2]')[0].text, to_type=str)  # 公司网站

            self.zyyw = html.xpath('/html/body/div[2]/div[4]/table/tr[10]/td[2]')[0].text  # 主营业务
            self.zyyw = self.zyyw.strip() if self.zyyw else ''
            self.jyfw = html.xpath('/html/body/div[2]/div[4]/table/tr[11]/td[2]')[0].text.strip()  # 经营范围
            self.clrq = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[1]/td[2]')[0].text,
                                    to_type=str)  # 成立日期
            self.ssrq = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[2]/td[2]')[0].text,
                                    to_type=str)  # 上市日期
            self.sssc = self.market()  # 上市市场
            self.zcxs = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[16]/td[2]')[0].text,
                                    to_type=str)  # 主承销商
            self.ssbjr = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[17]/td[2]')[0].text,
                                     to_type=str)  # 上市保荐人
            self.kjssws = change_text(html.xpath('/html/body/div[2]/div[5]/table/tr[18]/td[2]')[0].text,
                                      to_type=str)  # 会计师事务所

            del response
            gc.collect()

    # 分红派息
    def __get_data_fhpx(self):

        self.fhpx_ggrq = []  # 公告日期
        self.fhpx_years = []  # 分红派息年份
        self.fhpx_sg = []  # 送股
        self.fhpx_zz = []  # 转增
        self.fhpx_px = []  # 派息
        self.fhpx_cqcxr = []  # 除权除息日

        response = requests.get(self.__url_fhpx)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            nodes = html.cssselect('body > div.area > div:nth-child(5) > table > tr')
            for i, node in enumerate(nodes):
                all_td = node.findall('td')
                if len(all_td) == 1:  # 暂无数据
                    break
                self.fhpx_ggrq.append(all_td[0].text)
                self.fhpx_years.append(all_td[1].text)
                self.fhpx_sg.append(change_text(all_td[2].text, 0))
                self.fhpx_zz.append(change_text(all_td[3].text, 0))
                self.fhpx_px.append(change_text(all_td[4].text, 0))
                self.fhpx_cqcxr.append(change_text(all_td[6].text, to_type=str))

            del response
            gc.collect()

    # 资产负债表
    def __get_data_zcfzb(self):

        self.zcfzb_dates = []
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

        response = requests.get(self.__url_zcfzb)
        if response.status_code == 200:
            df = pd.read_csv(self.__url_zcfzb, encoding=self.encoding)
            self.zcfzb_dates = [ymd for ymd in df.columns.to_list()[1:] if ymd.strip() != '' and ymd[:4].isdigit()]
            for date in self.zcfzb_dates:
                data = df[date]
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

            del df
            gc.collect()

    # 利润表
    def __get_data_lrb(self):

        self.lrb_dates = []
        self.lrb_jlr_gm = []  # 归属于母公司所有者的净利润  CSV_LINE:42  DF_INDEX:40
        self.lrb_jlr = []  # 净利润  CSV_LINE:41  DF_INDEX:39
        self.lrb_yysr = []  # 营业收入  CSV_LINE:2  DF_INDEX:0
        self.lrb_yysr_hj = []  # 营业收入合计  CSV_LINE:3+4+5+6+7+8  DF_INDEX:1+2+3+4+5+6
        self.lrb_yycb = []  # 营业成本  CSV_LINE:10  DF_INDEX:8
        self.lrb_yycb_hj = []  # 营业成本合计  CSV_LINE:10~21  DF_INDEX:8~19
        self.lrb_yylr = []  # 营业利润  CSV_LINE:34  DF_INDEX:32
        self.lrb_mgyy = []  # 每股盈余  CSV_LINE:45  DF_INDEX:43

        response = requests.get(self.__url_lrb)
        if response.status_code == 200:
            df = pd.read_csv(self.__url_lrb, encoding=self.encoding)
            self.lrb_dates = [ymd for ymd in df.columns.to_list()[1:] if ymd.strip() != '' and ymd[:4].isdigit()]
            for date in self.lrb_dates:
                data = df[date]
                self.lrb_jlr_gm.append(change_text(data[40], 0))
                self.lrb_jlr.append(change_text(data[39], 0))
                self.lrb_yysr.append(change_text(data[0], 0))
                self.lrb_yysr_hj.append(sum([change_text(v, 0) for v in data[1:7]]))
                self.lrb_yycb.append(change_text(data[8], 0))
                self.lrb_yycb_hj.append(sum([change_text(v, 0) for v in data[8:20]]))
                self.lrb_yylr.append(change_text(data[32], 0))
                self.lrb_mgyy.append(change_text(data[43], 0))

            del df
            gc.collect()

    # 现金流量表
    def __get_data_xjllb(self):

        self.xjllb_dates = []
        self.xjllb_yyhdxjll = []  # 营业活动现金流量  CSV_LINE:26  DF_INDEX:24
        self.xjllb_tzhdxjll = []  # 投资活动现金流量  CSV_LINE:41  DF_INDEX:39
        self.xjllb_czhdxjll = []  # 筹资活动现金流量  CSV_LINE:53  DF_INDEX:51
        self.xjllb_xjgl = []  # 现金股利  CSV_LINE:49  DF_INDEX:47
        self.xjllb_zbzc = []  # 资本支出  CSV_LINE:34  DF_INDEX:32
        self.xjllb_chjse = []  # 存货减少额  CSV_LINE:76  DF_INDEX:74

        response = requests.get(self.__url_xjllb)
        if response.status_code == 200:
            df = pd.read_csv(self.__url_xjllb, encoding=self.encoding)
            self.xjllb_dates = [ymd for ymd in df.columns.to_list()[1:] if ymd.strip() != '' and ymd[:4].isdigit()]
            for date in self.xjllb_dates:
                data = df[date]
                self.xjllb_yyhdxjll.append(change_text(data[24], 0))
                self.xjllb_tzhdxjll.append(change_text(data[39], 0))
                self.xjllb_czhdxjll.append(change_text(data[51], 0))
                self.xjllb_xjgl.append(change_text(data[47], 0))
                self.xjllb_zbzc.append(change_text(data[32], 0))
                self.xjllb_chjse.append(change_text(data[74], 0))

            del df
            gc.collect()

    # @staticmethod
    def get_stocks(type):
        urls = {
            'SZ50': URL_INDEX_SZ50,
            'HS300': URL_INDEX_HS300,
            'ZZ500': URL_INDEX_ZZ500,
            'HLZS': URL_INDEX_HLZS,
            'KC50': URL_INDEX_KC50,
        }
        if type not in urls:
            return []
        df = read_net_file(urls[type], file_type='EXCEL')
        codes = [str(code).zfill(6) for code in df['成分券代码Constituent Code'].tolist()]
        return codes

    # SZ50 = get_stocks.__func__('SZ50')
    # HS300 = get_stocks.__func__('HS300')
    # ZZ500 = get_stocks.__func__('ZZ500')
    # HLZS = get_stocks.__func__('HLZS')
    # KC50 = get_stocks.__func__('KC50')
