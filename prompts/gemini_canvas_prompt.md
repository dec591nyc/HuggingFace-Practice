You are an expert AI app developer.

Please help me build a Streamlit app for HW3.

Goal:
Create a text-to-image generation web app using Hugging Face and the model:
nvidia/Cosmos3-Super-Text2Image

Requirements:
1. Use Python and Streamlit.
2. The app must allow users to input a text prompt.
3. The app must include optional controls:
   - image style
   - aspect ratio
   - negative prompt
   - seed
   - number of images
4. The app must call Hugging Face Inference API or a compatible endpoint.
5. The app must not hardcode API keys.
6. If no API key is found in Streamlit secrets, show a password input field:
   "Enter your Hugging Face API Token".
7. Show the generated image on the page.
8. Add clear error handling if the API key is missing, the model is unavailable, or the request fails.
9. Add a README.md explaining:
   - project goal
   - how to run locally
   - how to deploy to Streamlit.io
   - where to put API keys
   - GitHub link
   - Streamlit demo link
10. Generate clean, readable code suitable for a beginner-level AI homework project.

Please output:
- app.py
- requirements.txt
- README.md
- .gitignore
