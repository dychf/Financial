# 企业的确定性 1.利润是否为真 2.利润是否可持续 3.维持当前盈利水平是否需要大量资本支出
# 企业的成长性 1.成长的幅度会有多大 2.成长是否需要依赖于大量的再投资

from comet_ml import Experiment
import numpy as np
import time

experiment = Experiment(
    api_key="gH9ClXMtOUFDSwRt0RGupJC2W",
    project_name="value-investing",
    workspace="investment",
)



def stock_price(market, equity):
    """
    计算股票价格, 股票价格=总市值/总股本
    market: 市值
    equity: 总股本
    """
    return round(market/equity,2)

def buysell(equity, netprofit, growthrate, riskfree_rate=4):
    """
    计算买/卖点
    equity: 总股本
    netprofit: 净利润
    growthrate: 增长率
    riskfree_rate: 无风险收益率
    """
    # 估算三年后净利润
    netprofit_after=netprofit*(1+growthrate/100)**3

    # 计算合理估值
    valuation=netprofit_after*(100/riskfree_rate)
    
    # 买点1
    buy=[]
    buy.append(stock_price(valuation*0.5, equity))
    buy.append(stock_price(valuation*0.5*0.9, equity))
    buy.append(stock_price(valuation*0.5*0.8, equity))
    buy.sort()

    # 卖点
    sell=[]
    sell.append(stock_price(valuation*1.5, equity))
    sell.append(stock_price(netprofit*50, equity))
    sell.append(stock_price(netprofit*50*0.9, equity))
    sell.append(stock_price(netprofit*50*0.8, equity))
    sell.sort()
    
    return buy, sell[0:3]
    

if __name__=="__main__":
    # 公司信息
    company='海康威视'# 名称
    code='002415' #股票代码
    equity=94.33 #总股本

    # 上年净利润
    netprofit=168
    # 近三年净利润增长率(%)
    growthrates=[9.52,9.73,28.02]
    params={
        "公司名称": company+"("+code+")",
        "总股本": equity,
        "上年净利润": netprofit,
        "近三年净利润增长率": growthrates
    }
    experiment.log_parameters(params)

    tag='mean'
    if tag=='mean':
        experiment.add_tag("mean")
        growthrate=np.mean(growthrates)
    else:
        experiment.add_tag("min")
        growthrate=np.min(growthrates)
    buy, sell=buysell(equity, netprofit, growthrate)
    experiment.log_parameter("净利润增长率", growthrate)
    experiment.log_parameter("买1", buy[0])
    experiment.log_parameter("买2", buy[1])
    experiment.log_parameter("买3", buy[2])
    experiment.log_parameter("卖1", sell[0])
    experiment.log_parameter("卖2", sell[1])
    experiment.log_parameter("卖3", sell[2])
    
    