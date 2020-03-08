import time
import logging
from datetime import datetime
from proj.app import app

__logger = logging.getLogger(__name__)


def log_task_status(task_desc, status):
    __logger.info('Task {}({}) - {} - priority: {} - {}'.format(
        app.current_worker_task.name,
        app.current_worker_task.request.id,
        task_desc,
        app.current_worker_task.request.delivery_info['priority'],
        status
    ))

@app.task
def high_priority_task(task_number):
    log_task_status(task_number, 'started')
    time.sleep(5)
    log_task_status(task_number, 'ended')

@app.task
def default_priority_task(task_number):
    log_task_status(task_number, 'started')
    time.sleep(5)
    log_task_status(task_number, 'ended')

@app.task
def shared_task(consumer):
    log_task_status(consumer, 'started')
    time.sleep(5)
    log_task_status(consumer, 'ended')

@app.task
def gracefully_shutdown_test_task():
    log_task_status(datetime.now().isoformat(), 'started')
    time.sleep(60)
    log_task_status(datetime.now().isoformat(), 'ended')

@app.task
def interval_task():
    log_task_status(datetime.now().isoformat(), 'started')
    time.sleep(5)
    log_task_status(datetime.now().isoformat(), 'ended')

@app.task
def crontab_task():
    log_task_status(datetime.now().isoformat(), 'started')
    time.sleep(60)
    log_task_status(datetime.now().isoformat(), 'ended')
