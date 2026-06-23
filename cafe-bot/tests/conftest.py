import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["CUSTOMER_BOT_TOKEN"] = "test:token"
os.environ["WORKER_BOT_TOKEN"] = "test:token"
os.environ["WORKER_CHAT_ID"] = "12345"
os.environ["SERVER_URL"] = "http://localhost:8000"
os.environ["SECRET_TOKEN"] = "test_secret"
