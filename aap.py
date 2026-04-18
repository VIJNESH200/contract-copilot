import streamlit as st
import fitz
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ---- PAGE SETUP ----
st.set_page_config(
    page_title="Contract Copilot",
    page_icon="⚖️",
    layout="centered"
)

# ---- CUSTOM STYLING ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: #0f0f0f;
        color: #e8e8e8;
    }
    .main { background-color: #0f0f0f; }

    h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem !important;
        color: #f5c842 !important;
        letter-spacing: -1px;
    }
    .subtitle {
        font-family: 'IBM Plex Mono', monospace;
        color: #888;
        font-size: 0.85rem;
        margin-top: -16px;
        margin-bottom: 32px;
    }
    .risk-high {
        background: #2a0a0a;
        border-left: 4px solid #ff4444;
        padding: 16px 20px;
        border-radius: 4px;
        margin-bottom: 16px;
    }
    .risk-medium {
        background: #1f1a0a;
        border-left: 4px solid #f5c842;
        padding: 16px 20px;
        border-radius: 4px;
        margin-bottom: 16px;
    }
    .risk-low {
        background: #0a1f0a;
        border-left: 4px solid #44bb44;
        padding: 16px 20px;
        border-radius: 4px;
        margin-bottom: 16px;
    }
    .clause-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #888;
        margin-bottom: 4px;
    }
    .badge-high { color: #ff4444; font-weight: 600; font-size: 0.8rem; }
    .badge-medium { color: #f5c842; font-weight: 600; font-size: 0.8rem; }
    .badge-low { color: #44bb44; font-weight: 600; font-size: 0.8rem; }
    .quote-box {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #aaa;
        background: #1a1a1a;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 8px 0;
    }
    .stButton > button {
        background-color: #f5c842;
        color: #0f0f0f;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        border: none;
        padding: 12px 32px;
        border-radius: 4px;
        font-size: 0.9rem;
        letter-spacing: 1px;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #e6b800;
        color: #0f0f0f;
    }
    .stat-box {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 16px;
        text-align: center;
    }
    .stat-number {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        line-height: 1;
    }
    .stat-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---- FUNCTIONS ----
def extract_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyse_contract(text):
    client = genai.Client(api_key=API_KEY)
    prompt = f"""
You are a legal risk analyst helping small business owners understand contracts.
Analyse this contract and find risky, unusual or predatory clauses.

For each risky clause found, respond in this EXACT format:

CLAUSE: [short title]
QUOTE: [exact words from contract]
EXPLANATION: [plain English, max 2 sentences]
RISK: [HIGH or MEDIUM or LOW]
REASON: [one sentence why it's risky]
---

Focus on: hidden fees, auto-renewals, termination terms, liability limits, 
predatory interest rates, one-sided obligations.

Contract:
{text[:12000]}
"""
    response = client.models.generate_content(
        model="gemma-4-26b-a4b-it",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction="You are a contract risk analyser. Output ONLY the structured clause analysis in the exact format requested. No disclaimers, no preamble, no extra commentary, no markdown formatting outside the structure. Start directly with CLAUSE:",
            max_output_tokens=3000,
            temperature=0.1
        )
    )
    return response.text

def parse_clauses(raw_text):
    clauses = []
    blocks = raw_text.strip().split("---")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        clause = {}
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("CLAUSE:"):
                clause["title"] = line.replace("CLAUSE:", "").strip()
            elif line.startswith("QUOTE:"):
                clause["quote"] = line.replace("QUOTE:", "").strip()
            elif line.startswith("EXPLANATION:"):
                clause["explanation"] = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("RISK:"):
                clause["risk"] = line.replace("RISK:", "").strip().upper()
            elif line.startswith("REASON:"):
                clause["reason"] = line.replace("REASON:", "").strip()
        if "title" in clause and "risk" in clause:
            clauses.append(clause)
    return clauses

def display_clause(clause):
    risk = clause.get("risk", "LOW")
    if "HIGH" in risk:
        css_class = "risk-high"
        badge_class = "badge-high"
        emoji = "🔴"
    elif "MEDIUM" in risk:
        css_class = "risk-medium"
        badge_class = "badge-medium"
        emoji = "🟡"
    else:
        css_class = "risk-low"
        badge_class = "badge-low"
        emoji = "🟢"

    st.markdown(f"""
    <div class="{css_class}">
        <div class="clause-title">{emoji} <span class="{badge_class}">{risk} RISK</span></div>
        <strong style="font-size:1rem;">{clause.get('title','Unknown Clause')}</strong>
        <div class="quote-box">"{clause.get('quote','')}"</div>
        <p style="margin:8px 0 4px 0; color:#ccc;">{clause.get('explanation','')}</p>
        <p style="margin:0; font-size:0.82rem; color:#888;">⚠️ {clause.get('reason','')}</p>
    </div>
    """, unsafe_allow_html=True)

# ---- MAIN UI ----
st.markdown("<h1>⚖️ Contract Copilot</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">// AI-powered contract risk analyser · Powered by Gemma 4</p>', unsafe_allow_html=True)

st.markdown("Upload any contract PDF and get an instant plain-English breakdown of risky clauses — free, private, and powered by Gemma 4.")

st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload your contract PDF",
    type=["pdf"],
    help="Your file never leaves your session"
)

if uploaded_file:
    st.success(f"✅ Loaded: {uploaded_file.name}")
    
    if st.button("⚖️ ANALYSE CONTRACT"):
        with st.spinner("Gemma 4 is reading your contract..."):
            contract_text = extract_text(uploaded_file)
            raw_result = analyse_contract(contract_text)
            clauses = parse_clauses(raw_result)

        if clauses:
            high = sum(1 for c in clauses if "HIGH" in c.get("risk",""))
            medium = sum(1 for c in clauses if "MEDIUM" in c.get("risk",""))
            low = sum(1 for c in clauses if "LOW" in c.get("risk",""))

            st.markdown("### Risk Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number" style="color:#ff4444;">{high}</div>
                    <div class="stat-label">High Risk</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number" style="color:#f5c842;">{medium}</div>
                    <div class="stat-label">Medium Risk</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number" style="color:#44bb44;">{low}</div>
                    <div class="stat-label">Low Risk</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("### Flagged Clauses")
            for clause in clauses:
                display_clause(clause)

            st.markdown("---")
            st.markdown('<p style="font-size:0.75rem; color:#555; font-family: IBM Plex Mono, monospace;">⚠️ This tool is for informational purposes only and does not constitute legal advice. Consult a qualified lawyer before signing any contract.</p>', unsafe_allow_html=True)
        else:
            st.warning("Analysis complete but couldn't parse structured results. Raw output:")
            st.text(raw_result)

else:
    st.markdown("""
    <div style="background:#1a1a1a; border:1px dashed #333; border-radius:8px; 
    padding:40px; text-align:center; color:#555; font-family: IBM Plex Mono, monospace; font-size:0.85rem;">
        ↑ Upload a PDF contract to begin analysis
    </div>
    """, unsafe_allow_html=True)
