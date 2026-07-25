import json
from typing import Any

from services.analyzer import get_openai_client


async def generate_project_roadmap(project_name: str, description: str, tech_stack: list[str]) -> list[dict[str, Any]]:
    """
    Generates a structured 5-phase project implementation roadmap.
    """
    client = get_openai_client()
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
            res = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior technical architect. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content)
            return data.get("phases", [])
        except Exception as e:
            print(f"Roadmap LLM error: {e}")

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
