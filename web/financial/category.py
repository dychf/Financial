from flask import Blueprint, request, jsonify, current_app
from utils import query_data

category = Blueprint('category', __name__, url_prefix='/category')

@category.route('/query', methods=['GET'])
def query():
    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': []}
    parent_id = request.args.get('pid')
    if parent_id is None:
        query_data_sql = 'SELECT id, name FROM category WHERE parent_id IS NULL ORDER BY display'
        query_data_params = []
    else:
        query_data_sql = 'SELECT id, name FROM category WHERE parent_id = %s ORDER BY display'
        query_data_params = [parent_id]
    result['data'] = query_data(query_data_sql, query_data_params)
    return jsonify(result)


@category.route('/stocks', methods=['GET'])
def stocks():
    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': []}

    category_id = request.args.get('cid')
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    offset = 0 if offset is None else offset
    limit = 10 if limit is None else limit

    if category_id is None:
        return jsonify(result)

    query_data_sql = f"""
        SELECT code, zwjc AS name, p_name AS category, dy AS area
        FROM stock AS t1
        INNER JOIN (
            SELECT c1.id AS id, c1.name AS name, c2.id AS pid, c2.name AS p_name
            FROM category AS c1 INNER JOIN category AS c2 ON c1.parent_id = c2.id
        ) AS t2
        ON t1.category_id = t2.id
        WHERE t2.id = %s OR t2.pid = %s
        ORDER BY code
        LIMIT {limit} OFFSET {offset}
    """
    query_data_params = [category_id, category_id]
    result['data'] = query_data(query_data_sql, query_data_params)

    return jsonify(result)
