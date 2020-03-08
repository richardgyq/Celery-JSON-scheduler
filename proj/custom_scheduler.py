import os
import datetime
import json
import math
import logging
import dateutil.parser
import time
import traceback
from celery import schedules as celery_schedules, current_app
from celery.beat import Scheduler, ScheduleEntry

log = logging.getLogger(__name__)

CELERYBEAT_MAX_LOOP_INTERVAL = 5  # seconds
PERIODS = ('days', 'hours', 'minutes', 'seconds', 'microseconds')
TOTAL_RUN_COUNT_KEY = 'total_run_count'
LAST_RUN_AT_KEY = 'last_run_at'
RUN_IMMEDIATELY_KEY = 'run_immediately'


def to_date(date_str):
    result = dateutil.parser.parse(date_str)
    return result


def get_schedules_filepath():
    root_path = os.path.abspath('')
    result = "{}/proj/task_schedules.json".format(root_path)
    return result


def get_schedules_status_filepath():
    root_path = os.path.abspath('')
    result = "{}/proj/task_schedules_status.json".format(root_path)
    return result


def load_schedules_from_file():
    filepath = get_schedules_filepath()
    with open(filepath, "r") as schedules_file:
        result = json.load(schedules_file)
    return result


def save_schedules_to_file(schedules):
    filepath = get_schedules_filepath()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            schedules, f, ensure_ascii=False, indent=4
        )


def load_schedules_status_from_file():
    filepath = get_schedules_status_filepath()
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as status_file:
        result = json.load(status_file)
    return result


def save_schedules_status_to_file(schedules_status):
    filepath = get_schedules_status_filepath()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            schedules_status, f, ensure_ascii=False, indent=4
        )


def convert_to_celery_schedule(task_schedule):
    if 'interval' in task_schedule and 'crontab' in task_schedule:
        raise Exception("Cannot define both interval and crontab schedule")

    if 'interval' in task_schedule:
        interval = task_schedule['interval']
        if interval['period'] in PERIODS:
            result = (
                celery_schedules.schedule(
                    datetime.timedelta(**{interval['period']: interval['every']})
                )
            )
            return result
        else:
            raise Exception(
                "The value of an interval must be {}".format(PERIODS)
            )
    elif 'crontab' in task_schedule:
        crontab = task_schedule['crontab']
        options = {}
        option_keys = (
            'minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year'
        )
        for option_key in option_keys:
            value = crontab.get(option_key, None)
            if value is not None:
                options[option_key] = value
        result = celery_schedules.crontab(**options)
        return result
    else:
        raise Exception(
            "You must define interval or crontab schedule - {}".format(
                task_schedule
            )
        )


def get_task_options(task_schedule):
    option_keys = (
        'queue', 'exchange', 'routing_key', 'expires', 'soft_time_limit'
    )
    options = {}
    for option_key in option_keys:
        if option_key in task_schedule:
            options[option_key] = task_schedule[option_key]
    return options


