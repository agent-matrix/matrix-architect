"""Kubernetes deployment adapter"""

import logging
from typing import Dict, Any
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException

from .base import DeploymentAdapter
from ..core.models import Job, DeploymentConfig

logger = logging.getLogger(__name__)


class KubernetesAdapter(DeploymentAdapter):
    """Deploy to Kubernetes clusters"""

    def __init__(self):
        """Initialize Kubernetes client"""
        try:
            # Try in-cluster config first
            k8s_config.load_incluster_config()
        except k8s_config.ConfigException:
            # Fall back to kubeconfig
            k8s_config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()

    def deploy(self, job: Job, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy to Kubernetes

        Args:
            job: The job to deploy
            config: Kubernetes deployment configuration

        Returns:
            Deployment results
        """
        namespace = config.namespace or "default"
        deployment_name = config.config.get("deployment_name", f"job-{job.id}")
        image = config.config.get("image")
        replicas = config.config.get("replicas", 1)

        if not image:
            raise ValueError("Kubernetes deployment requires 'image' in config")

        logger.info(f"Deploying {deployment_name} to namespace {namespace}")

        try:
            # Create deployment manifest
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(
                    name=deployment_name,
                    namespace=namespace,
                    labels={
                        "app": deployment_name,
                        "matrix-job-id": job.id,
                        "environment": config.environment
                    }
                ),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels={"app": deployment_name}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": deployment_name}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=deployment_name,
                                    image=image,
                                    ports=[client.V1ContainerPort(container_port=8080)],
                                    env=[
                                        client.V1EnvVar(name=k, value=v)
                                        for k, v in config.config.get("env", {}).items()
                                    ]
                                )
                            ]
                        )
                    )
                )
            )

            # Try to update existing deployment, or create new
            try:
                self.apps_v1.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace,
                    body=deployment
                )
                action = "updated"
            except ApiException as e:
                if e.status == 404:
                    self.apps_v1.create_namespaced_deployment(
                        namespace=namespace,
                        body=deployment
                    )
                    action = "created"
                else:
                    raise

            logger.info(f"Deployment {deployment_name} {action} successfully")

            return {
                "status": "success",
                "action": action,
                "deployment": deployment_name,
                "namespace": namespace,
                "replicas": replicas
            }

        except ApiException as exc:
            logger.error(f"Kubernetes API error: {exc}")
            raise

    def rollback(self, job: Job, config: DeploymentConfig) -> Dict[str, Any]:
        """Rollback Kubernetes deployment"""
        namespace = config.namespace or "default"
        deployment_name = config.config.get("deployment_name", f"job-{job.id}")

        logger.info(f"Rolling back deployment {deployment_name}")

        try:
            # Get deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )

            # Trigger rollback by updating annotation
            if not deployment.spec.template.metadata.annotations:
                deployment.spec.template.metadata.annotations = {}

            deployment.spec.template.metadata.annotations["matrix.rollback"] = "true"

            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )

            return {
                "status": "success",
                "deployment": deployment_name,
                "namespace": namespace
            }

        except ApiException as exc:
            logger.error(f"Rollback failed: {exc}")
            raise

    def health_check(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Check health of Kubernetes deployment"""
        namespace = config.namespace or "default"
        deployment_name = config.config.get("deployment_name")

        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )

            ready_replicas = deployment.status.ready_replicas or 0
            desired_replicas = deployment.spec.replicas or 0

            healthy = ready_replicas == desired_replicas

            return {
                "healthy": healthy,
                "ready_replicas": ready_replicas,
                "desired_replicas": desired_replicas,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason
                    }
                    for c in (deployment.status.conditions or [])
                ]
            }

        except ApiException as exc:
            logger.error(f"Health check failed: {exc}")
            return {
                "healthy": False,
                "error": str(exc)
            }

    def get_logs(self, config: DeploymentConfig, lines: int = 100) -> str:
        """Get logs from Kubernetes pods"""
        namespace = config.namespace or "default"
        deployment_name = config.config.get("deployment_name")

        try:
            # Get pods for deployment
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment_name}"
            )

            if not pods.items:
                return "No pods found"

            # Get logs from first pod
            pod_name = pods.items[0].metadata.name
            logs = self.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=lines
            )

            return logs

        except ApiException as exc:
            logger.error(f"Failed to get logs: {exc}")
            return f"Error: {exc}"
