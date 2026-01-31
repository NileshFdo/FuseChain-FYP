# FuseChain Deployment Guide

This guide will help you deploy the FuseChain application for free using **Render** (Backend) and **Vercel** (Frontend).

## Prerequisites
- A GitHub account.
- Your code pushed to a GitHub repository.

---

## Part 1: Backend Deployment (Render)
We will deploy the backend as a Docker container.

1.  **Sign Up/Login**: Go to [render.com](https://render.com/) and log in with GitHub.
2.  **New Web Service**: Click **New +** -> **Web Service**.
3.  **Connect Repo**: Select your `FuseChain` repository.
4.  **Configure**:
    - **Name**: `fusechain-backend` (or similar)
    - **Language**: Docker
    - **Region**: Choose one close to you (e.g., Singapore, Frankfurt).
    - **Branch**: `main` (or your working branch).
    - **Instance Type**: **Free**
5.  **Environment Variables**:
    - Not strictl required unless you have API keys (e.g., if you added external APIs later).
6.  **Deploy**: Click **Create Web Service**.

> **Note**: The first build might take a few minutes. Once done, Render will give you a URL like `https://fusechain-backend.onrender.com`. **Copy this URL.**

---

## Part 2: Frontend Deployment (Vercel)
We will deploy the React frontend.

1.  **Sign Up/Login**: Go to [vercel.com](https://vercel.com/) and log in with GitHub.
2.  **Add New Project**: Click **Add New...** -> **Project**.
3.  **Import Repo**: Import your `FuseChain` repository.
4.  **Configure Project**:
    - **Framework Preset**: Vite (should detect automatically).
    - **Root Directory**: Click `Edit` and select `frontend`. **(Important!)**
5.  **Environment Variables**:
    - Expand the **Environment Variables** section.
    - Key: `VITE_API_URL`
    - Value: `https://fusechain-backend.onrender.com/api` (The URL you copied from Render + `/api`)
6.  **Deploy**: Click **Deploy**.

---

## Verification
1.  Open your new Vercel URL (e.g., `https://fusechain.vercel.app`).
2.  Try scanning an address.
3.  If it fails, check the **Console** (F12) for errors.
    - If you see `CORS` errors, you might need to update `backend/app/config.py` to include your Vercel domain in `CORS_ORIGINS` and redeploy the backend.

### Tips for Free Tier
- **Cold Starts**: Render's free tier sleeps after 15 mins. The first request might take ~50 seconds.
- **RAM Usage**: If the backend crashes, it might be running out of memory (512MB limit).
