"""
Sends document text to an LLM and gets back a classification, extracted
fields, and a suggested next action, all as one JSON response.
"""
import json
import re
import requests

import config

PROMPT_TEMPLATE = """You are an assistant that reads a document and returns ONLY a JSON object, nothing else.

Analyze the document below and respond with this exact JSON structure:
{{
  "document_type": "one of: invoice, contract, cv, request, general_note, other",
  "summary": "two to three sentences that name the specific sender, the specific amount or key figures, and the specific date or deadline found in the document, not a vague description",
  "key_fields": {{
    "sender": "name or company if identifiable, else empty string",
    "date": "date mentioned in the document if any, else empty string",
    "amount": "monetary amount if this is an invoice or payment related, else empty string",
    "deadline": "any deadline or due date mentioned, else empty string"
  }},
  "suggested_action": "a short, specific action someone should take next, based on what this document actually is and contains",
  "priority": "one of: low, medium, high"
}}

Rules:
- Base document_type and suggested_action on the actual content, not the filename.
- If a field does not apply, use an empty string, do not guess.
- Respond with ONLY the JSON object. No explanation, no markdown formatting.

DOCUMENT CONTENT:
\"\"\"
{content}
\"\"\"
"""


def _call_ollama(prompt: str) -> str:
    response = requests.post(
        config.OLLAMA_URL,
        json={
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",   # tells Ollama to only output valid JSON
            "options": {"temperature": 0},  # keep responses consistent
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def _call_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY from environment
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content


def _extract_json(raw_text: str) -> dict:
    """
    Pulls the JSON object out of the model's response and parses it.
    Tries a couple of quick repairs first if the raw text has small
    formatting issues like a trailing comma.
    """
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model response: {raw_text[:200]}")

    candidate = match.group(0)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # remove trailing commas before a closing } or ]
    repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # strip stray newlines/tabs that sometimes end up inside string values
    repaired = re.sub(r"[\x00-\x1f]+", " ", repaired)
    return json.loads(repaired)


def analyze_document(text: str) -> dict:
    """
    Sends the document text to the model and returns the parsed result.
    If anything goes wrong, returns a safe fallback instead of crashing.
    """
    truncated = text[: config.MAX_CHARS_TO_MODEL]
    prompt = PROMPT_TEMPLATE.format(content=truncated)

    try:
        if config.LLM_PROVIDER == "ollama":
            raw = _call_ollama(prompt)
        elif config.LLM_PROVIDER == "openai":
            raw = _call_openai(prompt)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {config.LLM_PROVIDER}")

        return _extract_json(raw)

    except Exception as e:
        print(f"[ai_engine] Analysis failed: {e}")
        return {
            "document_type": "other",
            "summary": "Could not analyze this document automatically.",
            "key_fields": {"sender": "", "date": "", "amount": "", "deadline": ""},
            "suggested_action": "Review manually.",
            "priority": "medium",
        }
