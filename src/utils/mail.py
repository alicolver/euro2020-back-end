from flask_mail import Mail, Message
from utils.environment_variables import EMAIL_PASSWORD, EMAIL_USERNAME, EMAIL_PORT, EMAIL_SERVER

mail = Mail()

missingMessage = """
Hello {user} 

You have forgotten to put a prediction for the {game} euros game.

You stil have 1 hour to submit your prediction by visiting www.alicolver.com/euro2020

Good luck!
"""

passwordResetMessage = """
     <html>
         <head>
         <h1>Your EURO 2020 Password Reset Code</h1>
         </head>
         <body>
         <p>Hi, %s<br>
            Your one time password reset code is %s.<br>
            Please return to https://alicolver.com/euro2020/reset. to reset your password.<br>
            <br>
            <br>

            EURO 2020.
         </body>
     </html>
     """


def registerApp(app):
    app.config['MAIL_USERNAME'] = EMAIL_USERNAME
    app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
    app.config['MAIL_SERVER'] = EMAIL_SERVER
    app.config['MAIL_PORT'] = EMAIL_PORT
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail.init_app(app)


def sendMissingPredictionEmail(userName, userEmail, teamOneName, teamTwoName):
    msg = Message("Mising Prediction",
                  sender=EMAIL_USERNAME, recipients=[userEmail])
    msg.body = missingMessage.format(
        user=userName,
        game="{} vs {}".format(teamOneName, teamTwoName)
    )
    mail.send(msg)


def sendPasswordResetEmail(userName, userEmail, otp):
    msg = Message("Password Reset", sender=EMAIL_USERNAME,
                  recipients=[userEmail])

    msg.html = (passwordResetMessage % (userName, otp))

    mail.send(msg)
