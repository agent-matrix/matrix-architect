"""Authentication and authorization"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()


def create_access_token(user_id: str, role: str = "user") -> str:
    """
    Create a JWT access token

    Args:
        user_id: User identifier
        role: User role

    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token

    Args:
        token: JWT token string

    Returns:
        Token payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def authenticate_request(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Authenticate request using JWT token

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User payload from token
    """
    token = credentials.credentials
    return decode_access_token(token)


def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """FastAPI dependency for requiring authentication"""
    return authenticate_request(credentials)
