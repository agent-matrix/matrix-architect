"""Sandbox manager for coordinating multiple sandboxed executions"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .docker_sandbox import DockerSandbox

logger = logging.getLogger(__name__)


class SandboxManager:
    """Manages multiple sandboxed execution environments"""

    def __init__(self, max_concurrent: int = 4):
        """
        Initialize sandbox manager

        Args:
            max_concurrent: Maximum concurrent sandboxes
        """
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    def execute_commands(
        self,
        commands: List[Dict[str, Any]],
        repo_path: Path,
        environment: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple commands in parallel sandboxes

        Args:
            commands: List of command dicts with "cmd" and optional "image"
            repo_path: Path to repository
            environment: Shared environment variables

        Returns:
            List of results for each command
        """
        futures = []
        results = []

        for cmd_config in commands:
            sandbox = DockerSandbox(
                image=cmd_config.get("image", "python:3.11-slim")
            )

            future = self.executor.submit(
                sandbox.execute_in_repo,
                repo_path=repo_path,
                command=cmd_config["cmd"],
                environment=environment,
            )
            futures.append((future, cmd_config))

        # Collect results
        for future, cmd_config in futures:
            try:
                result = future.result(timeout=600)
                result["command"] = cmd_config["cmd"]
                results.append(result)
            except Exception as exc:
                logger.error(f"Command failed: {cmd_config['cmd']} - {exc}")
                results.append({
                    "command": cmd_config["cmd"],
                    "stdout": "",
                    "stderr": str(exc),
                    "exit_code": -1,
                    "error": str(exc),
                })

        return results

    def execute_verification_suite(
        self,
        repo_path: Path,
        tests: bool = True,
        lint: bool = True,
        build: bool = True,
        security_scan: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a complete verification suite

        Args:
            repo_path: Path to repository
            tests: Run tests
            lint: Run linter
            build: Run build
            security_scan: Run security scan

        Returns:
            Dict with all verification results
        """
        commands = []

        if lint:
            commands.append({
                "name": "lint",
                "cmd": ["sh", "-c", "pip install ruff && ruff check ."],
                "image": "python:3.11-slim",
            })

        if tests:
            commands.append({
                "name": "test",
                "cmd": ["sh", "-c", "pip install pytest && pytest -v"],
                "image": "python:3.11-slim",
            })

        if build:
            commands.append({
                "name": "build",
                "cmd": ["sh", "-c", "pip install build && python -m build"],
                "image": "python:3.11-slim",
            })

        if security_scan:
            commands.append({
                "name": "security",
                "cmd": ["sh", "-c", "pip install safety && safety check"],
                "image": "python:3.11-slim",
            })

        results = self.execute_commands(commands, repo_path)

        # Organize results
        verification_results = {
            "passed": all(r["exit_code"] == 0 for r in results),
            "results": {}
        }

        for i, cmd in enumerate(commands):
            verification_results["results"][cmd["name"]] = results[i]

        return verification_results

    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
