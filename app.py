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
                            contributors=repo_data['contributors'])

def get_repo_data(repo_path):
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits('main'))

        repo_data = {
            "total_commits": len(commits),
            "last_commit_message": commits[0].message,
            "contributors": list({commit.author.name for commit in commits}),
        }

        return repo_data
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(debug=True)