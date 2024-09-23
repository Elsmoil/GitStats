import git
import plotly.graph_objects as go
import plotly.io as pio

def get_repo_data(repo_path):
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits('main'))

        branches = [str(branch) for branch in repo.branches]  # Get branches
        #Extract simple information
        repo_data = {"total_commits":
                     len(commits),
                     "last_commit_message":
                     commits[0].message,
                     "contributors":
                     list({commit.author.name for commit in commits}),
                     #"commit_history": commit_history,
            "branches": branches,
                     }
        return repo_data
    except Exception as e:
        return {"error": str(e)}

def generate_commit_graph(repo_data):
    commits = repo_data["total_commits"]
    contributors = repo_data["contributors"]

    fig = go.Figure(
        data=[go.Bar(x=contributors, y=[commits], name='Commits')],
        layout_title_text="Commits by Contributors"
    )

    graph_html = fig.to_html(full_html=False)
    return graph_html
