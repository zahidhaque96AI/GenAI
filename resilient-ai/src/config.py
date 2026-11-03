import os
from dotenv import load_dotenv

load_dotenv()

def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    
    if not value:
        RuntimeError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and set a value."
        )
    return value