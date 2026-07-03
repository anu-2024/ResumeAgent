# llm_config.py
# ─────────────────────────────────────────────
# Central LLM switcher
# Students only change the DEFAULT_PROVIDER line
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()  # reads API keys from .env file

# ✏️ STUDENTS: Change this to your provider
# Options: "groq" | "gemini" | "claude" | "ollama"
DEFAULT_PROVIDER = "groq"


def get_llm(provider: str = DEFAULT_PROVIDER):
    """
    Returns a LangChain-compatible chat model.
    Every agent calls this function to get the LLM.
    Change DEFAULT_PROVIDER above — all agents update automatically.
    """

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )

    elif provider == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3
        )

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="llama3.1",
            temperature=0.3
        )

    else:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            "Choose from: groq, gemini, claude, ollama"
        )