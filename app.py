from flask import Flask,jsonify
from git_analysis import get_repo_data

#   Create a Flask instance
app = Flask(__name__)

#   Define the home route 
@app.route('/')
def home():
    return "Welcome to GitStats"

@app.route('/gitdata')
def git_data():
    repo_path = "/home/sami/Desktop/GitStats"
    data = get_repo_data(repo_path)
    return jsonify(data)
if __name__ == "__main__":
    app.run(debug=True)