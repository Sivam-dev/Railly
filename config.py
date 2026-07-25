import os
from dotenv import load_dotenv
load_dotenv()

RAILRADAR_API_KEY = os.getenv("RAILRADAR_API_KEY")
IRCTC2_API_KEY = os.getenv("IRCTC2_API_KEY")

if not RAILRADAR_API_KEY:
    raise ValueError("Missing RAILRADAR_API_KEY in .env")
if not IRCTC2_API_KEY:
    raise ValueError("Missing IRCTC2_API_KEY in .env")