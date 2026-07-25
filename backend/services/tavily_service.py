import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

async def search_failure_context(repo_name: str, tech_stack_str: str) -> str | None:
    """
    Queries Tavily web search for post-mortems, discussions, or failure reasons related to the technology/repo pattern.
    """
    if not TAVILY_API_KEY or TAVILY_API_KEY.startswith("your_"):
        return "Web search skipped (Tavily API key not configured)."

    try:
        # pyrefly: ignore [missing-import]
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        query = f"why {repo_name} {tech_stack_str} project abandoned postmortem issues challenges"
        response = client.search(query=query, max_results=3, search_depth="basic")
        
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
        print(f"Tavily search error for {repo_name}: {e}")
        return None
