from app.ai.moteur_matching import generate_matching_and_explanation

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

def fake_ia_explainer(prompt: str) -> str:
    return f"[FAKE IA] Explication générée pour le prompt :\n{prompt}"

result = generate_matching_and_explanation(candidate, job, ia_explainer=fake_ia_explainer)
print(result.model_dump_json(indent=2))
