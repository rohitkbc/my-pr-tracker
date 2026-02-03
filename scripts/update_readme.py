import os
import requests
from datetime import datetime

# -------------------------------------------------
# Environment variables (REQUIRED)
# -------------------------------------------------
TOKEN = os.environ.get("GITHUB_TOKEN")
USERNAME = os.environ.get("GITHUB_USERNAME")

if not TOKEN or not USERNAME:
    raise RuntimeError("GITHUB_TOKEN or GITHUB_USERNAME is missing")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

SEARCH_API = "https://api.github.com/search/issues"

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def fetch_prs(query: str):
    params = {
        "q": query,
        "per_page": 100
    }
    r = requests.get(SEARCH_API, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json().get("items", [])

def format_pr(pr):
    repo = "/".join(pr["repository_url"].split("/")[-2:])
    title = pr["title"]
    url = pr["html_url"]
    return f"- **{repo}** – [{title}]({url})"

# -------------------------------------------------
# Fetch PRs
# -------------------------------------------------
print(f"Fetching PRs for user: {USERNAME}")

open_prs = fetch_prs(f"author:{USERNAME} type:pr is:open")
merged_prs = fetch_prs(f"author:{USERNAME} type:pr is:merged")

print(f"Open PRs   : {len(open_prs)}")
print(f"Merged PRs : {len(merged_prs)}")

# -------------------------------------------------
# Build README content (ALWAYS NON-EMPTY)
# -------------------------------------------------
today = datetime.utcnow().strftime("%d %b %Y")

lines = []
lines.append("# 📌 My Pull Request Tracker")
lines.append("")
lines.append(f"_Last updated: **{today}**_")
lines.append("")
lines.append("---")
lines.append("")

lines.append(f"## 🔓 Open Pull Requests ({len(open_prs)})")
lines.append("")
if open_prs:
    for pr in open_prs:
        lines.append(format_pr(pr))
else:
    lines.append("_No open pull requests found._")

lines.append("")
lines.append("---")
lines.append("")

lines.append(f"## ✅ Merged Pull Requests ({len(merged_prs)})")
lines.append("")
if merged_prs:
    for pr in merged_prs:
        lines.append(format_pr(pr))
else:
    lines.append("_No merged pull requests found._")

# -------------------------------------------------
# HARD fallback (cannot be optimized away)
# -------------------------------------------------
if len(open_prs) == 0 and len(merged_prs) == 0:
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("⚠️ **No pull requests were returned by the GitHub API.**")
    lines.append("")
    lines.append("This is expected if:")
    lines.append("- Your PRs are in **private repositories**")
    lines.append("- Your PRs belong to **organization accounts**")
    lines.append("- You are using the default `GITHUB_TOKEN`")
    lines.append("")
    lines.append("💡 **Solution:** Use a Personal Access Token (PAT) with:")
    lines.append("- Pull requests: Read")
    lines.append("- Issues: Read")
    lines.append("- Metadata: Read")

final_content = "\n".join(lines).strip() + "\n"

# -------------------------------------------------
# Write README (guaranteed content)
# -------------------------------------------------
with open("README.md", "w", encoding="utf-8") as f:
    f.write(final_content)

print("README.md written successfully")
print(f"README length: {len(final_content)} characters")
