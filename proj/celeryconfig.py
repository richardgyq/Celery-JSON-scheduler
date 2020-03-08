import os

__broker_host = os.getenv('RABBITMQ_HOST', 'localhost')
__broker_port = os.getenv('RABBITMQ_PORT', '5673')
# __broker_port = os.getenv('RABBITMQ_PORT', '5672')
broker_url = 'amqp://rabbitmquser:rabbitmquser@{}:{}/rabbitmqvhost'.format(
    __broker_host, __broker_port
)

task_serializer = 'json'
task_ignore_result = True
result_serializer = 'json'
accept_content = ['json']
timezone = 'Canada/Pacific'
enable_utc = True
task_queue_max_priority = 10
task_default_priority = 5
worker_prefetch_multiplier = 1
task_acks_late = True
worker_pool_restarts = True
beat_sync_every = 1
