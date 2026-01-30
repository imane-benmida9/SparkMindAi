from typing import Dict, Any, List, Union


def _join_list(values: List[Any]) -> str:
    items = []
    for v in values:
        if isinstance(v, str) and v.strip():
            items.append(v.strip())
    return ", ".join(items)


def build_cv_text(cv_json: Dict[str, Any]) -> str:
    """
    Convertit le JSON CV (issu du membre 3) en texte optimisé pour embeddings.
    """
    parts: List[str] = []

    # Profil / Résumé
    profil = cv_json.get("profil") or cv_json.get("resume") or cv_json.get("summary")
    if isinstance(profil, str) and profil.strip():
        parts.append(f"Profil: {profil.strip()}")

    # Titre / Poste
    titre = cv_json.get("titre") or cv_json.get("poste") or cv_json.get("headline")
    if isinstance(titre, str) and titre.strip():
        parts.append(f"Titre: {titre.strip()}")

    # Compétences
    skills = cv_json.get("competences") or cv_json.get("skills") or []
    if isinstance(skills, list):
        s = _join_list(skills)
        if s:
            parts.append(f"Compétences: {s}")

    # Expériences
    exps = cv_json.get("experiences") or cv_json.get("experience") or []
    if isinstance(exps, list):
        for e in exps[:8]:
            if not isinstance(e, dict):
                continue
            poste = e.get("poste") or e.get("title") or ""
            entreprise = e.get("entreprise") or e.get("company") or ""
            missions = e.get("missions") or e.get("description") or ""
            techs = e.get("technos") or e.get("technologies") or e.get("skills") or []

            line = []
            if poste: line.append(str(poste).strip())
            if entreprise: line.append(str(entreprise).strip())
            if isinstance(missions, str) and missions.strip():
                line.append(missions.strip())
            if isinstance(techs, list):
                t = _join_list(techs)
                if t:
                    line.append(f"Tech: {t}")

            if line:
                parts.append("Expérience: " + " | ".join(line))

    # Éducation / Formation
    edu = cv_json.get("education") or cv_json.get("formations") or []
    if isinstance(edu, list):
        for f in edu[:5]:
            if not isinstance(f, dict):
                continue
            diplome = f.get("diplome") or f.get("degree") or ""
            ecole = f.get("ecole") or f.get("school") or ""
            if diplome or ecole:
                parts.append(f"Formation: {str(diplome).strip()} {str(ecole).strip()}".strip())

    return "\n".join(parts).strip()


def build_offer_text(offer: Union[Dict[str, Any], str]) -> str:
    """
    Convertit une offre (dict ou texte) en texte optimisé pour embeddings.
    """
    if isinstance(offer, str):
        return offer.strip()

    parts: List[str] = []
    titre = offer.get("titre") or offer.get("title")
    desc = offer.get("description") or offer.get("desc")
    skills = offer.get("competences") or offer.get("skills") or []

    if isinstance(titre, str) and titre.strip():
        parts.append(f"Titre: {titre.strip()}")
    if isinstance(desc, str) and desc.strip():
        parts.append(desc.strip())
    if isinstance(skills, list):
        s = _join_list(skills)
        if s:
            parts.append(f"Compétences requises: {s}")

    return "\n".join(parts).strip()
