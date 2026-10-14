import abc
import hashlib
import json
import re
from typing import List
import urllib.request
import numpy as np

class BaseEmbedder(abc.ABC):
    @abc.abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

class GeminiEmbedder(BaseEmbedder):
    """Generates dense semantic embeddings via Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.api_key = api_key
        self.model = model

    def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent?key={self.api_key}"
        payload = {
            "content": {"parts": [{"text": text}]}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["embedding"]["values"]

class FastLocalEmbedder(BaseEmbedder):
    """
    Ultra-low latency local embedding using hashing and character/token n-grams.
    Zero external dependencies, runs in ~0.15ms.
    Useful for offline testing, high-throughput micro-benchmarks, and fallback.
    """

    def __init__(self, dim: int = 512):
        self.dim = dim

    def embed_text(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = re.findall(r"\w+", text.lower())

        if not tokens:
            return vec.tolist()

        for token in tokens:
            # Word level hash
            h = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim
            vec[h] += 1.0

            # Character 3-gram hashes for subword semantic capture
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    ngram = token[i:i+3]
                    h_ng = int(hashlib.sha256(ngram.encode()).hexdigest(), 16) % self.dim
                    vec[h_ng] += 0.5

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

def get_embedder(embedder_type: str, gemini_api_key: str = "", gemini_model: str = "gemini-embedding-001") -> BaseEmbedder:
    if embedder_type == "gemini" and gemini_api_key:
        return GeminiEmbedder(api_key=gemini_api_key, model=gemini_model)
    return FastLocalEmbedder()
