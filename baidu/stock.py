import json 
import jsonpath
import requests
import numpy as np
from config import cookies, url, headers

class Stock:
    def __init__(self, code):
        self.code = code
        self.__get_data()

    def __get_data(self):
        params = {
        'openapi': '1',
        'dspName': 'iphone',
        'tn': 'tangram',
        'client': 'app',
        'query': self.code,
        'code': self.code,
        'word': self.code,
        'resource_id': '5429',
        'ma_ver': '4',
        'finClientType': 'pc',
        }
        response = requests.get(url, params=params, cookies=cookies, headers=headers).text
        jsonobj = json.loads(response)
        # 名称
        name = jsonpath.jsonpath(
            jsonobj, '$.Result[1].DisplayData.resultData.tplData.result.name')
        # 当前价格
        currentPrice = jsonpath.jsonpath(
            jsonobj, '$.Result[1].DisplayData.resultData.tplData.result.minute_data.pankouinfos.origin_pankou.currentPrice')
        # 总股本
        totalShareCapital = jsonpath.jsonpath(
            jsonobj, '$..Result[1].DisplayData.resultData.tplData.result.minute_data.pankouinfos.origin_pankou.totalShareCapital')
        # 当前市值
        capitalization = jsonpath.jsonpath(
            jsonobj, '$..Result[1].DisplayData.resultData.tplData.result.minute_data.pankouinfos.origin_pankou.capitalization')
        # 年报数据
        FY = jsonpath.jsonpath(
            jsonobj, '$.Result[3].DisplayData.resultData.tplData.result.tabs[4].content.profitSheetV2.chartInfo[4].body')
        FY = np.asarray(FY)

        self.name = name[0] # 名称
        self.currentPrice = float(currentPrice[0]) # 当前价格
        self.totalShareCapital = round(float(totalShareCapital[0])/1e8, 2) # 总股本
        self.capitalization = round(float(capitalization[0])/1e8, 2) # 当前市值
        self.netprofits = FY[0, -3:, 7] # 近三年归母净利润
        self.growthrates = FY[0, -3:, 8]  # 近三年归母净利润增长率
