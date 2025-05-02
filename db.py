from github import Github
import json
import requests


def github_read() -> dict:
    url = "https://raw.githubusercontent.com/WillMcCall/streamlit_db/main/db.json"

    response = requests.get(url)
    data = response.json()

    return data


def github_write(data: dict):
    g = Github("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")

    repo = g.get_repo("WillMcCall/streamlit_db")
    file = "db.json"

    new_content = json.dumps(data, indent=4)

    contents = repo.get_contents(file)
    repo.update_file(contents.path, "Update db.json", new_content, contents.sha)
