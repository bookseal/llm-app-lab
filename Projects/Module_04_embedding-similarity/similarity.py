"""Embedding playground — cosine similarity between two phrases.

A tiny console app: type two phrases, get their cosine similarity score using a
local multilingual embedding model (no API key required). Because the model is
multilingual, the two phrases can be in different languages and still score as
similar when they mean the same thing.

    python similarity.py
    phrase 1 › a dog runs in the park
    phrase 2 › a puppy sprints across the grass
    cosine similarity: 0.541

One-shot mode (handy for quick checks / scripts):

    python similarity.py "cat" "고양이"
"""
import math
import sys

from sentence_transformers import SentenceTransformer

# Multilingual (50+ languages), so cross-lingual pairs (e.g. English ↔ Korean)
# score as similar instead of ~0. Embeddings are unit-normalized, so the cosine
# similarity of two vectors is just their dot product.
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model ({MODEL_NAME})... (one-time download)")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(a: str, b: str):
    """Turn two phrases into embedding vectors (one batched model call).

    Each phrase becomes a point in high-dimensional space (384 numbers for this
    model). `normalize_embeddings=True` scales each vector to length 1 so we can
    compare directions cleanly. Returns the two vectors.
    """
    vecs = get_model().encode([a, b], normalize_embeddings=True)
    return vecs[0], vecs[1]


def cosine_similarity(va, vb) -> float:
    """Measure how similar two embedding vectors are, in [-1, 1].

    Cosine similarity is the cosine of the ANGLE between the two vectors. It
    cares about *direction* (does the meaning point the same way?), not about
    how long the vectors are. Because the vectors are already normalized to
    length 1, cos(angle) is simply their dot product — multiply the vectors
    element-by-element and sum:  va · vb = Σ va[i] * vb[i].

    Reading the result:
        1.0  → same direction      (≈ same meaning)
        0.0  → perpendicular       (unrelated)
       -1.0  → opposite direction  (opposite meaning)
    """
    return float(va @ vb)  # @ is the dot product for these 1-D vectors


def _preview(vec, n: int = 5) -> str:
    """Show the first `n` numbers of a vector as [x, y, z, ...]."""
    head = ", ".join(f"{x:.3f}" for x in vec[:n])
    return f"[{head}, ...]  ({len(vec)} dims)"


def _report(a: str, b: str) -> None:
    va, vb = embed(a, b)
    # Show what each phrase actually became — a list of numbers.
    print(f"  vec({a!r}) = {_preview(va)}")
    print(f"  vec({b!r}) = {_preview(vb)}")

    cos = cosine_similarity(va, vb)
    # Turn the cosine score into the angle it represents (clamped to acos's
    # valid [-1, 1] domain to guard against tiny floating-point overshoot).
    angle = math.degrees(math.acos(max(-1.0, min(1.0, cos))))
    print(f"  angle between them: {angle:.1f}°")
    print(f"  cosine similarity:  {cos:.3f}")


def repl() -> None:
    print("Cosine similarity of two phrases. (Ctrl-C or empty input to quit.)\n")
    get_model()  # warm up once so the first answer isn't slow
    while True:
        try:
            a = input("phrase 1 › ").strip()
            if not a:
                break
            b = input("phrase 2 › ").strip()
            if not b:
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break
        _report(a, b)
        print()


def main() -> int:
    if len(sys.argv) == 3:  # one-shot: python similarity.py "phrase a" "phrase b"
        _report(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 1:
        repl()
    else:
        print('Usage: python similarity.py ["phrase a" "phrase b"]', file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
