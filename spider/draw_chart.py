import sys
import os
import operator
import matplotlib.pyplot as plt

from collections import defaultdict
from financial.utils import query_data
from financial.config import BASE_PATH

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['figure.figsize'] = 7, 3.5

# 查询数据
def fetch_data(column, stocks):
    codes, names = [], []
    for stock in stocks:
        codes.append(stock['code'])
        names.append(stock['name'])

    sql = f"""
        SELECT code, year, {column} FROM financial
        WHERE code IN (%s) AND report = 'Q4'
        ORDER BY year DESC
    """ % (','.join([f"'{code}'" for code in codes]))
    db_data = defaultdict(list)
    for row in query_data(sql):
        index = codes.index(row['code'])
        db_data[names[index]].append(row)

    # 排序 & 最后一年
    last_years = []
    data = {}
    for key, values in db_data.items():
        db_data[key] = sorted(values, key=operator.itemgetter('year'))
        data[key] = []
        last_years.append(db_data[key][-1]['year'])
    last_year = int(max(last_years))

    data['year'] = []
    for year in range(last_year - 4, last_year + 1):
        year = str(year)
        data['year'].append(f'{year}年')

        for name, rows in db_data.items():
            years = [item['year'] for item in rows]
            if year in years:
                data[name].append(rows[years.index(year)][f'{column}'])
            else:
                data[name].append(0)

    if len(names) == 1:
        data['趋势线'] = data[names[0]]
        data_exclude_0 = [value for value in data[names[0]] if value is not None]
        data['平均线'] = [round(sum(data_exclude_0) / len(data_exclude_0), 2)] * len(data['year'])
        del data[names[0]]

    return data

# 折线图
def make_line_chart(title, column='', stocks='', unit='比率（%）', data=None):
    data = fetch_data(column, stocks) if data is None else data

    for key, values in data.items():
        if key == 'year':
            continue
        if key == '平均线':
            plt.plot(data['year'], data[key], label=key)
        else:
            plt.plot(data['year'], data[key], label=key, marker = 'o')

    plt.title(title)
    if unit is not None:
        plt.ylabel(unit)

    plt.legend()
    plt.grid(linestyle='-.')

    plt.savefig(f'./charts/{title}.png')
    plt.close('all')

# 总资产
def zzc(stocks):
    sql = f"""
        SELECT
            year,
            IFNULL(gdqy_zzc_bl, 0) AS gdqy_zzc_bl,
            IFNULL(cqfz_zzc_bl, 0) AS cqfz_zzc_bl,
            IFNULL(ldfz_zzc_bl, 0) AS ldfz_zzc_bl
        FROM financial
        WHERE code = '{stocks[0]["code"]}' AND report = 'Q4'
        ORDER BY year DESC LIMIT 5
    """
    data = query_data(sql)
    data.reverse()

    years = [row['year'] for row in data]
    last_year = int(years[-1])

    labels = []
    gdqy_zzc_bl, cqfz_zzc_bl, ldfz_zzc_bl, top_offset = [], [], [], []
    for i in range(last_year - 4, last_year + 1):
        y = str(i)
        labels.append(f'{y}年')
        if y in years:
            item = data[years.index(y)]
            gdqy_zzc_bl.append(item['gdqy_zzc_bl'])
            cqfz_zzc_bl.append(item['cqfz_zzc_bl'])
            ldfz_zzc_bl.append(item['ldfz_zzc_bl'])
        else:
            gdqy_zzc_bl.append(0)
            cqfz_zzc_bl.append(0)
            ldfz_zzc_bl.append(0)
        top_offset.append(gdqy_zzc_bl[-1] + cqfz_zzc_bl[-1])

    plt.title('财务结构（总资产）')
    width = 0.25
    plt.bar(labels, gdqy_zzc_bl, width, color='#009933', label='股东权益')  
    plt.bar(labels, cqfz_zzc_bl, width, bottom=gdqy_zzc_bl, color='#2882E9', label='长期负债')
    plt.bar(labels, ldfz_zzc_bl, width, bottom=top_offset, color='#DB3439', label='流动负债')
    
    plt.legend(loc='lower left')
    plt.grid(linestyle='-.', axis='y')

    plt.savefig(f'./charts/财务结构（总资产）.png')
    plt.close('all')


