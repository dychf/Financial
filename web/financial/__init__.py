from flask import Flask, jsonify
from financial.category import category
from financial.stock import stock

app = Flask(__name__)
app.config.from_object('config')

app.register_blueprint(category)
app.register_blueprint(stock)

@app.errorhandler(500)
def handle_error(err):
    return jsonify({
        'code': app.config['ERROR_CODE_ERROR'],
        'message': f'{err.original_exception}'
    })
