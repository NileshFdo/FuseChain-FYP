# FuseChain: Multimodal Crypto Fraud Detection System 🛡️

FuseChain is an advanced AI system combining on-chain transaction analysis, market data, and social sentiment to detect fraudulent Ethereum addresses.

## Project Overview

This repo contains three main components:
1.  **Backend (FastAPI)**: Serves the ML model via REST API endpoints.
2.  **Frontend (React + Tailwind)**: Interactive dashboard for analysts to visualize risk scores and explanations.
3.  **ML Pipeline**: Notebooks and scripts for data processing, feature engineering, and model training.

## Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python run.py
# Server runs at http://localhost:8000
# API Docs at http://localhost:8000/docs
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Dashboard runs at http://localhost:5173
```

### 3. ML Environment

```bash
cd ml_pipeline
pip install -r requirements.txt
jupyter lab
```

## Model Architecture

The core model is an **XGBoost Classifier** trained on:
*   **On-Chain Features**: Transaction frequency, volume, unique peers.
*   **Market data**: Price volatility, market cap trends during activity periods.
*   **Social Signals**: Sentiment analysis from r/ethereum discussions.

Key performance metrics:
*   **Accuracy**: ~75.4%
*   **AUC-ROC**: 0.83
