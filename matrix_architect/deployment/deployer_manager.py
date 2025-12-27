"""Deployment manager to coordinate different adapters"""

import logging
from typing import Dict, Any

from .base import DeploymentAdapter
from .kubernetes_adapter import KubernetesAdapter
from .docker_compose_adapter import DockerComposeAdapter
from .serverless_adapter import ServerlessAdapter
from ..core.models import Job, DeploymentConfig, DeploymentTarget

logger = logging.getLogger(__name__)


class DeployerManager:
    """Manages deployment across different targets"""

    def __init__(self):
        self.adapters: Dict[DeploymentTarget, DeploymentAdapter] = {
            DeploymentTarget.kubernetes: KubernetesAdapter(),
            DeploymentTarget.docker_compose: DockerComposeAdapter(),
            DeploymentTarget.serverless: ServerlessAdapter(),
        }

    def deploy(self, job: Job) -> Dict[str, Any]:
        """
        Deploy a job using the appropriate adapter

        Args:
            job: Job to deploy

        Returns:
            Deployment results
        """
        if not job.deployment_config:
            raise ValueError("Job has no deployment configuration")

        config = job.deployment_config
        adapter = self.adapters.get(config.target)

        if not adapter:
            raise ValueError(f"No adapter for deployment target: {config.target}")

        logger.info(f"Deploying job {job.id} to {config.target.value}")

        result = adapter.deploy(job, config)

        logger.info(f"Deployment of job {job.id} completed")

        return result

    def rollback(self, job: Job) -> Dict[str, Any]:
        """Rollback a deployment"""
        if not job.deployment_config:
            raise ValueError("Job has no deployment configuration")

        config = job.deployment_config
        adapter = self.adapters.get(config.target)

        if not adapter:
            raise ValueError(f"No adapter for deployment target: {config.target}")

        logger.info(f"Rolling back job {job.id}")

        result = adapter.rollback(job, config)

        return result

    def health_check(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Check deployment health"""
        adapter = self.adapters.get(config.target)

        if not adapter:
            raise ValueError(f"No adapter for deployment target: {config.target}")

        return adapter.health_check(config)

    def get_logs(self, config: DeploymentConfig, lines: int = 100) -> str:
        """Get deployment logs"""
        adapter = self.adapters.get(config.target)

        if not adapter:
            raise ValueError(f"No adapter for deployment target: {config.target}")

        return adapter.get_logs(config, lines)
