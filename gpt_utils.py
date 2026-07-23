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
    "question, just answer it without padding. "
    "When someone asks what you think or for your take, give ONE genuine, specific answer -- don't hand back "
    "a menu of two or three alternative phrasings/options unless they explicitly asked for options. Commit to "
    "a stance instead of hedging between choices, and make sure that stance actually follows logically from "
    "what they just said (don't contradict yourself by ruling something out and then suggesting it anyway). "
    "Avoid generic advice-column wrap-up lines -- the kind that start with 'the important thing is...', "
    "'just remember to...', or 'as long as it feels natural...' -- real friends don't talk like a self-help "
    "caption, they just say what they think. "
    "This is a shared server channel, not a 1-on-1 DM -- more than one person can talk to you in the same "
    "conversation. Every user message below is prefixed with the sender's name, like 'Name: message', so you "
    "can tell who's who. Pay attention to those names: don't assume two messages came from the same person "
    "just because they're both stored as 'user' turns, and don't respond to one person as if they said "
    "something another person actually said. You don't need to repeat that 'Name:' format in your own replies "
    "-- just answer naturally, and address someone by name if it helps make clear who you're replying to."
)

# Per-conversation history so different channels/servers don't bleed into each other.
# Keyed by a conversation id (e.g. "guildid-channelid"); falls back to "default" if none given.
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


def clear_history(conversation_id):
    """Forget the stored conversation for this id. Returns True if there was anything to forget."""
    key = conversation_id or "default"
    return conversation_histories.pop(key, None) is not None


def gpt_response(message, language=None, image_urls=None, conversation_id=None, author_name=None):
    history = _get_history(conversation_id)

    if image_urls:
        image_prompt = (
            "The user included image attachments at these URLs: " + ", ".join(image_urls) + ". "
            "You can mention these image links in your response, but do not claim to see their visual contents if you cannot."
        )
        message = f"{message}\n\n{image_prompt}" if message else image_prompt

    if author_name:
        message = f"{author_name}: {message}" if message else f"{author_name}: (sent an image, no text)"

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