from flask import Flask, render_template, request
from config import Config
import os
import re
import git
import plotly.graph_objects as go
import tempfile
import shutil
from dotenv import load_dotenv
import logging
from flask_talisman import Talisman

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv('SECRET_KEY')

# Strict GitHub public URL pattern: https://github.com/<owner>/<repo>
# Owner: starts with alphanumeric, may contain alphanumeric/underscore/hyphen (no dots)
# Repo: may contain alphanumeric/underscore/dot/hyphen but must start with alphanumeric or underscore
_GITHUB_URL_RE = re.compile(
    r'^https://github\.com/'
    r'[A-Za-z0-9][A-Za-z0-9_-]*'
    r'/'
    r'[A-Za-z0-9_][A-Za-z0-9_.-]*'
    r'(\.git)?$'
)


def is_valid_github_url(url: str) -> bool:
    """Return True only for public GitHub repository URLs of the form
    https://github.com/<owner>/<repo> (with optional .git suffix).
    """
    if not _GITHUB_URL_RE.match(url):
        return False
    # Reject any path traversal sequences
    return '..' not in url


# Function to analyze repo
def get_repo_data(repo_path, branch='main'):
    try:
        repo = git.Repo(repo_path)
        # Check if the branch exists; fall back to the active branch
        if branch not in [h.name for h in repo.heads]:
            branch = repo.active_branch.name
        commits = list(repo.iter_commits(branch))
        if not commits:
            return {"error": "No commits found in the repository."}

        # Count actual commits per contributor
        commit_counts: dict = {}
        for commit in commits:
            name = commit.author.name
            commit_counts[name] = commit_counts.get(name, 0) + 1

        repo_data = {
            "total_commits": len(commits),
            "last_commit_message": commits[0].message.strip(),
            "contributors": list(commit_counts.keys()),
            "commit_counts": commit_counts,
            "branches": [str(b) for b in repo.branches],
        }
        logging.debug(f"Repo Data: {repo_data}")
        return repo_data
    except Exception as e:
        logging.error(f"Error analyzing repository: {str(e)}")
        return {"error": str(e)}


# Function to generate commit graph
def generate_commit_graph(repo_data):
    try:
        commit_counts = repo_data.get("commit_counts", {})
        contributors = list(commit_counts.keys())
        if not contributors:
            contributors = ["No contributors"]
            y_values = [0]
        else:
            y_values = [commit_counts[c] for c in contributors]

        fig = go.Figure(
            data=[go.Bar(x=contributors, y=y_values, name='Commits')],
            layout_title_text="Commits by Contributor"
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
    error = None

    if request.method == "POST":
        repo_url = request.form.get("repo_url", "").strip()

        if not repo_url:
            error = "Please provide a public GitHub repository URL."
            return render_template("index.html", repo_data=repo_data, graph_html=graph_html, error=error)

        if not is_valid_github_url(repo_url):
            error = "Invalid repository URL. Only public GitHub URLs of the form https://github.com/owner/repo are accepted."
            return render_template("index.html", repo_data=repo_data, graph_html=graph_html, error=error)

        selected_repo_url = repo_url
        logging.debug(f"Selected Repo URL: {selected_repo_url}")

        temp_dir = tempfile.mkdtemp()
        try:
            logging.debug(f"Cloning repository {selected_repo_url} to {temp_dir}")
            git.Repo.clone_from(selected_repo_url, temp_dir)
            logging.debug("Repository cloned successfully.")

            repo_data = get_repo_data(temp_dir)
            if "error" in repo_data:
                error = repo_data["error"]
                return render_template("index.html", repo_data=None, graph_html=None, error=error)

            graph_html = generate_commit_graph(repo_data)

        except git.GitCommandError as e:
            logging.error(f"Git error: {e}")
            error = "Failed to clone the repository. Please check the repository URL and ensure it is public."
        except Exception as e:
            logging.error(f"Error: {e}")
            error = "An unexpected error occurred while analyzing the repository."
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception as cleanup_err:
                logging.warning(f"Failed to clean up temporary directory {temp_dir}: {cleanup_err}")
            logging.debug(f"Cleaned up temporary directory {temp_dir}")

    return render_template("index.html", repo_data=repo_data, graph_html=graph_html, error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5500)
