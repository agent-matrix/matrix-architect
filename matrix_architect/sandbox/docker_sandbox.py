"""Docker-based sandbox for isolated code execution"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import docker
from docker.models.containers import Container
from docker.errors import DockerException, NotFound

logger = logging.getLogger(__name__)


class DockerSandbox:
    """Manages Docker-based sandboxed execution environments"""

    def __init__(
        self,
        image: str = "python:3.11-slim",
        network_mode: str = "none",
        mem_limit: str = "512m",
        cpu_quota: int = 50000,  # 50% of one CPU
        timeout: int = 300,
    ):
        """
        Initialize Docker sandbox

        Args:
            image: Docker image to use
            network_mode: Network isolation mode ("none", "bridge", etc.)
            mem_limit: Memory limit
            cpu_quota: CPU quota (100000 = 1 CPU)
            timeout: Execution timeout in seconds
        """
        self.image = image
        self.network_mode = network_mode
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.timeout = timeout
        self.client = docker.from_env()

    def execute_command(
        self,
        command: List[str],
        working_dir: str = "/workspace",
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a command in an isolated Docker container

        Args:
            command: Command to execute as list
            working_dir: Working directory inside container
            environment: Environment variables
            volumes: Volume mounts (host_path: {"bind": container_path, "mode": "rw"})

        Returns:
            Dict with stdout, stderr, exit_code
        """
        container: Optional[Container] = None

        try:
            logger.info(f"Creating sandbox container with image {self.image}")

            # Ensure network isolation for security
            if self.network_mode == "none":
                network_disabled = True
                network_mode = "none"
            else:
                network_disabled = False
                network_mode = self.network_mode

            # Create container
            container = self.client.containers.create(
                image=self.image,
                command=command,
                working_dir=working_dir,
                environment=environment or {},
                volumes=volumes or {},
                network_disabled=network_disabled,
                network_mode=network_mode,
                mem_limit=self.mem_limit,
                cpu_quota=self.cpu_quota,
                cpu_period=100000,
                detach=True,
                remove=False,  # We'll remove manually
                read_only=True,  # Read-only root filesystem
                tmpfs={"/tmp": "size=100m,mode=1777"},  # Writable tmp
            )

            logger.info(f"Starting container {container.id[:12]}")
            container.start()

            # Wait for completion with timeout
            result = container.wait(timeout=self.timeout)
            exit_code = result.get("StatusCode", -1)

            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")

            logger.info(
                f"Container {container.id[:12]} completed with exit code {exit_code}"
            )

            return {
                "stdout": logs,
                "stderr": "",  # Docker combines stdout/stderr
                "exit_code": exit_code,
                "container_id": container.id,
            }

        except Exception as exc:
            logger.error(f"Sandbox execution failed: {exc}")
            return {
                "stdout": "",
                "stderr": str(exc),
                "exit_code": -1,
                "error": str(exc),
            }

        finally:
            if container:
                try:
                    container.stop(timeout=5)
                    container.remove(force=True)
                    logger.info(f"Cleaned up container {container.id[:12]}")
                except Exception as exc:
                    logger.warning(f"Failed to cleanup container: {exc}")

    def execute_in_repo(
        self,
        repo_path: Path,
        command: List[str],
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a command with a repository mounted as a volume

        Args:
            repo_path: Path to repository on host
            command: Command to execute
            environment: Environment variables

        Returns:
            Dict with execution results
        """
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        # Mount repo as read-only, use tmpfs for modifications
        volumes = {
            str(repo_path.absolute()): {
                "bind": "/workspace",
                "mode": "ro"  # Read-only
            }
        }

        return self.execute_command(
            command=command,
            working_dir="/workspace",
            environment=environment,
            volumes=volumes,
        )

    def build_image(self, dockerfile_path: Path, tag: str) -> bool:
        """
        Build a custom Docker image

        Args:
            dockerfile_path: Path to Dockerfile
            tag: Tag for the built image

        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Building image {tag} from {dockerfile_path}")

            build_path = dockerfile_path.parent
            image, build_logs = self.client.images.build(
                path=str(build_path),
                tag=tag,
                rm=True,
                forcerm=True,
            )

            for log in build_logs:
                if "stream" in log:
                    logger.debug(log["stream"].strip())

            logger.info(f"Successfully built image {tag}")
            return True

        except DockerException as exc:
            logger.error(f"Failed to build image {tag}: {exc}")
            return False

    def pull_image(self, image: str) -> bool:
        """
        Pull a Docker image

        Args:
            image: Image name to pull

        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Pulling image {image}")
            self.client.images.pull(image)
            logger.info(f"Successfully pulled image {image}")
            return True

        except DockerException as exc:
            logger.error(f"Failed to pull image {image}: {exc}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.client.close()
        except Exception as exc:
            logger.warning(f"Failed to close Docker client: {exc}")
