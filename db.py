from github import Github
import json
import requests
import streamlit as st


def github_read() -> dict:
    url = "https://api.github.com/repos/WillMcCall/streamlit_db/contents/db.json"
    headers = {
        'Accept': 'application/vnd.github.v3.raw'
    }
    token = st.secrets["GITHUB_TOKEN"]
    response = requests.get(url, headers=headers, auth=('WillMcCall', token))
    response.raise_for_status()

    data = response.json()
    return data


def github_write(data: dict):
    token = st.secrets["GITHUB_TOKEN"]
    g = Github(token)

    repo = g.get_repo("WillMcCall/streamlit_db")
    file = "db.json"

    new_content = json.dumps(data, indent=4)

    contents = repo.get_contents(file)
    repo.update_file(contents.path, "Update db.json", new_content, contents.sha)
