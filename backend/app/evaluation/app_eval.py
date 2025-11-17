"""
Application Level Evaluation
Tests complete user journeys, response quality, latency, user satisfaction
"""

from typing import List, Dict
from app.core.rag import RAGPipeline
from app.core.metrics import metrics_tracker
import json
import time


class ApplicationEvaluator:
    """Evaluate complete application workflows"""

    def __init__(self):
        self.rag = RAGPipeline()

    def evaluate_user_journey(
        self,
        journey: Dict
    ) -> Dict:
        """
        Evaluate a complete user journey (multi-turn conversation)

        journey format:
        {
            "name": "Journey name",
            "steps": [
                {
                    "query": "First question",
                    "expected_elements": ["element1", "element2"]
                },
                ...
            ]
        }
        """
        journey_start = time.time()
        conversation_history = []
        step_results = []

        for i, step in enumerate(journey["steps"]):
            step_start = time.time()

            # Generate response
            rag_result = self.rag.generate_response(
                query=step["query"],
                conversation_history=conversation_history
            )

            step_latency = time.time() - step_start

            # Add to conversation history
            conversation_history.append({"role": "user", "content": step["query"]})
            conversation_history.append({"role": "assistant", "content": rag_result["answer"]})

            # Check if expected elements are in response
            expected = step.get("expected_elements", [])
            found_elements = [
                elem for elem in expected
                if elem.lower() in rag_result["answer"].lower()
            ]

            element_coverage = len(found_elements) / len(expected) if expected else 1.0

            step_results.append({
                "step_number": i + 1,
                "query": step["query"],
                "latency_ms": round(step_latency * 1000, 1),
                "element_coverage": round(element_coverage, 2),
                "found_elements": found_elements,
                "num_sources": len(rag_result["sources"]),
                "response_length": len(rag_result["answer"])
            })

        journey_latency = time.time() - journey_start

        # Calculate aggregate metrics
        avg_latency = sum(s["latency_ms"] for s in step_results) / len(step_results)
        avg_coverage = sum(s["element_coverage"] for s in step_results) / len(step_results)

        return {
            "journey_name": journey["name"],
            "total_steps": len(step_results),
            "total_latency_ms": round(journey_latency * 1000, 1),
            "avg_step_latency_ms": round(avg_latency, 1),
            "avg_element_coverage": round(avg_coverage, 2),
            "steps": step_results
        }

    def evaluate_response_quality(
        self,
        test_cases: List[Dict]
    ) -> Dict:
        """
        Evaluate response quality metrics

        Measures:
        - Response completeness
        - Source quality
        - Latency distribution
        """
        results = []

        for test_case in test_cases:
            start = time.time()

            rag_result = self.rag.generate_response(
                query=test_case["query"],
                category=test_case.get("category")
            )

            latency = time.time() - start

            # Evaluate response
            response_length = len(rag_result["answer"])
            num_sources = len(rag_result["sources"])
            avg_relevance = (
                sum(s.get("relevance_score", 0) for s in rag_result["sources"]) / num_sources
                if num_sources > 0 else 0
            )

            results.append({
                "query": test_case["query"],
                "response_length_chars": response_length,
                "num_sources": num_sources,
                "avg_source_relevance": round(avg_relevance, 3),
                "latency_ms": round(latency * 1000, 1)
            })

        # Aggregate metrics
        avg_length = sum(r["response_length_chars"] for r in results) / len(results)
        avg_sources = sum(r["num_sources"] for r in results) / len(results)
        avg_relevance = sum(r["avg_source_relevance"] for r in results) / len(results)
        avg_latency = sum(r["latency_ms"] for r in results) / len(results)

        # Latency percentiles
        latencies = sorted(r["latency_ms"] for r in results)
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        return {
            "num_test_cases": len(results),
            "avg_response_length": round(avg_length, 1),
            "avg_num_sources": round(avg_sources, 1),
            "avg_source_relevance": round(avg_relevance, 3),
            "latency": {
                "avg_ms": round(avg_latency, 1),
                "p50_ms": round(p50, 1),
                "p95_ms": round(p95, 1),
                "p99_ms": round(p99, 1)
            },
            "individual_results": results
        }

    def simulate_user_satisfaction(
        self,
        test_cases: List[Dict]
    ) -> Dict:
        """
        Simulate user satisfaction based on response quality

        Scoring:
        - Fast response (< 3s): +1 point
        - Multiple sources: +1 point
        - High relevance (>0.7): +1 point
        - Complete answer (>200 chars): +1 point
        Max: 4 points (100% satisfied)
        """
        satisfaction_scores = []

        for test_case in test_cases:
            start = time.time()

            rag_result = self.rag.generate_response(query=test_case["query"])

            latency = time.time() - start
            response_length = len(rag_result["answer"])
            num_sources = len(rag_result["sources"])
            avg_relevance = (
                sum(s.get("relevance_score", 0) for s in rag_result["sources"]) / num_sources
                if num_sources > 0 else 0
            )

            # Calculate satisfaction score
            score = 0
            if latency < 3.0:
                score += 1
            if num_sources >= 2:
                score += 1
            if avg_relevance > 0.7:
                score += 1
            if response_length > 200:
                score += 1

            satisfaction = (score / 4) * 100  # Convert to percentage

            satisfaction_scores.append({
                "query": test_case["query"],
                "satisfaction_score": satisfaction,
                "factors": {
                    "fast_response": latency < 3.0,
                    "multiple_sources": num_sources >= 2,
                    "high_relevance": avg_relevance > 0.7,
                    "complete_answer": response_length > 200
                }
            })

        avg_satisfaction = sum(s["satisfaction_score"] for s in satisfaction_scores) / len(satisfaction_scores)

        return {
            "num_test_cases": len(satisfaction_scores),
            "avg_satisfaction_percentage": round(avg_satisfaction, 1),
            "satisfaction_distribution": {
                "very_satisfied": sum(1 for s in satisfaction_scores if s["satisfaction_score"] == 100),
                "satisfied": sum(1 for s in satisfaction_scores if 75 <= s["satisfaction_score"] < 100),
                "neutral": sum(1 for s in satisfaction_scores if 50 <= s["satisfaction_score"] < 75),
                "unsatisfied": sum(1 for s in satisfaction_scores if s["satisfaction_score"] < 50)
            },
            "individual_scores": satisfaction_scores
        }


def run_application_evaluation(test_file: str = "evaluation_tests/app_test_cases.json") -> Dict:
    """
    Run complete application-level evaluation

    Test file format:
    {
        "user_journeys": [...],
        "response_quality_tests": [...],
        "satisfaction_tests": [...]
    }
    """
    evaluator = ApplicationEvaluator()

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"Test file not found: {test_file}"}

    results = {}

    if "user_journeys" in test_data:
        journey_results = []
        for journey in test_data["user_journeys"]:
            journey_results.append(evaluator.evaluate_user_journey(journey))
        results["user_journeys"] = journey_results

    if "response_quality_tests" in test_data:
        results["response_quality"] = evaluator.evaluate_response_quality(
            test_data["response_quality_tests"]
        )

    if "satisfaction_tests" in test_data:
        results["user_satisfaction"] = evaluator.simulate_user_satisfaction(
            test_data["satisfaction_tests"]
        )

    return results
