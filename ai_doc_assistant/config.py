"""
Settings for folder paths and which AI model to use.
Change these to fit your setup.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INBOX_DIR = os.path.join(BASE_DIR, "inbox")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SUMMARIES_DIR = os.path.join(OUTPUTS_DIR, "summaries")
CSV_PATH = os.path.join(OUTPUTS_DIR, "results.csv")

# Which file extensions to process
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".eml", ".md"}

# --- LLM settings ---
# Set to "ollama" for local Llama 3, or "openai" if you'd rather use the OpenAI API.
LLM_PROVIDER = "ollama"

# Ollama settings (default local server)
OLLAMA_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

# OpenAI settings (only used if LLM_PROVIDER = "openai")
OPENAI_MODEL = "gpt-4o-mini"
# Reads from environment variable OPENAI_API_KEY, never hardcode a key here.

# How many characters of a document to send to the model.
# Keeps prompts small and fast; long documents get truncated.
MAX_CHARS_TO_MODEL = 6000
