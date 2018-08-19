from flask import Flask, render_template, blueprints
from configparser import ConfigParser
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler


def create_app():
    # Rthandler = RotatingFileHandler('app.log', maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
    # Rthandler.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(message)s')
    # Rthandler.setFormatter(formatter)
    # logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', handlers=[Rthandler,])
    logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    app = Flask(__name__)
    Bootstrap(app)
    return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


from controller.image import image_view
from controller.container import container_view

app.register_blueprint(image_view)
app.register_blueprint(container_view)

if __name__ == '__main__':
    app.run(port='8080')
