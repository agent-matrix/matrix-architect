"""Celery tasks for job execution"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded

from .celery_app import celery_app
from ..core.models import JobStatus, JobStage
from ..storage.job_store import JobStore
from ..core.executor import JobExecutor
from ..core.verifier import Verifier
from ..core.deployer import Deployer

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks for state changes"""

    def on_success(self, retval, task_id, args, kwargs):
        """Success callback"""
        logger.info(f"Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback"""
        logger.error(f"Task {task_id} failed: {exc}")
        logger.error(f"Traceback: {einfo}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry callback"""
        logger.warning(f"Task {task_id} retrying: {exc}")


@celery_app.task(
    base=CallbackTask,
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def execute_job_task(self, job_id: str) -> Dict[str, Any]:
    """
    Main job execution task - runs the complete pipeline

    Args:
        job_id: ID of the job to execute

    Returns:
        Dict with execution results
    """
    job_store = JobStore()
    executor = JobExecutor()

    try:
        # Load job
        job = job_store.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Update status
        job.status = JobStatus.planning
        job.started_at = datetime.utcnow()
        job.worker_id = self.request.id
        job_store.update(job)

        logger.info(f"Starting execution of job {job_id}")

        # Execute the complete pipeline
        result = executor.execute(job)

        # Update final status
        job.status = JobStatus.succeeded
        job.completed_at = datetime.utcnow()
        job_store.update(job)

        logger.info(f"Job {job_id} completed successfully")

        return {
            "job_id": job_id,
            "status": "succeeded",
            "result": result
        }

    except SoftTimeLimitExceeded:
        logger.error(f"Job {job_id} exceeded time limit")
        job = job_store.get(job_id)
        if job:
            job.status = JobStatus.failed
            job.error = "Execution exceeded time limit"
            job_store.update(job)
        raise

    except Exception as exc:
        logger.error(f"Job {job_id} failed: {exc}")
        logger.error(traceback.format_exc())

        job = job_store.get(job_id)
        if job:
            job.status = JobStatus.failed
            job.error = str(exc)
            job.retry_count += 1
            job_store.update(job)

        # Retry logic
        if job and job.retry_count < 3:
            raise self.retry(exc=exc, countdown=60 * (2 ** job.retry_count))

        raise


@celery_app.task(base=CallbackTask, bind=True)
def verify_step_task(self, job_id: str, step_id: str) -> Dict[str, Any]:
    """
    Verify a specific step

    Args:
        job_id: ID of the job
        step_id: ID of the step to verify

    Returns:
        Dict with verification results
    """
    job_store = JobStore()
    verifier = Verifier()

    try:
        job = job_store.get(job_id)
        if not job or not job.plan:
            raise ValueError(f"Job {job_id} or plan not found")

        # Find the step
        step = next((s for s in job.plan.steps if s.id == step_id), None)
        if not step:
            raise ValueError(f"Step {step_id} not found")

        logger.info(f"Verifying step {step_id} for job {job_id}")

        # Run verification
        evidence = verifier.verify_step(job, step)

        # Update job with evidence
        job.evidence.append(evidence)
        job_store.update(job)

        return {
            "job_id": job_id,
            "step_id": step_id,
            "passed": evidence.passed,
            "evidence": evidence.dict()
        }

    except Exception as exc:
        logger.error(f"Verification failed for step {step_id}: {exc}")
        raise


@celery_app.task(base=CallbackTask, bind=True, max_retries=1)
def deploy_task(self, job_id: str) -> Dict[str, Any]:
    """
    Deploy artifacts from a job

    Args:
        job_id: ID of the job to deploy

    Returns:
        Dict with deployment results
    """
    job_store = JobStore()
    deployer = Deployer()

    try:
        job = job_store.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        if not job.deployment_config:
            raise ValueError(f"Job {job_id} has no deployment configuration")

        logger.info(f"Deploying job {job_id} to {job.deployment_config.environment}")

        # Update status
        job.status = JobStatus.deploying
        job.current_stage = JobStage.DEPLOY
        job_store.update(job)

        # Execute deployment
        result = deployer.deploy(job)

        # Update status
        job.status = JobStatus.succeeded
        job_store.update(job)

        logger.info(f"Deployment of job {job_id} completed successfully")

        return {
            "job_id": job_id,
            "status": "deployed",
            "result": result
        }

    except Exception as exc:
        logger.error(f"Deployment failed for job {job_id}: {exc}")

        job = job_store.get(job_id)
        if job:
            job.status = JobStatus.failed
            job.error = f"Deployment failed: {str(exc)}"
            job_store.update(job)

        raise


@celery_app.task(bind=True)
def cleanup_old_jobs_task(self, days: int = 30) -> Dict[str, Any]:
    """
    Cleanup old completed jobs

    Args:
        days: Number of days to keep jobs

    Returns:
        Dict with cleanup results
    """
    job_store = JobStore()

    try:
        count = job_store.cleanup_old_jobs(days)
        logger.info(f"Cleaned up {count} old jobs")

        return {
            "cleaned_up": count,
            "days": days
        }

    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}")
        raise
