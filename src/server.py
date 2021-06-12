from flask import Flask
from flask_cors import CORS
from blueprints.authentication import authentication
from blueprints.predictions import predictions
from blueprints.score import scores
from blueprints.leaderboard import leaderboard
from blueprints.matches import matches
from blueprints.notifications import notifications
import os

app = Flask(__name__)

app.register_blueprint(authentication)
app.register_blueprint(predictions)
app.register_blueprint(scores)
app.register_blueprint(leaderboard)
app.register_blueprint(matches)
app.register_blueprint(notifications)

CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'euros2020predictions@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

@app.route('/')
def index():
    return '<h1>Euro 2020 (It\'s coming hame)</h1>\n<h2>p.s you shouldn\'t be here, if you\'ve seen this message email me@alicolver.com :) thanks</h2>'


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

