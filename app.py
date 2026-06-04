import base64
import io
import json
import os
import random
import textwrap
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file if it exists
load_dotenv()

MODEL_ID = "black-forest-labs/FLUX.1-schnell"
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
    """Safely read value from environment variables or Streamlit secrets without failing."""
    val = os.environ.get(key)
    if val is not None:
        return val
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
        "Authorization": f"Bearer {str(api_key).strip()}",
        "Accept": "image/png",
        "Content-Type": "application/json",
    }

    errors = []
    for endpoint in hf_endpoints(model_id):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=180)
        except requests.RequestException as exc:
            errors.append(f"[{endpoint}] Request failed: {exc}")
            continue

        content_type = response.headers.get("content-type", "")
        if response.ok and content_type.startswith("image/"):
            try:
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
                return image, ""
            except Exception as exc:
                errors.append(f"[{endpoint}] Pillow could not open image: {exc}")
                continue

        try:
            error_detail = response.json()
            error_msg = json.dumps(error_detail, indent=2, ensure_ascii=False)
        except Exception:
            error_msg = response.text[:1200]

        if response.status_code in (401, 403):
            errors.append(
                f"[{endpoint}] Authentication failed (HTTP {response.status_code}).\n"
                f"Detail: {error_msg}\n"
                f"Please ensure your token is a 'Read' token or has 'Make calls to inference providers' permission enabled."
            )
        else:
            errors.append(f"[{endpoint}] HTTP {response.status_code}: {error_msg}")

    return None, "\n\n".join(errors)


def call_google_imagen(api_key: str, prompt: str, aspect_ratio: str, num_images: int) -> Tuple[Optional[List[Image.Image]], str]:
    # Aspect ratio mapping for Google Imagen 3 API
    ratio_map = {
        "1:1 Square": "1:1",
        "16:9 Landscape": "16:9",
        "9:16 Portrait": "9:16",
        "4:3 Classic": "4:3",
        "3:4 Mobile Poster": "3:4"
    }
    ratio = ratio_map.get(aspect_ratio, "1:1")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key.strip()}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": min(num_images, 4),
            "aspectRatio": ratio,
            "outputMimeType": "image/jpeg"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if not response.ok:
            return None, f"Google API Error {response.status_code}: {response.text}"
        
        data = response.json()
        predictions = data.get("predictions", [])
        if not predictions:
            return None, f"No predictions returned from Google. Response: {json.dumps(data)}"
            
        images = []
        for pred in predictions:
            img_bytes = base64.b64decode(pred.get("bytesBase64Encoded", ""))
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            images.append(image)
            
        return images, ""
    except Exception as e:
        return None, f"Failed to call Google Imagen API: {e}"


