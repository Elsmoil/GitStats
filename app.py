from flask import Flask, render_template, request, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Importing from config.py
import os
import git
import plotly.graph_objects as go
import plotly.io as pio
import tempfile
import shutil
from dotenv import load_dotenv
import logging
from flask_talisman import Talisman

load_dotenv() #load enviroment variables from .env

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(Config)

app.config['GITHUB_REDIRECT_URI'] = os.getenv('GITHUB_REDIRECT_URI')
app.secret_key = os.getenv('SECRET_KEY')
# SQLAlchemy MySQL setup
db = SQLAlchemy(app)

# Define user model to store GitHub user info
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)

# Define repository model to store repo info
class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repo_name = db.Column(db.String(255), nullable=False)
    repo_url = db.Column(db.String(255), nullable=False)
    total_commits = db.Column(db.Integer)
    last_commit_message = db.Column(db.String(255))
    contributors = db.Column(db.String(255))
    branches = db.Column(db.String(255))

# Uncomment the following line if you need to create tables
# db.create_all()

# GitHub OAuth configuration
github_bp = make_github_blueprint(
    client_id=app.config.get('GITHUB_CLIENT_ID'),
    client_secret=app.config.get('GITHUB_CLIENT_SECRET'),
    scope="repo"
)
app.register_blueprint(github_bp, url_prefix="/login")

# Function to analyze repo
def get_repo_data(repo_path, branch='main'):
    try:
        repo = git.Repo(repo_path)
        # Check if the branch exists
        if branch not in repo.heads:
            branch = repo.active_branch.name
        commits = list(repo.iter_commits(branch))
        if not commits:
            return {"error": "No commits found in the repository."}

        repo_data = {
            "total_commits": len(commits),
            "last_commit_message": commits[0].message.strip(),
            "contributors": list({commit.author.name for commit in commits}),
            "branches": [str(branch) for branch in repo.branches],
        }
        logging.debug(f"Repo Data: {repo_data}")
        return repo_data
    except Exception as e:
        logging.error(f"Error analyzing repository: {str(e)}")
        return {"error": str(e)}

# Function to generate commit graph
def generate_commit_graph(repo_data):
    try:
        commits = repo_data.get("total_commits", 0)
        contributors = repo_data.get("contributors", [])
        if not contributors:
            contributors = ["No contributors"]
        
        # Example graph: Commits per contributor (equal for simplicity)
        y_values = [commits] * len(contributors)

        fig = go.Figure(
            data=[go.Bar(x=contributors, y=y_values, name='Commits')],
            layout_title_text="Commits by Contributors"
        )

        graph_html = fig.to_html(full_html=False)
        return graph_html
    except Exception as e:
        logging.error(f"Error generating graph: {str(e)}")
        return ""

@app.route("/", methods=["GET", "POST"])
def home():
    repo_data = None
    graph_html = None
    repos = []
    github_linked = github.authorized
    error = None

    if github_linked:
        resp = github.get("/user/repos")
        if resp.ok:
            repos = resp.json()  # List of user's repositories
        else:
            logging.error("Failed to fetch user repositories from GitHub.")

    if request.method == "POST":
        repo_url = request.form.get("repo_url")
        repo_name = request.form.get("repo_name")

        # If user provides a URL, use it; else use selected repo from GitHub
        if repo_url:
            selected_repo_url = repo_url
            selected_repo_name = os.path.basename(repo_url).replace('.git', '')
        elif github_linked and repo_name:
            selected_repo_url = next((repo['clone_url'] for repo in repos if repo['name'] == repo_name), None)
            selected_repo_name = repo_name
        else:
            error = "Please provide a repository URL or select a repository from your GitHub account."
            return render_template("index.html", repos=repos, repo_data=repo_data, graph_html=graph_html, github_linked=github_linked, error=error)

        if not selected_repo_url:
            error = "Could not find the repository URL."
            return render_template("index.html", repos=repos, repo_data=repo_data, graph_html=graph_html, github_linked=github_linked, error=error)

        logging.debug(f"Selected Repo URL: {selected_repo_url}")
        logging.debug(f"Selected Repo Name: {selected_repo_name}")

        # Clone or pull repo to a temporary path and analyze it
        temp_dir = tempfile.mkdtemp()
        try:
            logging.debug(f"Cloning repository {selected_repo_url} to {temp_dir}")
            repo = git.Repo.clone_from(selected_repo_url, temp_dir)
            logging.debug("Repository cloned successfully.")

            # Get repo data
            repo_data = get_repo_data(temp_dir)
            if "error" in repo_data:
                error = repo_data["error"]
                return render_template("index.html", repos=repos, repo_data=None, graph_html=None, github_linked=github_linked, error=error)

            # Generate commit graph
            graph_html = generate_commit_graph(repo_data)

            # If GitHub linked, store in DB
            if github_linked:
                resp_user = github.get("/user")
                if resp_user.ok:
                    user_info = resp_user.json()
                    user = User.query.filter_by(github_id=str(user_info["id"])).first()
                    if user:
                        # Check if repo already exists
                        existing_repo = Repository.query.filter_by(repo_url=selected_repo_url, user_id=user.id).first()
                        if not existing_repo:
                            new_repo = Repository(
                                user_id=user.id,
                                repo_name=selected_repo_name,
                                repo_url=selected_repo_url,
                                total_commits=repo_data["total_commits"],
                                last_commit_message=repo_data["last_commit_message"],
                                contributors=','.join(repo_data["contributors"]),
                                branches=','.join(repo_data["branches"])
                            )
                            db.session.add(new_repo)
                            db.session.commit()
                            logging.debug(f"Repository {selected_repo_name} added to the database.")
                        else:
                            logging.debug(f"Repository {selected_repo_name} already exists in the database.")
                    else:
                        error = "User not found in the database."
                else:
                    logging.error("Failed to fetch user info from GitHub.")

        except git.GitCommandError as e:
            logging.error(f"Git error: {e}")
            error = "Failed to clone or pull the repository. Please check the repository URL."
        except Exception as e:
            logging.error(f"Error: {e}")
            error = "An unexpected error occurred while analyzing the repository."
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)
            logging.debug(f"Cleaned up temporary directory {temp_dir}")

    return render_template("index.html", repos=repos, repo_data=repo_data, graph_html=graph_html, github_linked=github_linked, error=error)

@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    user_info = resp.json()

    # Store user information in MySQL
    user = User.query.filter_by(github_id=str(user_info["id"])).first()
    if not user:
        # Note: github.get_access_token() returns a token object, not a string
        access_token = github.token['access_token'] if github.token else 'no-token'
        user = User(github_id=str(user_info["id"]), username=user_info["login"], access_token=access_token)
        db.session.add(user)
        db.session.commit()
        logging.debug(f"User {user_info['login']} added to the database.")
    else:
        logging.debug(f"User {user_info['login']} already exists in the database.")
    
    return redirect(url_for('home'))  # Redirect to home after login

if __name__ == "__main__":
    app.run(debug=True, port=5500)
