from huggingface_hub import InferenceClient
from app.core.config import settings

_client = None

def get_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(token=settings.hf_token)
    return _client

def generate(prompt: str, max_tokens: int = 500) -> str:
    """Single generic text-generation call — the shared entry point every
    feature (Q&A, summarization, etc.) builds on."""
    client = get_client()
    response = client.chat_completion(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    test_prompt = "In one sentence, explain what a wireless body area network is used for."
    print(generate(test_prompt, max_tokens=100))