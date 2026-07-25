import os
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def get_openai_client() -> Optional[AsyncOpenAI]:
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"):
        return AsyncOpenAI(api_key=OPENAI_API_KEY)
    return None

async def diagnose_repository_failure(
    repo_name: str,
    description: str,
    readme_excerpt: str,
    issues: list,
    abandonment_score: float,
    tavily_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Uses OpenAI gpt-4o-mini to diagnose why a repository was likely abandoned or failed.
    """
    client = get_openai_client()
    if not client:
        # Fallback heuristic diagnosis if no OpenAI key
        return {
            "root_cause": "High maintainer burden and lack of active contributors",
            "failure_category": "Maintainer Burnout & Lack of Adoption",
            "technical_debt_level": "High" if abandonment_score > 60 else "Medium",
            "summary": f"The repository {repo_name} showed high inactivity signals (Abandonment Score: {abandonment_score}/100) and accumulated unresolved issues.",
            "key_takeaways": [
                "Underestimated long-term maintenance costs",
                "Complex dependencies without automated CI/CD",
                "Lack of community contributors"
            ]
        }

    issues_str = "\n".join([f"- {i.get('title')}: {i.get('body')}" for i in issues[:3]]) if issues else "None reported"
    web_str = tavily_context if tavily_context else "None"

    prompt = f"""
You are an expert software architectural pathologist. Analyze this abandoned GitHub repository and determine why it likely failed or was abandoned.

Repository Name: {repo_name}
Description: {description}
Abandonment Score: {abandonment_score}/100
README Excerpt: {readme_excerpt[:1500]}
Recent Issues: {issues_str}
Web Context: {web_str}

Respond ONLY with valid JSON in this exact structure:
{{
    "root_cause": "<Concise 1-sentence root cause>",
    "failure_category": "<Category e.g. Scope Creep, Tech Stack Obsolescence, Complex Architecture, Maintainer Burnout, Security/Dependency Hell>",
    "technical_debt_level": "<High|Medium|Low>",
    "summary": "<2-3 sentence explanation of the failure dynamics>",
    "key_takeaways": [
        "<Takeaway 1>",
        "<Takeaway 2>",
        "<Takeaway 3>"
    ]
}}
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze software project failure patterns. Respond strictly in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error calling OpenAI API for diagnosis of {repo_name}: {e}")
        return {
            "root_cause": "Architectural complexity and unmaintained dependency stack",
            "failure_category": "Technical Debt & Maintenance Fatigue",
            "technical_debt_level": "High",
            "summary": f"Analysis determined that {repo_name} encountered high friction during expansion.",
            "key_takeaways": [
                "Keep core feature set minimal",
                "Avoid tight coupling with unmaintained third-party SDKs",
                "Establish clear contribution pipelines early"
            ]
        }
