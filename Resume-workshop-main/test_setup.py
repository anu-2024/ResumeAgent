# test_setup.py
import sys

# Check Python version
print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")

# Check all packages are installed
packages = [
    "streamlit",
    "langchain",
    "langgraph",
    "pdfplumber",
    "docx",
    "httpx",
    "bs4",
    "dotenv",
    "groq"
]

for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} — run: pip install {pkg}")

# Check API key exists and works
import os
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

key = os.getenv("GROQ_API_KEY")

if not key:
    print("\n❌ GROQ_API_KEY missing from .env file")
else:
    print("\n🔑 API key found — testing Groq connection...")
    from groq import Groq

    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # fast and free model
        messages=[{"role": "user", "content": "Say exactly: Setup successful!"}]
    )
    print(f"✅ Groq API: {response.choices[0].message.content.strip()}")