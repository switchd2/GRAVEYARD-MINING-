import asyncio
import hashlib
import json
import os
from typing import Any

from dotenv import load_dotenv
from logging_config import get_logger
from openai import AsyncOpenAI

load_dotenv()
logger = get_logger("AIService")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class AIService:
    def __init__(self):
        self.api_key = OPENAI_API_KEY

    def _get_client(self) -> AsyncOpenAI | None:
        if self.api_key and not self.api_key.startswith("your_"):
            return AsyncOpenAI(api_key=self.api_key)
        return None

    async def diagnose_repository_failure(
        self,
        repo_name: str,
        description: str,
        readme_excerpt: str,
        issues: list,
        abandonment_score: float,
        tavily_context: str | None = None
    ) -> dict[str, Any]:
        """
        Uses OpenAI gpt-4o-mini to diagnose why a repository was likely abandoned or failed.
        """
        client = self._get_client()
        if not client:
            logger.info(f"OpenAI key missing/placeholder. Using heuristic diagnosis for {repo_name}.")
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
            async def _call():
                return await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You analyze software project failure patterns. Respond strictly in valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

            response = await asyncio.wait_for(_call(), timeout=30.0)
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error calling OpenAI API for diagnosis of {repo_name}: {e}")
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

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generates text embedding vector using OpenAI text-embedding-3-small (1536 dims).
        Falls back to simple hash-based pseudo-vector if API call fails or key is missing.
        """
        client = self._get_client()
        if client:
            try:
                async def _call():
                    return await client.embeddings.create(
                        model="text-embedding-3-small",
                        input=text.replace("\n", " ")
                    )
                resp = await asyncio.wait_for(_call(), timeout=10.0)
                return resp.data[0].embedding
            except Exception as e:
                logger.error(f"Error generating OpenAI embedding: {e}")

        # Fallback deterministic pseudo-vector generator (128 dims)
        vec = []
        for i in range(128):
            h = hashlib.md5(f"{text}_{i}".encode()).hexdigest()
            val = (int(h[:4], 16) / 65535.0) * 2.0 - 1.0
            vec.append(round(val, 4))
        return vec

    async def summarize_cluster(self, affected_repos: list[str], categories: list[str], causes: list[str]) -> dict[str, Any]:
        """
        Summarizes a cluster of diagnoses into a cohesive failure cluster title and description.
        """
        client = self._get_client()
        if client:
            prompt = f"""
Synthesize these repository failure diagnoses into a single cohesive failure cluster title and description.

Affected Repositories: {', '.join(affected_repos)}
Failure Categories: {', '.join(categories)}
Root Causes:
{"".join([f'- {c}' for c in causes])}

Respond ONLY with valid JSON:
{{
    "cluster_name": "<Catchy 3-5 word cluster title e.g. Monolithic Complexity & State Inflation>",
    "description": "<2-sentence explanation of why projects in this cluster failed>",
    "risk_level": "<CRITICAL|HIGH|MEDIUM>"
}}
"""
            try:
                async def _call():
                    return await client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a software failure analyst. Respond in JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                res = await asyncio.wait_for(_call(), timeout=20.0)
                return json.loads(res.choices[0].message.content)
            except Exception as e:
                logger.error(f"Cluster summary LLM error: {e}")

        main_cat = categories[0] if categories else "Technical Debt Accumulation"
        return {
            "cluster_name": f"{main_cat} Pattern",
            "description": f"Common failure signals observed across {', '.join(affected_repos)}.",
            "risk_level": "HIGH"
        }

    async def generate_roadmap(self, project_name: str, description: str, tech_stack: list[str]) -> list[dict[str, Any]]:
        """
        Generates a structured 5-phase project implementation roadmap.
        """
        client = self._get_client()
        stack_str = ", ".join(tech_stack)

        if client:
            prompt = f"""
Generate a structured 5-phase software development roadmap for a project named "{project_name}".
Project Description: {description}
Tech Stack: {stack_str}

Return ONLY valid JSON matching this exact structure:
{{
    "phases": [
        {{
            "phase_number": 1,
            "title": "<Phase Title e.g. Core Architecture & Auth Setup>",
            "description": "<Phase Description>",
            "estimated_duration": "<e.g. 2 Weeks>",
            "key_deliverables": [
                "<Deliverable 1>",
                "<Deliverable 2>",
                "<Deliverable 3>"
            ],
            "risk_checkpoints": []
        }},
        ... (repeat for 5 phases)
    ]
}}
"""
            try:
                async def _call():
                    return await client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a senior technical architect. Output valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        response_format={"type": "json_object"}
                    )
                res = await asyncio.wait_for(_call(), timeout=45.0)
                data = json.loads(res.choices[0].message.content)
                return data.get("phases", [])
            except Exception as e:
                logger.error(f"Roadmap LLM error: {e}")

        # Fallback default 5-phase roadmap
        return [
            {
                "phase_number": 1,
                "title": "Architecture Setup & Core Foundation",
                "description": f"Establish repository structure, database schema, and initial {stack_str} boilerplate.",
                "estimated_duration": "1-2 Weeks",
                "key_deliverables": ["Project repository initialized", "Database migrations configured", "CI/CD baseline pipeline"],
                "risk_checkpoints": []
            },
            {
                "phase_number": 2,
                "title": "MVP Feature Core & Integration",
                "description": "Implement essential user flows, backend API endpoints, and database handlers.",
                "estimated_duration": "2-3 Weeks",
                "key_deliverables": ["Core backend endpoints live", "Frontend components connected", "Authentication flow"],
                "risk_checkpoints": []
            },
            {
                "phase_number": 3,
                "title": "State Management & Performance Optimization",
                "description": "Refactor state handling, add caching layers, and stress test system boundaries.",
                "estimated_duration": "2 Weeks",
                "key_deliverables": ["Caching layer integrated", "Async worker pool", "State synchronization"],
                "risk_checkpoints": []
            },
            {
                "phase_number": 4,
                "title": "Security, Monitoring & Dependency Audit",
                "description": "Audit third-party dependencies, add rate limiting, logging, and error tracking.",
                "estimated_duration": "1 Week",
                "key_deliverables": ["Snyk security audit passed", "Structured log aggregators", "API rate limiters"],
                "risk_checkpoints": []
            },
            {
                "phase_number": 5,
                "title": "Beta Deployment & Maintenance Pipeline",
                "description": "Deploy to cloud infrastructure with automated monitoring and community contribution guidelines.",
                "estimated_duration": "1-2 Weeks",
                "key_deliverables": ["Production deployment", "Monitoring dashboards", "Open source contributor guidelines"],
                "risk_checkpoints": []
            }
        ]
