# Claude Telegram Bot

A Telegram bot powered by Claude AI that allows users to interact with Claude through Telegram messages. The bot supports both private chats and group conversations, with features like rate limiting, permission control, and comprehensive logging.

## Features

- **Claude AI Integration**: Leverages Claude's powerful language model for intelligent responses
- **Group Chat Support**: Can be added to group chats and responds when mentioned
- **Rate Limiting**: Prevents abuse through configurable message rate limits
- **Permission Control**: Configurable user and group access control
- **Command System**: Built-in commands for basic interactions
- **Logging System**: Comprehensive logging for monitoring and debugging
- **Configuration Management**: Easy configuration through JSON file

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/botfather))
- An Anthropic API Key (obtained from [Anthropic's website](https://www.anthropic.com/))

## Installation

1. Clone the repository or download the source code:
```bash
git clone https://github.com/yourusername/claude-telegram-bot.git
cd claude-telegram-bot
```

2. Install required dependencies:
```bash
pip install python-telegram-bot anthropic python-json-logger
```

3. Create a configuration file `config.json` in the project root:
```json
{
    "telegram": {
        "token": "YOUR_TELEGRAM_BOT_TOKEN",
        "allowed_users": [],
        "allowed_groups": [],
        "max_response_length": 4096
    },
    "claude": {
        "api_key": "YOUR_CLAUDE_API_KEY",
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 1024,
        "temperature": 0.7,
        "api_url": "https://api.anthropic.com/v1"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "bot.log"
    }
}
```

## Telegram Bot Setup

1. Create a new bot on Telegram:
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` command
   - Follow the instructions to choose a name and username for your bot
   - Copy the API token provided by BotFather

2. Configure your bot:
   - Set bot commands using BotFather (optional):
     ```
     /start - Start the bot and see welcome message
     /help - Display help information
     /status - Check system status
     /reset - Reset conversation history
     ```
   - Enable inline mode if needed: `/setinline`
   - Set bot profile picture: `/setuserpic`
   - Set bot description: `/setdescription`
   - Set bot about text: `/setabouttext`

3. Configure permissions (optional):
   - Add allowed user IDs to `allowed_users` in config.json
   - Add allowed group IDs to `allowed_groups` in config.json
   - Leave arrays empty to allow all users/groups

## Running the Bot

1. Start the bot:
```bash
python bot.py
```

2. The bot will begin logging to both console and the specified log file.

## Usage

### Basic Commands

- `/start`: Initialize the bot and see welcome message
- `/help`: Display help information and available commands
- `/status`: Check the current status of the bot
- `/reset`: Reset your conversation history

### Group Chat Usage

1. Add the bot to a group
2. Mention the bot (@your_bot_username) followed by your message
3. The bot will respond to the message if:
   - The group is in the allowed list (if configured)
   - The user has permission (if configured)
   - The rate limit hasn't been exceeded

### Private Chat Usage

Simply send messages to the bot directly. The same permission and rate limit rules apply.

## Configuration Options

### Telegram Settings
- `token`: Your Telegram Bot API token
- `allowed_users`: Array of user IDs allowed to use the bot
- `allowed_groups`: Array of group IDs where the bot can operate
- `max_response_length`: Maximum length of bot responses

### Claude Settings
- `api_key`: Your Anthropic API key
- `model`: Claude model to use
- `max_tokens`: Maximum tokens in the response
- `temperature`: Response randomness (0.0 to 1.0)

### Logging Settings
- `level`: Logging level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
- `format`: Log message format
- `file`: Log file location

## Security Considerations

- Keep your `config.json` file secure and never commit it to version control
- Regularly rotate your API keys
- Monitor the bot's usage through logs
- Use the permission system to restrict access when needed
- Rate limiting helps prevent abuse

## Troubleshooting

### Common Issues

1. Bot not responding:
   - Check if the bot is running
   - Verify your Telegram token
   - Check the log file for errors
   - Ensure the user/group has permission

2. Rate limit issues:
   - Wait for the cooldown period
   - Check the rate limit settings in the code

3. API errors:
   - Verify your Claude API key
   - Check your API usage quota
   - Ensure the model name is correct

### Logging

The bot logs all activities to both console and file. Check the log file specified in `config.json` for detailed information about:
- Incoming messages
- API calls
- Errors and exceptions
- Rate limit triggers
- Permission denials

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
