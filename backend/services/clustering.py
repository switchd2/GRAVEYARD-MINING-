from typing import Any

import numpy as np
from logging_config import get_logger
from services.ai_service import AIService
from sklearn.cluster import KMeans

logger = get_logger("Clustering")

async def cluster_diagnoses(diagnoses_data: list[dict[str, Any]], ai_service: AIService | None = None) -> list[dict[str, Any]]:
    """
    Groups repository diagnoses into failure clusters based on embedding vectors & categories.
    Returns list of failure cluster dictionaries.
    """
    ai = ai_service or AIService()

    if not diagnoses_data:
        return []

    if len(diagnoses_data) <= 2:
        repos = [d["repo_name"] for d in diagnoses_data]
        categories = list(set([d["diagnosis"].get("failure_category", "Scope Creep") for d in diagnoses_data]))
        return [{
            "cluster_name": categories[0] if categories else "General Architecture Bottlenecks",
            "description": f"Failure signals identified across {', '.join(repos)}.",
            "repo_count": len(repos),
            "risk_level": "HIGH",
            "affected_repos": repos
        }]

    # Extract vectors
    embeddings = []
    valid_diagnoses = []
    for d in diagnoses_data:
        emb = d.get("diagnosis", {}).get("embedding")
        if emb:
            embeddings.append(emb)
            valid_diagnoses.append(d)

    if not embeddings:
        valid_diagnoses = diagnoses_data

    n_clusters = min(3, len(valid_diagnoses))
    clusters_dict: dict[int, list[dict[str, Any]]] = {i: [] for i in range(n_clusters)}

    if embeddings and len(embeddings) >= n_clusters:
        try:
            X = np.array(embeddings)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            for idx, label in enumerate(labels):
                clusters_dict[int(label)].append(valid_diagnoses[idx])
        except Exception as e:
            logger.error(f"KMeans clustering failed, falling back to category grouping: {e}")
            for idx, item in enumerate(valid_diagnoses):
                clusters_dict[idx % n_clusters].append(item)
    else:
        for idx, item in enumerate(valid_diagnoses):
            clusters_dict[idx % n_clusters].append(item)

    result_clusters = []

    for cluster_id, items in clusters_dict.items():
        if not items:
            continue

        affected_repos = [i["repo_name"] for i in items]
        causes = [i["diagnosis"].get("root_cause", "") for i in items]
        categories = [i["diagnosis"].get("failure_category", "") for i in items]

        summary = await ai.summarize_cluster(affected_repos, categories, causes)
        result_clusters.append({
            "cluster_name": summary.get("cluster_name", categories[0] if categories else "Architecture Strain"),
            "description": summary.get("description", "Projects encountered friction in state management and maintainer velocity."),
            "repo_count": len(affected_repos),
            "risk_level": summary.get("risk_level", "HIGH"),
            "affected_repos": affected_repos
        })

    return result_clusters
