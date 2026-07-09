from sentence_transformers import SentenceTransformer

from src.config import settings

_model = None


def get_model() -> SentenceTransformer:
    """Lazily load and cache the sentence-transformer embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Return embedding vectors (as plain lists) for a batch of texts."""
    vectors = get_model().encode(texts)
    return vectors.tolist()

