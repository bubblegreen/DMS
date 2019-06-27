import logging, os
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = '请登录.'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    # app.debug = False
    app.config.from_object(Config)
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.endpoint import bp as endpoint_bp
    app.register_blueprint(endpoint_bp, url_prefix='/endpoint')

    from app.group import bp as group_bp
    app.register_blueprint(group_bp, url_prefix='/group')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.image import bp as image_bp
    app.register_blueprint(image_bp, url_prefix='/image')

    from app.container import bp as container_bp
    app.register_blueprint(container_bp, url_prefix='/container')

    # from app.sampleCalculation import bp as sc_bp
    # app.register_blueprint(sc_bp, url_prefix='/sc')

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Aisino Docker Manager Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/mng.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Aisino Docker Manager startup')
    return app


from app import models
