# Claude Telegram 机器人

[English](README.md) | [中文](README_CN.md)

一个由 Anthropic 的 Claude AI 驱动的 Telegram 机器人，可以在私聊和群组对话中回应消息。该机器人使用 Claude 的 API 提供智能回复，并具有速率限制、权限控制和完整的日志记录功能。

## 功能特点

- **Claude AI 集成**: 
  - 由 Anthropic 的 Claude 3.5 模型驱动
  - 可配置的模型参数
  - 错误处理和重试机制
- **聊天支持**: 
  - 支持私聊和群组
  - 在群组中被提及时回应（@机器人）
  - 群组特定配置
- **安全功能**:
  - 速率限制防止滥用
  - 用户和群组访问控制
  - 安全的 API 密钥管理
  - 完整的日志记录

## 安装指南

### 1. 创建 Telegram 机器人

1. 在 Telegram 中搜索 [@BotFather](https://t.me/botfather)
2. 开始对话并发送 `/newbot`
3. 按照以下步骤操作：
   - 发送机器人的显示名称（例如："My Claude Assistant"）
   - 发送机器人的用户名（必须以 'bot' 结尾，例如："my_claude_bot"）
4. BotFather 会回复你的机器人令牌（token）。格式如下：
   ```
   123456789:ABCdefGHIjklmNOPqrstUVwxyz
   ```
   请保管好此令牌！

5. 使用 BotFather 设置机器人命令：
   ```
   /setcommands
   ```
   然后发送此列表：
   ```
   start - 启动机器人并查看欢迎消息
   help - 显示帮助信息
   status - 检查系统状态
   reset - 重置对话历史
   ```

### 2. 获取 Claude API 密钥

1. 在 [Anthropic 官网](https://www.anthropic.com/) 注册
2. 进入账户设置/API 部分
3. 生成新的 API 密钥
4. 安全地保存你的 API 密钥

### 3. 安装

1. 克隆仓库：
```bash
git clone https://github.com/vyoz/claude-telegram-bot.git
cd claude-telegram-bot
```

2. 安装依赖：
```bash
pip install python-telegram-bot anthropic tenacity python-json-logger
```

3. 创建并配置 `config.json`：
```json
{
    "telegram": {
        "token": "你的_TELEGRAM_机器人令牌",
        "allowed_users": ["用户名1", "用户名2"],  // Telegram 用户名，不带 @ 符号
        "allowed_groups": ["-1001234567890"],    // 群组 ID，带 -100 前缀
        "max_response_length": 4096
    },
    "claude": {
        "api_key": "你的_CLAUDE_API_密钥",
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

配置说明：
- `telegram.token`：从 BotFather 获取的机器人令牌
- `telegram.allowed_users`：允许使用机器人的 Telegram 用户名数组（不带 @ 符号）
- `telegram.allowed_groups`：允许机器人运行的 Telegram 群组 ID 数组
- `telegram.max_response_length`：机器人回复的最大长度
- `claude.api_key`：你的 Claude API 密钥
- `claude.model`：使用的 Claude 模型（claude-3-5-sonnet-20240229）
- `claude.max_tokens`：回复的最大令牌数
- `claude.temperature`：回复的随机性（0.0-1.0）
- `rate_limit.max_messages_per_hour`：每个用户每小时的最大消息数
- `rate_limit.cooldown_seconds`：消息之间的最小间隔秒数

## 权限控制

### 用户权限

1. 允许特定用户：
   ```json
   "allowed_users": ["用户名1", "用户名2"]
   ```
   - 使用不带 @ 符号的 Telegram 用户名
   - 区分大小写
   - 空数组允许所有用户

2. 获取用户信息：
   - 向 [@userinfobot](https://t.me/userinfobot) 发送消息
   - 记下你的用户名（不带 @）
   - 将其添加到 allowed_users 列表中

### 群组权限

1. 允许特定群组：
   ```json
   "allowed_groups": ["-1001234567890", "-1009876543210"]
   ```

2. 获取群组 ID：
   方法一：使用机器人命令
   - 将机器人添加到群组
   - 使用 `/chatid` 命令
   - 复制返回的 ID（包含 -100 前缀）

   方法二：使用 Raw Data Bot
   - 将 [@RawDataBot](https://t.me/RawDataBot) 添加到群组
   - 复制 "chat.id" 值
   - 如果没有 -100 前缀则添加

3. 群组隐私设置：
   - 与 @BotFather 对话
   - 使用 `/mybots`
   - 选择你的机器人
   - 进入 "Bot Settings" > "Group Privacy"
   - 选择 "Turn off"

## 测试

### 1. 设置测试环境

1. 安装测试依赖：
```bash
pip install pytest pytest-asyncio pytest-cov
```

2. 创建测试配置：
```bash
cp config.json config.test.json
```
- 修改 config.test.json 使用测试凭据
- 切勿在测试中使用生产环境的 API 密钥

### 2. 运行测试

运行所有测试：
```bash
python -m pytest test_bot.py -v
```

运行特定测试用例：
```bash
python -m pytest test_bot.py -k "测试名称" -v
```

获取测试覆盖率报告：
```bash
python -m pytest --cov=bot test_bot.py
```

### 3. 可用测试套件

测试套件包括：
- UserRateLimit 测试
- AIProvider 测试
- 消息处理器测试
- 命令处理器测试
- 权限控制测试

### 4. 编写新测试

将你的测试添加到 `test_bot.py`：
```python
class TestYourFeature(unittest.TestCase):
    async def test_your_function(self):
        # 你的测试代码
        pass
```

## 运行机器人

标准启动：
```bash
python bot.py
```

使用 Screen（推荐在服务器上使用）：
```bash
screen -S claudebot
python bot.py
# 按 Ctrl+A+D 分离
```

## 使用方法

### 私聊
直接向机器人发送消息即可。

### 群组中
1. 将机器人添加到群组
2. 在消息中提及机器人：
   ```
   @你的机器人用户名 生命的意义是什么？
   ```

### 命令
- `/start` - 初始化机器人
- `/help` - 显示可用命令
- `/status` - 检查机器人状态
- `/reset` - 重置对话

## 安全建议

1. 确保 `config.json` 安全：
```bash
chmod 600 config.json
```

2. 不要分享或提交你的配置文件

3. 定期轮换你的 API 密钥

4. 监控日志文件中的未授权访问尝试

## 故障排除

### 常见问题

1. 机器人没有响应：
   - 检查机器人是否在运行
   - 验证 Telegram 令牌
   - 检查 config.json 中的权限设置
   - 查看 bot.log 中的错误

2. 速率限制问题：
   - 默认：每个用户每 5 秒 1 条消息
   - 需要时在代码中调整

3. 权限错误：
   - 在 config.json 中添加用户/群组 ID
   - 检查日志文件中的访问拒绝记录

4. 权限拒绝错误：
   - 检查 config.json 中的用户名拼写
   - 验证群组 ID 格式（应包含 -100 前缀）
   - 查找日志中的"未授权访问尝试"
   - 确保机器人有正确的群组隐私设置

## 贡献

欢迎贡献！请随时提交问题和拉取请求。

## 支持

- 创建问题报告错误
- 检查 `bot.log` 中的错误
- 确保你的 API 密钥有效
- 验证你的配置与示例匹配

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。
