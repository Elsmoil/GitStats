import git
import plotly.graph_objs as go
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
    contributors = repo_data['contributors']
    commit_counts = [repo_data['total_commits']] * len(contributors)

    bar_chart = go.Bar(x=contributors, y=commit_counts, name='Commits by Contributor')

    layout = go.Layout(title='Commits by Contributor',
                       xaxis=dict(title='Contributors'),
                       yaxis=dict(title='Number of Commits'))

    fig = go.Figure(data=[bar_chart], layout=layout)
    graph_html = pio.to_html(fig, full_html=False)
    return graph_html