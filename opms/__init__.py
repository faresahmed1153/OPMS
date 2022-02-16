


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os


from flask_admin import Admin
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = b'\x86\x9a\xa5\x8d=\x87t\x15\x02l\xd4\xd6n\xd2\x0f\x07'
app.config['SECRET_KEY'] = 'e2a82c9ef95e5f76f56a8757e5da634c'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'faresahmed91920@gmail.com'
app.config['MAIL_PASSWORD'] = 'bupgarbyqzgmvtlc'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
s = URLSafeTimedSerializer('92e0deafcee26b4519b8d1f55f977987')
app.config['SQLALCHEMY_DATABASE_URI'] = ''
db = SQLAlchemy(app)
db.create_all()
admin = Admin(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from opms import routes