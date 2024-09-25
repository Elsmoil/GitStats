import os
import tempfile
import unittest
from flask import url_for
from app import app, db, User, Repository  # Replace `your_flask_app` with the actual file name

class FlaskAppTests(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app = app
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()  # Create all tables

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)  # Remove the temporary database

    def test_home_page(self):
        response = self.client.get(url_for('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)  # Replace 'Welcome' with actual content in your home page

    def test_invalid_repo_url(self):
        response = self.client.post(url_for('home'), data={
            'repo_url': 'invalid-url',
            'repo_name': ''
        })
        self.assertIn(b'Please provide a repository URL', response.data)

    def test_github_auth(self):
        with self.app.test_request_context('/github'):
            response = self.client.get(url_for('github_login'))
            self.assertEqual(response.status_code, 302)  # Check for redirect
            self.assertIn('location', response.headers)  # Check if it redirects

    def test_create_user(self):
        with self.app.app_context():
            new_user = User(github_id="12345", username="testuser", access_token="token123")
            db.session.add(new_user)
            db.session.commit()
            
            retrieved_user = User.query.filter_by(github_id="12345").first()
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.username, "testuser")

if __name__ == '__main__':
    unittest.main()