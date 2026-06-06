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
        "title": "AI Image Generator",
        "subtitle": "A modern AI Image Generator supporting FLUX and Stable Diffusion (SDXL).",
        "project_dashboard": "Model Settings",
        "select_model": "Select Model",
        "prompt_eng": "Prompt Engineering",
        "hf_token_label": "Enter your Hugging Face API Token",
        "hf_verified": "Hugging Face API token verified.",
        "prompt_label": "Text Prompt (Simple input)",
        "prompt_help": "Describe what you want to see. The app will use this to generate the image.",
        "prompt_default": "A small robot reading a book in a cozy futuristic library, warm lighting",
        "style_label": "Aesthetic Style Overlay",
        "aspect_ratio_label": "Canvas Aspect Ratio",
        "advanced_params": "Advanced Parameters",
        "neg_prompt_label": "Negative Prompt",
        "neg_prompt_default": "blurry, low quality, distorted, watermark, text artifacts, bad anatomy",
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
        "download_btn": "Download (Seed {seed})",
        "placeholder_text": "Your generated images will appear here. Enter a prompt and click 'Generate Image(s)' on the left.",
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
        "title": "AI 繪圖生成器",
        "subtitle": "支援 FLUX 與 Stable Diffusion (SDXL) 的精美 AI 繪圖工具。",
        "project_dashboard": "模型設定",
        "select_model": "選擇模型",
        "prompt_eng": "提示詞工程",
        "hf_token_label": "請輸入 Hugging Face API Token",
        "hf_verified": "已通過驗證 Hugging Face Token。",
        "prompt_label": "提示詞 (Prompt)",
        "prompt_help": "描述您想要看到的畫面，系統將根據此描述生成圖片。",
        "prompt_default": "一隻小機器人在溫馨的未來感圖書館裡看書，溫暖的燈光",
        "style_label": "藝術風格套用 (Style)",
        "aspect_ratio_label": "畫布比例 (Aspect Ratio)",
        "advanced_params": "進階參數設定",
        "neg_prompt_label": "負向提示詞",
        "neg_prompt_default": "模糊、低畫質、變形、浮水印、文字殘影、肢體畸形",
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
        "download_btn": "下載圖片 (種子 {seed})",
        "placeholder_text": "生成的圖片將會顯示在這裡。請在左側輸入提示詞並點選「開始生成圖片」。",
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
        page_title="AI Image Generator",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "lang" not in st.session_state:
        st.session_state.lang = "繁體中文"
    if "is_light" not in st.session_state:
        st.session_state.is_light = False

    lang = st.session_state.lang
    t = TRANSLATIONS[lang]

    with st.sidebar:
        col_lang, col_theme = st.columns(2)
        with col_lang:
            st.markdown(f"<p style='font-size:0.85rem; margin-bottom:5px; opacity:0.8; font-weight:600;'>{'🌐 Language' if lang == 'English' else '🌐 語言'}</p>", unsafe_allow_html=True)
            lang_toggle_label = "English" if lang == "繁體中文" else "繁體中文"
            if st.button(lang_toggle_label, use_container_width=True, key="lang_toggle_btn"):
                st.session_state.lang = "English" if lang == "繁體中文" else "繁體中文"
                st.rerun()
        with col_theme:
            st.markdown(f"<p style='font-size:0.85rem; margin-bottom:5px; opacity:0.8; font-weight:600;'>{'🌓 Theme' if lang == 'English' else '🌓 主題'}</p>", unsafe_allow_html=True)
            if st.session_state.is_light:
                theme_btn_label = "🌙 Dark" if lang == "English" else "🌙 深色"
            else:
                theme_btn_label = "☀️ Light" if lang == "English" else "☀️ 淺色"
            
            if st.button(theme_btn_label, use_container_width=True, key="theme_toggle_btn"):
                st.session_state.is_light = not st.session_state.is_light
                st.rerun()

    lang = st.session_state.lang
    t = TRANSLATIONS[lang]
    is_light = st.session_state.is_light

    if is_light:
        # A stunning light theme using a soft, modern pastel beige/sand gradient
        bg_gradient = "linear-gradient(135deg, #fdfbf7 0%, #f5efe6 100%)"
        sidebar_bg = "rgba(245, 239, 230, 0.75)"
        sidebar_border = "rgba(175, 143, 98, 0.15)"
        text_color = "#3d352e"
        primary_color = "#af8f62"
        border_color = "rgba(175, 143, 98, 0.2)"
        form_element_bg = "#ffffff"
        number_btn_bg = "#f5efe6"
        number_btn_hover = "#eaddcf"
        checkbox_border = "rgba(175, 143, 98, 0.5)"
        expander_summary_bg = "rgba(245, 239, 230, 0.85)"
        column_bg = "rgba(255, 255, 255, 0.7)"
        code_bg = "#f5efe6"
        popover_bg = "#ffffff"
        popover_hover = "#f5efe6"
        password_hover = "rgba(175, 143, 98, 0.08)"
    else:
        # Warm espresso dark background with zero blue/purple tint
        bg_gradient = "linear-gradient(135deg, #181512 0%, #2a241f 100%)"
        sidebar_bg = "rgba(24, 21, 18, 0.9)"
        sidebar_border = "rgba(255, 255, 255, 0.06)"
        text_color = "#f3efe9"
        primary_color = "#dfc39e"
        border_color = "rgba(255, 255, 255, 0.15)"
        form_element_bg = "#1e1915"
        number_btn_bg = "#2a241f"
        number_btn_hover = "#3a322b"
        checkbox_border = "rgba(255, 255, 255, 0.3)"
        expander_summary_bg = "#2a241f"
        column_bg = "rgba(30, 25, 21, 0.8)"
        code_bg = "#2a241f"
        popover_bg = "#1e1915"
        popover_hover = "#2a241f"
        password_hover = "rgba(223, 195, 158, 0.1)"

    # Single unified CSS template using Python string formatting
    st.markdown(f"""
        <style>
        /* ========================================================================= */
        /* CSS_SECTION_1: FONTS_AND_ICONS                                            */
        /* ========================================================================= */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

        /* Root Variables */
        :root {{
            --background-color: {form_element_bg} !important;
            --text-color: {text_color} !important;
            --primary-color: {primary_color} !important;
            --st-border-color: {border_color} !important;
        }}

        /* Apply custom font to text-bearing elements only, preserving icon fonts */
        html, body, [class*="css"],
        h1, h2, h3, h4, h5, h6, p, li, label,
        input, textarea, select, button,
        div[data-baseweb="select"],
        div[data-testid="stMarkdownContainer"],
        .stMarkdown, .stTextInput, .stTextArea, .stSelectbox,
        .stSlider, .stNumberInput, .stCheckbox {{
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", "Segoe UI Emoji", "Segoe UI Symbol", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
        }}

        /* Apply font to span elements EXCEPT Material Icons used by Streamlit for icons */
        span:not([class*="material"]):not([data-icon]):not([data-testid="stIconMaterial"]):not(.ed4y4ls0):not(.e1nzilvr5) {{
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", "Segoe UI Emoji", "Segoe UI Symbol", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
        }}

        /* Protect Material Icons / Material Symbols font from being overridden */
        [class*="material-symbols"],
        [class*="material-icons"],
        [data-testid="stIconMaterial"],
        .ed4y4ls0,
        .e1nzilvr5 {{
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }}


        /* ========================================================================= */
        /* CSS_SECTION_2: GLOBAL_APP_LAYOUT                                          */
        /* ========================================================================= */
        [data-testid="stApp"], .stApp {{
            background: {bg_gradient} !important;
            color: {text_color} !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {sidebar_border} !important;
        }}

        section[data-testid="stSidebar"] .stMarkdown, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] p {{
            color: {text_color} !important;
        }}

        header, [data-testid="stHeader"], .stAppHeader {{
            display: none !important;
        }}

        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        .stSidebarCollapseButton,
        section[data-testid="stSidebar"] button[aria-label="Close sidebar"],
        section[data-testid="stSidebar"] button[aria-label="Close"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }}

        .stAppDeployButton, .stDeployButton, .stAppToolbar, [data-testid="stAppToolbar"], #MainMenu {{
            display: none !important;
        }}

        /* Title styling with glowing champagne-bronze gradient */
        h1 {{
            background: linear-gradient(90deg, #c8a27c, #8e6e53);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -1px;
            font-size: 3rem !important;
            margin-bottom: 5px !important;
            text-align: center;
        }}
        
        .title-caption {{
            color: {text_color};
            opacity: 0.8;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 30px;
        }}


        /* ========================================================================= */
        /* CSS_SECTION_3: FORM_COMPONENTS                                            */
        /* ========================================================================= */
        
        /* Force text color on all text-bearing tags globally for dark/light contrast */
        h2, h4, h5, h6, p, span, li, label, .stMarkdown, .stMarkdown p, .stMarkdown span {{
            color: {text_color} !important;
        }}
        
        /* Base styles for user input widgets */
        textarea, 
        select,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {{
            background-color: {form_element_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
        }}

        /* BaseWeb styled component wrappers (Inputs and Selectboxes) */
        div[data-baseweb="select"],
        div[data-baseweb="input"],
        div[data-baseweb="textarea"] {{
            background-color: {form_element_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
        }}

        /* Make all nested child elements inside form fields inherit transparency to prevent overlays */
        div[data-baseweb="select"] *,
        div[data-baseweb="input"] *,
        div[data-baseweb="textarea"] * {{
            background-color: transparent !important;
            color: {text_color} !important;
        }}

        /* Keep dropdown menu list popover options styled */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        div[role="listbox"],
        div[role="listbox"] *,
        ul[role="listbox"],
        ul[role="listbox"] * {{
            background-color: {popover_bg} !important;
            color: {text_color} !important;
        }}
        div[role="option"]:hover,
        li[role="option"]:hover,
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] div[role="option"]:hover {{
            background-color: {popover_hover} !important;
            color: {text_color} !important;
        }}

        /* Ensure all text under sliders is readable */
        .stSlider p, .stSlider span, .stSlider div {{
            color: {text_color} !important;
        }}

        /* Number input +/- buttons styling */
        div[data-testid="stNumberInput"] button,
        div[data-baseweb="input"] button[kind="minimal"] {{
            background-color: {number_btn_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
        }}

        div[data-testid="stNumberInput"] button:hover {{
            background-color: {number_btn_hover} !important;
        }}

        /* Checkbox styling */
        div[data-testid="stCheckbox"] label span[data-testid="stCheckbox-label"] {{
            color: {text_color} !important;
        }}
        div[role="checkbox"],
        div[data-baseweb="checkbox"] div {{
            border-color: {checkbox_border} !important;
        }}


        /* ========================================================================= */
        /* CSS_SECTION_4: CONTAINERS_AND_EXPANDERS                                   */
        /* ========================================================================= */
        
        /* Column containers */
        div[data-testid="column"] {{
            background-color: {column_bg} !important;
            border: 1px solid {border_color} !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05) !important;
            color: {text_color} !important;
            backdrop-filter: blur(10px);
            padding: 25px !important;
            border-radius: 16px !important;
            margin-bottom: 20px;
        }}

        h3 {{
            color: {primary_color} !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
            border-bottom: 1px solid {border_color};
            padding-bottom: 10px;
            margin-bottom: 20px !important;
        }}

        /* Expander customization */
        div[data-testid="stExpander"] {{
            background-color: {form_element_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 12px !important;
            margin-top: 15px;
        }}
        div[data-testid="stExpander"] summary {{
            background-color: {expander_summary_bg} !important;
            color: {text_color} !important;
        }}
        div[data-testid="stExpander"] summary * {{
            background-color: transparent !important;
            color: {text_color} !important;
            fill: {text_color} !important;
        }}
        div[data-testid="stExpander"] summary svg {{
            fill: {text_color} !important;
            stroke: {text_color} !important;
        }}
        div[data-testid="stExpander"] > details > div {{
            background-color: {form_element_bg} !important;
        }}
        div[data-testid="stExpander"] [class*="st-"] {{
            background-color: transparent !important;
        }}

        code {{
            background-color: {code_bg} !important;
            color: {text_color} !important;
        }}


        /* ========================================================================= */
        /* CSS_SECTION_5: INTERACTIVE_BUTTONS                                        */
        /* ========================================================================= */
        
        /* Primary button styling with micro-animations and glowing champagne-bronze gradient */
        button[kind="primary"], .stBaseButton-primary {{
            background: linear-gradient(135deg, #c8a27c 0%, #8e6e53 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 30px !important;
            font-weight: 600 !important;
            width: 100%;
            font-size: 1.1rem !important;
            margin-top: 10px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 15px rgba(200, 162, 124, 0.25) !important;
        }}
        
        button[kind="primary"]:hover, .stBaseButton-primary:hover {{
            transform: translateY(-2px) scale(1.01) !important;
            box-shadow: 0 6px 22px rgba(200, 162, 124, 0.4) !important;
            background: linear-gradient(135deg, #c8a27c 0%, #8e6e53 100%) !important;
            color: white !important;
        }}
        
        button[kind="primary"]:active, .stBaseButton-primary:active {{
            transform: translateY(1px) !important;
        }}

        /* Secondary button styling (like toggle buttons and download buttons) */
        button[kind="secondary"], .stBaseButton-secondary, div.stButton > button:not([kind="primary"]) {{
            background-color: transparent !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            font-size: 0.95rem !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease !important;
        }}
        
        button[kind="secondary"]:hover, .stBaseButton-secondary:hover, div.stButton > button:not([kind="primary"]):hover {{
            background-color: {password_hover} !important;
            border-color: {primary_color} !important;
            color: {primary_color} !important;
            transform: translateY(-1px) !important;
        }}

        /* GitHub Button Hover State */
        .github-btn:hover {{
            opacity: 0.85 !important;
            border-color: var(--primary-color) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }}

        /* Password Show/Hide button */
        div[data-baseweb="input"] button,
        div[data-baseweb="input"] button:focus,
        div[data-baseweb="input"] button:active,
        div[data-testid="stTextInput"] button,
        div[data-testid="stTextInput"] button:focus,
        div[data-testid="stTextInput"] button:active {{
            background-color: transparent !important;
            color: {text_color} !important;
            border: none !important;
            box-shadow: none !important;
        }}
        div[data-baseweb="input"] button:hover,
        div[data-testid="stTextInput"] button:hover {{
            background-color: {password_hover} !important;
        }}

        textarea:focus, input:focus {{
            border-color: {primary_color} !important;
            box-shadow: 0 0 12px rgba(200, 162, 124, 0.15) !important;
        }}
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
        
        if "selected_model_id" not in st.session_state:
            st.session_state.selected_model_id = "black-forest-labs/FLUX.1-schnell"
        
        model_ids = list(POPULAR_MODELS.values())
        if st.session_state.selected_model_id in model_ids:
            model_idx = model_ids.index(st.session_state.selected_model_id)
        else:
            model_idx = 0
            
        model_selection = st.selectbox(
            t["select_model"], 
            list(POPULAR_MODELS.keys()), 
            index=model_idx,
            help=model_help,
            key=f"model_selection_{lang}"
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
        github_html = f"""
        <div id="github-link-outer-container" style="display: flex; justify-content: center; margin-top: 15px;">
            <a id="github-link-anchor" href="{github_link}" target="_blank" style="text-decoration: none; width: 100%;">
                <div id="github-link-btn" class="github-btn" style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    background: var(--background-color);
                    border: 1px solid var(--st-border-color);
                    border-radius: 8px;
                    padding: 10px 16px;
                    color: var(--text-color);
                    transition: all 0.2s ease;
                    cursor: pointer;
                ">
                    <svg height="18" width="18" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                    <span id="github-link-btn-text" style="font-weight: 600; font-size: 0.9rem;">GitHub</span>
                </div>
            </a>
        </div>
        """
        st.markdown(github_html, unsafe_allow_html=True)

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
        
        if "selected_style" not in st.session_state:
            st.session_state.selected_style = "Photorealistic"
            
        style_keys = list(style_map.keys())
        if st.session_state.selected_style in style_keys:
            style_idx = style_keys.index(st.session_state.selected_style)
        else:
            style_idx = 1
            
        # Display localized list
        selected_style_name = st.selectbox(
            t["style_label"], 
            list(style_map.values()), 
            index=style_idx,
            key=f"style_selection_{lang}"
        )
        # Map back to English key
        style = inv_style_map[selected_style_name]
        st.session_state.selected_style = style
        
        # Get localized aspect ratios names map
        ratio_map = t["ratios"]
        inv_ratio_map = {v: k for k, v in ratio_map.items()}
        
        if "selected_ratio" not in st.session_state:
            st.session_state.selected_ratio = "1:1 Square"
            
        ratio_keys = list(ratio_map.keys())
        if st.session_state.selected_ratio in ratio_keys:
            ratio_idx = ratio_keys.index(st.session_state.selected_ratio)
        else:
            ratio_idx = 0
            
        # Display localized list
        selected_ratio_name = st.selectbox(
            t["aspect_ratio_label"], 
            list(ratio_map.values()), 
            index=ratio_idx,
            key=f"ratio_selection_{lang}"
        )
        # Map back to English key
        aspect_ratio = inv_ratio_map[selected_ratio_name]
        st.session_state.selected_ratio = aspect_ratio
        
        width, height = ASPECT_RATIOS[aspect_ratio]
        final_prompt = build_prompt(prompt, style)
        final_payload_prompt = final_prompt

        # Collapse advanced settings inside an expander to keep layout clean and premium
        with st.expander(t["advanced_params"], expanded=False):
            negative_prompt = st.text_area(
                t["neg_prompt_label"],
                value=t["neg_prompt_default"],
                height=70,
                key=f"negative_prompt_widget_{lang}"
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
