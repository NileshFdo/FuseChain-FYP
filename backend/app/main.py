"""
FuseChain Backend - FastAPI Application
Ethereum Wallet Anomaly Detection API
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_PREFIX, CORS_ORIGINS
from app.routers import risk_router
from app.services import data_service, ml_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - load models and data on startup"""
    print("=" * 60)
    print("FuseChain Backend Starting...")
    print("=" * 60)
    
    # Load data
    data_service.load_data()
    
    # Load ML model
    ml_service.load_model()
    
    print("=" * 60)
    print("FuseChain Backend Ready!")
    print("=" * 60)
    
    yield
    
    # Cleanup on shutdown
    print("FuseChain Backend Shutting Down...")


# Create FastAPI app
app = FastAPI(
    title="FuseChain API",
    description="Ethereum Wallet Anomaly Detection using XGBoost with On-chain and Off-chain Features",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(risk_router, prefix=API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "FuseChain API",
        "version": "1.0.0",
        "description": "Ethereum Wallet Anomaly Detection",
        "docs": "/docs",
        "endpoints": {
            "risk_assess": f"{API_PREFIX}/risk/assess",
            "available_dates": f"{API_PREFIX}/risk/available-dates",
            "scan_date": f"{API_PREFIX}/risk/scan-date/{{date}}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
