#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Optional

from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
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

# User message rate limiting with config-based settings
message_cooldowns: Dict[int, datetime] = {}

class UserRateLimit:
    """User message rate limiting class"""
    def __init__(self, config: Dict):
        self.last_message_time: Dict[int, datetime] = {}
        self.message_count: Dict[int, int] = defaultdict(int)
        self.reset_time: Dict[int, datetime] = {}
        self.max_messages = config['rate_limit']['max_messages_per_hour']
        self.cooldown_time = timedelta(seconds=config['rate_limit']['cooldown_seconds'])
    
    def can_send_message(self, user_id: int) -> bool:
        now = datetime.now()
        
        # Reset counter
        if user_id in self.reset_time and now > self.reset_time[user_id]:
            self.message_count[user_id] = 0
            
        # Check frequency
        if user_id in self.last_message_time:
            time_diff = now - self.last_message_time[user_id]
            if time_diff < self.cooldown_time:
                return False
            
        return self.message_count[user_id] < self.max_messages

    def update_user(self, user_id: int):
        now = datetime.now()
        self.last_message_time[user_id] = now
        self.message_count[user_id] += 1
        
        # Set reset time to next hour
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        self.reset_time[user_id] = next_hour

class AIProvider:
    """Class to handle Claude AI interactions"""
    
    def __init__(self, config: Dict):
        """Initialize AI provider with configuration"""
        self.config = config
        self.api_url = config['claude']['api_url']
        self.headers = {
            "x-api-key": config['claude']['api_key'],
            "anthropic-version": config['claude']['api_version'],
            "content-type": "application/json"
        }
        self.model = config['claude']['model']
        self.max_tokens = config['claude']['max_tokens']
        self.temperature = config['claude']['temperature']
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_response(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Get response from Claude API
        
        Args:
            message: User message
            system_prompt (Optional[str]): Optional system prompt to set context
            
        Returns:
            AI response text
        """
        try:
            data = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                #"temperature": self.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }

            if system_prompt:
                data["system"] = system_prompt

            # Log request details with proper JSON formatting
            logger.debug("=== API Request ===")
            logger.debug(f"URL: {self.api_url}")
            logger.debug("Headers:")
            logger.debug(json.dumps(self.headers, indent=2, ensure_ascii=False))
            logger.debug("Request Body:")
            logger.debug(json.dumps(data, indent=2, ensure_ascii=False))
           
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data
                )
            
                response.raise_for_status()  # Raise an error for bad status codes
            
                response_data = response.json()
                logger.debug(f"API Response: {response_data}")
            
                if 'content' in response_data and len(response_data['content']) > 0:
                    return response_data['content'][0]['text']
                else:
                    raise Exception("No content in response")
            except requests.exceptions.RequestException as e:
                print(f"Error calling Claude API: {str(e)}")
                raise
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting response from Claude API: {str(e)}")
            logger.error(f"Response status code: {e.response.status_code if e.response else 'No response'}")
            logger.error(f"Response text: {e.response.text if e.response else 'No response'}")
            raise
        except Exception as e:
            logger.error(f"Error processing Claude API response: {str(e)}")
            raise

# Initialize providers with config
rate_limiter = UserRateLimit(CONFIG)
ai_provider = AIProvider(CONFIG)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "👋 Hello! I'm an AI assistant powered by Claude.\n\n"
        "📝 How to use:\n"
        "1. In private chat, just send me your questions directly\n"
        "2. In groups, mention me (@bot) with your question\n"
        "3. Use /help to see all available commands\n"
        "4. Use /status to check system status\n\n"
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
        "💡 Tips:\n"
        "- In private chat, just send your questions directly\n"
        "- In groups, mention me with @bot_username"
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
    """Handle messages mentioning the bot or direct messages in private chat"""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Check user permissions
    if CONFIG['telegram']['allowed_users'] and str(user_id) not in CONFIG['telegram']['allowed_users']:
        logger.warning(f"Unauthorized access attempt: {user_id} ({username})")
        await update.message.reply_text("⚠️ Sorry, you don't have permission to use this bot")
        return

    # Get bot info
    bot = await context.bot.get_me()
    
    # Process the message based on chat type
    if update.effective_chat.type == 'private':
        # In private chat, respond to all messages
        question = update.message.text.strip()
    else:
        # In groups, only respond when mentioned
        if f'@{bot.username}' not in update.message.text:
            return
        question = update.message.text.replace(f'@{bot.username}', '').strip()

    # Check if message is empty
    if not question:
        await update.message.reply_text("❓ Please ask a question")
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

    try:
        # Log user request
        logger.info(f"Received request - User: {user_id} ({username}) - Message: {question[:100]}...")

        #system prompt
        system_prompt = "You are a helpful AI assistant for telegram."

        # Get AI response
        response_text = await ai_provider.get_response(question, system_prompt)
        
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

async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when bot is added to a new group"""
    bot = await context.bot.get_me()
    chat = update.effective_chat

    # Check if the bot was added to the group
    new_members = update.message.new_chat_members
    if any(member.id == bot.id for member in new_members):
        # Check if group is in whitelist
        if 'allowed_groups' in CONFIG['telegram'] and str(chat.id) not in CONFIG['telegram']['allowed_groups']:
            logger.warning(f"Bot added to unauthorized group: {chat.id} ({chat.title})")
            await update.message.reply_text(
                "⚠️ This bot can only be used in authorized groups. Leaving the chat..."
            )
            # Leave the unauthorized group
            await chat.leave()
            return

def main():
    """Main function"""
    try:
        # Create application with group message permissions
        application = (
            Application.builder()
            .token(CONFIG['telegram']['token'])
            .arbitrary_callback_data(True)
            .post_init(lambda app: app.bot.set_my_commands([
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Show help message"),
                BotCommand("status", "Check bot status"),
                BotCommand("reset", "Reset conversation"),
            ]))
            .build()
        )

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("reset", reset_command))

        # Add handler for new chat members (bot being added to groups)
        application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            handle_new_chat_members
        ))

        # Message handler for both private and group messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE),
            handle_message
        ))

        # Add error handler
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot started...")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    except Exception as e:
        logger.critical(f"Bot stopped due to error: {str(e)}")
        raise

def main1():
    """Main function"""
    try:
        # Create application with group message permissions
        application = (
            Application.builder()
            .token(CONFIG['telegram']['token'])
            .arbitrary_callback_data(True)  # Enable arbitrary callback data
            .post_init(lambda app: app.bot.set_my_commands([  # Set bot commands
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Show help message"),
                BotCommand("status", "Check bot status"),
                BotCommand("reset", "Reset conversation"),
            ]))
            .build()
        )

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("reset", reset_command))
        
        # Message handler for both private and group messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE),
            handle_message
        ))
        
        # Add error handler
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot started...")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    except Exception as e:
        logger.critical(f"Bot stopped due to error: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        # Run the main function
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot stopped due to error: {str(e)}")
        print(f"Bot stopped due to error: {str(e)}")
