from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, Tuple


EXPECTED_LIVE_BRANCH = "blaize-customizations"


def get_current_git_branch(
    repo_root: Path,
    *,
    git_cmd: Optional[list[str]] = None,
    timeout: int = 5,
) -> Tuple[Optional[str], Optional[str]]:
    """Return the active git branch for ``repo_root``.

    Returns ``(branch, None)`` on success, or ``(None, error_message)`` if the
    branch cannot be determined safely.
    """
    if not (repo_root / ".git").exists():
        return None, f"{repo_root} is not a git repository"

    cmd = (git_cmd or ["git"]) + ["rev-parse", "--abbrev-ref", "HEAD"]
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as e:  # pragma: no cover - defensive wrapper
        return None, str(e)

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        return None, stderr or "failed to determine current git branch"

    branch = (result.stdout or "").strip()
    if not branch:
        return None, "git returned an empty branch name"

    return branch, None


def check_expected_live_branch(
    repo_root: Path,
    *,
    expected_branch: str = EXPECTED_LIVE_BRANCH,
    git_cmd: Optional[list[str]] = None,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate that the repo is on the expected live branch.

    Returns ``(True, branch, None)`` when the branch matches, otherwise
    ``(False, branch_or_none, error_or_none)``.
    """
    branch, error = get_current_git_branch(repo_root, git_cmd=git_cmd)
    if branch is None:
        return False, None, error
    if branch != expected_branch:
        return False, branch, None
    return True, branch, None