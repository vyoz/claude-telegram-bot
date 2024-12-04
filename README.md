# Claude Telegram Bot

A Telegram bot powered by Anthropic's Claude AI that responds to messages in both private chats and group conversations. The bot uses Claude's API to provide intelligent responses while featuring rate limiting, permission control, and comprehensive logging.

## Features

- **Claude AI Integration**: 
  - Powered by Anthropic's Claude 3 models
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
git clone https://github.com/yourusername/claude-telegram-bot.git
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
        "allowed_users": [],            // Empty array allows all users
        "allowed_groups": [],           // Empty array allows all groups
        "max_response_length": 4096
    },
    "claude": {
        "api_key": "YOUR_CLAUDE_API_KEY",
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 1024,
        "temperature": 0.7
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "bot.log"
    }
}
```

Configuration explanation:
- `telegram.token`: Your bot token from BotFather
- `telegram.allowed_users`: Array of Telegram user IDs that can use the bot
- `telegram.allowed_groups`: Array of Telegram group IDs where the bot can operate
- `telegram.max_response_length`: Maximum length of bot responses
- `claude.api_key`: Your Claude API key
- `claude.model`: Claude model to use
- `claude.max_tokens`: Maximum tokens in response
- `claude.temperature`: Response randomness (0.0-1.0)

### 4. Running the Bot

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

### Getting User and Group IDs

1. To get your user ID:
   - Send a message to [@userinfobot](https://t.me/userinfobot)

2. To get a group ID:
   - Add [@userinfobot](https://t.me/userinfobot) to your group
   - Check the ID it provides

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

- Create an issue for bug reports
- Check logs in `bot.log` for errors
- Make sure your API keys are valid
- Verify your configuration matches the example

## License

This project is licensed under the MIT License - see the LICENSE file for details.
