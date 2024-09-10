import git

def get_repo_data(repo_path):
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits('main'))

        #Extract simple information
        repo_data = {"total_commits":
                     len(commits),
                     "last_commit_massage":
                     commits[0].massage,
                     "contributors":
                     list({commit.author.name for commit in commits}),
                     }
        return repo_data
    except Exception as e:
        return {"error":
                str(e)}