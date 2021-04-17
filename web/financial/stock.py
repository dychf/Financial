from flask import Blueprint, request, jsonify, current_app
from utils import query_data

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
