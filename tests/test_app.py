import unittest
from app import app, is_valid_github_url


class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # ------------------------------------------------------------------
    # URL validation
    # ------------------------------------------------------------------

    def test_valid_github_url(self):
        self.assertTrue(is_valid_github_url("https://github.com/owner/repo"))

    def test_valid_github_url_with_git_suffix(self):
        self.assertTrue(is_valid_github_url("https://github.com/owner/repo.git"))

    def test_invalid_url_not_github(self):
        self.assertFalse(is_valid_github_url("https://gitlab.com/owner/repo"))

    def test_invalid_url_missing_repo(self):
        self.assertFalse(is_valid_github_url("https://github.com/owner"))

    def test_invalid_url_http(self):
        self.assertFalse(is_valid_github_url("http://github.com/owner/repo"))

    def test_invalid_url_empty(self):
        self.assertFalse(is_valid_github_url(""))

    def test_invalid_url_path_traversal(self):
        self.assertFalse(is_valid_github_url("https://github.com/../etc/passwd"))

    # ------------------------------------------------------------------
    # Home page
    # ------------------------------------------------------------------

    def test_home_page_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"GitStats", response.data)

    def test_home_page_no_url(self):
        response = self.client.post("/", data={"repo_url": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please provide", response.data)

    def test_home_page_invalid_url(self):
        response = self.client.post("/", data={"repo_url": "not-a-url"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid repository URL", response.data)

    def test_home_page_non_github_url(self):
        response = self.client.post("/", data={"repo_url": "https://gitlab.com/owner/repo"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid repository URL", response.data)


if __name__ == '__main__':
    unittest.main()
