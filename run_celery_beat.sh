#!/usr/bin/env bash
sleep 20

file="/home/appuser/celerybeat.pid"
if [ -f $file ] ; then
    rm $file
fi
/usr/local/bin/gunicorn --timeout 60 -w 2 -b 0.0.0.0:5000 --access-logfile - --error-logfile - --log-level info proj.flask_app:app &
exec celery -A proj.app.app beat --scheduler proj.custom_scheduler.CustomScheduler --pidfile=$file