def make_mock_image(prompt: str, width: int, height: int, seed: int, style: str) -> Image.Image:
    # A beautifully styled mock image generator using Pillow for local testing and demo mode.
    rng = random.Random(seed)
    
    # Create gradient background
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image, "RGBA")
    
    # Select color scheme based on style
    if style == "Cyberpunk":
        color_start = (15, 10, 30)   # Deep purple
        color_end = (40, 10, 70)     # Dark magenta
        accent_color = (255, 0, 128, 100) # Neon pink
        accent_color2 = (0, 255, 240, 100) # Neon cyan
    elif style == "Anime":
        color_start = (180, 210, 255) # Light blue
        color_end = (255, 190, 210)   # Light pink
        accent_color = (255, 255, 255, 120)
        accent_color2 = (255, 220, 100, 120)
    elif style == "Watercolor":
        color_start = (248, 246, 240) # Off-white/cream
        color_end = (215, 225, 235)   # Soft blue
        accent_color = (130, 170, 210, 60) # Blended soft blue
        accent_color2 = (210, 150, 170, 60) # Blended soft rose
    elif style in ["Photorealistic", "Cinematic"]:
        color_start = (10, 15, 25)    # Midnight blue
        color_end = (45, 35, 25)      # Warm gold/amber
        accent_color = (255, 180, 80, 60) # Golden glow
        accent_color2 = (100, 150, 200, 60) # Soft daylight blue
    else:
        color_start = (20, 25, 35)    # Slate dark
        color_end = (35, 45, 60)      # Lighter slate
        accent_color = (130, 140, 180, 70)
        accent_color2 = (180, 130, 150, 70)
        
    # Draw background gradient
    for y in range(height):
        t = y / height
        r = int(color_start[0] * (1 - t) + color_end[0] * t)
        g = int(color_start[1] * (1 - t) + color_end[1] * t)
        b = int(color_start[2] * (1 - t) + color_end[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Draw some abstract geometric shapes for artistic look
    for _ in range(8):
        shape_type = rng.choice(["circle", "line", "rectangle"])
        col = rng.choice([accent_color, accent_color2])
        if shape_type == "circle":
            r = rng.randint(40, min(width, height) // 3)
            cx = rng.randint(0, width)
            cy = rng.randint(0, height)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        elif shape_type == "line":
            x1 = rng.randint(0, width)
            y1 = rng.randint(0, height)
            x2 = rng.randint(0, width)
            y2 = rng.randint(0, height)
            w = rng.randint(2, 8)
            draw.line([(x1, y1), (x2, y2)], fill=col, width=w)
        else:
            w_rect = rng.randint(80, width // 2)
            h_rect = rng.randint(80, height // 2)
            x1 = rng.randint(0, width - w_rect)
            y1 = rng.randint(0, height - h_rect)
            draw.rectangle([x1, y1, x1 + w_rect, y1 + h_rect], fill=col)

    # Draw border outline
    border_color = (255, 255, 255, 40) if style in ["Anime", "Watercolor"] else (255, 255, 255, 20)
    draw.rectangle([20, 20, width - 20, height - 20], outline=border_color, width=4)

    # Draw title
    title_text = f"Demo Image [{style}]"
    
    # Text overlay
    margin = max(40, width // 20)
    title_font_size = max(24, width // 22)
    body_font_size = max(14, width // 42)
    
    try:
        title_font = ImageFont.load_default(size=title_font_size)
        body_font = ImageFont.load_default(size=body_font_size)
    except TypeError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        
    text_color = (255, 255, 255, 255) if style not in ["Anime", "Watercolor"] else (40, 40, 60, 255)
    sub_color = (220, 220, 235, 255) if style not in ["Anime", "Watercolor"] else (80, 80, 100, 255)
    
    draw.text((margin, margin), title_text, fill=text_color, font=title_font)
    
    # Prompt text wrap
    max_chars = max(25, int(width / (body_font_size * 0.55)))
    wrapped_prompt = textwrap.fill(prompt, width=max_chars)
    
    info_text = f"Prompt: {wrapped_prompt}\n\nSeed: {seed}\nDimensions: {width} x {height}\nMock Engine: Pillow Generative"
    draw.text((margin, margin + title_font_size + 25), info_text, fill=sub_color, font=body_font)
    
    return image


def main() -> None:
    st.set_page_config(
        page_title="Universal AI Image Generator",
        page_icon="🎨",
        layout="wide",
    )

    # Inject custom modern CSS styles for premium styling and design aesthetics
    st.markdown("""
        <style>
        /* Modern font and styling imports */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Transparent Header */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* Main background with premium light gradient */
        .stApp {
            background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
            color: #1e293b;
        }
        
        /* Glassmorphism sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.45) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(0, 0, 0, 0.06);
        }
        
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
            color: #1e293b !important;
        }
        
        /* Title styling with glowing indigo/pink gradient */
        h1 {
            background: linear-gradient(90deg, #4f46e5, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -1px;
            font-size: 3rem !important;
            margin-bottom: 5px !important;
            text-align: center;
        }
        
        .title-caption {
            color: rgba(30, 41, 59, 0.7);
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 30px;
        }
        
        /* Glassmorphic Column Containers */
        div[data-testid="column"] {
            background-color: rgba(255, 255, 255, 0.65) !important;
            backdrop-filter: blur(10px);
            padding: 25px !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
            color: #1e293b;
        }
        
        /* Subheader and Labels */
        h3 {
            color: #4f46e5 !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
            padding-bottom: 10px;
            margin-bottom: 20px !important;
        }
        
        label {
            color: #0f172a !important;
            font-weight: 500 !important;
        }
        
        /* Primary button styling with micro-animations */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #4f46e5 0%, #ec4899 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 30px !important;
            font-weight: 600 !important;
            width: 100%;
            font-size: 1.1rem !important;
            margin-top: 10px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2) !important;
        }
        
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) scale(1.01) !important;
            box-shadow: 0 6px 22px rgba(79, 70, 229, 0.4) !important;
        }
        
        div.stButton > button:first-child:active {
            transform: translateY(1px) !important;
        }
        
        /* Styling text areas and inputs */
        textarea, input, select, div[data-baseweb="select"] {
            border-radius: 10px !important;
            background-color: #ffffff !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            color: #1e293b !important;
        }
        
        textarea:focus, input:focus {
            border-color: #4f46e5 !important;
            box-shadow: 0 0 12px rgba(79, 70, 229, 0.15) !important;
        }
        
        /* Expander customization */
        div[data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.4) !important;
            border: 1px solid rgba(0, 0, 0, 0.05) !important;
            border-radius: 12px !important;
            margin-top: 15px;
        }
        
        /* Code block readability in light mode */
        code {
            background-color: rgba(0, 0, 0, 0.04) !important;
            color: #0f172a !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>Universal AI Image Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='title-caption'>A premium Streamlit Web App utilizing Google Imagen 3 and FLUX.1 Schnell.</p>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚡ Project Dashboard")
        
        POPULAR_MODELS = {
            "FLUX.1 Schnell (via Hugging Face)": "black-forest-labs/FLUX.1-schnell",
            "Google Imagen 3 (via Gemini API)": "google/imagen-3.0-generate-002",
            "Custom HF Model (Enter below)": "custom"
        }
        
        model_selection = st.selectbox(
            "Select Model", 
            list(POPULAR_MODELS.keys()), 
            index=0,
            help="Select a model. FLUX uses Hugging Face serverless tier, while Google Imagen uses Google AI Studio."
        )
        
        if POPULAR_MODELS[model_selection] == "custom":
            model_id = st.text_input("Custom Model ID", value="black-forest-labs/FLUX.1-schnell")
        else:
            model_id = POPULAR_MODELS[model_selection]
            
        github_link = st.text_input("GitHub Repository", value=get_secret_value("GITHUB_LINK", DEFAULT_GITHUB_LINK))
        demo_link = st.text_input("Deployment Link", value=get_secret_value("DEMO_LINK", DEFAULT_DEMO_LINK))
        
        st.markdown("---")
        st.markdown(f"**Current Model:** `{model_id}`")
        st.markdown(f"**GitHub:** [{github_link.split('/')[-1]}]({github_link})")
        st.markdown(f"**Live Demo:** [Streamlit.app]({demo_link})")

    # Access API Token based on selected model
    is_gemini_model = (model_id == "google/imagen-3.0-generate-002")
    
    if is_gemini_model:
        api_key = get_secret_value("GEMINI_API_KEY", None)
        if not api_key:
            api_key = get_secret_value("GOOGLE_API_KEY", None)
            
        if not api_key:
            api_key = st.text_input("Enter your Google Gemini API Key (GEMINI_API_KEY)", type="password")
        else:
            st.success("Google Gemini API key verified via environment/secrets.")
    else:
        api_key = get_secret_value("HF_TOKEN", None)
        if not api_key:
            api_key = st.text_input("Enter your Hugging Face API Token (HF_TOKEN)", type="password")
        else:
            st.success("Hugging Face API token verified via environment/secrets.")

    # Initialize session state for Cosmos 3 prompt properties
    if "prev_prompt" not in st.session_state:
        st.session_state.prev_prompt = ""
    if "subjects" not in st.session_state:
        st.session_state.subjects = "a small robot"
    if "background" not in st.session_state:
        st.session_state.background = "cozy futuristic library, warm lighting"
    if "text_elements" not in st.session_state:
        st.session_state.text_elements = ""

    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        st.subheader("Prompt Engineering")
        prompt = st.text_area(
            "Text Prompt (Simple input)",
            value="A small robot reading a book in a cozy futuristic library, warm lighting",
            height=100,
            help="Describe what you want to see. The app will use this to generate the image.",
        )
        negative_prompt = st.text_area(
            "Negative Prompt",
            value="blurry, low quality, distorted, watermark, text artifacts, bad anatomy",
            height=70,
        )
        
        style = st.selectbox("Aesthetic Style Overlay", list(STYLES.keys()), index=1)
        aspect_ratio = st.selectbox("Canvas Aspect Ratio", list(ASPECT_RATIOS.keys()), index=0)
        
        # Calculate aspect ratio string (e.g. "16,9" instead of "16:9" for Cosmos 3)
        ratio_part = aspect_ratio.split()[0]
        w_ratio, h_ratio = ratio_part.split(":")
        aspect_ratio_payload = f"{w_ratio},{h_ratio}"
        
        width, height = ASPECT_RATIOS[aspect_ratio]
        final_prompt = build_prompt(prompt, style)

        # Synchronize / parse prompt components into session state
        if prompt != st.session_state.prev_prompt:
            st.session_state.prev_prompt = prompt
            parts = [p.strip() for p in prompt.split(",")]
            if len(parts) > 1:
                st.session_state.subjects = parts[0]
                st.session_state.background = ", ".join(parts[1:])
            else:
                words = prompt.split()
                if len(words) > 3:
                    st.session_state.subjects = " ".join(words[:3])
                    st.session_state.background = " ".join(words[3:])
                else:
                    st.session_state.subjects = prompt
                    st.session_state.background = ""

        # Optional JSON-Upsampling Prompt Setup for Custom / Cosmos models
        st.markdown("---")
        use_json_prompt = st.checkbox(
            "Use NVIDIA Cosmos 3 JSON-Upsampled Prompt Format", 
            value=False, 
            help="Structures prompt metadata into JSON fields. Only toggle this if your custom model requires the Cosmos 3 JSON schema."
        )
        
        if use_json_prompt:
            with st.expander("🛠️ Cosmos 3 JSON-Upsampling Fields", expanded=True):
                st.markdown(
                    "<small style='color:rgba(30,41,59,0.6);'>Edit these fields to customize specific scene details passed to the model's structural inputs.</small>", 
                    unsafe_allow_html=True
                )
                subjects_input = st.text_input("Subjects (comma-separated)", value=st.session_state.subjects)
                st.session_state.subjects = subjects_input
                
                background_input = st.text_input("Background Setting", value=st.session_state.background)
                st.session_state.background = background_input
                
                text_elements_input = st.text_input("Text & Signage Elements (comma-separated)", value=st.session_state.text_elements)
                st.session_state.text_elements = text_elements_input
                
                comprehensive_caption = st.text_area("Comprehensive Caption", value=final_prompt, height=80)
                
                # Assemble structured JSON prompt
                json_prompt_dict = {
                    "subjects": [s.strip() for s in subjects_input.split(",") if s.strip()],
                    "background_setting": background_input.strip(),
                    "comprehensive_t2i_caption": comprehensive_caption.strip(),
                    "text_and_signage_elements": [t.strip() for t in text_elements_input.split(",") if t.strip()] if text_elements_input else [],
                    "resolution": {"H": height, "W": width},
                    "aspect_ratio": aspect_ratio_payload
                }
                final_payload_prompt = json.dumps(json_prompt_dict, indent=2, ensure_ascii=False)
        else:
            final_payload_prompt = final_prompt

    with col_right:
        st.subheader("Model Parameters")
        seed = st.number_input("Inference Seed", min_value=0, max_value=2_147_483_647, value=42, step=1)
        number_of_images = st.slider("Batch Count (Images)", min_value=1, max_value=4, value=1)
        guidance_scale = st.slider("Guidance Scale (CFG)", min_value=1.0, max_value=15.0, value=7.0, step=0.5)
        steps = st.slider("Inference Steps", min_value=10, max_value=60, value=30, step=5)
        
        demo_mode = st.checkbox(
            "Demo Mode / Mock Mode",
            value=False,
            help="Enable to simulate image generation locally without calling the API.",
        )
        
        st.markdown("### 🔍 Final Payload Preview")
        if use_json_prompt:
            st.caption("JSON-upsampled string sent in payload:")
            st.code(final_payload_prompt, language="json")
        else:
            st.caption("Standard text string sent in payload:")
            st.code(final_payload_prompt, language="text")

    generate = st.button("Generate Image(s)", type="primary")

    if generate:
        if not prompt.strip():
            st.error("Please enter a text prompt before generating an image.")
            return

        if not api_key and not demo_mode:
            st.error("Please enter the API key, or enable Demo Mode.")
            return

        st.info(f"Generating {number_of_images} image(s)...")
        images: List[Image.Image] = []

        if is_gemini_model and not demo_mode:
            with st.spinner("Requesting image(s) from Google Imagen API..."):
                images_result, error = call_google_imagen(
                    api_key=str(api_key),
                    prompt=final_prompt,
                    aspect_ratio=aspect_ratio,
                    num_images=number_of_images
                )
            if images_result is None:
                st.error("Google Imagen generation failed.")
                st.code(error, language="text")
            else:
                images = images_result
        else:
            for index in range(number_of_images):
                current_seed = int(seed) + index
                
                payload = build_payload(
                    prompt=final_payload_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    seed=current_seed,
                    guidance_scale=float(guidance_scale),
                    steps=int(steps),
                )

                if demo_mode:
                    image = make_mock_image(final_prompt, width, height, current_seed, style)
                    images.append(image)
                    continue

                with st.spinner(f"Requesting Image {index + 1} from Hugging Face Inference..."):
                    image, error = call_hugging_face(str(api_key), payload, model_id)

                if image is None:
                    st.error("Image generation failed.")
                    st.code(error, language="text")
                    break

                images.append(image)

        if images:
            st.success("Generation complete!")
            columns = st.columns(min(len(images), 2))
            for i, image in enumerate(images):
                with columns[i % len(columns)]:
                    st.image(image, caption=f"Generated Image {i + 1}", use_container_width=True)
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    st.download_button(
                        label=f"💾 Download Image {i + 1}",
                        data=buffer.getvalue(),
                        file_name=f"generated_{i + 1}.png",
                        mime="image/png",
                    )

    st.markdown("---")
    with st.expander("🔒 API Safety & Configuration Guidelines"):
        st.markdown("""
        * **No Hardcoding:** Never hardcode your API keys directly in the source file `app.py`.
        * **Local Testing:** Create `.streamlit/secrets.toml` and configure `HF_TOKEN = "your_token"` or `GEMINI_API_KEY = "your_key"` inside.
        * **Production Deployment:** Configure the secrets key in the **Streamlit Community Cloud Console** under app settings.
        """)


if __name__ == "__main__":
    main()
