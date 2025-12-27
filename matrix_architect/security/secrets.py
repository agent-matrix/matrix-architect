"""Secrets management"""

import os
from typing import Optional, Dict


class SecretsManager:
    """
    Manage secrets securely

    In production, integrate with HashiCorp Vault, AWS Secrets Manager, etc.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def get_secret(self, key: str) -> Optional[str]:
        """
        Get a secret value

        Args:
            key: Secret key

        Returns:
            Secret value or None
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Fall back to environment variables
        value = os.getenv(key)

        if value:
            self._cache[key] = value

        return value

    def set_secret(self, key: str, value: str):
        """
        Set a secret (cache only, not persisted)

        Args:
            key: Secret key
            value: Secret value
        """
        self._cache[key] = value

    def delete_secret(self, key: str):
        """Delete a secret from cache"""
        self._cache.pop(key, None)


# Global secrets manager
_secrets_manager = SecretsManager()


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager"""
    return _secrets_manager
