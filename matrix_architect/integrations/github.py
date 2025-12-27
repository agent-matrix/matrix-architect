from __future__ import annotations

"""GitHub integration (ported from GitPilot).

This module exposes a small surface area used by Matrix Architect. Internally it relies on
the GitPilot-originated helpers in `github_api.py`, `github_oauth.py`, and `github_app.py`.
"""

from .github_api import (
    list_user_repos,
    list_user_repos_paginated,
    search_user_repos,
    get_repo,
    create_branch,
    get_repo_tree,
    get_file,
    put_file,
    delete_file,
)

__all__ = [
    "list_user_repos",
    "list_user_repos_paginated",
    "search_user_repos",
    "get_repo",
    "create_branch",
    "get_repo_tree",
    "get_file",
    "put_file",
    "delete_file",
]
