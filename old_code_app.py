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
