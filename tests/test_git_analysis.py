import unittest
from git_analysis import get_repo_data

class TestGitAnalysis(unittest.TestCase):
    def test_get_repo_data(self):
        repo_data = get_repo_data('/path/to/local/repo')
        self.assertIsNotNone(repo_data)
        self.assertIn("total_commits", repo_data)