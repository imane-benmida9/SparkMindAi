import json
from typing import Any, Dict, Optional, Union

from app.core.config import settings
from app.vector_store.chroma_client import get_collection
from app.vector_store.text_builders import build_cv_text, build_offer_text


def index_cv_from_json(
    cv_id: str,
    cv_json: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
):
    col = get_collection(settings.CHROMA_COLLECTION_CVS)
    doc = build_cv_text(cv_json)

    md = metadata or {}
    md.setdefault("type", "cv")

    col.upsert(
        ids=[cv_id],
        documents=[doc],
        metadatas=[md],
    )


def index_offer(
    offer_id: str,
    offer: Union[Dict[str, Any], str],
    metadata: Optional[Dict[str, Any]] = None
):
    col = get_collection(settings.CHROMA_COLLECTION_OFFRES)
    doc = build_offer_text(offer)

    md = metadata or {}
    md.setdefault("type", "offre")

    col.upsert(
        ids=[offer_id],
        documents=[doc],
        metadatas=[md],
    )


def search_cvs_for_offer(offer: Union[Dict[str, Any], str], top_k: int = 10):
    col = get_collection(settings.CHROMA_COLLECTION_CVS)
    query_text = build_offer_text(offer)

    return col.query(
        query_texts=[query_text],
        n_results=top_k,
        include=["metadatas", "distances", "documents"],
    )


def search_offres_for_cv(cv_json: Dict[str, Any], top_k: int = 10):
    col = get_collection(settings.CHROMA_COLLECTION_OFFRES)
    query_text = build_cv_text(cv_json)

    return col.query(
        query_texts=[query_text],
        n_results=top_k,
        include=["metadatas", "distances", "documents"],
    )


def load_json_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
