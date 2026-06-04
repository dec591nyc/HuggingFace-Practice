# NVIDIA Cosmos3-Super-Text2Image Web Generator

This repository contains a deployable, high-fidelity Streamlit web application designed for generating images using NVIDIA's 64B parameter text-to-image model: **nvidia/Cosmos3-Super-Text2Image**.

The application is structured to conform to the NVIDIA Cosmos 3 architecture guidelines, supporting structured **JSON-upsampled prompts** to maximize image composition, physical correctness, and alignment with the model's training distribution.

## 🚀 Core Features

- **Text Prompt Engineering:** Standard text prompt input with automatic style overlay (Anime, Cyberpunk, Watercolor, Photorealistic, Cinematic).
- **JSON-Upsampled Prompt Mode (Recommended):** Auto-generates and compiles the prompt into a structured JSON string conforming to the Cosmos 3 schema:
  - `subjects`: Main entities in the scene.
  - `background_setting`: Contextual setting details.
  - `comprehensive_t2i_caption`: The complete descriptive prompt.
  - `text_and_signage_elements`: Specific text labels to render.
  - `resolution`: Target height and width.
  - `aspect_ratio`: Ratios formatted as `"W,H"` (e.g. `"16,9"`).
- **Interactive JSON Preview:** Live view of the compiled JSON string before generation.
- **Generation Parameters:** Granular control over Seed, Batch Count (Number of Images), Guidance Scale (CFG), and Inference Steps.
- **Premium Dark UI:** Sleek cyberpunk/space gradient theme using modern typography (Outfit font) and responsive glassmorphism containers.
- **Aesthetic Demo Mode:** High-quality mock image generation using custom Pillow art rendering for local testing if serverless Hugging Face endpoints are queued.
- **Hugging Face Integration:** Secure API call routing to the latest Hugging Face Inference Providers.
- **Security First:** No hardcoded tokens. Built-in support for Streamlit secrets and password fields.

---

## 🛠️ How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/yourname/hw3-cosmos-text2image.git
cd hw3-cosmos-text2image
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Key
For local testing, create a file named `.streamlit/secrets.toml` in your project root:
```toml
HF_TOKEN = "your_huggingface_access_token_here"
```
*(Get your free User Access Token from your Hugging Face account settings under Access Tokens. The `.streamlit/secrets.toml` file is in `.gitignore` and will never be committed.)*

### 4. Run the App
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8515` (or whichever port is active).

---

## ☁️ Deploying to Streamlit Community Cloud

Streamlit Community Cloud allows you to deploy and showcase your app online for free:

1. **Upload to GitHub:**
   - Commit all your code files (`app.py`, `requirements.txt`, `.gitignore`, `README.md`).
   - Push them to your GitHub repository.
2. **Deploy on Streamlit.io:**
   - Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in.
   - Click **New app**, select your GitHub repository, branch, and specify `app.py` as the main file path.
3. **Configure Secrets:**
   - Before clicking Deploy, open the **Advanced settings** (or go to App Settings -> Secrets after deploying).
   - Add your Hugging Face API Token under Secrets:
     ```toml
     HF_TOKEN = "your_huggingface_token_here"
     ```
   - Save and Deploy. Your app will automatically load the token securely.

---

## 🎨 Screenshots

Once your local testing or deployment is complete, add screenshots to the `screenshots/` directory and check them here:

### Main Interface
![App Home](/screenshots/app_home.png)

### Generation Results
![Generated Result](/screenshots/generated_result.png)

---

## 🔗 Submission Links

- **GitHub Repository:** `https://github.com/yourname/hw3-cosmos-text2image`
- **Streamlit Live Demo:** `https://your-app-name.streamlit.app`

*(Replace the links above with your actual links before submitting your homework!)*