def draw(keywords):
    sql_seg = []
    sql_params = []
    for keyword in keywords:
        sql_seg.append('code = %s OR zwjc = %s')
        sql_params += [keyword, keyword]
    sql_seg = ' OR '.join(sql_seg)
    sql = 'SELECT code, zwjc AS name FROM stock WHERE ' + sql_seg + ' ORDER BY code'
    stocks = query_data(sql, sql_params)

    stock_count = len(stocks)

    # 现金流量
    make_line_chart('现金流量比率', 'xjllbl', stocks)
    make_line_chart('现金流量允当比率', 'xjllydbl', stocks)
    make_line_chart('现金再投资比率', 'xjztzbl', stocks)

    # 获利能力
    make_line_chart('股东权益报酬率（ROE）', 'gdqybcl', stocks)
    make_line_chart('总资产报酬率（ROA）', 'zzcbcl', stocks)
    make_line_chart('营业毛利率', 'yymll', stocks)
    make_line_chart('营业利益率', 'yylyl', stocks)
    make_line_chart('净利率', 'jll', stocks)

    # 偿债能力
    make_line_chart('流动比率', 'ldbl', stocks)
    make_line_chart('速动比率', 'sdbl', stocks)

    # 经营能力
    make_line_chart('应收账款周转率（次）', 'yszkzzl', unit='次', stocks=stocks)
    make_line_chart('平均收现日数', 'pjsxrs', unit=None, stocks=stocks)
    make_line_chart('总资产周转率（次）', 'zzczzl', unit='次', stocks=stocks)

    # 财务结构
    make_line_chart('现金与约当现金占总资产比率', 'xjyydxj_zzc_bl', stocks=stocks)
    make_line_chart('流动资产占总资产比率', 'ldzc_zzc_bl', stocks=stocks)
    make_line_chart('应付账款占总资产比率', 'yfzk_zzc_bl', stocks=stocks)
    if stock_count == 1:
        zzc(stocks)
    else:
        make_line_chart('流动负债', 'ldfz_zzc_bl', stocks=stocks)
        make_line_chart('长期负债', 'cqfz_zzc_bl', stocks=stocks)
        make_line_chart('股东权益', 'gdqy_zzc_bl', stocks=stocks)
    
    if stock_count > 1:
        return

    # 分红水平
    data = {'year': [], '趋势线': [], '平均线': []}
    sql = f"SELECT year, fhl FROM dividend WHERE code = '{stocks[0]['code']}' ORDER BY year DESC"
    db_data = query_data(sql)
    db_data.reverse()
    years = [row['year'] for row in db_data]
    last_year = int(years[-1])
    for i, year in enumerate(range(last_year - 4, last_year + 1)):
        year = str(year)
        if years.count(year) > 0:
            for j, row in enumerate(db_data):
                if row['year'] == year:
                    data['year'].append(f"{year}年")
                    data['趋势线'].append(row['fhl'])
        else:
            data['year'].append(f"{year}年")
            data['趋势线'].append(0)
    data['平均线'] = [round(sum(data['趋势线']) / len(data['趋势线']), 2)] * len(data['year'])
    make_line_chart('分红率', data=data)


if __name__ == '__main__':
    target_dir = os.path.join(BASE_PATH, 'charts')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    if len(sys.argv) < 2:
        print('参数错误，示例：')
        print('\tpython show.py 五粮液')
        print('\tpython show.py 五粮液 泸州老窖')
        print('注：理论上支持多个财报的对比，为了美观建议最多3个')
    else:
        keywords = sys.argv[1:]
        draw(keywords)
