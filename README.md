# 🎨 Universal AI Image Generator | 通用 AI 繪圖生成器

A premium, state-of-the-art Streamlit Web Application featuring a modern UI layout, dual-language localization, dynamic light/dark theme toggles, multi-model backend execution (Hugging Face Serverless Inference API), and advanced custom **ComfyUI** workflow integrations.

這是一個精美且現代化的 Streamlit 網頁應用程式，支援中英文雙語切換、亮暗主題變更，並支援多模型（FLUX.1、Stable Diffusion XL、太乙中文等）與自訂 **ComfyUI** 工作流後端。

---

## 🚀 Core Features | 核心特色

### 1. Multi-Model Support | 多模型與後端支援
* **FLUX.1 Schnell (中英文/多國語言)**: High-fidelity, fast text-to-image generation.
* **Stable Diffusion XL (SDXL) & v1.5 (僅英文)**: Classic high-contrast image generation.
* **Taiyi Stable Diffusion 太乙 (僅中文)**: Specialized Chinese semantic text-to-image model.
* **Custom HF Model (自訂模型)**: Input any Hugging Face model ID directly to run serverless inference.
* **ComfyUI API Integration (工作流整合)**: Run your own local or remote ComfyUI server. The app automatically templates prompt inputs, seed, width, height, and negative prompts into your exported API JSON payload.

### 2. Premium Design & Dual Themes | 精美設計與雙網頁主題
* **Dynamic Dark/Light Mode**: Select side-by-side language and theme options. Switching modes dynamically injects custom CSS variables to style backgrounds, inputs, dropdown list selections, and expanders.
* **Glassmorphism Styling**: Sleek transparent headers, card-like column panels, and soft shadows built on top of the modern **Outfit** font family.
* **Locked Sidebar**: The sidebar settings panel is locked to the expanded state, preventing collapse errors and maintaining a fixed, structured workspace.
* **Canvas-Style Split Layout**: Left column for inputting prompts & parameters; right column serves as the image generation canvas.

### 3. Localization | 中英文在地化語系
* Instantly toggle between **English** and **繁體中文** via the sidebar.
* Fully localized select boxes (including aspect ratios and art styles) mapping automatically to English parameter keys in the backend.

### 4. Advanced Engine Performance | 進階效能與穩定機制
* **Parallel Image Generation**: Concurrently generates multiple images using Python `ThreadPoolExecutor` to minimize waiting times.
* **Retry Logic**: Built-in exponential backoff retry mechanism (up to 3 attempts) for serverless API errors (HTTP 503/429).
* **State Caching & Persistence**: Cached in-memory via `st.session_state` to prevent image loss upon widget redraws or download actions.
* **Secure Credentials**: API Keys are input directly on-screen or loaded via system environments, with no hardcoded credentials for public deployment safety.

---

## 🛠️ Local Installation & Run | 本機安裝與執行

### 1. Clone the Repository | 複製儲存庫
```bash
git clone https://github.com/dec591nyc/HuggingFace-Practice.git
cd HuggingFace-Practice
```

### 2. Create Virtual Environment | 建立虛擬環境
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies | 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 4. Run the Application | 啟動網頁
```bash
streamlit run app.py
```

---

## 🔒 Security & Secrets | 安全與配置指南

To run without inputting keys on screen during local development, you can create a `.streamlit/secrets.toml` file in the root of the project:

若要在本機開發時免手動輸入 API 金鑰，可在專案根目錄下建立 `.streamlit/secrets.toml` 檔案：

```toml
# Hugging Face Access Token
HF_TOKEN = "your_hugging_face_token_here"
```

*Note: The `.streamlit/secrets.toml` file is configured in `.gitignore` and will never be pushed to GitHub to prevent key leaks.*

*注意：`.streamlit/secrets.toml` 已預設加入 Git 忽略清單，絕不會被推送至 GitHub 以防金鑰外洩。*

---

## 🎨 Creative Parameter Settings | 創意參數與畫布設定

* **Aspect Ratios**: Supports 1:1 Square, 16:9 Landscape, 9:16 Portrait, 4:3 Classic, and 3:4 Mobile Poster.
* **Art Style Overlay**: Supports Anime, Cyberpunk, Watercolor, Photorealistic, Cinematic, or None.
* **NVIDIA Cosmos 3 Format**: Support for Cosmos 3 structural JSON prompt upsampling (Scene subjects, Background details, Comprehensive caption, Resolution metadata, and Aspect ratio parameters).
