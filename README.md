# ⚖️ Contract Copilot
> AI-powered contract risk analyser for small businesses and freelancers

## The Problem
Small businesses and freelancers sign contracts they don't fully understand 
every day — because legal advice is expensive. One bad clause can cost thousands.

## The Solution
Contract Copilot lets anyone upload a contract PDF and instantly get a 
plain-English breakdown of risky clauses — completely free, private, and 
running on Gemma 4.

## Features
- 📄 Upload any contract PDF
- 🔴 🟡 🟢 Risk level scoring per clause
- 💬 Plain English explanations
- 🔒 Private — your document never leaves your session
- ⚡ Powered by Gemma 4 via Google AI Studio

## How to Run

### 1. Clone the repository
git clone https://github.com/VIJNESH200/contract-copilot.git
cd contract-copilot

### 2. Install dependencies
pip install streamlit pymupdf google-genai python-dotenv

### 3. Add your API key
Create a `.env` file in the project folder:
GOOGLE_API_KEY=your_api_key_here

Get a free API key at: https://aistudio.google.com

### 4. Run the app
python -m streamlit run app.py

Open http://localhost:8501 in your browser

## Dataset
Tested against real contracts from the publicly available 
CUAD (Contract Understanding Atticus Dataset).

## Tech Stack
- Gemma 4 (gemma-4-26b-a4b-it) via Google AI Studio
- Streamlit
- PyMuPDF

## Disclaimer
This tool is for informational purposes only and does not 
constitute legal advice. Always consult a qualified lawyer 
before signing any contract.

## License
CC-BY 4.0
