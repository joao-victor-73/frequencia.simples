import os
from dotenv import load_dotenv

load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']
secret_key = os.environ['SECRET_KEY']


class Config:
    SECRET_KEY = secret_key
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:RQuWPWiVzhgzwiiVbvgzKFcEyEPyCrsJ@maglev.proxy.rlwy.net:54567/railway"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = os.environ['REMEMBER_COOKIE_DURATION']