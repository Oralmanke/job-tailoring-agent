"""Provider-agnostic LLM access layer.

Kept separate from tailoring/evaluation logic so both can depend on it without
importing each other (this also breaks the tailor <-> evaluator import cycle).
Supports Anthropic, OpenAI, and a local Ollama endpoint.
"""
import json

from anthropic import Anthropic
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.logger import get_logger

log = get_logger(__name__)

_clients: dict = {}


def get_client(provider: str):
    """Return a cached client for the given provider, creating it on first use."""
    if provider not in _clients:
        if provider == "ollama":
            _clients[provider] = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        elif provider == "openai":
            _clients[provider] = OpenAI(api_key=settings.openai_api_key)
        elif provider == "anthropic":
            _clients[provider] = Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    return _clients[provider]


@retry(
    stop=stop_after_attempt(settings.max_retries),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    reraise=True,
)
def generate(prompt: str, system: str, provider: str = None,
             temperature: float = 0.2, max_tokens: int = 1024) -> str:
    """Call the configured LLM and return its raw text response.

    Retries with exponential backoff on transient provider errors so a single
    slow/failed API call does not kill the whole pipeline.
    """
    provider = provider or settings.llm_provider
    client = get_client(provider)

    if provider == "anthropic":
        resp = client.messages.create(
            model=settings.model_name,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.content[0].text

    resp = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content


def parse_json(raw: str) -> dict:
    """Parse a JSON object out of an LLM response, tolerating ```code fences```."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].removeprefix("json").strip()
    return json.loads(raw)
