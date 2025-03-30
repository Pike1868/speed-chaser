import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# ------------------------------------------------------------------------------
# API CONFIGURATION SETTINGS
# ------------------------------------------------------------------------------
# Set your OpenRouter (or other) API key and default model. 
# Users should typically define these in a .env file.

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo")

# ------------------------------------------------------------------------------
# FILE REFERENCE & CONTEXT
# ------------------------------------------------------------------------------
# REFS_FOLDER: The default folder for project documents or additional references.
# This might be optional since we are focusing on self-reference mode.

REFS_FOLDER = os.getenv("REFS_FOLDER", "refs/")

# ------------------------------------------------------------------------------
# SYSTEM PROMPT (BASE PERSONALITY)
# ------------------------------------------------------------------------------
# A simple default prompt for Speed Chaser as a personal AI assistant
# that is self-aware of its own code and configuration files. 
# Users can add more context or instructions if desired.

SYSTEM_PROMPT = (
    "You are Speed Chaser, a personal AI assistant designed to help me with "
    "technical tasks, coding, debugging, documentation, and general support. "
    "You reference your own source code, the local 'refs/' folder, and any other "
    "configuration files in this directory. If you need more information, "
    "ask me to add relevant files or folders."
)

# ------------------------------------------------------------------------------
# SINGLE CONTEXT (SELF REFERENCE)
# ------------------------------------------------------------------------------
# This minimal context focuses on referencing Speed Chaser’s own code 
# (app.py, config.py, etc.) for self-awareness and improvement suggestions. 
# Users can add more contexts if they like, following this pattern.

CONTEXTS = {
    "self-reference": {
        "folder": ".",  # Points to current directory for code
        "prompt": (
            "You are referencing your own codebase and configuration files. "
            "Offer insights, suggestions, or help with debugging tasks based on "
            "the local source code and any references I add to 'refs/'."
        )
    }
}

# ------------------------------------------------------------------------------
# OPTIONAL VECTOR EMBEDDING SETTINGS
# ------------------------------------------------------------------------------
# Whether local doc embedding (FAISS) is enabled. If 'true', Speed Chaser 
# can ingest local files and do semantic search. Example usage in ingest.py.

ENABLE_LOCAL_EMBEDDINGS = (
    os.getenv("ENABLE_LOCAL_EMBEDDINGS", "false").lower() == "true"
)

# The default embedding model used when ingesting new files
DEFAULT_EMBEDDING_MODEL = os.getenv(
    "DEFAULT_EMBEDDING_MODEL", 
    "BAAI/bge-small-en-v1.5"
)

def get_embedding_device():
    import torch
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        return "cuda"
    print("Using CPU for embeddings.")
    return "cpu"


# ------------------------------------------------------------------------------
# NOTES / INSTRUCTIONS
# ------------------------------------------------------------------------------
# - This file is minimal. Users can modify SYSTEM_PROMPT or add new contexts 
#   to tailor Speed Chaser's focus. 
# - Provide an .env file for storing sensitive keys (OPENROUTER_API_KEY, etc.)
# - If you want to keep Speed Chaser purely self-reflexive, you can 
#   remove REFS_FOLDER or keep it for optional references.
