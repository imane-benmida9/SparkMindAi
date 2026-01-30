import os
from app.ai.moteur_matching import generate_matching_and_explanation
import json

def map_cv_json_to_candidate(cv_json):
    # Compétences
    skills = cv_json.get("competences", [])
    # Expérience : nombre d'années ou 1 si au moins une expérience
    experiences = cv_json.get("experiences", [])
    experience_years = len(experiences)
    # Éducation : prend le diplôme du premier élément
    formations = cv_json.get("formations", [])
    education = formations[0]["diplome"] if formations and "diplome" in formations[0] else ""
    return {
        "id": 0,
        "skills": skills,
        "experience": experience_years,
        "education": education.lower()
    }

cv_path = os.path.join(os.path.dirname(__file__), "cv_extraits", "CV_SANS_PHOTO_20260124_133454.json")
with open(cv_path, "r", encoding="utf-8") as f:
    cv_json = json.load(f)

candidate = map_cv_json_to_candidate(cv_json)

job_json = {
    "id": 101,
    "skills": ["Python", "SQL", "Docker"],
    "experience": 2,
    "education": "master"
}

shortlist = [candidate]

for cand in shortlist:
    result = generate_matching_and_explanation(cand, job_json)
    print(result.model_dump_json(indent=2))
