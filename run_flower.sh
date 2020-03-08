#!/usr/bin/env bash
sleep 25
exec celery -A proj.app.app flower --basic_auth=rguo:rguo
# http://localhost:5555
