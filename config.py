import os
from dotenv import load_dotenv
from flask_mail import Mail, Message

load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']
secret_key = os.environ['SECRET_KEY']


# E-MAIL
mail_server = os.environ['MAIL_SERVER']
mail_port = os.environ['MAIL_PORT']
mail_use_tls = os.environ['MAIL_USE_TLS']
mail_username = os.environ['MAIL_USERNAME']
mail_password = os.environ['MAIL_PASSWORD']
mail_default_sender = os.environ['MAIL_DEFAULT_SENDER']


class Config:
    SECRET_KEY = secret_key
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:RQuWPWiVzhgzwiiVbvgzKFcEyEPyCrsJ@maglev.proxy.rlwy.net:54567/railway"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = os.environ['REMEMBER_COOKIE_DURATION']