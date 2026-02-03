import os
import requests
from datetime import datetime

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

SEARCH_URL = "https://api.github.com/search/issues"

def fetch_prs(query):
    params = {
        "q": query,
        "per_page": 100
    }
    res = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    res.raise_for_status()
    return res.json()["items"]

open_prs = fetch_prs(f"author:{USERNAME} type:pr is:open")
merged_prs = fetch_prs(f"author:{USERNAME} type:pr is:merged")

def format_pr(pr):
    repo = pr["repository_url"].split("/")[-2:]
    repo_name = "/".join(repo)
    return f"- [{repo_name}]({pr['html_url']}) – {pr['title']}"

today = datetime.utcnow().strftime("%d %b %Y")

content = f"""# 📌 My Pull Request Tracker

_Last updated: **{today}**_

---

## 🔓 Open Pull Requests ({len(open_prs)})
"""
if open_prs:
    content += "\n".join(format_pr(pr) for pr in open_prs)
else:
    content += "_No open PRs 🎉_"

content += f"""

---

## ✅ Merged Pull Requests ({len(merged_prs)})
"""
if merged_prs:
    content += "\n".join(format_pr(pr) for pr in merged_prs)
else:
    content += "_No merged PRs yet_"

content += "\n"

with open("README.md", "w") as f:
    f.write(content)
