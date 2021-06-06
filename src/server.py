from flask import Flask
from flask_cors import CORS
from blueprints.authentication import authentication

app = Flask(__name__)

app.register_blueprint(authentication)
app.register_blueprint(user_information)

CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return '<h1>Euro 2020 (It\'s coming hame)</h1>\n<h2>p.s you shouldn\'t be here, if you\'ve seen this message email me@alicolver.com :) thanks</h2>'


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')