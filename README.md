# Universal AI Image Generator

This repository contains a deployable, high-fidelity Streamlit web application designed for generating images using Black Forest Labs' **FLUX.1 Schnell** (via Hugging Face API).

🔗 **Live Demo**: [https://huggingface-practice-dec591nyc.streamlit.app](https://huggingface-practice-dec591nyc.streamlit.app)

---

## 🚀 Core Features

- **FLUX.1 Schnell Integration:** Fast, free serverless text-to-image generation via Hugging Face.
- **Dynamic Configuration:** Supports custom Hugging Face model IDs, and allows inputting Hugging Face API credentials.
- **Aesthetic Overlay Styles:** Auto-appends style details (Anime, Cyberpunk, Watercolor, Photorealistic, Cinematic) to your prompt.
- **Interactive UI:** A modern light glassmorphism theme using clean typography, high contrast, and hover micro-animations.
- **Demo Mode:** Local PIL graphics mockup rendering for offline testing and verification.

---

## 🛠️ How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/dec591nyc/HuggingFace-Practice.git
cd HuggingFace-Practice
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
   - Add your API Key:
     ```toml
     HF_TOKEN = "your_huggingface_token_here"
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

- **GitHub Repository:** `https://github.com/dec591nyc/HuggingFace-Practice`
- **Streamlit Live Demo:** `https://huggingface-practice-dec591nyc.streamlit.app`
