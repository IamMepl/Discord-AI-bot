Setup
Clone the repository to your local machine:

[git clone https://github.com/IamMepl/Discord-AI-bot.git](URL)
Navigate to the project directory:

cd Discord-AI-bot
Install dependencies:

pip install -r requirements.txt
Create a .env file similar to the sample.env in the root directory of the project and add your GROQ API key and Discord bot token:

GROQ_API_KEY=your_groq_api_key
DISCORD_TOKEN=your_discord_token

Usage
You can mention bot or /register to chat with the bot

Start the bot:

python main.py

Customization
To change the model used by the bot, modify the model in ai.py file.

Available Options are:

LLaMA3 8b : "llama3-8b-8192"
LLaMA3 70b : "llama3-70b-8192"
Mixtral 8x7b : "mixtral-8x7b-32768"
Gemma 7b : "gemma-7b-it"
Groq API is easily replacable with OpenAI's GPT API without major code modifications.

Features
Responds to messages using a Large Language Model (LLM).
Maintains context for up to 10 conversation messages.
Utilizes the GROQ API internally.
Requires users to set up their GROQ API key and Discord bot token.

Contributing
Contributions are welcome! Please fork the repository and submit pull requests.
