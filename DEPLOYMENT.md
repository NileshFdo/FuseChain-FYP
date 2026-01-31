# FuseChain Deployment Guide

This guide will help you deploy the FuseChain application for free.

> [!TIP]
> **Best Free Combo (No Credit Card):**
> **Backend check:** Hugging Face Spaces (Free CPU tier)
> **Frontend:** Vercel (Free tier)

## Prerequisites
- A GitHub account.
- Your code pushed to a GitHub repository.

---

## Part 1: Backend Deployment (Hugging Face Spaces)
This is the best option for free ML hosting (no credit card required).

1.  **Sign Up**: Go to [huggingface.co](https://huggingface.co/) and create an account.
2.  **Create New Space**: Click **New Space** (top right).
3.  **Configure**:
    - **Name**: `fusechain-backend` (or similar)
    - **License**: MIT (optional)
    - **SDK**: **Docker** (Select Docker, then "Blank" or "Streamlit" doesn't matter as we use our own Dockerfile).
    - **Space Hardware**: **CPU Basic (Free)**.
    - **Visibility**: **Public**.
4.  **Connect Repo**:
    - You can't directly "link" a repo like Render. Instead, Hugging Face gives you a git repo for your Space.
    - **Easiest Way:** Use the "Sync with GitHub" feature in settings, OR manually push your files to the Hugging Face repo.
    - **Recommended:** In your Space, go to **Settings** -> **git repository**. Add your SSH key or use the HTTPS URL to push your code there.
    - Or, simpler: Copy the contents of your `Dockerfile` and `Run` command into the web editor if needed, but pushing code is better.
    
    **Wait! The easiest way for you:**
    1. Go to your Space.
    2. Click **Files** -> **Add file** -> **Upload files**.
    3. Drag and drop your **PROJECT FOLDER** (minus `node_modules` and `.git`).
    4. Ensure `Dockerfile` is at the root.
    5. Commit changes.
    
    **Better Way (Sync):**
    1. Go to **Settings** in your Space.
    2. Scroll to "Persistent Storage" -> No, wait, look for **"Docker"**.
    3. Actually, just push your code to the Hugging Face git remote:
       ```bash
       git remote add space https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
       git push space main
       ```

5.  **Get URL**:
    - Once built, your API URL will be: `https://YOUR_USERNAME-SPACE_NAME.hf.space`
    - **Important:** Add `/api` for your endpoints.
    - Example: `https://nileshfdo-fusechain-backend.hf.space/api`

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
    - Value: `https://YOUR_USERNAME-SPACE_NAME.hf.space/api` (Replace with your actual Space URL).
6.  **Deploy**: Click **Deploy**.

---

## Troubleshooting
- **CORS Errors**: If the frontend can't talk to the backend, ensure `backend/app/config.py` has `CORS_ORIGINS = ["*"]`.
- **Port**: Hugging Face expects port **7860**. I have already updated the Dockerfile to use this port.
