import logging
from proj.app import app

__logger = logging.getLogger(__name__)

HIGH_PRIORITY = 8
USER_PRIORITY = 9


def trigger_task(task_name, task_number, priority=None):
    signature = app.signature(task_name, args=[task_number])
    task_priority = (
        app.conf.task_default_priority if priority is None else priority
    )
    res = signature.apply_async(priority=task_priority)

    __logger.info(
        'Task {}#{} ({}) requested.'
        .format(task_name, task_number, res.task_id)
    )


def trigger_shutdown_test_task():
    task_name = 'proj.test_tasks.gracefully_shutdown_test_task'
    signature = app.signature(task_name)
    res = signature.delay()
    __logger.info(
        'Task {} ({}) requested.'
        .format(task_name, res.task_id)
    )


def trigger_tasks_with_different_priorities():
    for i in range(10):
        trigger_task(
            'proj.test_tasks.shared_task', 'service-{}'.format(i)
        )
    for i in range(10):
        trigger_task(
            'proj.test_tasks.shared_task', 'user-{}'.format(i),
            USER_PRIORITY
        )


def trigger_tasks_without_priorities():
    for i in range(10):
        trigger_task(
            'proj.test_tasks.default_priority_task', i
        )
    for i in range(10):
        trigger_task(
            'proj.test_tasks.high_priority_task', i
        )


def trigger_tasks_with_priority():
    for i in range(10):
        trigger_task(
            'proj.test_tasks.default_priority_task', i
        )
    for i in range(10):
        trigger_task(
            'proj.test_tasks.high_priority_task', i, HIGH_PRIORITY
        )

if __name__ == '__main__':
    # trigger_shutdown_test_task()
    # trigger_tasks_without_priorities()
    # trigger_tasks_with_priority()
    trigger_tasks_with_different_priorities()
