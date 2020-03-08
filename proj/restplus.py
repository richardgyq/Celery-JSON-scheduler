import os

from flask_restx import Api, apidoc

api = Api(
    version='1.0',
    title='Celery Test API',
    description='--- Celery Test API ---',
)
# to make swagger ui static files not under the root.
apidoc.apidoc.static_url_path = '/api/swaggerui'
