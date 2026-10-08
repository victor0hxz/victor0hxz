#!/usr/bin/env python3
"""Update the public repository list in the profile README."""
import json
import os
import urllib.request
from pathlib import Path

USER = "victor0hxz"
START = "<!-- REPOSITORIES:START -->"
END = "<!-- REPOSITORIES:END -->"

def fetch_repos():
    repos = []
    token = os.environ.get("GH_TOKEN", "")
    for page in range(1, 11):
        req = urllib.request.Request(
            f"https://api.github.com/users/{USER}/repos?type=owner&sort=updated&per_page=100&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "profile-readme-updater",
                **({"Authorization": f"Bearer {token}"} if token else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            batch = json.load(response)
        repos.extend(batch)
        if len(batch) < 100:
            break
    return [
        repo for repo in repos
        if not repo["fork"] and not repo["private"] and not repo["archived"]
        and repo["name"].lower() != USER.lower()
    ]

def main():
    repos = fetch_repos()
    repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    lines = [
        "| Repository | Description | Language |",
        "| --- | --- | --- |",
    ]
    for repo in repos[:12]:
        name = repo["name"].replace("|", r"\|")
        desc = (repo.get("description") or "—").replace("|", r"\|").replace("\n", " ")
        lang = (repo.get("language") or "—").replace("|", r"\|")
        lines.append(f'| [{name}]({repo["html_url"]}) | {desc} | {lang} |')
    if not repos:
        lines = ["No public repositories to display yet."]
    path = Path("README.md")
    original = path.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise ValueError("Missing or duplicate README repository markers")
    before, rest = original.split(START, 1)
    _, after = rest.split(END, 1)
    updated = before + START + "\n" + "\n".join(lines) + "\n" + END + after
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"Updated README with {min(len(repos), 12)} repositories.")
    else:
        print("Repository list is already up to date.")

if __name__ == "__main__":
    main()
