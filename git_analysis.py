import git
import plotly.graph_objects as go
import plotly.io as pio
import logging

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
    try:
        commits = repo_data.get("total_commits", 0)
        contributors = repo_data.get("contributors", [])
        
        if not contributors:
            contributors = ["No contributors"]
        
        # Example graph: Commits per contributor (equal for simplicity)
        y_values = [commits] * len(contributors)

        # Define colors for each contributor
        colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33FF', '#FFC300']  # Add more colors as needed
        bar_colors = colors * (len(contributors) // len(colors) + 1)  # Repeat colors if there are many contributors

        fig = go.Figure(
            data=[go.Bar(x=contributors, y=y_values, name='Commits', marker_color=bar_colors[:len(contributors)])],
            layout_title_text="Commits by Contributors"
        )

        graph_html = fig.to_html(full_html=False)
        return graph_html
    except Exception as e:
        logging.error(f"Error generating graph: {str(e)}")
        return ""