class CustomScheduleEntry(ScheduleEntry):
    def __init__(self, task, options={}, schedule=None, name=None, app=None):
        if schedule is not None:
            # to support Celery default entries
            converted_task = {
                'name': name,
                'task': task,
                'options': options,
                'schedule': schedule
            }
            self._task = converted_task
        else:
            self._task = task

        self.app = (
            app if app is not None
            else current_app._get_current_object()
        )

        if all(k in self._task for k in ('name', 'task')):
            self.name = self._task['name']
            self.task = self._task['task']
        else:
            raise Exception("'name' and 'task' are required!")

        self.args = self._task.get('args', [])
        self.kwargs = self._task.get('kwargs', {})
        self.options = (
            options if options is not None
            else get_task_options(self._task)
        )
        self.schedule = (
            schedule if schedule is not None
            else convert_to_celery_schedule(self._task)
        )

        if not TOTAL_RUN_COUNT_KEY in self._task:
            status_dict = load_schedules_status_from_file()
            schedule_status = status_dict.get(self.name, {})
            self._task.setdefault(
                TOTAL_RUN_COUNT_KEY,
                schedule_status.get(TOTAL_RUN_COUNT_KEY, 0)
            )

            app_now = self.default_now()
            self._task.setdefault(
                LAST_RUN_AT_KEY,
                schedule_status.get(LAST_RUN_AT_KEY, app_now.isoformat())
            )

        self.total_run_count = self._task[TOTAL_RUN_COUNT_KEY]
        self.last_run_at = to_date(self._task[LAST_RUN_AT_KEY])

    def next(self):
        self._task[LAST_RUN_AT_KEY] = self.default_now().isoformat()
        self._task[TOTAL_RUN_COUNT_KEY] += 1
        self._task[RUN_IMMEDIATELY_KEY] = False
        return self.__class__(self._task)

    __next__ = next

    def is_due(self):
        start_after = self._task.get('start_after', None)
        if start_after is not None:
            now = self.default_now()
            start_time = to_date(start_after)
            if now < start_time:
                delay = math.ceil(
                    (start_time - now).total_seconds()
                )
                return celery_schedules.schedstate(False, delay)
        max_run_count = self._task.get('max_run_count', -1)
        if max_run_count > 0 and self.total_run_count >= max_run_count:
            return celery_schedules.schedstate(False, None)
        run_immediately = self._task.get(RUN_IMMEDIATELY_KEY, False)
        if run_immediately:
            result = self.schedule.is_due(self.last_run_at)
            return celery_schedules.schedstate(True, result.next)
        result = self.schedule.is_due(self.last_run_at)
        return result

    def __repr__(self):
        return (u'<{0} ({1} {2}(*{3}, **{4}) {5})>'.format(
            self.__class__.__name__,
            self.name, self.task, self.args,
            self.kwargs, self.schedule
        ))


class CustomScheduler(Scheduler):
    Entry = CustomScheduleEntry

    def __init__(self, *args, **kwargs):
        self._schedule = {}
        self._schedule_file = get_schedules_filepath()
        self._last_file_timestamp = os.path.getmtime(self._schedule_file)

        Scheduler.__init__(self, *args, **kwargs)
        self.max_interval = (
            kwargs.get('max_interval')
            or self.app.conf.beat_max_loop_interval
            or CELERYBEAT_MAX_LOOP_INTERVAL
        )

    def setup_schedule(self):
        self.sync()
        schedule_settings = load_schedules_from_file()
        self._schedule = {}
        for schedule in schedule_settings:
            if schedule['enabled']:
                self._schedule[schedule['name']] = self.Entry(schedule)
        self.install_default_entries(self._schedule)
        log.info(
            'Current schedule:\n' + '\n'.join(
                repr(entry) for entry in self._schedule.values()
            )
        )

    def requires_update(self):
        ftimestamp = os.path.getmtime(get_schedules_filepath())
        if (ftimestamp > self._last_file_timestamp):
            self._last_file_timestamp = ftimestamp
            return True
        return False

    def get_schedule(self):
        if self.requires_update():
            self.setup_schedule()
        return self._schedule

    def set_schedule(self, schedule):
        self._schedule = schedule
    
    schedule = property(get_schedule, set_schedule)

    @property
    def sync_every(self):
        return self.app.conf.beat_sync_every or 1

    @property
    def info(self):
        return 'JSON schedule file -> {self._schedule_file}'.format(self=self)

    def sync(self):
        if len(self._schedule.values()) == 0:
            return
        status_dict = load_schedules_status_from_file()
        try:
            for entry in self._schedule.values():
                status = {}
                schedule_name = entry.name
                status[TOTAL_RUN_COUNT_KEY] = entry.total_run_count
                status[LAST_RUN_AT_KEY] = entry.last_run_at.isoformat()
                status_dict[schedule_name] = status
            save_schedules_status_to_file(status_dict)
        except Exception:
            log.error(traceback.format_exc())


if __name__ == "__main__":
    test = CustomScheduler(app=current_app)
    pass
