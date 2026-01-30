from typing import List
import os
from sentence_transformers import SentenceTransformer

# Réduire la verbosité des logs Transformers (évite warnings non critiques)
try:
    from transformers import logging as transformers_logging
    transformers_logging.set_verbosity_error()
except Exception:
    # transformers peut ne pas être importé dans certains environnements
    pass


# Si l'utilisateur a fourni un token HF, l'utiliser pour les téléchargements
_hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
if _hf_token:
    # Assurer que huggingface_hub trouve le token via variable d'env standard
    os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", _hf_token)

# Modèle local (1 seule instance)
# On passe `use_auth_token` si disponible pour éviter l'avertissement HF Hub
model_kwargs = {}
if _hf_token:
    model_kwargs["use_auth_token"] = _hf_token

model = SentenceTransformer("all-MiniLM-L6-v2", **model_kwargs)


def embed_text(text: str) -> List[float]:
    """Génère l'embedding d'un seul texte (LOCAL)"""
    if not text or not text.strip():
        raise ValueError("Texte vide pour embedding")

    return model.encode(text).tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Génère les embeddings pour plusieurs textes (LOCAL)"""
    if not texts:
        return []

    return model.encode(texts).tolist()
