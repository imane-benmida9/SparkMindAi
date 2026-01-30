from app.utils.scoring import WEIGHTS, THRESHOLDS
from app.utils.scoring import compute_matching_score
from app.schemas.matching import MatchResponse

def compute_final_score(details: dict) -> float:
    return round(sum(details[k] * WEIGHTS[k] for k in details), 2)

def get_decision(score: float) -> str:
    if score >= THRESHOLDS["excellent"]:
        return "Excellent match"
    elif score >= THRESHOLDS["good"]:
        return "Good match"
    elif score >= THRESHOLDS["average"]:
        return "Average match"
    return "Low match"

def match_candidate_to_job(candidate: dict, job: dict) -> MatchResponse:
    """
    Calcule le matching, la décision et prépare la réponse complète pour l'API.
    """
    result = compute_matching_score(candidate, job)
    return MatchResponse(
        candidate_id=candidate.get('id', 0),
        job_id=job.get('id', 0),
        final_score=result['final_score'],
        details=result['details'],
        decision=result['decision'],
        explanation=""  # À remplir par l'IA ou une fonction d'explication
    )
