import time
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

class VectorEntry:
    def __init__(
        self,
        key: str,
        embedding: np.ndarray,
        response_content: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        created_at: Optional[float] = None,
        ttl_seconds: int = 86400,
    ):
        self.key = key
        # Normalize embedding on insertion for fast dot-product cosine similarity
        norm = np.linalg.norm(embedding)
        self.embedding = embedding / (norm + 1e-12) if norm > 0 else embedding
        self.response_content = response_content
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.created_at = created_at or time.time()
        self.ttl_seconds = ttl_seconds
        self.hit_count = 0

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds

class InMemoryVectorStore:
    """High-performance in-memory vector store with cosine similarity matching."""

    def __init__(self):
        self._entries: List[VectorEntry] = []
        self._total_queries: int = 0
        self._total_hits: int = 0
        self._total_tokens_saved: int = 0
        self._recent_queries: List[Dict[str, Any]] = []

    def record_query_log(
        self,
        prompt: str,
        cached: bool,
        provider: str,
        latency_ms: float,
        tokens_saved: int = 0
    ):
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "prompt": prompt[:80] + ("..." if len(prompt) > 80 else ""),
            "cached": cached,
            "provider": provider,
            "latency_ms": round(latency_ms, 2),
            "tokens_saved": tokens_saved,
        }
        self._recent_queries.append(entry)
        if len(self._recent_queries) > 20:
            self._recent_queries.pop(0)

    def insert(
        self,
        key: str,
        embedding: List[float],
        response_content: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        ttl_seconds: int = 86400,
    ) -> VectorEntry:
        entry = VectorEntry(
            key=key,
            embedding=np.array(embedding, dtype=np.float32),
            response_content=response_content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            ttl_seconds=ttl_seconds,
        )
        self._entries.append(entry)
        return entry

    def search_nearest(
        self,
        query_embedding: List[float],
        min_threshold: float = 0.88
    ) -> Optional[Tuple[VectorEntry, float]]:
        """
        Search for the most semantically similar entry.
        Returns (best_entry, similarity_score) if score >= min_threshold, else None.
        """
        self._total_queries += 1

        if not self._entries:
            return None

        # Clean expired entries lazily
        self._entries = [e for e in self._entries if not e.is_expired()]
        if not self._entries:
            return None

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return None
        q_vec = q_vec / q_norm

        # Matrix of all stored embeddings
        matrix = np.vstack([e.embedding for e in self._entries])
        # Vectorized dot product cosine similarities
        scores = np.dot(matrix, q_vec)

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score >= min_threshold:
            best_entry = self._entries[best_idx]
            best_entry.hit_count += 1
            self._total_hits += 1
            self._total_tokens_saved += (best_entry.prompt_tokens + best_entry.completion_tokens)
            return best_entry, best_score

        return None

    def get_stats(self) -> Dict[str, Any]:
        hit_ratio = (self._total_hits / self._total_queries) if self._total_queries > 0 else 0.0
        # Average token price approx $2.50 per 1M tokens ($0.0000025 per token)
        est_savings = self._total_tokens_saved * 0.0000025
        return {
            "total_cached_entries": len(self._entries),
            "total_queries": self._total_queries,
            "total_hits": self._total_hits,
            "hit_ratio_percent": round(hit_ratio * 100, 2),
            "total_tokens_saved": self._total_tokens_saved,
            "estimated_cost_saved_usd": round(est_savings, 5),
            "recent_queries": list(reversed(self._recent_queries)),
        }

    def clear(self):
        self._entries.clear()
        self._total_queries = 0
        self._total_hits = 0
        self._total_tokens_saved = 0
        self._recent_queries.clear()
