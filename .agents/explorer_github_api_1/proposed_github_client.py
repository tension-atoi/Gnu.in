import subprocess
import requests
from typing import Any

class GitHubClient:
    """Wrapper around GitHub REST API using requests."""

    @staticmethod
    def is_installed() -> bool:
        """Verify that requests library is installed/available."""
        try:
            import requests
            return True
        except ImportError:
            return False

    @staticmethod
    def get_repo_info(cwd: str) -> tuple[str, str]:
        """Extract owner and repo from local git remote URL."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            url = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get git remote: {e.stderr.strip()}")

        if "github.com" not in url:
            raise ValueError(f"Not a GitHub repository remote URL: {url}")

        part = url.split("github.com")[-1].lstrip(":/")
        tokens = part.split("/")
        if len(tokens) < 2:
            raise ValueError(f"Could not parse owner/repo from URL: {url}")
        
        owner = tokens[0]
        repo = tokens[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo

    @staticmethod
    def get_pull_requests(cwd: str, token: str | None = None) -> list[dict[str, Any]]:
        """List open pull requests for the repository using GitHub REST API."""
        owner, repo = GitHubClient.get_repo_info(cwd)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        params = {"state": "open"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")
            
        prs = response.json()
        
        # Transform to match standard format
        return [
            {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"].upper(), # e.g. "open" -> "OPEN"
                "author": {"login": pr["user"]["login"]},
                "url": pr["html_url"]
            }
            for pr in prs
        ]

    @staticmethod
    def get_recent_runs(cwd: str, limit: int = 5, token: str | None = None) -> list[dict[str, Any]]:
        """List recent GitHub Actions runs using GitHub REST API."""
        owner, repo = GitHubClient.get_repo_info(cwd)
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        params = {"per_page": limit}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")
            
        data = response.json()
        runs = data.get("workflow_runs", [])
        
        # Transform to match standard format
        return [
            {
                "databaseId": run["id"],
                "name": run["name"],
                "status": run["status"],
                "conclusion": run["conclusion"],
                "url": run["html_url"]
            }
            for run in runs
        ]
