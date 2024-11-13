from fastapi import APIRouter

from app.api.endpoints.biochat import biochat_router

api_router = APIRouter()

api_router.include_router(biochat_router, tags=["Ingestion and Retrieval"])
