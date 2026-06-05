import base64
import concurrent.futures
import io
import json
import os
import random
import textwrap
import time
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file if it exists
load_dotenv()

MODEL_ID = "black-forest-labs/FLUX.1-schnell"
DEFAULT_GITHUB_LINK = "https://github.com/dec591nyc/HuggingFace-Practice"

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

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "English": {
        "title": "Universal AI Image Generator",
        "subtitle": "A modern AI Image Generator supporting FLUX and Stable Diffusion (SDXL).",
        "project_dashboard": "⚙️ Model Settings",
        "select_model": "Select Model",
        "prompt_eng": "Prompt Engineering",
        "hf_token_label": "Enter your Hugging Face API Token",
        "hf_verified": "Hugging Face API token verified.",
        "prompt_label": "Text Prompt (Simple input)",
        "prompt_help": "Describe what you want to see. The app will use this to generate the image.",
        "prompt_default": "A small robot reading a book in a cozy futuristic library, warm lighting",
        "style_label": "Aesthetic Style Overlay",
        "aspect_ratio_label": "Canvas Aspect Ratio",
        "advanced_params": "⚙️ Advanced Parameters",
        "neg_prompt_label": "Negative Prompt",
        "seed_label": "Inference Seed",
        "batch_count_label": "Batch Count (Images)",
        "cfg_label": "Guidance Scale (CFG)",
        "steps_label": "Inference Steps",
        "demo_mode_label": "Demo Mode / Mock Mode",
        "demo_mode_help": "Enable to simulate image generation locally without calling the API.",
        "generate_btn": "Generate Image(s)",
        "canvas_subheader": "Generation Canvas",
        "error_empty_prompt": "Please enter a text prompt before generating an image.",
        "error_missing_token": "Please enter the API key, or enable Demo Mode.",
        "info_generating": "Generating {count} image(s)...",
        "spinner_connecting": "Connecting to backend and generating images...",
        "error_failed_seed": "Seed {seed}: {error}",
        "error_gen_failed": "Image generation failed:\n{err}",
        "success_gen": "Generation completed successfully!",
        "download_btn": "💾 Download (Seed {seed})",
        "placeholder_text": "🎨 Your generated images will appear here. Enter a prompt and click 'Generate Image(s)' on the left.",
        "styles": {
            "None": "None",
            "Photorealistic": "Photorealistic",
            "Cinematic": "Cinematic",
            "Anime": "Anime",
            "Watercolor": "Watercolor",
            "Cyberpunk": "Cyberpunk"
        },
        "ratios": {
            "1:1 Square": "1:1 Square",
            "16:9 Landscape": "16:9 Landscape",
            "9:16 Portrait": "9:16 Portrait",
            "4:3 Classic": "4:3 Classic",
            "3:4 Mobile Poster": "3:4 Mobile Poster"
        }
    },
    "繁體中文": {
        "title": "通用 AI 繪圖生成器",
        "subtitle": "支援 FLUX 與 Stable Diffusion (SDXL) 的精美 AI 繪圖工具。",
        "project_dashboard": "⚙️ 模型設定",
        "select_model": "選擇模型",
        "prompt_eng": "提示詞工程",
        "hf_token_label": "請輸入 Hugging Face API Token",
        "hf_verified": "已通過驗證 Hugging Face Token。",
        "prompt_label": "提示詞 (Prompt)",
        "prompt_help": "描述您想要看到的畫面，系統將根據此描述生成圖片。",
        "prompt_default": "一隻小機器人在溫馨的未來感圖書館裡看書，溫暖的燈光",
        "style_label": "藝術風格套用 (Style)",
        "aspect_ratio_label": "畫布比例 (Aspect Ratio)",
        "advanced_params": "⚙️ 進階參數設定",
        "neg_prompt_label": "負向提示詞 (Negative Prompt)",
        "seed_label": "隨機種子 (Seed)",
        "batch_count_label": "生成張數 (Batch Count)",
        "cfg_label": "提示詞引導係數 (CFG)",
        "steps_label": "推論步數 (Steps)",
        "demo_mode_label": "Demo / 模擬生圖模式",
        "demo_mode_help": "啟用此模式將在本機模擬生成圖片，不會調用外部 API。",
        "generate_btn": "開始生成圖片",
        "canvas_subheader": "繪圖生成畫布",
        "error_empty_prompt": "請在生成前輸入提示詞。",
        "error_missing_token": "請輸入 API 金鑰，或啟用 Demo 模擬生圖模式。",
        "info_generating": "正在生成 {count} 張圖片...",
        "spinner_connecting": "正在連接後端並生成圖片中...",
        "error_failed_seed": "種子 {seed}: {error}",
        "error_gen_failed": "圖片生成失敗：\n{err}",
        "success_gen": "圖片生成成功！",
        "download_btn": "💾 下載圖片 (種子 {seed})",
        "placeholder_text": "🎨 生成的圖片將會顯示在這裡。請在左側輸入提示詞並點選「開始生成圖片」。",
        "styles": {
            "None": "無風格套用",
            "Photorealistic": "寫實相片風格",
            "Cinematic": "電影質感風格",
            "Anime": "動漫二次元風格",
            "Watercolor": "水彩畫藝術風格",
            "Cyberpunk": "賽博朋克風格"
        },
        "ratios": {
            "1:1 Square": "1:1 正方形",
            "16:9 Landscape": "16:9 橫向風景",
            "9:16 Portrait": "9:16 縱向肖像",
            "4:3 Classic": "4:3 經典比例",
            "3:4 Mobile Poster": "3:4 手機海報"
        }
    }
}


