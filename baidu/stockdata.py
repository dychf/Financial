import requests
import json
import jsonpath
import numpy as np

# code = '600519'
# code = '002304'
code = '000333'
cookies = {
    'PSTM': '1635248519',
    'BIDUPSID': '90EF3BD78F53BC8C96DF84CD3854CA2D',
    '__yjs_duid': '1_cd247776bc887ee300105fb75c8c2a331635258445589',
    'BDUSS': '1oWEtxQkpPR25ySTgtSHRHb0JOR2VXcm12MEk4V3ZBZ2VkOWZSVFI2QTBlWE5pRVFBQUFBJCQAAAAAAAAAAAEAAACRJsY-cGlwacnxu7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADTsS2I07EticS',
    'BDUSS_BFESS': '1oWEtxQkpPR25ySTgtSHRHb0JOR2VXcm12MEk4V3ZBZ2VkOWZSVFI2QTBlWE5pRVFBQUFBJCQAAAAAAAAAAAEAAACRJsY-cGlwacnxu7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADTsS2I07EticS',
    'BDORZ': 'B490B5EBF6F3CD402E515D22BCDA1598',
    'MCITY': '-158%3A',
    'BA_HECTOR': '8h242g8hah002l0g0g1h9pekn15',
    'ZFY': 'uYCFmlJSV5rn3KHYBSLi6naqucpmiTVS5c4ql8gHf3c:C',
    'BAIDUID_V4': '59DEA2219CA3CC71798923390803C00A:FG=1',
    'RT': '"z=1&dm=baidu.com&si=xgb0bofv4d&ss=l41exipa&sl=3&tt=jbz&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=12pi&ul=1jdc&hd=1jej"',
    'BDRCVFR[feWj1Vr5u3D]': 'I67x6TjHwwYf0',
    'delPer': '0',
    'PSINO': '2',
    'BAIDUID_BFESS': '488CA1A354CAFF05B0D67E0E09E83335:FG=1',
    'H_PS_PSSID': '36426_36549_36465_36455_36512_36452_36167_36488_36517_36074_36519_26350_36467_36314',
    'BAIDUID': 'B0C47089A4FF26A4CB78746AB1FD2529:FG=1',
    'Hm_lvt_c8bd3584daa59ca83c2ec1247d343576': '1654438355,1654506317',
    'Hm_lpvt_c8bd3584daa59ca83c2ec1247d343576': '1654506958',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'PSTM=1635248519; BIDUPSID=90EF3BD78F53BC8C96DF84CD3854CA2D; __yjs_duid=1_cd247776bc887ee300105fb75c8c2a331635258445589; BDUSS=1oWEtxQkpPR25ySTgtSHRHb0JOR2VXcm12MEk4V3ZBZ2VkOWZSVFI2QTBlWE5pRVFBQUFBJCQAAAAAAAAAAAEAAACRJsY-cGlwacnxu7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADTsS2I07EticS; BDUSS_BFESS=1oWEtxQkpPR25ySTgtSHRHb0JOR2VXcm12MEk4V3ZBZ2VkOWZSVFI2QTBlWE5pRVFBQUFBJCQAAAAAAAAAAAEAAACRJsY-cGlwacnxu7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADTsS2I07EticS; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; MCITY=-158%3A; BA_HECTOR=8h242g8hah002l0g0g1h9pekn15; ZFY=uYCFmlJSV5rn3KHYBSLi6naqucpmiTVS5c4ql8gHf3c:C; BAIDUID_V4=59DEA2219CA3CC71798923390803C00A:FG=1; RT="z=1&dm=baidu.com&si=xgb0bofv4d&ss=l41exipa&sl=3&tt=jbz&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=12pi&ul=1jdc&hd=1jej"; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; PSINO=2; BAIDUID_BFESS=488CA1A354CAFF05B0D67E0E09E83335:FG=1; H_PS_PSSID=36426_36549_36465_36455_36512_36452_36167_36488_36517_36074_36519_26350_36467_36314; BAIDUID=B0C47089A4FF26A4CB78746AB1FD2529:FG=1; Hm_lvt_c8bd3584daa59ca83c2ec1247d343576=1654438355,1654506317; Hm_lpvt_c8bd3584daa59ca83c2ec1247d343576=1654506958',
}

