from app.ai.embeddings import embed_text

vec = embed_text("Développeur Python avec 3 ans d'expérience en FastAPI")
print("Embedding length:", len(vec))
print("First 5 values:", vec[:5])
