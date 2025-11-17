"""
Monitoring and Analytics System
Tracks token usage, costs, latency, and performance metrics
"""

from datetime import datetime
from typing import Dict, List, Optional
import time
import json
from pathlib import Path


class MetricsTracker:
    """Track and store metrics for RAG system"""

    def __init__(self, metrics_file: str = "metrics.jsonl"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def log_query(
        self,
        query: str,
        response: str,
        sources: List[Dict],
        model: str,
        input_tokens: int,
        output_tokens: int,
        total_latency: float,
        first_token_latency: Optional[float] = None,
        retrieval_latency: float = 0,
        conversation_id: Optional[str] = None,
    ) -> Dict:
        """Log a complete query interaction"""

        # Calculate costs (OpenAI pricing)
        costs = self._calculate_costs(model, input_tokens, output_tokens)

        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_id": conversation_id,
            "query": query,
            "response": response,
            "model": model,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
            },
            "costs_usd": costs,
            "latency_ms": {
                "total": total_latency * 1000,
                "first_token": first_token_latency * 1000 if first_token_latency else None,
                "retrieval": retrieval_latency * 1000,
            },
            "retrieval": {
                "num_sources": len(sources),
                "avg_relevance": sum(s.get("relevance_score", 0) for s in sources) / len(sources)
                if sources
                else 0,
            },
        }

        # Append to JSONL file
        with open(self.metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(metric, ensure_ascii=False) + "\n")

        return metric

    def _calculate_costs(self, model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """Calculate costs based on model pricing"""

        # OpenAI pricing (as of 2025)
        pricing = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},  # per 1K tokens
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "text-embedding-3-large": {"input": 0.00013, "output": 0},
            "text-embedding-3-small": {"input": 0.00002, "output": 0},
        }

        prices = pricing.get(model, {"input": 0, "output": 0})

        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]

        return {
            "input": round(input_cost, 6),
            "output": round(output_cost, 6),
            "total": round(input_cost + output_cost, 6),
        }

    def get_stats(self, hours: Optional[int] = None) -> Dict:
        """Get aggregated statistics"""

        if not self.metrics_file.exists():
            return {"error": "No metrics data available"}

        metrics = []
        cutoff_time = None
        if hours:
            cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)

        with open(self.metrics_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    metric = json.loads(line)
                    if cutoff_time:
                        metric_time = datetime.fromisoformat(metric["timestamp"]).timestamp()
                        if metric_time < cutoff_time:
                            continue
                    metrics.append(metric)
                except:
                    continue

        if not metrics:
            return {"error": "No metrics in timeframe"}

        # Aggregate stats
        total_queries = len(metrics)
        total_tokens = sum(m["tokens"]["total"] for m in metrics)
        total_cost = sum(m["costs_usd"]["total"] for m in metrics)
        avg_latency = sum(m["latency_ms"]["total"] for m in metrics) / total_queries
        avg_retrieval_latency = sum(m["latency_ms"]["retrieval"] for m in metrics) / total_queries
        avg_sources = sum(m["retrieval"]["num_sources"] for m in metrics) / total_queries
        avg_relevance = sum(m["retrieval"]["avg_relevance"] for m in metrics) / total_queries

        # First token latency (only for streaming)
        first_token_latencies = [
            m["latency_ms"]["first_token"] for m in metrics if m["latency_ms"]["first_token"]
        ]
        avg_first_token = (
            sum(first_token_latencies) / len(first_token_latencies) if first_token_latencies else None
        )

        return {
            "period_hours": hours,
            "total_queries": total_queries,
            "tokens": {
                "total": total_tokens,
                "avg_per_query": round(total_tokens / total_queries, 1),
            },
            "costs_usd": {
                "total": round(total_cost, 4),
                "avg_per_query": round(total_cost / total_queries, 6),
            },
            "latency_ms": {
                "avg_total": round(avg_latency, 1),
                "avg_retrieval": round(avg_retrieval_latency, 1),
                "avg_first_token": round(avg_first_token, 1) if avg_first_token else None,
            },
            "retrieval": {
                "avg_sources": round(avg_sources, 1),
                "avg_relevance": round(avg_relevance, 3),
            },
        }


# Global instance
metrics_tracker = MetricsTracker()
