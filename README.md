# Discord AI Chatbot

<p align="center">
<img src="https://raw.githubusercontent.com/IamMepl/IamMepl/refs/heads/main/static.png" alt="Discord AI Bot" />
</p>

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/IamMepl/Discord-AI-bot.git
   ```

2. Enter the project folder:

   ```bash
   cd Discord-AI-bot
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with:

   ```env
   GROQ_API_KEY=your_groq_api_key
   DISCORD_TOKEN=your_discord_token
   ```

## Usage

Run the bot:

```bash
python main.py
```

The bot supports:

- Mention-based replies
- Random chat replies in non-registered channels (~20% chance)
- Language-specific replies with `/language`
- Separate conversation memory per channel, so chats in different channels/servers don't mix together

## Slash Commands

Use `/help` in Discord to see the full command list (shown as a rich embed, grouped by category). Available commands include:

**Chat**
- `/register` - Register the current channel for always-on bot replies
- `/unregister` - Remove the current channel from always-on bot replies
- `/reset` - Make the bot forget this channel's conversation so far
- `/language <language>` - Set response language for the server

**Utility**
- `/help` - Show the command list
- `/ping` - Check the bot's latency
- `/uptime` - See how long the bot has been running
- `/wack` - Reload the bot configuration from disk (admin only)

**Moderation** (each requires the relevant Discord permission)
- `/kick` - Kick a member
- `/ban` - Ban a member
- `/timeout` - Timeout a member
- `/purge <amount>` - Delete multiple messages (1-100)

## AI Mode

This bot runs in a casual AI chat mode:

- Uses the GROQ API with `openai/gpt-oss-safeguard-20b` by default
- Responds with a playful, natural tone -- like chatting with a friend, not a formal assistant
- Casual/slang phrasing is generated naturally by the model itself based on the conversation's language and vibe, rather than applied through fixed word-substitution rules
- Keeps a separate conversation history per channel (up to the last 20 messages) so context doesn't leak between different channels or servers

## Reliability & Permissions

- Moderation commands (`/kick`, `/ban`, `/timeout`, `/purge`) and `/wack` 
- All slash commands share a centralized error handler, so failures show a clear message instead of a generic "interaction failed"
- Config reads/writes are protected with a lock to avoid two servers' changes overwriting each other

## Available GROQ Models

This bot is currently configured to use the free model:

- `openai/gpt-oss-safeguard-20b` — Safety GPT OSS 20B

Model availability may vary by account and permissions.

## Model Customization

The active model is configured in `gpt_utils.py`. You can change it there if you want to use another GROQ-supported model.

## Requirements

Install the required packages from `requirements.txt`.

## Hosting 24/7

Use services like UptimeRobot to keep your bot alive if you host it on a remote server.

## Features

- Multi-language response support via `/language`
- Non-registered channels may get random chat replies
- Per-channel conversation memory (no context bleed between channels/servers), resettable with `/reset`
- Uptime tracking via `/uptime`
- Enforced permission checks and centralized error handling for all slash commands
- Uses GROQ API and `discord.py` for Discord integration

## Contributing

Contributions are welcome! Fork the project and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
