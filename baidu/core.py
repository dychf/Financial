
import numpy as np
from stock import Stock
import pandas as pd

# pd.set_option('display.unicode.ambiguous_as_wide', True)
# pd.set_option('display.unicode.east_asian_width', True)
# pd.set_option('display.width', 300)  # 设置打印宽度(**重要**)
# pd.set_option('expand_frame_repr', False)  # 数据超过总宽度后，是否折叠显示


def price(market, equity):
    """
    计算股票价格, 股票价格=总市值/总股本
    market: 市值
    equity: 总股本
    """
    return round(market/equity, 2)


def valuation(code, riskfree_rate):

    PE = 100 / riskfree_rate

    stock = Stock(code)

    netprofit = np.average([float(p)for p in stock.netprofits],
                           weights=[0.2, 0.3, 0.5])
    netprofit = round(netprofit, 2)  # 当前利润

    growthrate = np.average([float(rate) for rate in stock.growthrates],
                            weights=[0.2, 0.3, 0.5])
    growthrate = round(growthrate, 2)  # 当前增长率

    netprofit3 = round(netprofit*(1+growthrate*0.01)**3, 2)  # 估算三年后利润
    valuation = round(netprofit3*PE, 2)  # 估算市值
    ideal_buy = round(valuation/2, 2)  # 理想买点
    ideal_sell = round(min(valuation*1.5, netprofit*50), 2)  # 理想卖点

    columns = ['名称', '总股本', '利润', '增长率', '给定PE', '三年后利润',
               '当前市值', '三年后估值', '理想买入点', '理想卖出点']
    df = pd.DataFrame([[stock.name, stock.totalShareCapital, netprofit, growthrate, round(PE, 2), netprofit3,
                        '{} ({})'.format(stock.capitalization, price(
                            stock.capitalization, stock.totalShareCapital)),
                        '{} ({})'.format(valuation, price(
                            valuation, stock.totalShareCapital)),
                        '{} ({})'.format(ideal_buy, price(
                            ideal_buy, stock.totalShareCapital)),
                        '{} ({})'.format(ideal_sell, price(
                            ideal_sell, stock.totalShareCapital))
                        ]], columns=columns)
    return df
