"""Role-Based Access Control (RBAC)"""

from enum import Enum
from typing import Set
from fastapi import HTTPException


class Permission(str, Enum):
    """System permissions"""
    # Job permissions
    JOB_CREATE = "job:create"
    JOB_READ = "job:read"
    JOB_UPDATE = "job:update"
    JOB_DELETE = "job:delete"
    JOB_EXECUTE = "job:execute"
    JOB_ABORT = "job:abort"

    # Deployment permissions
    DEPLOY_STAGING = "deploy:staging"
    DEPLOY_PRODUCTION = "deploy:production"
    DEPLOY_ROLLBACK = "deploy:rollback"

    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_POLICIES = "admin:policies"


class Role(str, Enum):
    """User roles"""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.VIEWER: {
        Permission.JOB_READ,
    },
    Role.OPERATOR: {
        Permission.JOB_CREATE,
        Permission.JOB_READ,
        Permission.JOB_UPDATE,
        Permission.JOB_EXECUTE,
        Permission.JOB_ABORT,
        Permission.DEPLOY_STAGING,
        Permission.DEPLOY_ROLLBACK,
    },
    Role.ADMIN: set(Permission),  # All permissions
}


def get_role_permissions(role: Role) -> Set[Permission]:
    """Get permissions for a role"""
    return ROLE_PERMISSIONS.get(role, set())


def check_permission(user_role: str, required_permission: Permission) -> bool:
    """
    Check if a user role has a specific permission

    Args:
        user_role: User's role
        required_permission: Required permission

    Returns:
        bool: True if user has permission
    """
    try:
        role = Role(user_role)
    except ValueError:
        return False

    permissions = get_role_permissions(role)
    return required_permission in permissions


def require_permission(user: dict, permission: Permission):
    """
    Require a specific permission, raise exception if not granted

    Args:
        user: User dict from auth
        permission: Required permission

    Raises:
        HTTPException: If permission not granted
    """
    user_role = user.get("role", "viewer")

    if not check_permission(user_role, permission):
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission.value} required"
        )
