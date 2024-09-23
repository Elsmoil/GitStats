import matplotlib.pyplot as plt
import io
import base64
from flask import send_file
from flask import Flask, render_template
import git
import os

app = Flask(__name__)

@app.route('/')
def home():
    repo_path = '/home/sami/Desktop/GitStats'  # Replace with your Git repository path
    repo_data = get_repo_data(repo_path)
    return render_template('index.html', 
                            total_commits=repo_data['total_commits'], 
                            last_commit_message=repo_data['last_commit_message'], 
                            contributors=repo_data['contributors'],
                            commit_history=repo_data['commit_history'])
@app.route('/commit-graph')
def commit_graph():
    repo_path = '/home/sami/Desktop/GitStats'  # this is the path to your local repo
    repo = git.Repo(repo_path)
    commits = list(repo.iter_commits('main'))

    dates = [commit.committed_datetime for commit in commits]

    # Create a simple histogram of commit dates
    plt.hist(dates, bins=10)
    plt.title("Commits over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Commits")

    # Save plot to a bytes object to send to frontend
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')
    
def get_repo_data(repo_path):
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits('main'))
	
	 # Get recent commit history (last 5 commits)
        commit_history = [
            {
                "message": commit.message,
                "author": commit.author.name,
                "date": commit.committed_datetime.strftime("%Y-%m-%d"),
                "hash": commit.hexsha[:7]
            }
            for commit in commits[:5]
        ]
        repo_data = {
            "total_commits": len(commits),
            "last_commit_message": commits[0].message,
            "contributors": list({commit.author.name for commit in commits}),
            "commit_history": commit_history,
        }

        return repo_data
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(debug=True)
    
    
    improved code but not complete yet 
    
    from flask import Flask, render_template, request, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
from flask_sqlalchemy import SQLAlchemy
from config import config
import os
import git
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)
app.config.from_object(Config)
# GitHub OAuth configuration
#app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
#github_bp = make_github_blueprint(client_id=os.getenv('GITHUB_CLIENT_ID'), client_secret=os.getenv('GITHUB_CLIENT_SECRET'))
#app.register_blueprint(github_bp, url_prefix="/login")

"""# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'GitStats_db'
app.config['MYSQL_PASSWORD'] = '4545'
app.config['MYSQL_DB'] = 'gitstats'
mysql = MySQL(app)
"""
# SQLAlchemy MySQL setup
db = SQLAlchemy(app)
def get_repo_data(repo_path):
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits('main'))  # Adjust if the default branch is not 'main'

        repo_data = {
            "total_commits": len(commits),
            "last_commit_message": commits[0].message if commits else "No commits found",
            "contributors": list({commit.author.name for commit in commits}),
            "branches": [str(branch) for branch in repo.branches],
        }
        return repo_data
    except Exception as e:
        return {"error": str(e)}

def generate_commit_graph(repo_data):
    commits = repo_data.get("total_commits", 0)
    contributors = repo_data.get("contributors", [])

    fig = go.Figure(
        data=[go.Bar(x=contributors, y=[commits] * len(contributors), name='Commits')],
        layout_title_text="Commits by Contributors"
    )

    graph_html = fig.to_html(full_html=False)
    return graph_html

@app.route("/", methods=["GET", "POST"])
def home():
    repo_data = None
    graph_html = None
    repos = []
    github_linked = github.authorized

    if github_linked:
        resp = github.get("/user/repos")
        if resp.ok:
            repos = resp.json()  # List of user's repositories

            if request.method == "POST":
                repo_name = request.form.get("repo_name")
                repo_url = next((repo['clone_url'] for repo in repos if repo['name'] == repo_name), None)

                if repo_url:
                    # Clone or pull repo to a local path and analyze it
                    repo_path = f"/tmp/{repo_name}"  # A temporary path for cloned repo
                    if not os.path.exists(repo_path):
                        os.system(f'git clone {repo_url} {repo_path}')
                    else:
                        repo = git.Repo(repo_path)
                        origin = repo.remotes.origin
                        origin.pull()

                    repo_data = get_repo_data(repo_path)
                    graph_html = generate_commit_graph(repo_data)
                    
                    # Store repository data in MySQL
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT id FROM users WHERE github_id = %s", (github.get("/user").json()["id"],))
                    user_id = cur.fetchone()[0]

                    cur.execute("""
                        INSERT INTO repositories (user_id, repo_name, repo_url, total_commits, last_commit_message, contributors, branches)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_commits = VALUES(total_commits),
                        last_commit_message = VALUES(last_commit_message),
                        contributors = VALUES(contributors),
                        branches = VALUES(branches)
                    """, (user_id, repo_name, repo_url, repo_data["total_commits"], repo_data["last_commit_message"], ','.join(repo_data["contributors"]), ','.join(repo_data["branches"])))
                    mysql.connection.commit()
                    cur.close()

    return render_template("index.html", repos=repos, repo_data=repo_data, graph_html=graph_html, github_linked=github_linked)

@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    user_info = resp.json()
    
    # Store user information in MySQL
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (github_id, username, access_token) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE username = VALUES(username), access_token = VALUES(access_token)",
                (user_info["id"], user_info["login"], github.get_access_token()))
    mysql.connection.commit()
    cur.close()
    
    return f"Welcome, {user_info['login']}!"

if __name__ == "__main__":
    app.run(debug=True, port=5500)
