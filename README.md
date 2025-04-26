<p align="center">
  <img src="https://raw.githubusercontent.com/IamMepl/IamMepl/refs/heads/main/static.png" />
</p>

## Setup

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/IamMepl/Discord-AI-bot.git
   ```

2. Navigate to the project directory:

    ```bash
    cd Discord-AI-bot
    ```

3. Install dependencies:

   ```bash
   pip install -r setup.txt
   ```

4. Create a `.env` and add your GROQ API key and Discord bot token:

   ```
   GROQ_API_KEY=your_groq_api_key
   DISCORD_TOKEN=your_discord_token
   ```
## Usage

*You can mention the bot or /register to start chat with the bot.*

To run the bot

   ```bash
   python main.py
   ```

Get Your Groq API key here:

```bash
https://console.groq.com/keys
```
## Hosting 24/7

```bash
https://uptimerobot.com/
```

## Customization

To change the model used by the bot, modify the model in `gpt_utils.py` file.

Available Options are:
- LLaMA3 8b    : "llama3-8b-8192"
- LLaMA3 70b   : "llama3-70b-8192"
- Mixtral 8x7b : "mixtral-8x7b-32768"
- Gemma 7b     : "gemma-7b-it"

Groq API is easily replacable with OpenAI's GPT API without major code modifications.

## Features

- Responds to messages using a Large Language Model (LLM).
- Maintains context for up to 10 conversation messages.
- Utilizes the GROQ API internally.
- Requires users to set up their GROQ API key and Discord bot token.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.
