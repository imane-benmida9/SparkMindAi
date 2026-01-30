from app.services.matching_service import match_candidate_to_job

# Exemple de données fictives
candidate = {
    "id": 1,
    "skills": ["Python", "FastAPI", "SQL"],
    "experience": 3,
    "education": "master"
}

job = {
    "id": 101,
    "skills": ["Python", "SQL", "Docker"],
    "experience": 2,
    "education": "master"
}

result = match_candidate_to_job(candidate, job)
# Utilise la méthode recommandée par Pydantic v2
print(result.model_dump_json(indent=2))