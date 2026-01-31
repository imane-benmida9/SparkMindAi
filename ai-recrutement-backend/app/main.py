from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logger import setup_logging

from app.api.auth import router as auth_router
from app.api.cv import router as cv_router
from app.api.offres import router as offres_router
from app.api.candidats import router as candidats_router
from app.api.candidatures import router as candidatures_router
from app.api.matching import router as matching_router
from app.api.dashboard_api import router as dashboard_router
# -------------------------------------------------
# Setup logging
# -------------------------------------------------
setup_logging()

# -------------------------------------------------
# Create FastAPI app
# -------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI-powered recruitment platform API"
)

# -------------------------------------------------
# CORS configuration
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Root route (pour éviter le 404 sur /)
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API AI Recruitment"}

# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# -------------------------------------------------
# API Routers
# -------------------------------------------------
app.include_router(auth_router)
app.include_router(cv_router)          # ✅ AJOUT
app.include_router(offres_router)      # ✅ AJOUT
app.include_router(candidats_router)
app.include_router(candidatures_router)
app.include_router(matching_router)
app.include_router(dashboard_router)
