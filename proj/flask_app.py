from flask import Flask, Blueprint
from proj.loggingsetup import logging
from proj.restplus import api
from proj.api.beat_schedules import ns as beat_schedules_namespace

log = logging.getLogger(__name__)
app = Flask(__name__)

def initialize_api(blueprint):
    api.init_app(blueprint)
    api.namespaces.clear()
    api.add_namespace(beat_schedules_namespace)


def initialize_app(flask_app):
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    initialize_api(blueprint)
    flask_app.register_blueprint(blueprint)


def run_dev_server():
    host = '0.0.0.0'
    port = 5000
    app.run(host=host, port=port)

initialize_app(app)
log.info('initialization of flask app done.')

if __name__ == "__main__":
    run_dev_server()
