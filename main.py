import os
from slack_sdk import WebClient
from pathlib import Path
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(env_path)

app = Flask(__name__)

class SlackTranslateBot:
    def __init__(self):
        self.client = WebClient(token=os.environ['SLACK_TOKEN'])
        self.translator = GoogleTranslator(source='auto', target='en')
        
        self.token = os.environ.get('SLACK_TOKEN')
        if not self.token:
            raise ValueError("SLACK_TOKEN environment variable is not set")
    
    def handle_slash_command(self, channel_id, text, target_lang="en"):
        try:
            self.translator.target = target_lang
            translated = self.translator.translate(text)
            print(translated)
            print(channel_id)
            
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"Original: {text}\nTranslated: {translated}"
            )
        except SlackApiError as e:
            print(f"Authentication Error: {e.response['error']}")
            raise ValueError(f"Slack authentication failed: {e.response['error']}")
        except Exception as e:
            print(f"Translation error: {e}")


@app.route('/slack/translate', methods=['POST'])
def translate_command():
    data = request.form
    try:
        bot = SlackTranslateBot()
        bot.handle_slash_command(data['channel_id'], text=data.get('text', ''))
        return Response(), 200
    except Exception as e:
        print(f"Error: {e}")
        return Response(f"Error: {str(e)}"), 400  


@app.route('/health', methods=['GET'])
def health_check():
    return Response({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True) # automatically re run
    