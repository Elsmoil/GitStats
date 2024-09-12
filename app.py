from flask import Flask, render_template, request, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
from git_analysis import get_repo_data, generate_commit_graph
import os

app = Flask(__name__)

# GitHub OAuth configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
github_bp = make_github_blueprint(client_id=os.getenv('GITHUB_CLIENT_ID'), client_secret=os.getenv('GITHUB_CLIENT_SECRET'))
app.register_blueprint(github_bp, url_prefix="/login")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        repo_url = request.form["repo_url"]
        repo_path = "/path/to/local/repo"  # Convert URL to local path if needed
        repo_data = get_repo_data(repo_path)
        graph_html = generate_commit_graph(repo_data)
        return render_template("index.html", repo_data=repo_data, graph_html=graph_html, github_linked=github.authorized)
    return render_template("index.html", repo_data=None, graph_html=None, github_linked=github.authorized)

# GitHub OAuth login route
@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    return f"Welcome, {resp.json()['login']}!"

if __name__ == "__main__":
    app.run(debug=True)