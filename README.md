# GitStats

## Introduction

**GitStats** is a web-based application that helps developers and project managers extract and analyze Git repository data. The tool provides insights, statistics, and visual representations of repository activity, making it easier to manage projects and understand team dynamics.

### Deployed Site
You can view the live version of GitStats here: https://gitstats.onrender.com

### Blog Article
Read more about the development process on our blog: https://www.linkedin.com/pulse/building-gitstats-journey-code-challenges-insights-ibrahim-ahmed-ca9nf/

### Author
Developed by [Elsmoal Suliman Ibrahim](www.linkedin.com/in/elsmoal-suliman-ibrahim-ahmed-01bb27228)

## Installation

To run this project locally, follow these steps:

1. Clone the repository
   git clone https://github.com/Elsmoil/GitStats.git
   cd GitStats

    Set up a virtual environment:


python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install the dependencies:


pip install -r requirements.txt

Set up the .env file for environment variables (use .env.template as a guide).

Run the application:


    flask run

Now, visit http://127.0.0.1:5500/ to see the app in action.
Usage

    Enter the URL of a Git repository in the input field.
    Click on "Analyze" to extract data from the repository.
    View various statistics like the number of commits, contributors, and detailed visualizations.
    Optionally, log in with your GitHub account to monitor your repositories continuously.

You can view the deployed version here: (https://gitstats.onrender.com)
Contributing

Contributions are welcome! Here's how you can help:

    Fork the repository.
    Create a new branch for your feature or bug fix.


git checkout -b feature-branch-name

Commit your changes.


git commit -m "Your descriptive commit message"

Push to your branch.


    git push origin feature-branch-name

    Submit a pull request and describe your changes.

Related Projects

    GitHub Insights: An official GitHub tool to visualize repository data.
    RepoSense: Another tool for visualizing Git repository statistics.

Licensing

This project is licensed under the MIT License. See the LICENSE file for more details.

yaml
