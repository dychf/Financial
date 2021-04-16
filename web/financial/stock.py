from flask import Blueprint, request, jsonify, current_app
from financial.utils import query_data

stock = Blueprint('stock', __name__, url_prefix='/stock')

@stock.route('/suggest', methods=['GET'])
def suggest():
    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': []}
    keyword = request.args.get('keyword')
    if keyword is None:
        return jsonify(result)
    query_data_sql = """
        SELECT code, name, category, area
        FROM (
            SELECT code, zwjc AS name, dy AS area, category_id FROM stock
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
    result['data'] = query_data(query_data_sql, query_data_params)
    return result
