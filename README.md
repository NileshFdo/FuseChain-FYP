---
title: my-backend
sdk: docker
app_port: 7860
---

# FuseChain: Multimodal Ethereum Scam Classification System

FuseChain is a supervised scam classification system that fuses on-chain Ethereum transaction features with off-chain contextual signals market dynamics, Reddit sentiment, and Twitter engagement to classify EOA addresses as scam or normal.

Unlike conventional on-chain-only approaches, FuseChain operates at the **address level**, aggregating a behavioural profile across each EOA's full transaction history and the prevailing off-chain conditions during its operational period.

## Project Architecture

This repository operates on three decoupled components:
1. **Backend (FastAPI)**: Serves the XGBoost classifier via REST API endpoints, with pre-loaded feature caches for zero-latency inference and SHAP-based explainability.
2. **Frontend (React + Tailwind)**: Interactive dashboard for analysts to visualise risk scores, SHAP feature contributions, narrative explanations, and batch analysis results.
3. **ML Pipeline**: Seven-notebook pipeline that processes raw data through temporal alignment, address-level aggregation, SHAP feature selection, and model training.

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

## Dataset

The FuseChain dataset used to train this model is publicly available on Hugging Face:

[FuseChain Multimodal Ethereum Fraud Dataset](https://huggingface.co/datasets/Nileshka/fusechain-data)


## Model

The FuseChain model is publicly available on Hugging Face:

[FuseChain Model Repository](https://huggingface.co/Nileshka/fusechain-model)
