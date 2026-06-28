import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to python path so we can import cockpit.github_client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cockpit.github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    @patch('subprocess.check_output')
    def test_get_repo_info_https(self, mock_subprocess):
        mock_subprocess.return_value = "https://github.com/owner/repo.git\n"
        info = GitHubClient._get_repo_info("/dummy/path")
        self.assertEqual(info, ("owner", "repo"))

    @patch('subprocess.check_output')
    def test_get_repo_info_ssh(self, mock_subprocess):
        mock_subprocess.return_value = "git@github.com:owner/repo.git\n"
        info = GitHubClient._get_repo_info("/dummy/path")
        self.assertEqual(info, ("owner", "repo"))

    @patch('subprocess.check_output')
    @patch('requests.get')
    def test_get_pull_requests_success(self, mock_get, mock_subprocess):
        mock_subprocess.return_value = "https://github.com/owner/repo.git\n"
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "number": 42,
                "title": "Fix bug",
                "state": "open",
                "html_url": "https://github.com/owner/repo/pull/42",
                "user": {"login": "testuser"}
            }
        ]
        mock_get.return_value = mock_response

        prs = GitHubClient.get_pull_requests("/dummy/path", token="my-token")
        
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]["number"], 42)
        self.assertEqual(prs[0]["title"], "Fix bug")
        self.assertEqual(prs[0]["state"], "OPEN")
        self.assertEqual(prs[0]["author"]["login"], "testuser")
        self.assertEqual(prs[0]["url"], "https://github.com/owner/repo/pull/42")

        # Verify headers
        mock_get.assert_called_once()
        headers = mock_get.call_args[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer my-token")

    @patch('subprocess.check_output')
    @patch('requests.get')
    def test_get_recent_runs_success(self, mock_get, mock_subprocess):
        mock_subprocess.return_value = "https://github.com/owner/repo.git\n"
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 999,
                    "name": "CI Build",
                    "status": "completed",
                    "conclusion": "success",
                    "html_url": "https://github.com/owner/repo/actions/runs/999"
                }
            ]
        }
        mock_get.return_value = mock_response

        runs = GitHubClient.get_recent_runs("/dummy/path", limit=3, token="my-token")
        
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["databaseId"], 999)
        self.assertEqual(runs[0]["name"], "CI Build")
        self.assertEqual(runs[0]["status"], "completed")
        self.assertEqual(runs[0]["conclusion"], "success")
        self.assertEqual(runs[0]["url"], "https://github.com/owner/repo/actions/runs/999")

        # Verify headers and params
        mock_get.assert_called_once()
        headers = mock_get.call_args[1]["headers"]
        params = mock_get.call_args[1]["params"]
        self.assertEqual(headers["Authorization"], "Bearer my-token")
        self.assertEqual(params["per_page"], 3)

    def test_is_installed(self):
        self.assertTrue(GitHubClient.is_installed())

if __name__ == '__main__':
    unittest.main()
