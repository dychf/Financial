import random
import requests

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


@category.route('/updown', methods=['GET'])
def updown():
    result = {
        'code': current_app.config['ERROR_CODE_OK'],
        'data': {
            'all': [],
            'top': [],
            'last': []
        }
    }

    headers = {
        'Accept': request.headers.get('Accept', current_app.config['HTTP_HEADERS']['Accept']),
        'Referer': current_app.config['HTTP_HEADERS']['Referer']['163'],
        'User-Agent': random.choice(current_app.config['HTTP_HEADERS']['User-Agent'])
    }

    url = current_app.config['URL_CATEGORY']
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify(result)

    data = response.json()
    if len(data['list']) == 0:
        return jsonify(result)

    type = request.args.get('type')

    if type == 'all':
        for item in data['list']:
            result['data']['all'].append({
                'id': item['PLATE_ID'],
                'name': item['NAME'],
                'up': item['UPNUM'],
                'down': item['DOWNNUM'],
                'percent': f'{round(item["PERCENT"] * 100, 2)}%'
            })
    else:
        for item in data['list'][:3]:
            result['data']['top'].append({
                'id': item['PLATE_ID'],
                'name': item['NAME'],
                'up': item['UPNUM'],
                'down': item['DOWNNUM'],
                'percent': f'{round(item["PERCENT"] * 100, 2)}%'
            })
        
        for item in data['list'][-3:][::-1]:
            result['data']['last'].append({
                'id': item['PLATE_ID'],
                'name': item['NAME'],
                'up': item['UPNUM'],
                'down': item['DOWNNUM'],
                'percent': f'{round(item["PERCENT"] * 100, 2)}%'
            })

    return jsonify(result)


@category.route('/preview', methods=['GET'])
def preview():
    result = {'code': current_app.config['ERROR_CODE_OK'], 'data': []}

    query_data_sql = """
        SELECT L1_name, L2_name, cnt
        FROM (
            SELECT category_id, COUNT(*) AS cnt FROM stock GROUP BY category_id
        ) AS t1
        INNER JOIN (
            SELECT
                c2.name AS L1_name, c2.display AS L1_display,
                c1.name AS L2_name, c1.id AS category_id, c1.display AS L2_display
            FROM category AS c1 INNER JOIN category AS c2
            ON c1.parent_id = c2.id
        ) AS t2
        ON t1.category_id = t2.category_id
        ORDER BY L1_display, L2_display
    """
    data = query_data(query_data_sql)

    for row in data:
        L1_names = [item['name'] for item in result['data']]
        if row['L1_name'] not in L1_names:
            result['data'].append({
                'name': row['L1_name'],
                'children': [{
                    'name': row['L2_name'],
                    'count': row['cnt']
                }],
                'count': row['cnt']
            })
        else:
            L1_index = L1_names.index(row['L1_name'])
            result['data'][L1_index]['children'].append({
                'name': row['L2_name'],
                'count': row['cnt']
            })
            result['data'][L1_index]['count'] += row['cnt']

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
