# 🎨 通用 AI 繪圖生成器

這是基於 Streamlit 建立的現代化 AI 繪圖網頁應用程式，專注於提供極致簡潔且穩定的操作體驗。

🔗 **線上展示 (Live Demo)**: [https://huggingface-practice-dec591nyc.streamlit.app](https://huggingface-practice-dec591nyc.streamlit.app)

---

## 🚀 核心特色
- **雙模型支援**: 支援 **FLUX.1 Schnell** (中英文/多國語言) 與 **Stable Diffusion XL (SDXL)** (僅英文) 免費伺服器生圖。
- **高質感介面**: 精美磨砂玻璃風格 (Glassmorphism)，支援側邊欄一鍵切換**繁體中文/英文**與**深色/淺色**主題。
- **固定側邊欄**: 側邊欄（模型設定）鎖定展開，防止收合後無法復原的排版問題。
- **多圖並行生成**: 支援多張圖片並行生成，大幅減少等待時間。
- **快取持久化**: 生成圖片與金鑰安全快取，防止網頁重整時遺失。

---

## 🛠️ 本機快速啟動
1. **複製專案**:
   ```bash
   git clone https://github.com/dec591nyc/HuggingFace-Practice.git
   cd HuggingFace-Practice
   ```
2. **建立虛擬環境與安裝**:
   ```bash
   python -m venv .venv
   # Windows 啟動:
   .\.venv\Scripts\activate
   # Mac/Linux 啟動:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```
3. **執行專案**:
   ```bash
   streamlit run app.py
   ```

---

## 🔒 憑證配置
在本機開發時，可在專案根目錄建立 `.streamlit/secrets.toml`，以避免每次都要手動輸入 Token：
```toml
HF_TOKEN = "您的_Hugging_Face_Token"
```
