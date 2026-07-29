import requests
from agent import config


def _try_model_request(url: str, headers: dict, payload: dict, model: str) -> dict:
    """Attempt a single chat completion request for a specific model."""
    body = payload.copy()
    body["model"] = model
    response = requests.post(url, headers=headers, json=body, timeout=30)
    response.raise_for_status()

    result = response.json()
    if "choices" not in result or len(result["choices"]) == 0:
        raise ValueError(f"Invalid API response: {result}")
    return result["choices"][0]["message"]


def _call_groq(payload: dict) -> dict:
    """Try Groq as the primary provider."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    print(f"Calling Groq ({config.GROQ_MODEL})...")
    
    import time
    for attempt in range(3):
        try:
            return _try_model_request(url, headers, payload, config.GROQ_MODEL)
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status == 429 and attempt < 2:
                print(f"Groq rate-limited (429). Sleeping 10 seconds before retry {attempt + 1}/3...")
                time.sleep(10)
                continue
            raise e


def _call_gemini(payload: dict) -> dict:
    """Try Gemini chain as the fallback provider after Groq fails."""
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    print("Falling back to Gemini chain...")
    for i, model in enumerate(config.GEMINI_MODELS):
        print(f"Calling Gemini ({model})...")
        try:
            return _try_model_request(url, headers, payload, model)
        except Exception as e:
            # Check if it failed due to 429 or 503
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (429, 503):
                reason = "rate-limited" if status == 429 else "overloaded"
                print(f"{model} is {reason}.")
            else:
                print(f"{model} call failed ({e}).")

            if i < len(config.GEMINI_MODELS) - 1:
                next_model = config.GEMINI_MODELS[i + 1]
                print(f"Trying next model {next_model}...")
            else:
                print("All Gemini models failed.")

    return None


def call_llm(messages: list[dict], tools: list[dict] = None) -> dict:
    """Call an LLM with tool support. Tries Groq first, then falls back to Gemini chain."""
    payload = {"messages": messages}
    if tools:
        payload["tools"] = tools

    try:
        return _call_groq(payload)
    except Exception as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 400:
            print(f"Groq API 400 Bad Request body: {e.response.text}")
        print(f"Groq call failed: {e}")
        
    result = _call_gemini(payload)
    if result is not None:
        return result

    raise RuntimeError("All Groq and Gemini models in the fallback chain failed.")