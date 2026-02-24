import json
import sys
import requests

def main():
    base_url = "http://localhost:11434"
    # model = "llama3.2"  # "llama3.1:8b" # change to qwen3:8b, deepseek-r1:8b, etc.
    # model = "llama3.1:8b"  
    model = "qwen3:8b"  

    url = f"{base_url}/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Reply in one sentence."},
            {"role": "user", "content": "Say hello and tell me the current weekday (just guess)."},
        ],
        "options": {"temperature": 0.0,
                    "num_ctx": 8192,      # <- context window
                    "num_predict": 128,   # <- cap output tokens (optional but good practice)
},
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print("ERROR: Failed to call Ollama API.")
        print(e)
        sys.exit(1)

    data = r.json()
    content = data.get("message", {}).get("content", "")

    print("=== Model reply ===")
    print(content.strip())
    print()

    # These fields are useful for performance sanity checks
    stats = {
        "prompt_tokens": data.get("prompt_eval_count"),
        "gen_tokens": data.get("eval_count"),
        "total_duration_ms": (data.get("total_duration", 0) or 0) / 1e6,
        "prompt_eval_ms": (data.get("prompt_eval_duration", 0) or 0) / 1e6,
        "eval_ms": (data.get("eval_duration", 0) or 0) / 1e6,
    }

    print("=== Stats ===")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()