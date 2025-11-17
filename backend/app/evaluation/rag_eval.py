"""
RAG Level Evaluation
Tests retrieval quality: precision, recall, MRR (Mean Reciprocal Rank)
"""

from typing import List, Dict, Tuple
from app.services.vector_store import VectorStore
import json


class RAGEvaluator:
    """Evaluate RAG retrieval performance"""

    def __init__(self):
        self.vector_store = VectorStore()

    def evaluate_retrieval(
        self,
        query: str,
        expected_doc_ids: List[str],
        k: int = 5
    ) -> Dict:
        """
        Evaluate retrieval quality for a single query

        Args:
            query: The search query
            expected_doc_ids: List of relevant document IDs
            k: Number of results to retrieve

        Returns:
            Dict with precision, recall, MRR scores
        """
        # Retrieve results
        results = self.vector_store.search(query, n_results=k)

        retrieved_doc_ids = [r['metadata']['doc_id'] for r in results]

        # Calculate metrics
        relevant_retrieved = set(retrieved_doc_ids) & set(expected_doc_ids)

        precision = len(relevant_retrieved) / len(retrieved_doc_ids) if retrieved_doc_ids else 0
        recall = len(relevant_retrieved) / len(expected_doc_ids) if expected_doc_ids else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Calculate MRR (Mean Reciprocal Rank)
        mrr = 0
        for i, doc_id in enumerate(retrieved_doc_ids):
            if doc_id in expected_doc_ids:
                mrr = 1 / (i + 1)
                break

        return {
            "query": query,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "mrr": round(mrr, 3),
            "num_results": len(results),
            "num_relevant": len(relevant_retrieved),
            "retrieved_docs": retrieved_doc_ids[:3],  # Top 3 for debugging
        }

    def evaluate_embedding_quality(
        self,
        test_cases: List[Dict[str, any]]
    ) -> Dict:
        """
        Evaluate embedding model performance

        test_cases format:
        [
            {
                "query": "Mennyit térít jégkárra?",
                "expected_docs": ["doc_uuid_1", "doc_uuid_2"]
            },
            ...
        ]
        """
        results = []

        for test_case in test_cases:
            result = self.evaluate_retrieval(
                query=test_case["query"],
                expected_doc_ids=test_case["expected_docs"],
                k=5
            )
            results.append(result)

        # Aggregate metrics
        avg_precision = sum(r["precision"] for r in results) / len(results)
        avg_recall = sum(r["recall"] for r in results) / len(results)
        avg_f1 = sum(r["f1_score"] for r in results) / len(results)
        avg_mrr = sum(r["mrr"] for r in results) / len(results)

        return {
            "num_test_cases": len(test_cases),
            "avg_precision": round(avg_precision, 3),
            "avg_recall": round(avg_recall, 3),
            "avg_f1_score": round(avg_f1, 3),
            "avg_mrr": round(avg_mrr, 3),
            "individual_results": results
        }

    def evaluate_chunking_strategy(
        self,
        test_cases: List[Dict]
    ) -> Dict:
        """
        Evaluate how well the chunking strategy works
        Tests if chunks contain relevant information
        """
        chunk_scores = []

        for test_case in test_cases:
            query = test_case["query"]
            expected_keywords = test_case.get("expected_keywords", [])

            results = self.vector_store.search(query, n_results=3)

            # Check if expected keywords are in retrieved chunks
            found_keywords = 0
            for result in results:
                chunk_text = result['text'].lower()
                for keyword in expected_keywords:
                    if keyword.lower() in chunk_text:
                        found_keywords += 1
                        break

            keyword_coverage = found_keywords / len(expected_keywords) if expected_keywords else 0
            chunk_scores.append({
                "query": query,
                "keyword_coverage": keyword_coverage,
                "avg_chunk_length": sum(len(r['text']) for r in results) / len(results) if results else 0
            })

        avg_coverage = sum(s["keyword_coverage"] for s in chunk_scores) / len(chunk_scores)

        return {
            "num_tests": len(test_cases),
            "avg_keyword_coverage": round(avg_coverage, 3),
            "chunk_analyses": chunk_scores
        }


def run_rag_evaluation(test_file: str = "evaluation_tests/rag_test_cases.json") -> Dict:
    """
    Run complete RAG evaluation from test file

    Test file format:
    {
        "retrieval_tests": [...],
        "embedding_tests": [...],
        "chunking_tests": [...]
    }
    """
    evaluator = RAGEvaluator()

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"Test file not found: {test_file}"}

    results = {}

    if "retrieval_tests" in test_data:
        results["retrieval"] = evaluator.evaluate_embedding_quality(test_data["retrieval_tests"])

    if "chunking_tests" in test_data:
        results["chunking"] = evaluator.evaluate_chunking_strategy(test_data["chunking_tests"])

    return results
