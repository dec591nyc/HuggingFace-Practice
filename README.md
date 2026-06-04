# Universal AI Image Generator

This repository contains a deployable, high-fidelity Streamlit web application designed for generating images using Google's **Imagen 3** (via Gemini API) and Black Forest Labs' **FLUX.1 Schnell** (via Hugging Face API).

---

## 🚀 Core Features

- **Google Imagen 3 Integration:** Leverage Google's state-of-the-art image generation model via the Gemini API (`imagen-3.0-generate-002`).
- **FLUX.1 Schnell Integration:** Fast, free serverless text-to-image generation via Hugging Face.
- **Dynamic Configuration:** Supports custom Hugging Face model IDs, and allows inputting either Hugging Face or Gemini API credentials dynamically depending on the selected model.
- **Aesthetic Overlay Styles:** Auto-appends style details (Anime, Cyberpunk, Watercolor, Photorealistic, Cinematic) to your prompt.
- **Interactive UI:** A modern light glassmorphism theme using clean typography, high contrast, and hover micro-animations.
- **Demo Mode:** Local PIL graphics mockup rendering for offline testing and verification.

---

## 🛠️ How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/dec591nyc/HuggingFace_Practice.git
cd HuggingFace_Practice
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
For local testing, create a file named `.streamlit/secrets.toml` in your project root:
```toml
# Hugging Face Access Token (for FLUX.1 Schnell)
HF_TOKEN = "your_huggingface_token_here"

# Google Gemini API Key (for Google Imagen 3)
GEMINI_API_KEY = "your_gemini_api_key_here"
```
*(The `.streamlit/secrets.toml` file is git-ignored and will never be pushed to your repository.)*

### 4. Run the App
```bash
streamlit run app.py
```

---

## ☁️ Deploying to Streamlit Community Cloud

1. **Upload to GitHub:**
   - Commit all your code files (`app.py`, `requirements.txt`, `.gitignore`, `README.md`).
   - Push them to your GitHub repository.
2. **Deploy on Streamlit.io:**
   - Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in.
   - Click **New app**, select your GitHub repository, branch, and specify `app.py` as the main file path.
3. **Configure Advanced Secrets:**
   - Go to App Settings -> Secrets in your Streamlit Cloud console.
   - Add your API Keys:
     ```toml
     HF_TOKEN = "your_huggingface_token_here"
     GEMINI_API_KEY = "your_gemini_api_key_here"
     ```
   - Save. Your app will automatically load these credentials securely.

---

## 🎨 Screenshots

Add screenshots to the `screenshots/` directory and check them here:

### Main Interface
![App Home](/screenshots/app_home.png)

### Generation Results
![Generated Result](/screenshots/generated_result.png)

---

## 🔗 Submission Links

- **GitHub Repository:** `https://github.com/dec591nyc/HuggingFace_Practice`
- **Streamlit Live Demo:** `https://your-app-name.streamlit.app`
