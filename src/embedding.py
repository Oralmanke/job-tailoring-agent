from sentence_transformers import SentenceTransformer, util

_model = None

def get_model():
    global _model
    if _model == None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    vectors = get_model().encode(texts)
    return vectors.tolist()

