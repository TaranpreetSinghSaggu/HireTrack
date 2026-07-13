import json
import requests

from flask import current_app
from utils.gemini import generate_gemini_content


def clean_json_content(content):
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if len(lines) >= 3:
            content = "\n".join(lines[1:-1]).strip()

    return content


def analyze_resume_ai(resume_text):
    if not current_app.config.get("GEMINI_API_KEY"):
        return None

    prompt = f"""
    Extract the following from this resume:

    - Full Name
    - Contact (email or phone)
    - Degree (e.g., B.Tech, B.Sc, BE, etc.)
    - Institution/University
    - Branch/Major
    - Year/Current Year (1-4)
    - Passout Year (graduation year)
    - CGPA (Grade Point Average)
    - Skills (list of technical skills)
    - Experience (work experience summary)

    Return ONLY valid JSON in this format:

    {{
        "name": "",
        "contact": "",
        "degree": "",
        "institution": "",
        "branch": "",
        "year": null,
        "passout_year": null,
        "cgpa": null,
        "skills": [],
        "experience": ""
    }}

    Resume:

    {resume_text}
    """

    try:
        content = clean_json_content(generate_gemini_content(prompt, temperature=0, timeout=20))
        result = json.loads(content)

        if not isinstance(result, dict):
            return None

        return {
            "name": result.get("name"),
            "contact": result.get("contact"),
            "degree": result.get("degree"),
            "institution": result.get("institution"),
            "branch": result.get("branch"),
            "year": result.get("year"),
            "passout_year": result.get("passout_year"),
            "cgpa": result.get("cgpa"),
            "skills": result.get("skills") if isinstance(result.get("skills"), list) else [],
            "experience": result.get("experience"),
        }

    except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as error:
        print(f"Gemini resume analysis failed, using fallback parser: {error}")

        return None
