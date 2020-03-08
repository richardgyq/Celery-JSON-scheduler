import logging
from celery.bin import beat
from celery import Celery, signals

from proj.loggingsetup import logging

__log = logging.getLogger(__name__)


task_modules = ['proj.test_tasks']
app = Celery("CeleryTest", include=task_modules)
app.config_from_object('celeryconfig')
# Alternatively, tasks can be automatically discovered.
# By default, a module containing tasks should be named as tasks.py
# app.autodiscover_tasks(['proj'])

def setup_logging(**kwargs):
    app.log.redirect_stdouts_to_logger(__log)

signals.setup_logging.connect(setup_logging)

__log.info("initialization of celery app done")

if __name__ == '__main__':
    # debug Celery worker
    # argv = [
    #     'worker',
    #     '--loglevel=DEBUG',
    #     '-B'
    # ]
    # app.worker_main(argv)

    # debug Celery beat
    beat = beat.beat(app=app)
    options = {
        'scheduler': 'proj.custom_scheduler.CustomScheduler'
    }
    beat.run(**options)
