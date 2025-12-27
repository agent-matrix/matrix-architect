"""Docker Compose deployment adapter"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

from .base import DeploymentAdapter
from ..core.models import Job, DeploymentConfig

logger = logging.getLogger(__name__)


class DockerComposeAdapter(DeploymentAdapter):
    """Deploy using Docker Compose"""

    def deploy(self, job: Job, config: DeploymentConfig) -> Dict[str, Any]:
        """Deploy with docker-compose"""
        compose_file = config.config.get("compose_file", "docker-compose.yml")
        project_dir = Path(config.config.get("project_dir", "."))

        logger.info(f"Deploying with docker-compose from {project_dir}")

        try:
            # Run docker-compose up
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "up", "-d", "--build"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"docker-compose failed: {result.stderr}")

            return {
                "status": "success",
                "output": result.stdout,
                "compose_file": compose_file
            }

        except Exception as exc:
            logger.error(f"Docker Compose deployment failed: {exc}")
            raise

    def rollback(self, job: Job, config: DeploymentConfig) -> Dict[str, Any]:
        """Rollback docker-compose deployment"""
        compose_file = config.config.get("compose_file", "docker-compose.yml")
        project_dir = Path(config.config.get("project_dir", "."))

        logger.info("Rolling back docker-compose deployment")

        try:
            # Stop and remove containers
            subprocess.run(
                ["docker-compose", "-f", compose_file, "down"],
                cwd=project_dir,
                check=True
            )

            return {"status": "success", "action": "rollback"}

        except Exception as exc:
            logger.error(f"Rollback failed: {exc}")
            raise

    def health_check(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Check docker-compose services health"""
        compose_file = config.config.get("compose_file", "docker-compose.yml")
        project_dir = Path(config.config.get("project_dir", "."))

        try:
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "ps"],
                cwd=project_dir,
                capture_output=True,
                text=True
            )

            # Simple check: if ps succeeds and has output
            healthy = result.returncode == 0 and "Up" in result.stdout

            return {
                "healthy": healthy,
                "services": result.stdout
            }

        except Exception as exc:
            return {"healthy": False, "error": str(exc)}

    def get_logs(self, config: DeploymentConfig, lines: int = 100) -> str:
        """Get docker-compose logs"""
        compose_file = config.config.get("compose_file", "docker-compose.yml")
        project_dir = Path(config.config.get("project_dir", "."))

        try:
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "logs", "--tail", str(lines)],
                cwd=project_dir,
                capture_output=True,
                text=True
            )

            return result.stdout

        except Exception as exc:
            return f"Error: {exc}"
