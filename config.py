import os
from dotenv import load_dotenv

#
load_dotenv()


host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']
secret_key = os.environ['SECRET_KEY']
port = os.environ['MYSQL_PORT']


class Config:
    SECRET_KEY = secret_key
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?connect_timeout=30"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = os.environ['REMEMBER_COOKIE_DURATION']

    # Evitar erro de lost connection
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,    # testa se a conexão ainda está viva
        "pool_recycle": 280       # reinicia conexão a cada 280s
    }
