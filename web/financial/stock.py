from flask import Blueprint

stock = Blueprint('stock', __name__, url_prefix='/stock')

@stock.route('/hello', methods=['GET'])
def hello():
    return 'hello stock html'
