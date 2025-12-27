"""Celery application configuration for distributed job processing"""

import os
from celery import Celery
from kombu import Exchange, Queue

# Redis connection URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "matrix_architect",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["matrix_architect.queue.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minute soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # 24 hours
    task_default_queue="architect_default",
    task_default_exchange="architect",
    task_default_exchange_type="topic",
    task_default_routing_key="architect.default",
    task_queues=(
        Queue(
            "architect_default",
            Exchange("architect", type="topic"),
            routing_key="architect.default"
        ),
        Queue(
            "architect_high_priority",
            Exchange("architect", type="topic"),
            routing_key="architect.high_priority",
            priority=10
        ),
        Queue(
            "architect_low_priority",
            Exchange("architect", type="topic"),
            routing_key="architect.low_priority",
            priority=1
        ),
    ),
    task_routes={
        "matrix_architect.queue.tasks.execute_job_task": {
            "queue": "architect_default",
            "routing_key": "architect.default"
        },
        "matrix_architect.queue.tasks.verify_step_task": {
            "queue": "architect_default",
            "routing_key": "architect.default"
        },
        "matrix_architect.queue.tasks.deploy_task": {
            "queue": "architect_high_priority",
            "routing_key": "architect.high_priority"
        },
    }
)

# Autodiscover tasks
celery_app.autodiscover_tasks(["matrix_architect.queue"])
