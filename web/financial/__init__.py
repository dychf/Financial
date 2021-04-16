from flask import Flask
from financial.category import category
from financial.stock import stock

app = Flask(__name__)
app.config.from_object('config')

app.register_blueprint(category)
app.register_blueprint(stock)
