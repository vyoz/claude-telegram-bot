# Claude Telegram Bot

[English](README.md) | [中文](README_CN.md)

A Telegram bot powered by Anthropic's Claude AI that responds to messages in both private chats and group conversations. The bot uses Claude's API to provide intelligent responses while featuring rate limiting, permission control, and comprehensive logging.

## Features

- **Claude AI Integration**: 
  - Powered by Anthropic's Claude 3.5 model
  - Configurable model parameters
  - Error handling and retry mechanism
- **Chat Support**: 
  - Works in private chats and groups
  - Responds when mentioned (@bot)
  - Group-specific configurations
- **Security Features**:
  - Rate limiting to prevent abuse
  - User and group access control
  - Secure API key management
  - Comprehensive logging

## Setup Guide

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Start a chat and send `/newbot`
3. Follow these steps:
   - Send your bot's display name (e.g., "My Claude Assistant")
   - Send your bot's username (must end in 'bot', e.g., "my_claude_bot")
4. BotFather will respond with your bot token. It looks like:
   ```
   123456789:ABCdefGHIjklmNOPqrstUVwxyz
   ```
   Keep this token secure!

5. Set up bot commands with BotFather:
   ```
   /setcommands
   ```
   Then send this list:
   ```
   start - Start the bot and see welcome message
   help - Display help information
   status - Check system status
   reset - Reset conversation history
   ```

### 2. Get Claude API Key

1. Sign up at [Anthropic's website](https://www.anthropic.com/)
2. Navigate to your account settings/API section
3. Generate a new API key
4. Copy your API key securely

### 3. Installation

1. Clone the repository:
```bash
git clone https://github.com/vyoz/claude-telegram-bot.git
cd claude-telegram-bot
```

2. Install dependencies:
```bash
pip install python-telegram-bot anthropic tenacity python-json-logger
```

3. Create and configure `config.json`:
```json
{
    "telegram": {
        "token": "YOUR_TELEGRAM_BOT_TOKEN",
        "allowed_users": ["username1", "username2"],  // Telegram usernames without @
        "allowed_groups": ["-1001234567890"],        // Group IDs with -100 prefix
        "max_response_length": 4096
    },
    "claude": {
        "api_key": "YOUR_CLAUDE_API_KEY",
        "model": "claude-3-5-sonnet-20240229",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "bot.log"
    },
    "rate_limit": {
        "max_messages_per_hour": 50,
        "cooldown_seconds": 5
    }
}
```

Configuration explanation:
- `telegram.token`: Your bot token from BotFather
- `telegram.allowed_users`: Array of Telegram usernames (without @ symbol) that can use the bot
- `telegram.allowed_groups`: Array of Telegram group IDs where the bot can operate
- `telegram.max_response_length`: Maximum length of bot responses
- `claude.api_key`: Your Claude API key
- `claude.model`: Claude model to use (claude-3-5-sonnet-20240229)
- `claude.max_tokens`: Maximum tokens in response
- `claude.temperature`: Response randomness (0.0-1.0)
- `rate_limit.max_messages_per_hour`: Maximum messages per user per hour
- `rate_limit.cooldown_seconds`: Minimum seconds between messages

## Permission Control

### User Permissions

1. Allow specific users:
   ```json
   "allowed_users": ["username1", "username2"]
   ```
   - Use Telegram usernames without @ symbol
   - Case-sensitive
   - Empty array allows all users

2. Get user information:
   - Send a message to [@userinfobot](https://t.me/userinfobot)
   - Note your username (without @)
   - Add it to the allowed_users list

### Group Permissions

1. Allow specific groups:
   ```json
   "allowed_groups": ["-1001234567890", "-1009876543210"]
   ```

2. Get group ID:
   Method 1: Using Bot Commands
   - Add the bot to your group
   - Use the `/chatid` command
   - Copy the returned ID (includes -100 prefix)

   Method 2: Using Raw Data Bot
   - Add [@RawDataBot](https://t.me/RawDataBot) to your group
   - Copy the "chat.id" value
   - Add -100 prefix if not present

3. Group Privacy Settings:
   - Talk to @BotFather
   - Use `/mybots`
   - Select your bot
   - Go to "Bot Settings" > "Group Privacy"
   - Select "Turn off"

## Testing

### 1. Setup Test Environment

1. Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov
```

2. Create test configuration:
```bash
cp config.json config.test.json
```
- Modify config.test.json with test credentials
- Never use production API keys in tests

### 2. Running Tests

Run all tests:
```bash
python -m pytest test_bot.py -v
```

Run specific test cases:
```bash
python -m pytest test_bot.py -k "test_name" -v
```

Get test coverage report:
```bash
python -m pytest --cov=bot test_bot.py
```

### 3. Available Test Suites

The test suite includes:
- UserRateLimit tests
- AIProvider tests
- Message handler tests
- Command handler tests
- Permission control tests

### 4. Writing New Tests

Add your tests to `test_bot.py`:
```python
class TestYourFeature(unittest.TestCase):
    async def test_your_function(self):
        # Your test code here
        pass
```

## Running the Bot

Standard start:
```bash
python bot.py
```

Using Screen (recommended for servers):
```bash
screen -S claudebot
python bot.py
# Press Ctrl+A+D to detach
```

## Usage

### In Private Chat
Simply send messages directly to the bot.

### In Groups
1. Add the bot to your group
2. Mention the bot with your message:
   ```
   @your_bot_username What is the meaning of life?
   ```

### Commands
- `/start` - Initialize the bot
- `/help` - Show available commands
- `/status` - Check bot status
- `/reset` - Reset conversation

## Security Recommendations

1. Keep your `config.json` secure:
```bash
chmod 600 config.json
```

2. Don't share or commit your configuration file

3. Regularly rotate your API keys

4. Monitor the log file for unauthorized access attempts

## Troubleshooting

### Common Issues

1. Bot not responding:
   - Check if bot is running
   - Verify Telegram token
   - Check permissions in config.json
   - Look for errors in bot.log

2. Rate limit issues:
   - Default: 1 message per 5 seconds per user
   - Adjust in code if needed

3. Permission errors:
   - Add user/group IDs to config.json
   - Check log file for denied access attempts

4. Permission denied errors:
   - Check username spelling in config.json
   - Verify group ID format (should include -100 prefix)
   - Look for "Unauthorized access attempt" in logs
   - Ensure bot has correct privacy settings for groups

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

- Create an issue for bug reports
- Check logs in `bot.log` for errors
- Make sure your API keys are valid
- Verify your configuration matches the example

## License

This project is licensed under the MIT License - see the LICENSE file for details.
