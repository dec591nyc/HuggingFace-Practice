# HW3 Cosmos3-Super-Text2Image App

## Project Goal

This project uses Streamlit and Hugging Face to build a text-to-image generation app with NVIDIA Cosmos3-Super-Text2Image.

The app allows users to enter a text prompt, adjust basic generation settings, call a Hugging Face inference endpoint, and display the generated image in a web interface.

## Model

Model: `nvidia/Cosmos3-Super-Text2Image`

## Main Features

- Text prompt input
- Image style selector
- Aspect ratio selector
- Seed control
- Number of images control
- Negative prompt input
- Hugging Face API token password field
- Streamlit secrets support
- Generated image preview
- Image download button
- Error handling for missing API key, failed requests, or unavailable model
- Demo Mode / Mock Mode for showing the complete app flow when the real model is unavailable

## Project Structure

```text
hw3-cosmos-text2image/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
├── screenshots/
│   ├── app_home.png
│   └── generated_result.png
└── prompts/
    └── gemini_canvas_prompt.md
```

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## API Key

Do not hardcode your API key in `app.py`.

You can either:

1. Enter the Hugging Face API token on the web page, or
2. Put it in Streamlit secrets.

For local testing, create this file:

```text
.streamlit/secrets.toml
```

Then add:

```toml
HF_TOKEN = "your_huggingface_token_here"
```

The repository includes `.streamlit/secrets.toml.example` only as a template. The real `secrets.toml` file must not be uploaded to GitHub.

## Deployment

Deploy this project to Streamlit Community Cloud.

Suggested steps:

1. Push this project to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set the main file path to `app.py`.
5. Add `HF_TOKEN` in Streamlit Cloud Secrets.
6. Deploy the app.

## Important Note About Model Availability

`nvidia/Cosmos3-Super-Text2Image` is a very large text-to-image model. Depending on Hugging Face availability, permissions, and provider support, it may not always run through serverless inference.

If the model is unavailable, this app includes Demo Mode / Mock Mode to preserve the complete homework workflow and UI demonstration. In a real production deployment, the model may need a dedicated Hugging Face Inference Endpoint or another compatible provider.

## Links

GitHub Repo:

```text
https://github.com/yourname/hw3-cosmos-text2image
```

Streamlit Demo:

```text
https://your-app-name.streamlit.app
```

Replace the links above after deploying the project.

## Screenshots

Add screenshots here after running the app:

- `screenshots/app_home.png`
- `screenshots/generated_result.png`

## Submission

Submit these two links:

```text
GitHub:
https://github.com/yourname/hw3-cosmos-text2image

Streamlit Demo:
https://your-app-name.streamlit.app
```