params = {
    'openapi': '1',
    'dspName': 'iphone',
    'tn': 'tangram',
    'client': 'app',
    'query': code,
    'code': code,
    'word': code,
    'resource_id': '5429',
    'ma_ver': '4',
    'finClientType': 'pc',
}


def price(market, equity):
    """
    计算股票价格, 股票价格=总市值/总股本
    market: 市值
    equity: 总股本
    """
    return round(market/equity, 2)


def buysell(netprofit, growthrate, riskfree_rate=4):
    """
    计算买/卖点
    netprofit: 净利润
    growthrate: 增长率
    riskfree_rate: 无风险收益率
    """
    # 估算三年后净利润
    netprofit3 = netprofit*(1+growthrate/100)**3

    # 计算合理估值
    valuation = netprofit3*(100/riskfree_rate)

    # 理想买点
    ideal_buy = valuation*0.5

    # 卖点
    sell  = min(valuation*1.5, netprofit*50)

    return round(valuation,2), round(ideal_buy,2), round(sell,2)


response = requests.get('https://gushitong.baidu.com/opendata',
                        params=params, cookies=cookies, headers=headers).text
jsonobj = json.loads(response)

name = jsonpath.jsonpath(
    jsonobj, '$.Result[1].DisplayData.resultData.tplData.result.name')
currentPrice = jsonpath.jsonpath(
    jsonobj, '$.Result[1].DisplayData.resultData.tplData.result.minute_data.pankouinfos.origin_pankou.currentPrice')
totalShareCapital = jsonpath.jsonpath(
    jsonobj, '$..Result[1].DisplayData.resultData.tplData.result.minute_data.pankouinfos.origin_pankou.totalShareCapital')
capitalization = jsonpath.jsonpath(
    jsonobj, '$..Result[1].DisplayData.resultData.tplData.result.minute_data.pankouinfos.origin_pankou.capitalization')
FY = jsonpath.jsonpath(
    jsonobj, '$.Result[3].DisplayData.resultData.tplData.result.tabs[4].content.profitSheetV2.chartInfo[4].body')

name = name[0]
currentPrice = float(currentPrice[0])
totalShareCapital = round(float(totalShareCapital[0])/1e8, 2)
capitalization = round(float(capitalization[0])/1e8, 2)

FY = np.asarray(FY)
FY = FY[0, -3:, 7:9]
# FY = FY[0,-3:,17:19]
# print(FY)

netprofit = float(FY[-1, 0])
# 归属于母公司所有者的综合收益
# print(FY[0,-3:,17:19])

# netprofit = np.average(np.sort([float(profit) for profit in FY[:, 0]]), weights=[0.5, 0.3, 0.2])
netprofit = np.average([float(profit) for profit in FY[:, 0]], weights=[0.2, 0.3, 0.5])
netprofit= round(netprofit, 2)

# growthrate = np.average(np.sort([float(rate) for rate in FY[:, 1]]), weights=[0.5, 0.3, 0.2])
growthrate = np.average([float(rate) for rate in FY[:, 1]], weights=[0.2, 0.3, 0.5])
growthrate = round(growthrate, 2)

print('名称', name)
print('总股本', totalShareCapital)
print('上年利润', netprofit)
print('平均增长率', growthrate)
print('当前市值 {}({})'.format(capitalization, price(capitalization, totalShareCapital)))
valuation, buy, sell = buysell(netprofit, growthrate, riskfree_rate=5)
print('3年后估值', valuation)
print('买入 {}({})'.format(buy,price(buy, totalShareCapital)))
print('卖出 {}({})'.format(sell,price(sell, totalShareCapital)))
