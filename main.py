from slack_sdk import WebClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(env_path)

client = WebClient(token=os.environ['SLACK_TOKEN'])
print("Client created successfully!")