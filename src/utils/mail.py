from flask_mail import Mail, Message

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
    mail.init_app(app)


def sendMissingPredictionEmail(userName, userEmail, teamOneName, teamTwoName):
    msg = Message("Mising Prediction",
                  sender="euros2020predictions@gmail.com", recipients=[userEmail])
    msg.body = missingMessage.format(
        user=userName,
        game="{} vs {}".format(teamOneName, teamTwoName)
    )
    mail.send(msg)


def sendPasswordResetEmail(userName, userEmail, otp):
    msg = Message("Subject", sender="euros2020predictions@gmail.com",
                  recipients=[userEmail])

    msg.html = (passwordResetMessage % (userName, otp))

    mail.send(msg)
