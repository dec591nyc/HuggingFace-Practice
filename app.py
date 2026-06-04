import io
import json
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st
from PIL import Image, ImageDraw

MODEL_ID = "nvidia/Cosmos3-Super-Text2Image"
DEFAULT_GITHUB_LINK = "https://github.com/yourname/hw3-cosmos-text2image"
DEFAULT_DEMO_LINK = "https://your-app-name.streamlit.app"

ASPECT_RATIOS: Dict[str, Tuple[int, int]] = {
    "1:1 Square": (1024, 1024),
    "16:9 Landscape": (1024, 576),
    "9:16 Portrait": (576, 1024),
    "4:3 Classic": (1024, 768),
    "3:4 Mobile Poster": (768, 1024),
}

STYLES: Dict[str, str] = {
    "None": "",
    "Photorealistic": "photorealistic, ultra detailed, natural lighting",
    "Cinematic": "cinematic lighting, dramatic composition, film still",
    "Anime": "anime style, clean line art, vibrant colors",
    "Watercolor": "watercolor painting, soft texture, artistic brush strokes",
    "Cyberpunk": "cyberpunk, neon lights, futuristic city atmosphere",
}


def get_secret_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Safely read Streamlit secrets without failing during local development."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def build_prompt(prompt: str, style: str) -> str:
    style_suffix = STYLES.get(style, "")
    if style_suffix:
        return f"{prompt.strip()}, {style_suffix}"
    return prompt.strip()


def build_payload(
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    seed: int,
    guidance_scale: float,
    steps: int,
) -> Dict:
    parameters = {
        "width": width,
        "height": height,
        "seed": seed,
        "guidance_scale": guidance_scale,
        "num_inference_steps": steps,
    }
    if negative_prompt.strip():
        parameters["negative_prompt"] = negative_prompt.strip()

    return {
        "inputs": prompt,
        "parameters": parameters,
        "options": {
            "wait_for_model": True,
            "use_cache": False,
        },
    }


def hf_endpoints(model_id: str) -> List[str]:
    # Current Hugging Face Inference Providers router plus legacy Serverless API fallback.
    encoded_model = model_id.replace("/", "%2F")
    return [
        f"https://router.huggingface.co/hf-inference/models/{model_id}",
        f"https://api-inference.huggingface.co/models/{encoded_model}",
    ]


def call_hugging_face(api_key: str, payload: Dict, model_id: str) -> Tuple[Optional[Image.Image], str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/png",
        "Content-Type": "application/json",
    }

    last_error = ""
    for endpoint in hf_endpoints(model_id):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=180)
        except requests.RequestException as exc:
            last_error = f"Request failed for {endpoint}: {exc}"
            continue

        content_type = response.headers.get("content-type", "")
        if response.ok and content_type.startswith("image/"):
            try:
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
                return image, ""
            except Exception as exc:
                last_error = f"The API returned image bytes, but Pillow could not open them: {exc}"
                continue

        try:
            error_detail = response.json()
            last_error = json.dumps(error_detail, indent=2, ensure_ascii=False)
        except Exception:
            last_error = response.text[:1200]

        if response.status_code in (401, 403):
            return None, "Authentication failed. Please check that your Hugging Face token is valid and has Inference Providers permission."

    return None, last_error or "No response was returned by the Hugging Face API."


