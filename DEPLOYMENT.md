# Factify Deployment Guide (Free Hosting)

Since your project uses heavy ML libraries (TensorFlow), the best free combination is:
1.  **Backend**: Hugging Face Spaces (Free 2 vCPU, 16GB RAM)
2.  **Frontend**: Vercel (Best for React)

---

## Part 1: Backend Deployment (Hugging Face Spaces)

1.  **Create a Space**:
    - Go to [huggingface.co/spaces](https://huggingface.co/spaces) and create a new Space.
    - Name: `factify-backend` (or similar).
    - SDK: **Docker** (Select "Docker" as the SDK, not Streamlit/Gradio).
    - Template: **Blank**.

2.  **Upload Files**:
    - You can upload files directly via the browser or use git.
    - **Essential Files to Upload**:
        - `Dockerfile` (I created this for you in the root)
        - `requirements.txt`
        - `run.py`
        - `app/` (folder)
        - `models/` (folder - **Important**: This is large (~13MB), so it might take a moment)
        - `logs/` (empty folder is fine, or let Docker create it)

3.  **Build**:
    - Hugging Face will automatically build the Docker image.
    - Wait for it to show "Running".
    - **Copy the Direct URL**: Click on the "Embed this space" or look at the top menu to find the direct URL (e.g., `https://huggingface.co/spaces/username/factify-backend`). It usually looks like `https://username-factify-backend.hf.space`. **You need this URL for the frontend.**

---

## Part 2: Frontend Deployment (Vercel)

1.  **Push to GitHub**:
    - Ensure your project is pushed to your GitHub repository.

2.  **Import to Vercel**:
    - Go to [vercel.com](https://vercel.com) and "Add New Project".
    - Import your `Factify` repository.

3.  **Configure Project**:
    - **Framework Preset**: Vite (should be auto-detected).
    - **Root Directory**: Click "Edit" and select `frontend`. **(Crucial Step)**.

4.  **Environment Variables**:
    - Expand "Environment Variables".
    - Add a new variable:
        - **Key**: `VITE_API_URL`
        - **Value**: `https://YOUR-SPACE-NAME.hf.space` (The URL from Part 1).
        - **Important**: Do not add a trailing slash `/` at the end.

5.  **Deploy**:
    - Click "Deploy".
    - Vercel will build your React app.

6.  **Done**:
    - Vercel will give you a live link (e.g., `https://factify-frontend.vercel.app`).
    - Open it and test!

---

## Troubleshooting

-   **CORS Error**: If the frontend says "Network Error" or "CORS", you might need to update `app/main.py` in the backend to explicitly allow the Vercel domain.
    -   *Quick Fix*: In `app/main.py`, update `allow_origins=["*"]` temporarily to allow all, or add your Vercel domain once you know it.
-   **Model Loading Error**: If the backend fails to start on HF, check the "Logs" tab in the Space. It might be a memory issue (unlikely with 16GB) or a path issue.
