#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import logging
from telegram import Update, Chat, Message, User, Bot
from telegram.ext import ContextTypes

# Import the classes and functions to test
from bot import (
    UserRateLimit,
    AIProvider,
    load_config,
    handle_message,
    handle_new_chat_members,
    start,
    help_command,
    status_command,
    reset_command
)

class TestConfig:
    """Mock configuration for testing"""
    @staticmethod
    def get_test_config():
        return {
            'telegram': {
                'token': 'test_token',
                'allowed_users': ['test_user'],
                'allowed_groups': ['-1001234567890'],
                'max_response_length': 4000
            },
            'claude': {
                'api_url': 'https://test.api.anthropic.com/v1/messages',
                'api_key': 'test_key',
                'api_version': '2023-06-01',
                'model': 'claude-3-opus-20240229',
                'max_tokens': 4000,
                'temperature': 0.7
            },
            'rate_limit': {
                'max_messages_per_hour': 50,
                'cooldown_seconds': 5
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'test_bot.log'
            }
        }

class TestUserRateLimit(unittest.TestCase):
    """Test the UserRateLimit class"""
    
    def setUp(self):
        self.config = TestConfig.get_test_config()
        self.rate_limiter = UserRateLimit(self.config)
        self.test_user_id = 12345

    def test_can_send_message_initial(self):
        """Test initial message sending permission"""
        self.assertTrue(self.rate_limiter.can_send_message(self.test_user_id))

    def test_cooldown_period(self):
        """Test cooldown period between messages"""
        self.rate_limiter.update_user(self.test_user_id)
        self.assertFalse(self.rate_limiter.can_send_message(self.test_user_id))

    def test_message_limit(self):
        """Test hourly message limit"""
        for _ in range(self.config['rate_limit']['max_messages_per_hour']):
            self.rate_limiter.update_user(self.test_user_id)
            # Simulate waiting for cooldown
            self.rate_limiter.last_message_time[self.test_user_id] -= timedelta(
                seconds=self.config['rate_limit']['cooldown_seconds'] + 1
            )
        
        self.assertFalse(self.rate_limiter.can_send_message(self.test_user_id))

class TestAIProvider(unittest.TestCase):
    """Test the AIProvider class"""
    
    def setUp(self):
        self.config = TestConfig.get_test_config()
        self.ai_provider = AIProvider(self.config)

    @patch('requests.post')
    async def test_get_response(self, mock_post):
        """Test getting response from AI provider"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'content': [{'text': 'Test response'}]
        }
        mock_post.return_value = mock_response

        response = await self.ai_provider.get_response("Test message")
        self.assertEqual(response, "Test response")

    @patch('requests.post')
    async def test_get_response_with_error(self, mock_post):
        """Test error handling in AI provider"""
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        with self.assertRaises(requests.exceptions.RequestException):
            await self.ai_provider.get_response("Test message")

class TestMessageHandlers(unittest.TestCase):
    """Test message handlers"""

    async def asyncSetUp(self):
        self.config = TestConfig.get_test_config()
        
        # Mock update object
        self.update = Mock(spec=Update)
        self.update.effective_user = Mock(spec=User)
        self.update.effective_user.id = 12345
        self.update.effective_user.username = 'test_user'
        self.update.message = Mock(spec=Message)
        self.update.effective_chat = Mock(spec=Chat)
        
        # Mock context
        self.context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        self.context.bot = Mock(spec=Bot)
        
        # Mock bot response
        self.context.bot.get_me = AsyncMock(return_value=Mock(username='test_bot'))

    @patch('bot.ai_provider')
    async def test_handle_private_message(self, mock_ai):
        """Test handling private chat message"""
        self.update.effective_chat.type = 'private'
        self.update.message.text = 'Test message'
        
        mock_ai.get_response = AsyncMock(return_value='Test response')
        
        await handle_message(self.update, self.context)
        
        # Verify AI provider was called
        mock_ai.get_response.assert_called_once()

    async def test_handle_unauthorized_user(self):
        """Test handling message from unauthorized user"""
        self.update.effective_user.username = 'unauthorized_user'
        
        await handle_message(self.update, self.context)
        
        self.update.message.reply_text.assert_called_with(
            "⚠️ Sorry, you don't have permission to use this bot"
        )

class TestCommandHandlers(unittest.TestCase):
    """Test command handlers"""

    async def asyncSetUp(self):
        self.update = Mock(spec=Update)
        self.update.message = Mock(spec=Message)
        self.context = Mock(spec=ContextTypes.DEFAULT_TYPE)

    async def test_start_command(self):
        """Test /start command"""
        await start(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    async def test_help_command(self):
        """Test /help command"""
        await help_command(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    async def test_status_command(self):
        """Test /status command"""
        await status_command(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    async def test_reset_command(self):
        """Test /reset command"""
        await reset_command(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

if __name__ == '__main__':
    unittest.main()
