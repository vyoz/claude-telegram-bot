import json
import logging
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Optional

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

# Load configuration
def load_config() -> dict:
    """Load configuration file"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Config file config.json not found")
    except json.JSONDecodeError:
        raise ValueError("Invalid config file format")

CONFIG = load_config()

# Setup logging
logging.basicConfig(
    level=getattr(logging, CONFIG['logging']['level']),
    format=CONFIG['logging']['format'],
    handlers=[
        logging.FileHandler(CONFIG['logging']['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
anthropic = Anthropic(
    api_key=CONFIG['claude']['api_key']
)

# User message rate limiting
message_cooldowns: Dict[int, datetime] = {}
COOLDOWN_TIME = timedelta(seconds=5)  # Message cooldown time

class UserRateLimit:
    """User message rate limiting class"""
    def __init__(self):
        self.last_message_time: Dict[int, datetime] = {}
        self.message_count: Dict[int, int] = defaultdict(int)
        self.reset_time: Dict[int, datetime] = {}
    
    def can_send_message(self, user_id: int) -> bool:
        now = datetime.now()
        
        # Reset counter
        if user_id in self.reset_time and now > self.reset_time[user_id]:
            self.message_count[user_id] = 0
            
        # Check frequency
        if user_id in self.last_message_time:
            time_diff = now - self.last_message_time[user_id]
            if time_diff < COOLDOWN_TIME:
                return False
            
        return self.message_count[user_id] < 10  # Maximum 10 messages per hour

    def update_user(self, user_id: int):
        now = datetime.now()
        self.last_message_time[user_id] = now
        self.message_count[user_id] += 1
        
        # Set reset time to next hour
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        self.reset_time[user_id] = next_hour

rate_limiter = UserRateLimit()

class AIProvider:
    """Class to handle Claude AI interactions"""
    
    def __init__(self, config: Dict):
        """Initialize AI provider with configuration"""
        self.config = config
        self.client = Anthropic(api_key=config['claude']['api_key'])
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_response(self, message: str) -> str:
        """
        Get response from Claude API
        
        Args:
            message: User message
            
        Returns:
            AI response text
        """
        try:
            response = self.client.messages.create(
                model=self.config['claude']['model'],
                max_tokens=self.config['claude']['max_tokens'],
                temperature=self.config['claude']['temperature'],
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )
            
            return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error getting response from Claude: {str(e)}")
            raise

# Initialize AI provider
ai_provider = AIProvider(CONFIG)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "👋 Hello! I'm an AI assistant powered by Claude.\n\n"
        "📝 How to use:\n"
        "1. Mention me (@bot) in a group to start a conversation\n"
        "2. Use /help to see all available commands\n"
        "3. Use /status to check system status\n\n"
        "⚠️ Note: Message rate limiting is enabled to prevent abuse"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 Bot Commands:\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Display this help message\n"
        "/status - Check system status\n"
        "/reset - Reset your conversation\n"
        "\n"
        "💡 Tip: Simply mention the bot in a group to start chatting"
    )
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    try:
        status_text = (
            "🔄 System Status:\n\n"
            f"✅ Bot is running normally\n"
            f"📊 Current model: {CONFIG['claude']['model']}\n"
            f"⏰ Server time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        await update.message.reply_text(status_text)
    except Exception as e:
        logger.error(f"Error while getting status: {str(e)}")
        await update.message.reply_text("❌ Error while retrieving status")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command"""
    user_id = update.effective_user.id
    await update.message.reply_text("✨ Your conversation history has been reset")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages mentioning the bot"""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Check user permissions
    if CONFIG['telegram']['allowed_users'] and str(user_id) not in CONFIG['telegram']['allowed_users']:
        logger.warning(f"Unauthorized access attempt: {user_id} ({username})")
        await update.message.reply_text("⚠️ Sorry, you don't have permission to use this bot")
        return

    # Check if message is from an allowed group
    if update.effective_chat.type != 'private':
        if CONFIG['telegram']['allowed_groups'] and str(update.effective_chat.id) not in CONFIG['telegram']['allowed_groups']:
            logger.warning(f"Message from unauthorized group: {update.effective_chat.id}")
            return

    # Check if bot is mentioned
    bot = await context.bot.get_me()
    if f'@{bot.username}' not in update.message.text:
        return

    # Check message rate limit
    if not rate_limiter.can_send_message(user_id):
        await update.message.reply_text(
            "⚠️ You're sending messages too frequently. Please wait a moment.",
            reply_to_message_id=update.message.message_id
        )
        return

    # Update user message rate statistics
    rate_limiter.update_user(user_id)

    # Get the actual question
    question = update.message.text.replace(f'@{bot.username}', '').strip()
    
    if not question:
        await update.message.reply_text("❓ Please include your question when mentioning me")
        return

    try:
        # Log user request
        logger.info(f"Received request - User: {user_id} ({username}) - Message: {question[:100]}...")

        # Get AI response
        response_text = await ai_provider.get_response(question)
        
        # Check response length
        if len(response_text) > CONFIG['telegram']['max_response_length']:
            response_text = response_text[:CONFIG['telegram']['max_response_length']] + "...(response truncated)"

        await update.message.reply_text(
            response_text,
            reply_to_message_id=update.message.message_id
        )
        
        # Log response
        logger.info(f"Sent response - User: {user_id} - Length: {len(response_text)}")

    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        logger.error(error_message)
        await update.message.reply_text(
            f"❌ Sorry, an error occurred while processing your request. Please try again later.",
            reply_to_message_id=update.message.message_id
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An internal error occurred. Please try again later."
        )

async def setup_commands(application: Application):
    """Setup bot commands"""
    commands = [
        BotCommand("start", "Start the bot and see welcome message"),
        BotCommand("help", "Display help information"),
        BotCommand("status", "Check system status"),
        BotCommand("reset", "Reset conversation history")
    ]
    await application.bot.set_my_commands(commands)

async def main():
    """Main function"""
    try:
        # Create application
        application = Application.builder().token(CONFIG['telegram']['token']).build()

        # Setup commands
        await setup_commands(application)

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("reset", reset_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot started...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Critical error while starting bot: {str(e)}")
        raise

if __name__ == '__main__':
    # Run the async main function
    import asyncio
    asyncio.run(main())
