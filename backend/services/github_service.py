import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv
from logging_config import get_logger
from services.repo_triage import calculate_abandonment_score

load_dotenv()
logger = get_logger("GitHubService")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

class GitHubService:
    def __init__(self):
        self.github_token = GITHUB_TOKEN
        self.tavily_token = TAVILY_API_KEY

    def _get_github_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Graveyard-Mining-App"
        }
        if self.github_token and not self.github_token.startswith("your_"):
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    async def search_repositories(self, keywords: str, tech_stack: list[str], max_results: int = 6) -> list[dict[str, Any]]:
        headers = self._get_github_headers()
        query_parts = [keywords]
        if tech_stack:
            query_parts.append(tech_stack[0])

        query = " ".join(query_parts) + " stars:<2000"
        url = f"https://api.github.com/search/repositories?q={httpx.QueryParams({'q': query})['q']}&sort=updated&order=asc&per_page={max_results}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=15.0)) as client:
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", [])
                    if items:
                        return items
            except Exception as e:
                logger.error(f"Error searching GitHub repos: {e}")

            fallback_url = f"https://api.github.com/search/repositories?q={keywords}&sort=updated&order=asc&per_page={max_results}"
            try:
                resp = await client.get(fallback_url, headers=headers)
                if resp.status_code == 200:
                    return resp.json().get("items", [])
            except Exception as e:
                logger.error(f"Fallback search error: {e}")

        return []

    async def fetch_repo_details(self, owner: str, repo: str) -> dict[str, Any]:
        headers = self._get_github_headers()
        details = {
            "readme": "",
            "last_commit_date": None,
            "recent_issues": []
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=10.0)) as client:
            try:
                readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
                resp = await client.get(readme_url, headers=headers)
                if resp.status_code == 200:
                    content_resp = await client.get(resp.json().get("download_url", ""), headers=headers)
                    if content_resp.status_code == 200:
                        details["readme"] = content_resp.text[:3000]
            except Exception as e:
                logger.error(f"Error fetching readme for {owner}/{repo}: {e}")

            try:
                commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
                resp = await client.get(commits_url, headers=headers)
                if resp.status_code == 200:
                    commits = resp.json()
                    if commits and isinstance(commits, list) and len(commits) > 0:
                        commit_date_str = commits[0].get("commit", {}).get("committer", {}).get("date")
                        details["last_commit_date"] = commit_date_str
            except Exception as e:
                logger.error(f"Error fetching commits for {owner}/{repo}: {e}")

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
                logger.error(f"Error fetching issues for {owner}/{repo}: {e}")

        return details

    def calculate_abandonment_score(self, item: dict[str, Any], last_commit_date: str | None) -> float:
        return calculate_abandonment_score(item, last_commit_date)

    async def search_failure_context(self, repo_name: str, tech_stack_str: str) -> str | None:
        if not self.tavily_token or self.tavily_token.startswith("your_"):
            return "Web search skipped (Tavily API key not configured)."

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_token)
            query = f"why {repo_name} {tech_stack_str} project abandoned postmortem issues challenges"

            def _search():
                return client.search(query=query, max_results=3, search_depth="basic")

            response = await asyncio.wait_for(asyncio.to_thread(_search), timeout=10.0)
            results = response.get("results", [])
            if not results:
                return None

            snippets = []
            for r in results[:3]:
                title = r.get("title", "")
                content = r.get("content", "")
                snippets.append(f"• [{title}]: {content[:250]}")

            return "\n".join(snippets)
        except Exception as e:
            logger.error(f"Tavily search error for {repo_name}: {e}")
            return None

# For backward compatibility if imported directly
search_repositories = GitHubService().search_repositories
fetch_repo_details = GitHubService().fetch_repo_details
