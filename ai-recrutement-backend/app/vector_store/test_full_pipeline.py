import os
from app.vector_store.indexing import load_json_file, index_cv_from_json, index_offer, search_cvs_for_offer

def main():
    base = os.path.abspath(os.getcwd())
    cv_dir = os.path.join(base, "app", "cv_extraits")

    files = [f for f in os.listdir(cv_dir) if f.lower().endswith(".json")]
    if not files:
        raise RuntimeError("Aucun JSON trouvé dans app/cv_extraits")

    # Indexer plusieurs CV (jusqu'à 5)
    for i, filename in enumerate(files[:5], start=1):
        path = os.path.join(cv_dir, filename)
        cv_json = load_json_file(path)
        index_cv_from_json(
            cv_id=f"cv_{i}",
            cv_json=cv_json,
            metadata={"source_file": filename}
        )

    # Indexer 1 offre (optionnel, mais utile)
    offer_text = "Backend Python FastAPI PostgreSQL, authentification JWT, API REST, SQLAlchemy."
    index_offer("offre_1", offer_text, metadata={"titre": "Backend Python"})

    # Rechercher Top-N CV pour cette offre
    res = search_cvs_for_offer(offer_text, top_k=3)

    print("=== TOP 3 CVS POUR L'OFFRE ===")
    print(res)

if __name__ == "__main__":
    main()
