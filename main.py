import os
from slack_sdk import WebClient
from pathlib import Path
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response
import json

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
        
        # Add SIGNING_SECRET verification
        self.signing_secret = os.environ.get('SLACK_SIGNING_SECRET')
        if not self.signing_secret:
            raise ValueError("SLACK_SIGNING_SECRET environment variable is not set")
        
        self.supported_languages = {
            'en': 'English',
            'ja': 'Japanese',
            'si': 'Sinhala',
            'ta': 'Tamil',
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
        
        # Store user language preferences
        self.user_languages = {}
    
    def set_user_language(self, user_id, language_code):
        """Set preferred translation language for a user"""
        if language_code in self.supported_languages:
            self.user_languages[user_id] = language_code
            return True
        return False
    
    def get_user_language(self, user_id):
        """Get user's preferred language, default to English"""
        return self.user_languages.get(user_id, 'en')
    
    def detect_language(self, text):
        """Detect the language of the input text"""
        try:
            detected = self.translator.detect(text)
            return detected
        except:
            return 'en'
    
    async def handle_message(self, event_data):
        """Handle incoming message events"""
        try:
            # Ignore bot messages and message_changed events
            if (
                'bot_id' in event_data or 
                'subtype' in event_data or 
                event_data.get('type') != 'message'
            ):
                return
            
            channel_id = event_data['channel']
            user_id = event_data['user']
            text = event_data.get('text', '')
            
            if not text:
                return
            
            # Detect source language
            source_lang = self.detect_language(text)
            target_lang = self.get_user_language(user_id)
            
            # Only translate if source and target languages are different
            if source_lang != target_lang:
                self.translator.source = source_lang
                self.translator.target = target_lang
                
                translated = self.translator.translate(text)
                
                # Post translation as a thread reply
                self.client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=event_data.get('ts'),
                    text=f"Translation ({self.supported_languages[target_lang]}):\n```{translated}```"
                )
                
        except Exception as e:
            print(f"Error handling message: {e}")

    def handle_command(self, channel_id, user_id, text):
        """Handle slash commands for setting preferences"""
        try:
            parts = text.split()
            command = parts[0].lower() if parts else ''
            
            if command == 'setlang' and len(parts) > 1:
                lang_code = parts[1].lower()
                if self.set_user_language(user_id, lang_code):
                    response = f"Your preferred language has been set to {self.supported_languages[lang_code]}"
                else:
                    response = f"Unsupported language code. Use one of: {', '.join(self.supported_languages.keys())}"
            else:
                response = self.get_help_message()
            
            self.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=response
            )
            
        except Exception as e:
            print(f"Error handling command: {e}")

    def get_help_message(self):
        help_text = "*Auto Translation Bot Help*\n\n"
        help_text += "*Features:*\n"
        help_text += "• Messages are automatically translated to your preferred language\n"
        help_text += "• Translations appear as thread replies\n\n"
        
        help_text += "*Commands:*\n"
        help_text += "• `/translate setlang <language_code>` - Set your preferred language\n"
        help_text += "• `/translate help` - Show this help message\n\n"
        
        help_text += "*Supported Languages:*\n"
        for code, name in self.supported_languages.items():
            help_text += f"• `{code}` - {name}\n"
        
        return help_text


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Handle Slack events"""
    data = json.loads(request.data)
    
    # Handle URL verification challenge
    if data.get('type') == 'url_verification':
        return Response(
            data.get('challenge'),
            mimetype='text/plain'
        )
    
    # Verify request is from Slack
    if not verify_slack_request(request):
        return Response('Invalid request'), 403
    
    # Handle events
    if data.get('type') == 'event_callback':
        event_data = data.get('event', {})
        bot = SlackTranslateBot()
        bot.handle_message(event_data)
    
    return Response(), 200


@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    """Handle slash commands"""
    data = request.form
    
    # Verify request is from Slack
    if not verify_slack_request(request):
        return Response('Invalid request'), 403
    
    try:
        bot = SlackTranslateBot()
        bot.handle_command(
            data['channel_id'],
            user_id=data['user_id'],
            text=data.get('text', '')
        )
        return Response(), 200
    except Exception as e:
        print(f"Error: {e}")
        return Response(f"Error: {str(e)}"), 400


def verify_slack_request(request):
    """Verify that the request came from Slack"""
    # Implementation of Slack's request verification
    # https://api.slack.com/authentication/verifying-requests-from-slack
    # You'll need to implement this based on Slack's documentation
    return True

@app.route("/")
def home():
    return "Hello, Flask on Vercel!"

@app.route('/health', methods=['GET'])
def health_check():
    return Response({"status": "healthy"})


if __name__ == "__main__":
    app.run()