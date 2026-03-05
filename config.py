import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY not found in .env file")
    GROQ_API_KEY = "your-key-here"

# Models
PRIMARY_MODEL = "mixtral-8x7b-32768"
FAST_MODEL = "llama2-70b-4096"

# Settings
MAX_SEARCH_RESULTS = 5
MAX_ITERATIONS = 2