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
- Casual and slangy responses in multiple languages

## Slash Commands

Use `/help` in Discord to see the full command list. Available commands include:

- `/help` - Show command list
- `/register` - Register the current channel for bot replies
- `/unregister` - Remove the current channel from registered bot replies
- `/language <language>` - Set response language for the server
- `/wack` - Reload the bot configuration
- `/kick` - Kick a member (requires permissions)
- `/ban` - Ban a member (requires permissions)
- `/timeout` - Timeout a member (requires permissions)
- `/purge <amount>` - Delete multiple messages (requires permissions)

## AI Mode

This bot runs in a casual AI chat mode:

- Uses the GROQ API with `openai/gpt-oss-safeguard-20b` by default
- Responds with a playful tone and light jokes

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
- Uses GROQ API and `discord.py` for Discord integration

## Contributing

Contributions are welcome! Fork the project and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.