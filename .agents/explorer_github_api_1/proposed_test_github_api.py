import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src/ to python path so we can import cockpit
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cockpit.github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_repo_info_https(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/gnu-in-labs/gnu.in-cockpit.git\n"
        mock_run.return_value = mock_result

        owner, repo = GitHubClient.get_repo_info("/dummy/path")
        self.assertEqual(owner, "gnu-in-labs")
        self.assertEqual(repo, "gnu.in-cockpit")

    @patch("subprocess.run")
    def test_get_repo_info_ssh(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:gnu-in-labs/gnu.in-os.git\n"
        mock_run.return_value = mock_result

        owner, repo = GitHubClient.get_repo_info("/dummy/path")
        self.assertEqual(owner, "gnu-in-labs")
        self.assertEqual(repo, "gnu.in-os")

    @patch("subprocess.run")
    def test_get_repo_info_invalid(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "https://gitlab.com/some/repo.git\n"
        mock_run.return_value = mock_result

        with self.assertRaises(ValueError):
            GitHubClient.get_repo_info("/dummy/path")

    @patch("cockpit.github_client.GitHubClient.get_repo_info")
    @patch("requests.get")
    def test_get_pull_requests_success(self, mock_get, mock_repo_info):
        mock_repo_info.return_value = ("gnu-in-labs", "gnu.in-cockpit")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Fix bug",
                "state": "open",
                "user": {"login": "octocat"},
                "html_url": "https://github.com/gnu-in-labs/gnu.in-cockpit/pull/1"
            }
        ]
        mock_get.return_value = mock_response

        # Test without token
        prs = GitHubClient.get_pull_requests("/dummy/path")
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]["number"], 1)
        self.assertEqual(prs[0]["title"], "Fix bug")
        self.assertEqual(prs[0]["state"], "OPEN")
        self.assertEqual(prs[0]["author"]["login"], "octocat")
        self.assertEqual(prs[0]["url"], "https://github.com/gnu-in-labs/gnu.in-cockpit/pull/1")

        mock_get.assert_called_with(
            "https://api.github.com/repos/gnu-in-labs/gnu.in-cockpit/pulls",
            headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
            params={"state": "open"},
            timeout=10
        )

        # Test with token
        prs_token = GitHubClient.get_pull_requests("/dummy/path", token="my_pat_token")
        mock_get.assert_called_with(
            "https://api.github.com/repos/gnu-in-labs/gnu.in-cockpit/pulls",
            headers={
                "Accept": "application/vnd.github+json", 
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": "Bearer my_pat_token"
            },
            params={"state": "open"},
            timeout=10
        )

    @patch("cockpit.github_client.GitHubClient.get_repo_info")
    @patch("requests.get")
    def test_get_pull_requests_error(self, mock_get, mock_repo_info):
        mock_repo_info.return_value = ("gnu-in-labs", "gnu.in-cockpit")
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError):
            GitHubClient.get_pull_requests("/dummy/path")

    @patch("cockpit.github_client.GitHubClient.get_repo_info")
    @patch("requests.get")
    def test_get_recent_runs_success(self, mock_get, mock_repo_info):
        mock_repo_info.return_value = ("gnu-in-labs", "gnu.in-cockpit")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 12345,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "html_url": "https://github.com/gnu-in-labs/gnu.in-cockpit/actions/runs/12345"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Test without token
        runs = GitHubClient.get_recent_runs("/dummy/path", limit=5)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["databaseId"], 12345)
        self.assertEqual(runs[0]["name"], "CI")
        self.assertEqual(runs[0]["status"], "completed")
        self.assertEqual(runs[0]["conclusion"], "success")
        self.assertEqual(runs[0]["url"], "https://github.com/gnu-in-labs/gnu.in-cockpit/actions/runs/12345")

        mock_get.assert_called_with(
            "https://api.github.com/repos/gnu-in-labs/gnu.in-cockpit/actions/runs",
            headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
            params={"per_page": 5},
            timeout=10
        )

        # Test with token
        runs_token = GitHubClient.get_recent_runs("/dummy/path", limit=10, token="my_pat_token")
        mock_get.assert_called_with(
            "https://api.github.com/repos/gnu-in-labs/gnu.in-cockpit/actions/runs",
            headers={
                "Accept": "application/vnd.github+json", 
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": "Bearer my_pat_token"
            },
            params={"per_page": 10},
            timeout=10
        )

    @patch("cockpit.github_client.GitHubClient.get_repo_info")
    @patch("requests.get")
    def test_get_recent_runs_error(self, mock_get, mock_repo_info):
        mock_repo_info.return_value = ("gnu-in-labs", "gnu.in-cockpit")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError):
            GitHubClient.get_recent_runs("/dummy/path")

if __name__ == "__main__":
    unittest.main()
