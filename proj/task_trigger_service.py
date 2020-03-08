import logging
from celery import current_app

__logger = logging.getLogger(__name__)


def trigger_task(task_name, args=[], kwargs={}):
    __logger.info('Queuing task {}...'.format(task_name))

    signature = current_app.signature(
        task_name, args=args, kwargs=kwargs
    )
    res = signature.delay()

    __logger.info(
        'Task {} (#{}) triggered.'
        .format(task_name, res.task_id)
    )
    return res.task_id
