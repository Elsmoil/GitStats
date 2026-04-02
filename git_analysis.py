import git
import plotly.graph_objects as go
import logging


def get_repo_data(repo_path):
    try:
        repo = git.Repo(repo_path)
        # Fall back to the active branch if 'main' does not exist
        branch = 'main' if 'main' in [h.name for h in repo.heads] else repo.active_branch.name
        commits = list(repo.iter_commits(branch))

        branches = [str(b) for b in repo.branches]

        # Count actual commits per contributor
        commit_counts: dict = {}
        for commit in commits:
            name = commit.author.name
            commit_counts[name] = commit_counts.get(name, 0) + 1

        repo_data = {
            "total_commits": len(commits),
            "last_commit_message": commits[0].message if commits else "",
            "contributors": list(commit_counts.keys()),
            "commit_counts": commit_counts,
            "branches": branches,
        }
        return repo_data
    except Exception as e:
        return {"error": str(e)}


def generate_commit_graph(repo_data):
    try:
        commit_counts = repo_data.get("commit_counts", {})
        contributors = list(commit_counts.keys())

        if not contributors:
            contributors = ["No contributors"]
            y_values = [0]
        else:
            y_values = [commit_counts[c] for c in contributors]

        # Define colors for each contributor
        colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33FF', '#FFC300']
        bar_colors = (colors * (len(contributors) // len(colors) + 1))[:len(contributors)]

        fig = go.Figure(
            data=[go.Bar(x=contributors, y=y_values, name='Commits', marker_color=bar_colors)],
            layout_title_text="Commits by Contributor"
        )

        graph_html = fig.to_html(full_html=False)
        return graph_html
    except Exception as e:
        logging.error(f"Error generating graph: {str(e)}")
        return ""
