import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

CUSTOMER_BOT_TOKEN = os.getenv("CUSTOMER_BOT_TOKEN", "YOUR_CUSTOMER_BOT_TOKEN")
WORKER_BOT_TOKEN = os.getenv("WORKER_BOT_TOKEN", "YOUR_WORKER_BOT_TOKEN")
WORKER_CHAT_ID = os.getenv("WORKER_CHAT_ID", "YOUR_WORKER_CHAT_ID")
SERVER_URL = os.getenv("SERVER_URL", "https://your-server.com")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "your-secret-token-here")
