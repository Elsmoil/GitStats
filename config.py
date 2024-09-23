import os

class Config:
    # MySQL configuration (already included)
    MYSQL_USER = 'GitStats_db'
    MYSQL_PASSWORD = '4545'
    MYSQL_HOST = 'localhost'
    MYSQL_DB = 'gitstats'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://GitStats_db:4545@localhost/gitstats'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # GitHub OAuth configuration
    GITHUB_CLIENT_ID = 'Ov23liLvS4vwi0Y40iFO'
    GITHUB_CLIENT_SECRET = '77e2df256e696eb6cd3a7e901d56ca9b15d414ff'
    GITHUB_REDIRECT_URI = 'http://localhost:5500/login/github/authorized'
    
    # Secret key for session management
    SECRET_KEY = 'your_secret_key'