def make_mock_image(prompt: str, width: int, height: int, seed: int) -> Image.Image:
    # A simple generated placeholder so the app can still demonstrate its full flow if the model is unavailable.
    image = Image.new("RGB", (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)
    margin = max(20, width // 24)
    title = "Mock / Demo Mode"
    body = f"Prompt:\n{prompt}\n\nSeed: {seed}\nSize: {width} x {height}"
    draw.rectangle([margin, margin, width - margin, height - margin], outline=(40, 40, 40), width=4)
    draw.text((margin * 1.5, margin * 1.5), title, fill=(20, 20, 20))
    draw.text((margin * 1.5, margin * 3.2), body[:900], fill=(40, 40, 40))
    return image


def main() -> None:
    st.set_page_config(
        page_title="HW3 Cosmos3 Text-to-Image App",
        page_icon="🎨",
        layout="wide",
    )

    st.title("HW3 Cosmos3-Super-Text2Image App")
    st.caption("A Streamlit text-to-image app using Hugging Face and NVIDIA Cosmos3-Super-Text2Image.")

    with st.sidebar:
        st.header("Project Info")
        model_id = st.text_input("Model name", value=MODEL_ID)
        github_link = st.text_input("GitHub repo link", value=get_secret_value("GITHUB_LINK", DEFAULT_GITHUB_LINK))
        demo_link = st.text_input("Streamlit.io demo link", value=get_secret_value("DEMO_LINK", DEFAULT_DEMO_LINK))
        st.markdown(f"**Model:** `{model_id}`")
        st.markdown(f"**GitHub:** {github_link}")
        st.markdown(f"**Demo:** {demo_link}")

    st.subheader("How to use")
    st.write(
        "Enter a prompt, adjust image settings, provide your Hugging Face token, "
        "then click Generate Image. If the model is unavailable, enable Demo Mode to show the full app flow."
    )

    api_key = get_secret_value("HF_TOKEN", None)
    if not api_key:
        api_key = st.text_input("Enter your Hugging Face API Token", type="password")
    else:
        st.success("Hugging Face token loaded from Streamlit secrets.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Prompt Settings")
        prompt = st.text_area(
            "Text prompt",
            value="A small robot reading a book in a cozy futuristic library, warm lighting",
            height=120,
        )
        negative_prompt = st.text_area(
            "Negative prompt",
            value="blurry, low quality, distorted, watermark, text artifacts",
            height=90,
        )
        style = st.selectbox("Image style", list(STYLES.keys()), index=1)
        aspect_ratio = st.selectbox("Aspect ratio", list(ASPECT_RATIOS.keys()), index=0)

    with col_right:
        st.subheader("Generation Parameters")
        seed = st.number_input("Seed", min_value=0, max_value=2_147_483_647, value=42, step=1)
        number_of_images = st.slider("Number of images", min_value=1, max_value=4, value=1)
        guidance_scale = st.slider("Guidance scale", min_value=1.0, max_value=15.0, value=7.5, step=0.5)
        steps = st.slider("Inference steps", min_value=10, max_value=60, value=30, step=5)
        demo_mode = st.checkbox(
            "Demo Mode / Mock Mode",
            value=False,
            help="Use this if the Hugging Face model is temporarily unavailable or too large for serverless inference.",
        )

    width, height = ASPECT_RATIOS[aspect_ratio]
    final_prompt = build_prompt(prompt, style)

    st.markdown("### Final prompt preview")
    st.code(final_prompt, language="text")

    generate = st.button("Generate Image", type="primary")

    if generate:
        if not prompt.strip():
            st.error("Please enter a text prompt before generating an image.")
            return

        if not api_key and not demo_mode:
            st.error("Please enter a Hugging Face API Token, or enable Demo Mode.")
            return

        st.info(f"Generating {number_of_images} image(s) at {width}x{height}...")
        images: List[Image.Image] = []

        for index in range(number_of_images):
            current_seed = int(seed) + index
            payload = build_payload(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=current_seed,
                guidance_scale=float(guidance_scale),
                steps=int(steps),
            )

            if demo_mode:
                image = make_mock_image(final_prompt, width, height, current_seed)
                images.append(image)
                continue

            with st.spinner(f"Calling Hugging Face API for image {index + 1}..."):
                image, error = call_hugging_face(str(api_key), payload, model_id)

            if image is None:
                st.error("Image generation failed.")
                st.code(error, language="text")
                st.warning(
                    "If Cosmos3-Super-Text2Image is unavailable through serverless inference, "
                    "you can enable Demo Mode and explain this limitation in the README."
                )
                break

            images.append(image)

        if images:
            st.success("Generation complete.")
            columns = st.columns(min(len(images), 2))
            for i, image in enumerate(images):
                with columns[i % len(columns)]:
                    st.image(image, caption=f"Generated image {i + 1}", use_container_width=True)
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    st.download_button(
                        label=f"Download image {i + 1}",
                        data=buffer.getvalue(),
                        file_name=f"cosmos_generated_{i + 1}.png",
                        mime="image/png",
                    )

    with st.expander("API safety notes"):
        st.write(
            "This app never hardcodes API keys. Use the password field on the page, "
            "or put HF_TOKEN in Streamlit Cloud secrets. Do not commit .env or secrets.toml to GitHub."
        )


if __name__ == "__main__":
    main()
