import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=(int(os.environ.get('SESSION_TIMEOUT') or 60)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'dms.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # MAIL_USERNAME = 'xu.wu@txcro.com'
    # MAIL_PASSWORD = 'Qw!@#123'
    ADMINS = [os.environ.get('ADMIN') or '']
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_folder')
    SQLALCHEMY_POOL_RECYCLE = 500
