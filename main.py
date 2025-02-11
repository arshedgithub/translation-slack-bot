from slack_sdk import WebClient
import os
from pathlib import Path
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from slack_sdk.errors import SlackApiError

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(env_path)

class SlackTranslateBot:
    def __init__(self):
        self.client = WebClient(token=os.environ['SLACK_TOKEN'])
        self.translator = GoogleTranslator(source='auto', target='en')
    
    def translate_text(self, text, target_lang='en'):
        try:
            self.translator.target = target_lang
            return self.translator.translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return None

if __name__ == "__main__":
    bot = SlackTranslateBot()
    translated = bot.translate_text("こんにちは、お元気ですか、私は元気です")
    if translated:
        print("#test-bot", translated)