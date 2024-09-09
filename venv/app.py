from flask import Flask,render_template

#Create a Flask instance
app = Flask(__name__)

#Define the home route @app.route('/')
def home():
    return "Welcome to GiutStats"
if __name__ == "__main__":
    app.run(depug=True)