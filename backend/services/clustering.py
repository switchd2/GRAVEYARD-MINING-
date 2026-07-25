import numpy as np
from typing import List, Dict, Any
from sklearn.cluster import KMeans
from services.analyzer import get_openai_client
import json

async def cluster_diagnoses(diagnoses_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Groups repository diagnoses into failure clusters based on embedding vectors & categories.
    Returns list of failure cluster dictionaries.
    """
    if not diagnoses_data:
        return []

    if len(diagnoses_data) <= 2:
        # Not enough data to cluster, group into 1 cluster
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
    
    clusters_dict: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(n_clusters)}

    if embeddings and len(embeddings) >= n_clusters:
        try:
            X = np.array(embeddings)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            for idx, label in enumerate(labels):
                clusters_dict[int(label)].append(valid_diagnoses[idx])
        except Exception as e:
            print(f"KMeans clustering failed, falling back to category grouping: {e}")
            for idx, item in enumerate(valid_diagnoses):
                clusters_dict[idx % n_clusters].append(item)
    else:
        for idx, item in enumerate(valid_diagnoses):
            clusters_dict[idx % n_clusters].append(item)

    # Summarize each cluster
    client = get_openai_client()
    result_clusters = []

    for cluster_id, items in clusters_dict.items():
        if not items:
            continue

        affected_repos = [i["repo_name"] for i in items]
        causes = [i["diagnosis"].get("root_cause", "") for i in items]
        categories = [i["diagnosis"].get("failure_category", "") for i in items]

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
                res = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "You are a software failure analyst. Respond in JSON."},
                              {"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                parsed = json.loads(res.choices[0].message.content)
                result_clusters.append({
                    "cluster_name": parsed.get("cluster_name", categories[0] if categories else "Architecture Strain"),
                    "description": parsed.get("description", "Projects encountered friction in state management and maintainer velocity."),
                    "repo_count": len(affected_repos),
                    "risk_level": parsed.get("risk_level", "HIGH"),
                    "affected_repos": affected_repos
                })
                continue
            except Exception as e:
                print(f"Cluster summary error: {e}")

        # Fallback cluster summary
        main_cat = categories[0] if categories else "Technical Debt Accumulation"
        result_clusters.append({
            "cluster_name": f"{main_cat} Pattern",
            "description": f"Common failure signals observed across {', '.join(affected_repos)}.",
            "repo_count": len(affected_repos),
            "risk_level": "HIGH",
            "affected_repos": affected_repos
        })

    return result_clusters
