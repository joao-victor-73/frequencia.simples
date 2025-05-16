import os
from dotenv import load_dotenv

load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']
secret_key = os.environ['SECRET_KEY']
port = os.environ['MYSQL_PORT']


class Config:
    SECRET_KEY = secret_key
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = os.environ['REMEMBER_COOKIE_DURATION']