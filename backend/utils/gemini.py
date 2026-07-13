import requests

from flask import current_app


GEMINI_ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def generate_gemini_content(prompt, temperature=0.3, timeout=20):
    """Return Gemini's text response for a single prompt."""
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini AI is not configured")

    model = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")
    response = requests.post(
        GEMINI_ENDPOINT_TEMPLATE.format(model=model),
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
