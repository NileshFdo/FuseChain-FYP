from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_PREFIX, CORS_ORIGINS
from app.routers import risk_router
from app.services import data_service, ml_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("Backend Starting...")
    print("=" * 60)
    
    # Pre-load datasets and the ML model into memory upon startup
    data_service.load_data()
    ml_service.load_model()
    
    print("=" * 60)
    print("Backend Ready!")
    print("=" * 60)
    
    yield

    print("Shutting Down...")


app = FastAPI(
    title="FuseChain API",
    description="Ethereum Address-Level Scam Classification",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the risk assessment routes
app.include_router(risk_router, prefix=API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint to acknowledge API is running and provide links."""
    return {
        "name": "FuseChain API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint for monitoring."""
    return {"status": "healthy"}
