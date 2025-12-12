import streamlit as st
import requests
import json
import datetime
import csv
import os
import time

# --- 1. KONFIGURASI API KEY (HARDENED SECURITY) ---
# Mengambil KUNCI DARI STREAMLIT SECRETS (Wajib Terisi di Settings Streamlit!)
# Jika kunci gagal dimuat, aplikasi tidak akan crash, tapi menampilkan error yang jelas.
try:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except KeyError:
    # Set nilai default yang pasti gagal, agar logic error di tombol bisa menangkapnya.
    DEEPSEEK_API_KEY = "KEY_NOT_FOUND_IN_SECRETS"

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"

# ... (Baris 15)
st.set_page_config(
    layout="wide", 
    page_title="Python Code Audit: Fix Bugs, Security & Performance Optimizer AI", # <--- GANTI BARIS INI (17)
    page_icon="⚡"
)
# ...
# CSS untuk Tampilan Premium & Cepat
st.markdown("""
<style>
    .main-header {font-size: 2.2rem !important; color: #000000; font-weight: 800;}
    .sub-header {font-size: 1.1rem !important; color: #424242; font-weight: 500;}
    .metric-box {border: 1px solid #e0e0e0; padding: 10px; border-radius: 5px; text-align: center;}
    .stTextArea textarea {font-family: 'Consolas', monospace; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGGING SYSTEM (PENCATAT AKTIVITAS) ---
def log_activity(language, status, code_len, processing_time):
    file_name = "business_data.csv"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Time", "Language", "Code Length", "Process Time (s)", "Status"])
        writer.writerow([timestamp, language, code_len, f"{processing_time:.2f}", status])

# --- 4. SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.title("⚡ Speed Control")
    st.markdown("### 🌍 Target Market")
    
    target_language = st.selectbox(
        "Client's Region:",
        (
            "🇺🇸 English (Global Standard)",
            "🇮🇩 Indonesia (South East Asia)",
            "🇧🇷 Portuguese (Brazil - Major Market)",
            "🇪🇸 Spanish (LATAM/Europe)",
            "🇮🇳 Hindi (India - Tech Hub)",
            "🇷🇺 Russian (Eastern Europe)",
            "🇨🇳 Chinese (Asia Tech)",
            "🇯🇵 Japanese (High Value)",
        )
    )
    
    st.markdown("---")
    
    # STATUS SERVER (HANYA AKAN ON JIKA API KEY VALID)
    if DEEPSEEK_API_KEY != "KEY_NOT_FOUND_IN_SECRETS":
        st.success("✅ **Server Status: ONLINE**")
    else:
        st.error("❌ **Server Status: OFFLINE (API Key Missing)**")

    # STATISTIK BISNIS REAL-TIME
    if os.path.isfile("business_data.csv"):
        st.markdown("### 📊 Business Performance")
        with open("business_data.csv", "r") as f:
            total_clients = sum(1 for row in f) - 1
        st.metric("Clients Served", total_clients)

# --- 5. MAIN INTERFACE ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">⚡ CodeGuard Ultimate</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">AI-Powered Rapid Security Audit & Optimization Engine</p>', unsafe_allow_html=True)

with col2:
    st.markdown("### 🚀 Speed Mode")
    st.caption("Latency: < 9s Optimized")

# --- 6. INPUT AREA ---
code_input = st.text_area(
    "👇 PASTE CODE TO AUDIT:", 
    height=300,
    placeholder=f"// Paste Python/JS/Java code here...\n// AI will audit instantly in {target_language}..."
)

# --- 7. LOGIKA AI (TURBO PROMPT) ---
def get_audit_result(code_snippet, language):
    if not code_snippet: return None, "⚠️ Empty Code"
    
    master_prompt = f"""
    ROLE: Senior Code Auditor.
    TASK: Audit this code for Fatal Bugs, Security Risks, and Performance.
    OUTPUT LANGUAGE: {language}.
    
    FORMAT (Strict Markdown):
    
    ## 📊 Executive Summary
    - **Security:** (0-100) | **Performance:** (0-100)
    - **Verdict:** (Safe/Risky)
    
    ## 🚨 Critical Issues (Brief & Direct)
    - List fatal bugs & security holes.
    
    ## ⚡ Optimization (Speed Fix)
    - How to make it O(1) or O(n)?
    
    ## ✅ Final Fixed Code
    (Provide full working code with comments in {language}).
    
    CODE:
    {code_snippet}
    """
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {
        "model": "deepseek-coder", 
        "messages": [{"role": "user", "content": master_prompt}],
        "stream": False
    }

    try:
        response = requests.post(DEEPSEEK_ENDPOINT, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'], None
    except Exception as e:
        return None, str(e)

# --- 8. ACTION BUTTON (DENGAN TIMER & KEAMANAN AKHIR) ---
if st.button("🚀 INSTANT AUDIT (START)", type="primary"):
    
    # ⚠️ KEAMANAN: Cek apakah API Key berhasil dimuat dari brankas
    if DEEPSEEK_API_KEY == "KEY_NOT_FOUND_IN_SECRETS":
        st.error("❌ ERROR SISTEM: API Key Belum TERSIMPAN di Streamlit Secrets. Silakan cek Advanced Settings!")
        st.stop()

    start_time = time.time()
    
    with st.spinner(f"⚡ Processing logic in {target_language}..."):
        result, error = get_audit_result(code_input, target_language)
        
    end_time = time.time()
    duration = end_time - start_time
    
    if error:
        st.error(f"System Error: {error}")
        log_activity(target_language, "FAILED", len(code_input), duration)
    else:
        # Tampilkan Hasil
        st.success(f"✅ Audit Complete in {duration:.2f} seconds!")
        st.markdown(result)
        log_activity(target_language, "SUCCESS", len(code_input), duration)