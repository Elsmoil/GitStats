import os
import subprocess
import tempfile
import unittest
from git_analysis import get_repo_data, generate_commit_graph


def _make_test_repo() -> str:
    """Create a minimal git repo with two commits from different authors."""
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-b", "main", tmp], check=True, capture_output=True)
    subprocess.run(["git", "-C", tmp, "config", "user.email", "a@test.com"], check=True)
    subprocess.run(["git", "-C", tmp, "config", "user.name", "Alice"], check=True)
    # First commit by Alice
    with open(os.path.join(tmp, "readme.txt"), "w"):
        pass
    subprocess.run(["git", "-C", tmp, "add", "."], check=True)
    subprocess.run(["git", "-C", tmp, "commit", "-m", "init"], check=True, capture_output=True)
    # Second commit by Bob
    subprocess.run(["git", "-C", tmp, "config", "user.name", "Bob"], check=True)
    subprocess.run(["git", "-C", tmp, "config", "user.email", "b@test.com"], check=True)
    with open(os.path.join(tmp, "file2.txt"), "w"):
        pass
    subprocess.run(["git", "-C", tmp, "add", "."], check=True)
    subprocess.run(["git", "-C", tmp, "commit", "-m", "second"], check=True, capture_output=True)
    return tmp


class TestGitAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_path = _make_test_repo()

    def test_get_repo_data_returns_expected_keys(self):
        data = get_repo_data(self.repo_path)
        self.assertNotIn("error", data, msg=data.get("error"))
        for key in ("total_commits", "last_commit_message", "contributors", "commit_counts", "branches"):
            self.assertIn(key, data)

    def test_total_commits(self):
        data = get_repo_data(self.repo_path)
        self.assertEqual(data["total_commits"], 2)

    def test_commit_counts_per_contributor(self):
        data = get_repo_data(self.repo_path)
        counts = data["commit_counts"]
        # Each author made exactly one commit
        self.assertEqual(counts.get("Alice"), 1)
        self.assertEqual(counts.get("Bob"), 1)

    def test_generate_commit_graph_returns_html(self):
        data = get_repo_data(self.repo_path)
        html = generate_commit_graph(data)
        self.assertIsInstance(html, str)
        self.assertIn("<div", html)

    def test_get_repo_data_invalid_path(self):
        data = get_repo_data("/nonexistent/path")
        self.assertIn("error", data)


if __name__ == '__main__':
    unittest.main()
