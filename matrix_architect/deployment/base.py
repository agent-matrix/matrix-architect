"""Base deployment adapter interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.models import Job, DeploymentConfig


class DeploymentAdapter(ABC):
    """Base class for deployment adapters"""

    @abstractmethod
    def deploy(self, job: Job, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy artifacts from a job

        Args:
            job: The job to deploy
            config: Deployment configuration

        Returns:
            Dict with deployment results
        """
        pass

    @abstractmethod
    def rollback(self, job: Job, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Rollback a deployment

        Args:
            job: The job to rollback
            config: Deployment configuration

        Returns:
            Dict with rollback results
        """
        pass

    @abstractmethod
    def health_check(self, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Check health of deployed service

        Args:
            config: Deployment configuration

        Returns:
            Dict with health status
        """
        pass

    @abstractmethod
    def get_logs(self, config: DeploymentConfig, lines: int = 100) -> str:
        """
        Get logs from deployed service

        Args:
            config: Deployment configuration
            lines: Number of log lines to retrieve

        Returns:
            Log output
        """
        pass
