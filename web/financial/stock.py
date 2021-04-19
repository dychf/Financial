import requests

from flask import Blueprint, request, jsonify, current_app
from utils import query_data, parse_jsonp

stock = Blueprint('stock', __name__, url_prefix='/stock')

@stock.route('/suggest', methods=['GET'])
def suggest():
    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': []}

    keyword = request.args.get('keyword')
    if keyword is None:
        return jsonify(result)

    query_data_sql = """
        SELECT code, name, category, area, sz50, hs300, zz500, hlzs, kc50
        FROM (
            SELECT
                code, zwjc AS name, dy AS area, category_id,
                sz50, hs300, zz500, hlzs, kc50
            FROM stock
            WHERE code LIKE %s OR zwjc LIKE %s OR zwjc_py LIKE %s
        ) AS t1
        INNER JOIN (
            SELECT c1.id AS id, c2.name AS category
            FROM category AS c1 INNER JOIN category AS c2 ON c1.parent_id = c2.id
        ) AS t2
        ON t1.category_id = t2.id
        ORDER BY code
        LIMIT 10
    """
    query_data_params = [keyword + '%'] * 3
    for item in query_data(query_data_sql, query_data_params):
        index = []
        if item['sz50']:
            index.append('上证50')
        if item['hs300']:
            index.append('沪深300')
        if item['zz500']:
            index.append('中证500')
        if item['hlzs']:
            index.append('红利指数')
        if item['kc50']:
            index.append('科创50')
        result['data'].append({
            'code': item['code'],
            'name': item['name'],
            'category': item['category'],
            'area': item['area'],
            'index': index
        })
    return result


@stock.route('/index', methods=['GET'])
def index():
    codes = [
        '000001', '399001', '399006',  # 上证指数、深证成指、创业板指
        '000016', '000300', '000905',  # 上证50、沪深300、中证500
        '000688', '399005', '399008'   # 科创50、中小100、中小300
    ]
    data = [
        {'code': code, 'name': '?', 'value': '?', 'percent': '?', 'updown': '?'}
        for code in codes
    ]

    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': data}

    headers = {
        'Accept': request.headers.get('Accept', current_app.config['HTTP_HEADERS']['Accept']),
        'Host': current_app.config['HTTP_HEADERS']['Host'],
        'User-Agent': request.headers.get('User-Agent', current_app.config['HTTP_HEADERS']['User-Agent'])
    }

    url = current_app.config['URL_INDEX']
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify(result)

    index_data = parse_jsonp(response.text)
    if index_data['data'] is None:
        return jsonify(result)

    for k, v in index_data['data']['diff'].items():
        code = v['f12']
        if code in codes:
            data_index = codes.index(code)
            data[data_index]['name'] = v['f14']
            data[data_index]['value'] = v['f2']
            data[data_index]['percent'] = v['f3']
            data[data_index]['updown'] = v['f4']

    result['data'] = data
    return jsonify(result)


@stock.route('/data', methods=['GET'])
def data():
    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': None}

    code = request.args.get('code')
    if code is None:
        return jsonify(result)

    query_data_sql = 'SELECT * FROM financial WHERE code = %s ORDER BY year DESC LIMIT 5'
    data = query_data(query_data_sql, [code])
    if len(data) == 0:
        return jsonify(result)

    data.reverse()
    result['data'] = {}
    for k, v in data[0].items():
        result['data'][k] = []
    for obj in data:
        for k, v in obj.items():
            result['data'][k].append(v)
    del result['data']['code']
    return jsonify(result)
