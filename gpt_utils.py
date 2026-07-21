import os
from dotenv import load_dotenv
from groq import Groq
from slang import apply_slang, normalize_language

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set. Please add it to your .env file or environment variables.")

client = Groq(api_key=api_key)

system_prompt = [
    {
        "role": "system",
        "content": (
            "You are a funny and casual Discord bot. Answer with a friendly tone, make light jokes, "
            "use emojis occasionally, and keep the conversation relaxed. Be playful but helpful. "
            "When possible, use casual slang appropriate to the user's language without being offensive."
        )
    }
]

messages = []

def gpt_response(message, language=None, image_urls=None):
    global messages

    if image_urls:
        image_prompt = (
            "The user included image attachments at these URLs: " + ", ".join(image_urls) + ". "
            "You can mention these image links in your response, but do not claim to see their visual contents if you cannot."
        )
        message = f"{message}\n\n{image_prompt}" if message else image_prompt

    messages.append({"role": "user", "content": message})
    if len(messages) > 20:
        messages = messages[-20:]

    prompt_messages = system_prompt.copy()
    if language:
        prompt_messages.append({
            "role": "system",
            "content": f"Answer all user messages in {language}."
        })

    response = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=prompt_messages + messages
    )

    assistant_content = response.choices[0].message.content
    # Apply slang post-processing based on language (non-destructive)
    try:
        lang_key = normalize_language(language)
        assistant_content = apply_slang(assistant_content, lang_key, probability=0.14)
    except Exception:
        pass

    messages.append({"role": "assistant", "content": assistant_content})
    return assistant_content