import os
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def get_github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Graveyard-Mining-App"
    }
    if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("your_"):
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

async def search_repositories(keywords: str, tech_stack: List[str], max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Search GitHub for repositories related to keywords and tech stack.
    Targeting repositories that might be abandoned/archived or inactive.
    """
    headers = get_github_headers()
    query_parts = [keywords]
    if tech_stack:
        # include primary language/framework
        query_parts.append(tech_stack[0])
    
    query = " ".join(query_parts) + " stars:<2000"
    url = f"https://api.github.com/search/repositories?q={httpx.QueryParams({'q': query})['q']}&sort=updated&order=asc&per_page={max_results}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    return items
        except Exception as e:
            print(f"Error searching GitHub repos: {e}")

        # Fallback search if first query was too restrictive
        fallback_query = f"{keywords} sort:updated-asc"
        fallback_url = f"https://api.github.com/search/repositories?q={keywords}&sort=updated&order=asc&per_page={max_results}"
        try:
            resp = await client.get(fallback_url, headers=headers)
            if resp.status_code == 200:
                return resp.json().get("items", [])
        except Exception as e:
            print(f"Fallback search error: {e}")
            
    return []

async def fetch_repo_details(owner: str, repo: str) -> Dict[str, Any]:
    """
    Fetch comprehensive details for a repository: last commit date, README excerpt, issues.
    """
    headers = get_github_headers()
    details = {
        "readme": "",
        "last_commit_date": None,
        "recent_issues": []
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Fetch README
        try:
            readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            resp = await client.get(readme_url, headers=headers)
            if resp.status_code == 200:
                content_resp = await client.get(resp.json().get("download_url", ""), headers=headers)
                if content_resp.status_code == 200:
                    details["readme"] = content_resp.text[:3000] # First 3000 chars
        except Exception as e:
            print(f"Error fetching readme for {owner}/{repo}: {e}")

        # 2. Fetch last commit date
        try:
            commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
            resp = await client.get(commits_url, headers=headers)
            if resp.status_code == 200:
                commits = resp.json()
                if commits and isinstance(commits, list) and len(commits) > 0:
                    commit_date_str = commits[0].get("commit", {}).get("committer", {}).get("date")
                    details["last_commit_date"] = commit_date_str
        except Exception as e:
            print(f"Error fetching commits for {owner}/{repo}: {e}")

        # 3. Fetch recent closed/open issues for context
        try:
            issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=5"
            resp = await client.get(issues_url, headers=headers)
            if resp.status_code == 200:
                issues = resp.json()
                details["recent_issues"] = [
                    {"title": i.get("title"), "state": i.get("state"), "body": (i.get("body") or "")[:200]}
                    for i in issues if isinstance(i, dict)
                ]
        except Exception as e:
            print(f"Error fetching issues for {owner}/{repo}: {e}")

    return details
