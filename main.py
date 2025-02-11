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
        
        self.supported_languages = {
            'en': 'English',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Simplified)',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'ru': 'Russian',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'pt': 'Portuguese',
            'vi': 'Vietnamese',
            'th': 'Thai'
        }
    
    def handle_slash_command(self, channel_id, user_id, text, target_lang="en"):
        try:
            if not text or text.lower().strip() == 'help':
                help_message = self.get_help_message()
                self.client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=help_message,
                    mrkdwn=True
                )
                return
            
            self.translator.target = target_lang
            translated = self.translator.translate(text)
            print(translated)
            print(channel_id)
            
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"{text}\n\n*Translation:*\n`{translated}`"
            )
            
        except SlackApiError as e:
            print(f"Authentication Error: {e.response['error']}")
            raise ValueError(f"Slack authentication failed: {e.response['error']}")
        
        except Exception as e:
            print(f"Translation error: {e}")

    def get_help_message(self):
        help_text = "*Translation Bot Help*\n\n"
        help_text += "*Usage:*\n"
        help_text += "• `/translate <text>` - Translate text to English (default)\n"
        help_text += "• `/translate <language_code> <text>` - Translate text to specific language\n"
        help_text += "• `/translate help` - Show this help message\n\n"
        
        help_text += "*Supported Languages:*\n"
        for code, name in self.supported_languages.items():
            help_text += f"• `{code}` - {name}\n"
        
        help_text += "\n*Examples:*\n"
        help_text += "• `/translate Hello, how are you?`\n"
        help_text += "• `/translate ja Hello, how are you?`\n"
        
        return help_text

@app.route('/slack/translate', methods=['POST'])
def translate_command():
    data = request.form
    try:
        bot = SlackTranslateBot()
        bot.handle_slash_command(data['channel_id'], user_id=data['user_id'], text=data.get('text', ''))
        return Response(), 200
    except Exception as e:
        print(f"Error: {e}")
        return Response(f"Error: {str(e)}"), 400  


@app.route('/health', methods=['GET'])
def health_check():
    return Response({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True) # automatically re run
    