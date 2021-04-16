from flask import Blueprint, request, jsonify, current_app
from financial.utils import query_data

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
