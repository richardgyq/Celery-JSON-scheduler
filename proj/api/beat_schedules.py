import os
import logging
from flask import request
from flask_restx import Resource, fields
from proj.restplus import api
from proj.custom_scheduler import (
    load_schedules_from_file,
    save_schedules_to_file,
    load_schedules_status_from_file
)
from proj.task_trigger_service import trigger_task

log = logging.getLogger(__name__)

ns = api.namespace(
    'celery_beat', description='APIs related to Celery Beat schedules'
)

schedules_request_model = api.model('Schedules request data', {
    'payload': fields.Raw(description='Schedules json')
})
task_arguments_model = api.model('Task arguments data', {
    'kwargs': fields.Raw(description='kwargs')
})


@ns.route('/')
class BeatScheduler(Resource):
    def get(self):
        """
        Get Celery Beat schedules.
        """
        try:
            result = load_schedules_from_file()
            return result
        except Exception:
            logging.exception('Failed to get Celery Beat schedules!')
            raise

    @api.expect(schedules_request_model)
    def put(self):
        """
        Update Celery Beat schedules.
        """
        try:
            save_schedules_to_file(request.json['payload'])
            return 'Celery Beat schedules updated.'
        except Exception:
            logging.exception('Failed to update Celery Beat schedules!')
            raise


@ns.route('/status')
class BeatSchedulerStatus(Resource):
    def get(self):
        """
        Get Celery Beat schedules status.
        """
        try:
            result = load_schedules_status_from_file()
            return result
        except Exception:
            logging.exception('Failed to get Celery Beat schedules status!')
            raise


@ns.route('/trigger/<string:task_full_name>')
@api.doc(params={'task_full_name': 'The full name of a task'})
class TaskTrigger(Resource):
    @api.expect(task_arguments_model)
    def post(self, task_full_name):
        """
        Trigger a task.
        """
        try:
            kwargs = request.json['kwargs']
            result = trigger_task(task_full_name, kwargs=kwargs)
            return result
        except Exception:
            logging.exception('Failed to trigger task!')
            raise
