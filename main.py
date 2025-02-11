from slack_sdk import WebClient
import os
from pathlib import Path
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from slack_sdk.errors import SlackApiError
from flask import Flask, Response

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(env_path)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return ({"status": "healthy"})

class SlackTranslateBot:
    def __init__(self):
        self.client = WebClient(token=os.environ['SLACK_TOKEN'])
        self.translator = GoogleTranslator(source='auto', target='en')
    
    def handle_slash_command(self, channel_id, text, target_lang="en"):
        try:
            self.translator.target = target_lang
            translated = self.translator.translate(text)
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"Original: {text}\nTranslated: {translated}"
            )
        except SlackApiError as e:
            print(f"Error: {e.response['error']}")
        except Exception as e:
            print(f"Translation error: {e}")

if __name__ == "__main__":
    app.run(debug=True) # automatically re run
    
    bot = SlackTranslateBot()
    text_to_translate="おはようございます, 今日の進捗はどうですか"
    bot.handle_slash_command("test-bot", text_to_translate)
        
        
    