import os
import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings


def _persist_dir() -> str:
    """
    Dossier où Chroma stocke ses données (persistant).
    On le résout en chemin absolu pour éviter les surprises.
    """
    base = os.path.abspath(os.getcwd())
    path = os.path.abspath(os.path.join(base, settings.CHROMA_PERSIST_DIR))
    os.makedirs(path, exist_ok=True)
    return path


# Embedding local (pas de clé, pas de quota)
_embedding_fn = embedding_functions.DefaultEmbeddingFunction()


def get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=_persist_dir())


def get_collection(name: str):
    """
    Récupère ou crée une collection Chroma (cvs / offres).
    """
    client = get_client()
    return client.get_or_create_collection(
        name=name,
        embedding_function=_embedding_fn,
    )
