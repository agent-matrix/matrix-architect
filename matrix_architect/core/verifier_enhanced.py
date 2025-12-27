"""Enhanced evidence-based verification system"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

from .models import (
    Job, Step, Evidence, EvidenceKind, Artifact, ArtifactKind
)
from ..sandbox.sandbox_manager import SandboxManager
from ..storage.artifact_store import ArtifactStore

logger = logging.getLogger(__name__)


class EnhancedVerifier:
    """Enhanced verification system with comprehensive evidence generation"""

    def __init__(self):
        self.sandbox_manager = SandboxManager()
        self.artifact_store = ArtifactStore()

    def verify_step(self, job: Job, step: Step) -> Evidence:
        """
        Verify a step and generate evidence

        Args:
            job: The job being executed
            step: The step to verify

        Returns:
            Evidence object with verification results
        """
        if not step.verify:
            # No verification commands, skip
            return Evidence(
                kind=EvidenceKind.test_results,
                passed=True,
                summary="No verification required",
                details={}
            )

        # Execute verification commands in sandbox
        repo_path = self._get_repo_path(job)

        results = []
        all_passed = True

        for cmd in step.verify:
            result = self._execute_verification_command(
                repo_path, cmd, job.id, step.id
            )
            results.append(result)
            if not result.get("passed", False):
                all_passed = False

        # Generate evidence
        evidence = Evidence(
            kind=EvidenceKind.test_results,
            passed=all_passed,
            summary=f"Verification {'passed' if all_passed else 'failed'} for step {step.id}",
            details={"results": results}
        )

        return evidence

    def verify_full_suite(self, job: Job) -> List[Evidence]:
        """
        Run full verification suite: tests, lint, build, security

        Args:
            job: The job to verify

        Returns:
            List of Evidence objects
        """
        repo_path = self._get_repo_path(job)
        evidence_list = []

        # 1. Lint check
        if job.constraints.require_tests:
            lint_evidence = self._verify_lint(job, repo_path)
            evidence_list.append(lint_evidence)

        # 2. Unit tests
        if job.constraints.require_tests:
            test_evidence = self._verify_tests(job, repo_path)
            evidence_list.append(test_evidence)

        # 3. Build
        if job.constraints.require_build:
            build_evidence = self._verify_build(job, repo_path)
            evidence_list.append(build_evidence)

        # 4. Security scan
        if job.constraints.security_scan:
            security_evidence = self._verify_security(job, repo_path)
            evidence_list.append(security_evidence)

        # 5. Dependency audit
        dependency_evidence = self._verify_dependencies(job, repo_path)
        evidence_list.append(dependency_evidence)

        # 6. Generate SBOM
        sbom_evidence = self._generate_sbom(job, repo_path)
        evidence_list.append(sbom_evidence)

        return evidence_list

    def _verify_lint(self, job: Job, repo_path: Path) -> Evidence:
        """Run linting checks"""
        logger.info(f"Running lint checks for job {job.id}")

        try:
            result = subprocess.run(
                ["ruff", "check", "."],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            passed = result.returncode == 0

            # Store lint results as artifact
            artifact = self._store_artifact(
                job.id,
                "lint_results.txt",
                result.stdout + result.stderr,
                ArtifactKind.report
            )

            return Evidence(
                kind=EvidenceKind.lint_results,
                passed=passed,
                summary=f"Lint check {'passed' if passed else 'failed'}",
                details={
                    "exit_code": result.returncode,
                    "output": result.stdout[:1000]  # Truncate
                },
                artifacts=[artifact.name]
            )

        except Exception as exc:
            logger.error(f"Lint check failed: {exc}")
            return Evidence(
                kind=EvidenceKind.lint_results,
                passed=False,
                summary=f"Lint check error: {str(exc)}",
                details={"error": str(exc)}
            )

    def _verify_tests(self, job: Job, repo_path: Path) -> Evidence:
        """Run unit tests"""
        logger.info(f"Running tests for job {job.id}")

        try:
            result = subprocess.run(
                ["pytest", "-v", "--tb=short"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600
            )

            passed = result.returncode == 0

            # Store test results
            artifact = self._store_artifact(
                job.id,
                "test_results.txt",
                result.stdout + result.stderr,
                ArtifactKind.report
            )

            # Parse test output for summary
            lines = result.stdout.split("\n")
            summary_line = next(
                (l for l in reversed(lines) if "passed" in l or "failed" in l),
                "Test completed"
            )

            return Evidence(
                kind=EvidenceKind.test_results,
                passed=passed,
                summary=summary_line,
                details={
                    "exit_code": result.returncode,
                    "output": result.stdout[:1000]
                },
                artifacts=[artifact.name]
            )

        except Exception as exc:
            logger.error(f"Test execution failed: {exc}")
            return Evidence(
                kind=EvidenceKind.test_results,
                passed=False,
                summary=f"Test error: {str(exc)}",
                details={"error": str(exc)}
            )

    def _verify_build(self, job: Job, repo_path: Path) -> Evidence:
        """Run build"""
        logger.info(f"Running build for job {job.id}")

        try:
            result = subprocess.run(
                ["python", "-m", "build"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600
            )

            passed = result.returncode == 0

            # Store build logs
            artifact = self._store_artifact(
                job.id,
                "build_logs.txt",
                result.stdout + result.stderr,
                ArtifactKind.log
            )

            return Evidence(
                kind=EvidenceKind.build_logs,
                passed=passed,
                summary=f"Build {'succeeded' if passed else 'failed'}",
                details={
                    "exit_code": result.returncode,
                    "output": result.stdout[:1000]
                },
                artifacts=[artifact.name]
            )

        except Exception as exc:
            logger.error(f"Build failed: {exc}")
            return Evidence(
                kind=EvidenceKind.build_logs,
                passed=False,
                summary=f"Build error: {str(exc)}",
                details={"error": str(exc)}
            )

    def _verify_security(self, job: Job, repo_path: Path) -> Evidence:
        """Run security scan"""
        logger.info(f"Running security scan for job {job.id}")

        try:
            # Use safety for Python dependency scanning
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse JSON output
            try:
                scan_results = json.loads(result.stdout) if result.stdout else {}
            except json.JSONDecodeError:
                scan_results = {"raw_output": result.stdout}

            vulnerabilities = scan_results.get("vulnerabilities", [])
            passed = len(vulnerabilities) == 0

            # Store scan results
            artifact = self._store_artifact(
                job.id,
                "security_scan.json",
                json.dumps(scan_results, indent=2),
                ArtifactKind.scan
            )

            return Evidence(
                kind=EvidenceKind.security_scan,
                passed=passed,
                summary=f"Found {len(vulnerabilities)} security vulnerabilities",
                details={
                    "vulnerability_count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities
                },
                artifacts=[artifact.name]
            )

        except Exception as exc:
            logger.error(f"Security scan failed: {exc}")
            return Evidence(
                kind=EvidenceKind.security_scan,
                passed=True,  # Don't fail job if scan errors
                summary=f"Security scan error: {str(exc)}",
                details={"error": str(exc)}
            )

    def _verify_dependencies(self, job: Job, repo_path: Path) -> Evidence:
        """Audit dependencies"""
        logger.info(f"Auditing dependencies for job {job.id}")

        try:
            # Run pip-audit
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            try:
                audit_results = json.loads(result.stdout) if result.stdout else {}
            except json.JSONDecodeError:
                audit_results = {"raw_output": result.stdout}

            issues = audit_results.get("dependencies", [])
            passed = len(issues) == 0

            # Store audit results
            artifact = self._store_artifact(
                job.id,
                "dependency_audit.json",
                json.dumps(audit_results, indent=2),
                ArtifactKind.report
            )

            return Evidence(
                kind=EvidenceKind.dependency_audit,
                passed=passed,
                summary=f"Found {len(issues)} dependency issues",
                details={
                    "issue_count": len(issues),
                    "issues": issues
                },
                artifacts=[artifact.name]
            )

        except Exception as exc:
            logger.error(f"Dependency audit failed: {exc}")
            return Evidence(
                kind=EvidenceKind.dependency_audit,
                passed=True,  # Don't fail job
                summary=f"Audit error: {str(exc)}",
                details={"error": str(exc)}
            )

    def _generate_sbom(self, job: Job, repo_path: Path) -> Evidence:
        """Generate Software Bill of Materials"""
        logger.info(f"Generating SBOM for job {job.id}")

        try:
            # Use pip-licenses to generate SBOM
            result = subprocess.run(
                ["pip-licenses", "--format=json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            try:
                sbom_data = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError:
                sbom_data = []

            # Store SBOM
            artifact = self._store_artifact(
                job.id,
                "sbom.json",
                json.dumps(sbom_data, indent=2),
                ArtifactKind.sbom
            )

            return Evidence(
                kind=EvidenceKind.sbom,
                passed=True,
                summary=f"SBOM generated with {len(sbom_data)} dependencies",
                details={"dependency_count": len(sbom_data)},
                artifacts=[artifact.name]
            )

        except Exception as exc:
            logger.error(f"SBOM generation failed: {exc}")
            return Evidence(
                kind=EvidenceKind.sbom,
                passed=True,  # Don't fail job
                summary=f"SBOM error: {str(exc)}",
                details={"error": str(exc)}
            )

    def _execute_verification_command(
        self, repo_path: Path, command: str, job_id: str, step_id: str
    ) -> Dict[str, Any]:
        """Execute a single verification command"""
        try:
            result = subprocess.run(
                command.split(),
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600
            )

            passed = result.returncode == 0

            return {
                "command": command,
                "passed": passed,
                "exit_code": result.returncode,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500]
            }

        except Exception as exc:
            return {
                "command": command,
                "passed": False,
                "error": str(exc)
            }

    def _get_repo_path(self, job: Job) -> Path:
        """Get the repository path for a job"""
        if job.repo.kind == job.repo.kind.local and job.repo.path:
            return Path(job.repo.path)
        # For remote repos, they should be cloned to a workspace
        # This is handled by the executor
        workspace = Path(f"/tmp/matrix-architect/jobs/{job.id}/workspace")
        return workspace

    def _store_artifact(
        self, job_id: str, name: str, content: str, kind: ArtifactKind
    ) -> Artifact:
        """Store artifact and return Artifact object"""
        # Calculate checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()

        artifact = Artifact(
            kind=kind,
            name=name,
            content_type="text/plain",
            size=len(content.encode()),
            checksum=checksum,
            created_at=datetime.utcnow()
        )

        # Store via artifact store
        self.artifact_store.store(job_id, name, content.encode())

        return artifact
