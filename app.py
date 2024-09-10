from flask import Flask, jsonify
from git_analysis import get_repo_data

#   Create a Flask instance
app = Flask(__name__)

#   Define the home route 
@app.route('/')
def home():
    return "Welcome to GitStats"

@app.route('/repo-stats')
def repo_stats():
    repo_path = "/home/sami/Desktop/GitStats"
    data = get_repo_data(repo_path)
    if "error" in data:
        return jsonify({"Error":data['error']}), 400
#return the error massage with 400 status code

    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True)