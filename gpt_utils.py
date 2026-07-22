import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set. Please add it to your .env file or environment variables.")

client = Groq(api_key=api_key)

BASE_SYSTEM_PROMPT = (
    "Your name is Mepl. If someone asks your name, who you are, or what you're called, tell them your name "
    "is Mepl -- naturally, in one line, don't turn it into a whole introduction unless they ask more. "
    "You're chatting in a Discord server, not writing formal replies. Talk like a real person texting "
    "a friend: casual, a bit playful, sometimes short and blunt, sometimes rambly if the topic is interesting. "
    "Don't over-explain things nobody asked about. Don't start every message with a greeting or with the "
    "person's name. Skip the therapist-y phrasing ('I understand that...', 'It sounds like...') -- just react "
    "the way a friend would. You can disagree, tease a little, or be sarcastic if it fits, but don't be mean. "
    "Use slang and casual phrasing naturally where it fits the vibe of the conversation and the user's language, "
    "instead of sounding like a customer support bot. Keep emoji use light and only when it actually adds "
    "something -- not on every message. Vary your sentence length and structure so replies don't all sound "
    "the same. If something's genuinely funny or interesting, you can be enthusiastic; if it's a simple "
    "question, just answer it without padding."
)

conversation_histories = {}
MAX_HISTORY = 20
MAX_TRACKED_CONVERSATIONS = 200


def _get_history(conversation_id):
    key = conversation_id or "default"
    if key not in conversation_histories:
        if len(conversation_histories) >= MAX_TRACKED_CONVERSATIONS:
            oldest_key = next(iter(conversation_histories))
            del conversation_histories[oldest_key]
        conversation_histories[key] = []
    return conversation_histories[key]


def gpt_response(message, language=None, image_urls=None, conversation_id=None):
    history = _get_history(conversation_id)

    if image_urls:
        image_prompt = (
            "The user included image attachments at these URLs: " + ", ".join(image_urls) + ". "
            "You can mention these image links in your response, but do not claim to see their visual contents if you cannot."
        )
        message = f"{message}\n\n{image_prompt}" if message else image_prompt

    history.append({"role": "user", "content": message})
    if len(history) > MAX_HISTORY:
        del history[:-MAX_HISTORY]

    prompt_messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
    if language:
        prompt_messages.append({
            "role": "system",
            "content": f"Reply in {language}, using natural, everyday phrasing a native speaker would actually use."
        })

    response = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=prompt_messages + history
    )

    assistant_content = response.choices[0].message.content

    history.append({"role": "assistant", "content": assistant_content})
    return assistant_content