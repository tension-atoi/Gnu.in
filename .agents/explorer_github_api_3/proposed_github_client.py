import subprocess
import re
import requests
from typing import Any

class GitHubClient:
    """Helper to interact with GitHub REST API."""

    @staticmethod
    def is_installed() -> bool:
        """Check if requests library is installed."""
        try:
            import requests
            return True
        except ImportError:
            return False

    @staticmethod
    def _get_repo_info(cwd: str) -> tuple[str, str] | None:
        """Extract owner and repo name from the local git remote URL."""
        try:
            url = subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=cwd,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            # Parse git remote URL:
            # - https://github.com/owner/repo.git
            # - git@github.com:owner/repo.git
            # - ssh://git@github.com/owner/repo.git
            match = re.search(
                r'(?:git@github\.com:|https?://github\.com/|ssh://git@github\.com/)([^/]+)/([^/.]+)(?:\.git)?',
                url
            )
            if match:
                return match.group(1), match.group(2)
        except Exception:
            pass
        return None

    @staticmethod
    def get_pull_requests(cwd: str, token: str = "") -> list[dict[str, Any]]:
        """List open pull requests for the repository using GitHub REST API."""
        repo_info = GitHubClient._get_repo_info(cwd)
        if not repo_info:
            return []
        owner, repo = repo_info

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {"state": "open"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            prs = response.json()
            
            mapped_prs = []
            for pr in prs:
                user = pr.get("user") or {}
                mapped_prs.append({
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": (pr.get("state") or "").upper(),
                    "author": {"login": user.get("login", "ghost")},
                    "url": pr.get("html_url"),
                })
            return mapped_prs
        except Exception as e:
            raise RuntimeError(f"GitHub REST API error: {e}")

    @staticmethod
    def get_recent_runs(cwd: str, limit: int = 5, token: str = "") -> list[dict[str, Any]]:
        """List recent GitHub Actions runs using GitHub REST API."""
        repo_info = GitHubClient._get_repo_info(cwd)
        if not repo_info:
            return []
        owner, repo = repo_info

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        params = {"per_page": limit}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            runs = data.get("workflow_runs", [])
            
            mapped_runs = []
            for run in runs:
                mapped_runs.append({
                    "databaseId": run.get("id"),
                    "name": run.get("name"),
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "url": run.get("html_url"),
                })
            return mapped_runs
        except Exception as e:
            raise RuntimeError(f"GitHub REST API error: {e}")
