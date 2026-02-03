import os
import requests
from datetime import datetime

# --------------------------------------------------
# Config
# --------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")

if not GITHUB_TOKEN or not USERNAME:
    raise RuntimeError("GITHUB_TOKEN or GITHUB_USERNAME not set")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

SEARCH_URL = "https://api.github.com/search/issues"

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def fetch_prs(query):
    """Fetch PRs using GitHub search API"""
    params = {
        "q": query,
        "per_page": 100
    }
    resp = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json().get("items", [])


def format_pr(pr):
    repo = pr["repository_url"].split("/")[-2:]
    repo_name = "/".join(repo)
    title = pr["title"]
    url = pr["html_url"]
    return f"- **{repo_name}** – [{title}]({url})"


# --------------------------------------------------
# Fetch PRs
# --------------------------------------------------
print("Fetching PRs for user:", USERNAME)

open_prs = fetch_prs(f"author:{USERNAME} type:pr is:open")
merged_prs = fetch_prs(f"author:{USERNAME} type:pr is:merged")

print(f"Open PRs found   : {len(open_prs)}")
print(f"Merged PRs found : {len(merged_prs)}")

# --------------------------------------------------
# Build README content
# --------------------------------------------------
today = datetime.utcnow().strftime("%d %b %Y")

content = [
    "# 📌 My Pull Request Tracker",
    "",
    f"_Last updated: **{today}**_",
    "",
    "---",
    "",
    f"## 🔓 Open Pull Requests ({len(open_prs)})",
    ""
]

if open_prs:
    content.extend(format_pr(pr) for pr in open_prs)
else:
    content.append("_No open pull requests found._")

content.extend([
    "",
    "---",
    "",
    f"## ✅ Merged Pull Requests ({len(merged_prs)})",
    ""
])

if merged_prs:
    content.extend(format_pr(pr) for pr in merged_prs)
else:
    content.append("_No merged pull requests found._")

# --------------------------------------------------
# Fallback (IMPORTANT)
# --------------------------------------------------
if not open_prs and not merged_prs:
    content.extend([
        "",
        "---",
        "",
        "⚠️ **No pull requests were returned by the GitHub API.**",
        "",
        "Possible reasons:",
        "- PRs are in **private repositories**",
        "- PRs belong to **organization repos**",
        "- `GITHUB_TOKEN` has limited search scope",
        "",
        "💡 **Fix:** Use a Personal Access Token (PAT) instead of `GITHUB_TOKEN`."
    ])

final_content = "\n".join(content) + "\n"

# --------------------------------------------------
# Write README
# --------------------------------------------------
with open("README.md", "w", encoding="utf-8") as f:
    f.write(final_content)

print("README.md successfully generated")