def get_secret_value(key: str, default: Optional[str] = None) -> Optional[str]:
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
    max_retries = 3
    for endpoint in hf_endpoints(model_id):
        for attempt in range(max_retries):
            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=180)
            except requests.RequestException as exc:
                if attempt == max_retries - 1:
                    errors.append(f"[{endpoint}] Request failed after {max_retries} attempts: {exc}")
                time.sleep(2 * (attempt + 1))
                continue

            content_type = response.headers.get("content-type", "")
            if response.ok and content_type.startswith("image/"):
                try:
                    image = Image.open(io.BytesIO(response.content)).convert("RGB")
                    return image, ""
                except Exception as exc:
                    errors.append(f"[{endpoint}] Pillow could not open image: {exc}")
                    break

            if response.status_code in (503, 504, 429) and attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))
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
                break
            else:
                errors.append(f"[{endpoint}] HTTP {response.status_code}: {error_msg}")
                break

    return None, "\n\n".join(errors)


def make_mock_image(prompt: str, width: int, height: int, seed: int, style: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image, "RGBA")
    
    if style == "Cyberpunk":
        color_start = (15, 10, 30)
        color_end = (40, 10, 70)
        accent_color = (255, 0, 128, 100)
        accent_color2 = (0, 255, 240, 100)
    elif style == "Anime":
        color_start = (180, 210, 255)
        color_end = (255, 190, 210)
        accent_color = (255, 255, 255, 120)
        accent_color2 = (255, 220, 100, 120)
    elif style == "Watercolor":
        color_start = (248, 246, 240)
        color_end = (215, 225, 235)
        accent_color = (130, 170, 210, 60)
        accent_color2 = (210, 150, 170, 60)
    elif style in ["Photorealistic", "Cinematic"]:
        color_start = (10, 15, 25)
        color_end = (45, 35, 25)
        accent_color = (255, 180, 80, 60)
        accent_color2 = (100, 150, 200, 60)
    else:
        color_start = (20, 25, 35)
        color_end = (35, 45, 60)
        accent_color = (130, 140, 180, 70)
        accent_color2 = (180, 130, 150, 70)
        
    for y in range(height):
        t = y / height
        r = int(color_start[0] * (1 - t) + color_end[0] * t)
        g = int(color_start[1] * (1 - t) + color_end[1] * t)
        b = int(color_start[2] * (1 - t) + color_end[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
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

    border_color = (255, 255, 255, 40) if style in ["Anime", "Watercolor"] else (255, 255, 255, 20)
    draw.rectangle([20, 20, width - 20, height - 20], outline=border_color, width=4)

    title_text = f"Demo Image [{style}]"
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
        initial_sidebar_state="expanded",
    )

    # Determine language and theme first to use in styles
    if "lang" not in st.session_state:
        st.session_state.lang = "繁體中文"

    lang = st.session_state.lang
    t = TRANSLATIONS[lang]

    with st.sidebar:
        col_lang, col_theme = st.columns(2)
        with col_lang:
            lang_label = "🌐 Language" if lang == "English" else "🌐 語言"
            lang_idx = 0 if lang == "English" else 1
            lang = st.selectbox(lang_label, ["English", "繁體中文"], index=lang_idx, key="lang")
            t = TRANSLATIONS[lang]
        with col_theme:
            # 使用固定選項和 Label 以維持 widget 在語系切換時的狀態穩定性
            theme_label = "🌓 主題 / Theme"
            theme_options = ["Dark / 深色 🌙", "Light / 淺色 ☀️"]
            
            # Use boolean state for language-independent theme tracking
            if "is_light" not in st.session_state:
                st.session_state.is_light = False
            
            theme_idx = 1 if st.session_state.is_light else 0
            theme_mode = st.selectbox(theme_label, theme_options, index=theme_idx)
            st.session_state.is_light = (theme_mode == "Light / 淺色 ☀️")
            is_light = st.session_state.is_light

    if is_light:
        theme_css = """
        :root {
            --background-color: #f8fafc !important;
            --secondary-background-color: #ffffff !important;
            --text-color: #0f172a !important;
            --primary-color: #4f46e5 !important;
            --st-border-color: rgba(15, 23, 42, 0.08) !important;
        }
        
        /* Light mode adjustments */
        [data-testid="stApp"] {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
            color: #0f172a !important;
        }
        
        section[data-testid="stSidebar"] {
            background-color: rgba(241, 245, 249, 0.9) !important;
            border-right: 1px solid rgba(15, 23, 42, 0.08) !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p {
            color: #0f172a !important;
        }
        
        /* Make form elements legible in Light Mode */
        textarea, input, select, div[data-baseweb="select"], div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid rgba(15, 23, 42, 0.15) !important;
        }
        
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid rgba(15, 23, 42, 0.1) !important;
        }
        
        div[data-testid="column"] {
            background-color: rgba(255, 255, 255, 0.8) !important;
            border: 1px solid rgba(15, 23, 42, 0.08) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.03) !important;
            color: #0f172a !important;
        }

        h1, h2, h3, h4, h5, h6, p, span, li, label {
            color: #0f172a !important;
        }
        
        code {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
        }

        /* Fix selectbox dropdown options for Light Mode */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        div[role="listbox"],
        div[role="listbox"] *,
        ul[role="listbox"],
        ul[role="listbox"] * {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        div[role="option"]:hover,
        li[role="option"]:hover,
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] div[role="option"]:hover {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
        }

        /* Fix Password Show/Hide button for Light Mode (covering focus/active/state-change states) */
        div[data-baseweb="input"] button,
        div[data-baseweb="input"] button:focus,
        div[data-baseweb="input"] button:active,
        div[data-testid="stTextInput"] button,
        div[data-testid="stTextInput"] button:focus,
        div[data-testid="stTextInput"] button:active {
            background-color: transparent !important;
            color: #0f172a !important;
            border: none !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"] button:hover,
        div[data-testid="stTextInput"] button:hover {
            background-color: rgba(15, 23, 42, 0.08) !important;
        }
        """
    else:
        theme_css = """
        :root {
            --background-color: #0b0f19 !important;
            --secondary-background-color: #111827 !important;
            --text-color: #f3f4f6 !important;
            --primary-color: #6366f1 !important;
            --st-border-color: rgba(255, 255, 255, 0.08) !important;
        }
        
        /* Dark mode adjustments */
        [data-testid="stApp"] {
            background: linear-gradient(135deg, #0b0f19 0%, #1f2937 100%) !important;
            color: #f3f4f6 !important;
        }
        
        section[data-testid="stSidebar"] {
            background-color: rgba(17, 24, 39, 0.9) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p {
            color: #f3f4f6 !important;
        }
        
        /* Make form elements legible in Dark Mode */
        textarea, input, select, div[data-baseweb="select"], div[data-baseweb="select"] > div {
            background-color: #111827 !important;
            color: #f3f4f6 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }
        
        div[data-testid="stExpander"] {
            background-color: #111827 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        
        div[data-testid="column"] {
            background-color: rgba(17, 24, 39, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
            color: #f3f4f6 !important;
        }

        h1, h2, h3, h4, h5, h6, p, span, li, label {
            color: #f3f4f6 !important;
        }
        
        code {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
        }

        /* Fix selectbox dropdown options for Dark Mode */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        div[role="listbox"],
        div[role="listbox"] *,
        ul[role="listbox"],
        ul[role="listbox"] * {
            background-color: #111827 !important;
            color: #f3f4f6 !important;
        }
        div[role="option"]:hover,
        li[role="option"]:hover,
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] div[role="option"]:hover {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
        }

        /* Fix Password Show/Hide button for Dark Mode (covering focus/active/state-change states) */
        div[data-baseweb="input"] button,
        div[data-baseweb="input"] button:focus,
        div[data-baseweb="input"] button:active,
        div[data-testid="stTextInput"] button,
        div[data-testid="stTextInput"] button:focus,
        div[data-testid="stTextInput"] button:active {
            background-color: transparent !important;
            color: #f3f4f6 !important;
            border: none !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"] button:hover,
        div[data-testid="stTextInput"] button:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
        }
        """

    st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

    # Inject custom modern CSS styles for premium styling and design aesthetics
    st.markdown("""
        <style>
        /* Modern font and styling imports */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Hide Header entirely to save space */
        header, [data-testid="stHeader"], .stAppHeader {
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
            padding: 0 !important;
        }
        
        /* Disable/hide all sidebar collapse and expansion controls to keep sidebar permanently open */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        .stSidebarCollapseButton,
        section[data-testid="stSidebar"] button[aria-label="Close sidebar"],
        section[data-testid="stSidebar"] button[aria-label="Close"] {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Adjust page top padding for tight alignment */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Hide Deploy button and Toolbar in top right */
        .stAppDeployButton, .stDeployButton, .stAppToolbar, [data-testid="stAppToolbar"], #MainMenu {
            display: none !important;
        }
        
        /* Main background using Streamlit variables for Dark/Light responsiveness */
        .stApp {
            background: linear-gradient(135deg, var(--background-color) 0%, var(--secondary-background-color) 100%);
            color: var(--text-color);
        }
        
        /* Glassmorphism sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: var(--secondary-background-color) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid var(--st-border-color, rgba(128, 128, 128, 0.2));
        }
        
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {
            color: var(--text-color) !important;
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
            color: var(--text-color);
            opacity: 0.8;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 30px;
        }
        
        /* Glassmorphic Column Containers */
        div[data-testid="column"] {
            background-color: var(--secondary-background-color) !important;
            backdrop-filter: blur(10px);
            padding: 25px !important;
            border-radius: 16px !important;
            border: 1px solid var(--st-border-color, rgba(128, 128, 128, 0.2)) !important;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05);
            color: var(--text-color) !important;
        }
        
        /* Subheader and Labels */
        h3 {
            color: var(--primary-color, #4f46e5) !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
            border-bottom: 1px solid var(--st-border-color, rgba(128, 128, 128, 0.2));
            padding-bottom: 10px;
            margin-bottom: 20px !important;
        }
        
        label, p, span, li {
            color: var(--text-color) !important;
            font-weight: 500;
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
            background-color: var(--background-color) !important;
            border: 1px solid var(--st-border-color, rgba(128, 128, 128, 0.2)) !important;
            color: var(--text-color) !important;
        }
        
        textarea:focus, input:focus {
            border-color: var(--primary-color, #4f46e5) !important;
            box-shadow: 0 0 12px rgba(79, 70, 229, 0.15) !important;
        }
        
        /* Expander customization */
        div[data-testid="stExpander"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid var(--st-border-color, rgba(128, 128, 128, 0.2)) !important;
            border-radius: 12px !important;
            margin-top: 15px;
        }
        
        /* Code block readability */
        code {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='title-caption'>{t['subtitle']}</p>", unsafe_allow_html=True)

    with st.sidebar:
        st.header(t["project_dashboard"])
        
        if lang == "繁體中文":
            POPULAR_MODELS = {
                "FLUX.1 Schnell (中英文/多國語言)": "black-forest-labs/FLUX.1-schnell",
                "Stable Diffusion XL (SDXL) (僅英文)": "stabilityai/stable-diffusion-xl-base-1.0",
            }
            model_help = "選擇要使用的生成模型。"
        else:
            POPULAR_MODELS = {
                "FLUX.1 Schnell (Multilingual)": "black-forest-labs/FLUX.1-schnell",
                "Stable Diffusion XL (SDXL) (English Only)": "stabilityai/stable-diffusion-xl-base-1.0",
            }
            model_help = "Select a generation model."
        
        model_selection = st.selectbox(
            t["select_model"], 
            list(POPULAR_MODELS.keys()), 
            index=0,
            help=model_help
        )
        model_id = POPULAR_MODELS[model_selection]
        
        model_id_label = "Model ID:" if lang == "English" else "模型 ID:"
        st.markdown(
            f"<p style='font-size: 0.9rem; margin-top: -5px; opacity: 0.85; margin-bottom: 2px;'>{model_id_label}</p>"
            f"<p style='font-size: 0.9rem; margin-top: 0px; opacity: 0.95; word-break: break-all;'><strong>{model_id}</strong></p>",
            unsafe_allow_html=True
        )
            
        st.markdown("---")
        github_link = get_secret_value("GITHUB_LINK", DEFAULT_GITHUB_LINK)
        st.markdown(f"🔗 **GitHub:** [HuggingFace-Practice]({github_link})")

    # Initialize session state
    if "prev_prompt" not in st.session_state:
        st.session_state.prev_prompt = ""
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []

    col_left, col_right = st.columns([1.0, 1.2])

    with col_left:
        st.subheader(t["prompt_eng"])
        
        # Access API Token for Hugging Face
        api_key = get_secret_value("HF_TOKEN", None)
        if not api_key:
            api_key = st.text_input(t["hf_token_label"], type="password", key="hf_token_input")
        else:
            st.success(t["hf_verified"])
            
        prompt = st.text_area(
            t["prompt_label"],
            value=t["prompt_default"],
            height=100,
            help=t["prompt_help"],
        )
        
        # Get localized style names map
        style_map = t["styles"]
        inv_style_map = {v: k for k, v in style_map.items()}
        
        # Display localized list
        selected_style_name = st.selectbox(t["style_label"], list(style_map.values()), index=1)
        # Map back to English key
        style = inv_style_map[selected_style_name]
        
        # Get localized aspect ratios names map
        ratio_map = t["ratios"]
        inv_ratio_map = {v: k for k, v in ratio_map.items()}
        
        # Display localized list
        selected_ratio_name = st.selectbox(t["aspect_ratio_label"], list(ratio_map.values()), index=0)
        # Map back to English key
        aspect_ratio = inv_ratio_map[selected_ratio_name]
        
        width, height = ASPECT_RATIOS[aspect_ratio]
        final_prompt = build_prompt(prompt, style)
        final_payload_prompt = final_prompt

        # Collapse advanced settings inside an expander to keep layout clean and premium
        with st.expander(t["advanced_params"], expanded=False):
            negative_prompt = st.text_area(
                t["neg_prompt_label"],
                value="blurry, low quality, distorted, watermark, text artifacts, bad anatomy",
                height=70,
            )
            seed = st.number_input(t["seed_label"], min_value=0, max_value=2_147_483_647, value=42, step=1)
            number_of_images = st.slider(t["batch_count_label"], min_value=1, max_value=4, value=1)
            guidance_scale = st.slider(t["cfg_label"], min_value=1.0, max_value=15.0, value=7.0, step=0.5)
            steps = st.slider(t["steps_label"], min_value=10, max_value=60, value=30, step=5)
            
            demo_mode = st.checkbox(
                t["demo_mode_label"],
                value=False,
                help=t["demo_mode_help"],
            )

        generate = st.button(t["generate_btn"], type="primary")

    with col_right:
        st.subheader(t["canvas_subheader"])
        
        if generate:
            if not prompt.strip():
                st.error(t["error_empty_prompt"])
            elif not api_key and not demo_mode:
                st.error(t["error_missing_token"])
            else:
                # Clear previous cached images
                st.session_state.generated_images = []
                st.info(t["info_generating"].format(count=number_of_images))
                
                # Parallel generation using ThreadPoolExecutor
                def generate_single_image(index):
                    current_seed = int(seed) + index
                    if demo_mode:
                        img = make_mock_image(final_prompt, width, height, current_seed, style)
                        return {"image": img, "seed": current_seed, "error": None}
                        
                    payload = build_payload(
                        prompt=final_payload_prompt,
                        negative_prompt=negative_prompt,
                        width=width,
                        height=height,
                        seed=current_seed,
                        guidance_scale=float(guidance_scale),
                        steps=int(steps),
                    )
                    img, err = call_hugging_face(str(api_key), payload, model_id)
                    return {"image": img, "seed": current_seed, "error": err}

                with st.spinner(t["spinner_connecting"]):
                    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_images) as executor:
                        # Submit all tasks
                        futures = [executor.submit(generate_single_image, i) for i in range(number_of_images)]
                        # Wait for all to complete
                        results = [future.result() for future in futures]
                
                # Check results
                success_images = []
                errors = []
                for res in results:
                    if res["image"] is not None:
                        success_images.append(res)
                    else:
                        errors.append(t["error_failed_seed"].format(seed=res['seed'], error=res['error']))
                
                # Cache results in session state
                st.session_state.generated_images = success_images
                
                if errors:
                    for err in errors:
                        st.error(t["error_gen_failed"].format(err=err))

        # Render generated images from cache (persists across download interactions)
        if st.session_state.generated_images:
            st.success(t["success_gen"])
            
            num_cols = min(len(st.session_state.generated_images), 2)
            grid_cols = st.columns(num_cols)
            
            for idx, item in enumerate(st.session_state.generated_images):
                img = item["image"]
                s_val = item["seed"]
                with grid_cols[idx % num_cols]:
                    st.image(img, caption=f"Seed: {s_val}", use_container_width=True)
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    st.download_button(
                        label=t["download_btn"].format(seed=s_val),
                        data=buffer.getvalue(),
                        file_name=f"generated_{s_val}.png",
                        mime="image/png",
                        key=f"download_{s_val}_{idx}"
                    )
        else:
            st.info(t["placeholder_text"])


if __name__ == "__main__":
    main()
