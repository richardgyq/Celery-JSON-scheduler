#!/usr/bin/env bash
sleep 20
exec celery -A proj.app.app worker --without-gossip --without-mingle --concurrency=3 -n worker1@%h
