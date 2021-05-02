import sys
import os
import matplotlib.pyplot as plt

from financial.utils import query_data
from financial.config import BASE_PATH

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['figure.figsize'] = 7, 3.5

# 查询数据
def fetch_data(column, stock_code, year=5):
    sql = f"""
        SELECT year, {column} FROM financial
        WHERE code = '{stock_code}' AND report = 'Q4'
        ORDER BY year DESC LIMIT {year}
    """
    db_data = query_data(sql)
    db_data.reverse()
    years = [row['year'] for row in db_data]
    last_year = int(years[-1])
    data = {'year': [], 'data': [], 'avg': []}
    for i in range(last_year - 4, last_year + 1):
        y = str(i)
        data['year'].append(f'{y}年')
        if y in years:
            data['data'].append(db_data[years.index(y)][column])
        else:
            data['data'].append(0)
    data['avg'] = [round(sum(data['data']) / len(years), 2)] * len(years)
    return data

# 折线图
def make_line_chart(title, column='', stock_code='', unit='比率（%）', data=None):
    data = fetch_data(column, stock_code) if data is None else data

    plt.plot(data['year'], data['data'], label='趋势线', marker = 'o')
    plt.plot(data['year'], data['avg'], label='平均线')

    plt.title(title)
    if unit is not None:
        plt.ylabel(unit)

    plt.legend()
    plt.grid(linestyle='-.')

    plt.savefig(f'./charts/{title}.png')
    plt.close('all')

# 总资产
def zzc(stock_code, year=5):
    sql = f"""
        SELECT
            year,
            IFNULL(gdqy_zzc_bl, 0) AS gdqy_zzc_bl,
            IFNULL(cqfz_zzc_bl, 0) AS cqfz_zzc_bl,
            IFNULL(ldfz_zzc_bl, 0) AS ldfz_zzc_bl
        FROM financial
        WHERE code = '{stock_code}' AND report = 'Q4'
        ORDER BY year DESC LIMIT {year}
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


def draw(keyword):
    sql = 'SELECT code FROM stock WHERE code = %s OR zwjc = %s'
    data = query_data(sql, [keyword, keyword], fetchone=True)

    stock_code = data['code']

    # 现金流量
    make_line_chart('现金流量比率', 'xjllbl', stock_code)
    make_line_chart('现金流量允当比率', 'xjllydbl', stock_code)
    make_line_chart('现金再投资比率', 'xjztzbl', stock_code)

    # 获利能力
    make_line_chart('股东权益报酬率（ROE）', 'gdqybcl', stock_code)
    make_line_chart('总资产报酬率（ROA）', 'zzcbcl', stock_code)
    make_line_chart('营业毛利率', 'yymll', stock_code)
    make_line_chart('营业利益率', 'yylyl', stock_code)
    make_line_chart('净利率', 'jll', stock_code)

    # 偿债能力
    make_line_chart('流动比率', 'ldbl', stock_code)
    make_line_chart('速动比率', 'sdbl', stock_code)

    # 经营能力
    make_line_chart('应收账款周转率（次）', 'yszkzzl', unit='次', stock_code=stock_code)
    make_line_chart('平均收现日数', 'pjsxrs', unit=None, stock_code=stock_code)
    make_line_chart('总资产周转率（次）', 'zzczzl', unit='次', stock_code=stock_code)

    # 财务结构
    make_line_chart('现金与约当现金占总资产比率', 'xjyydxj_zzc_bl', stock_code=stock_code)
    make_line_chart('流动资产占总资产比率', 'ldzc_zzc_bl', stock_code=stock_code)
    make_line_chart('应付账款占总资产比率', 'yfzk_zzc_bl', stock_code=stock_code)
    zzc(stock_code)

    # 分红水平
    data = {'year': [], 'data': [], 'avg': []}
    sql = f'SELECT year, fhl FROM dividend WHERE code = {stock_code} ORDER BY year DESC'
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
                    data['data'].append(row['fhl'])
        else:
            data['year'].append(f"{year}年")
            data['data'].append(0)
    data['avg'] = [round(sum(data['data']) / len(data['data']), 2)] * len(data['year'])
    make_line_chart('分红率', data=data)


if __name__ == '__main__':
    target_dir = os.path.join(BASE_PATH, 'charts')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    if len(sys.argv) != 2:
        print('参数错误，示例：python show.py 600031/三一重工')
    else:
        draw(sys.argv[1])
