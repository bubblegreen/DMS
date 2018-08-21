from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import logging


def create_app():
    logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    app = Flask(__name__)
    Bootstrap(app)
    return app


application = create_app()


@application.route('/')
def index():
    return render_template('index.html')


from controller.image import image_view
from controller.container import container_view

application.register_blueprint(image_view)
application.register_blueprint(container_view)

if __name__ == '__main__':
    application.run(port='8080')
