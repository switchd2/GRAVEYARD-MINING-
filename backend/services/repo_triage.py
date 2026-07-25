from datetime import datetime, timezone
from typing import Any


def calculate_abandonment_score(repo_data: dict[str, Any], last_commit_date_str: str = None) -> float:
    """
    Calculates Abandonment Score from 0.0 (active/healthy) to 100.0 (completely abandoned/dead).
    """
    score = 0.0

    # 1. Is Archived check
    if repo_data.get("archived", False):
        score += 30.0

    # 2. Last commit age calculation
    last_date = None
    if last_commit_date_str:
        try:
            last_date = datetime.fromisoformat(last_commit_date_str.replace("Z", "+00:00"))
        except Exception:
            pass

    if not last_date:
        pushed_at = repo_data.get("pushed_at") or repo_data.get("updated_at")
        if pushed_at:
            try:
                last_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            except Exception:
                pass

    if last_date:
        now = datetime.now(timezone.utc)
        days_inactive = (now - last_date).days
        if days_inactive > 730: # > 2 years
            score += 45.0
        elif days_inactive > 365: # > 1 year
            score += 35.0
        elif days_inactive > 180: # > 6 months
            score += 20.0
        elif days_inactive > 90:
            score += 10.0
    else:
        score += 25.0 # Unknown date default penalty

    # 3. Issue backlog ratio vs stars
    open_issues = repo_data.get("open_issues_count", 0)
    stars = repo_data.get("stargazers_count", 1)
    if open_issues > 20 and open_issues / max(stars, 1) > 0.3:
        score += 15.0
    elif open_issues > 10:
        score += 10.0

    # 4. Lack of description / license / maintenance indicators
    if not repo_data.get("license"):
        score += 5.0
    if not repo_data.get("description"):
        score += 5.0

    return min(round(score, 1), 100.0)
