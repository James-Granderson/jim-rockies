import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    def load_dotenv():
        return False

try:
    from google import genai
except ImportError:  # pragma: no cover - installed via requirements
    genai = None


load_dotenv()


def get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your environment or a .env file."
        )
    return api_key


def generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        )

    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=model, contents=prompt)
    return getattr(response, "text", str(response))


def chat(messages, model: str = "gemini-2.5-flash") -> str:
    if isinstance(messages, str):
        return generate_text(messages, model=model)

    prompt = "\n".join(
        f"{message.get('role', 'user')}: {message.get('content', '')}"
        for message in messages
    )
    return generate_text(prompt, model=model)
