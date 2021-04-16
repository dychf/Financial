from flask import Blueprint

category = Blueprint('category', __name__, url_prefix='/category')

@category.route('/hello', methods=['GET'])
def hello():
    return 'hello category html'
