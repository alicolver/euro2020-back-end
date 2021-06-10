from flask import Flask
from flask_cors import CORS
from blueprints.authentication import authentication
from blueprints.predictions import predictions
from blueprints.score import scores
from blueprints.leaderboard import leaderboard
from blueprints.matches import matches

app = Flask(__name__)

app.register_blueprint(authentication)
app.register_blueprint(predictions)
app.register_blueprint(scores)
app.register_blueprint(leaderboard)
app.register_blueprint(matches)

CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return '<h1>Euro 2020 (It\'s coming hame)</h1>\n<h2>p.s you shouldn\'t be here, if you\'ve seen this message email me@alicolver.com :) thanks</h2>'


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
