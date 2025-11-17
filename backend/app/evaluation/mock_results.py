"""
Mock evaluation results for testing without API calls
"""

def get_mock_rag_results():
    """Mock RAG evaluation results"""
    return {
        "retrieval_quality": {
            "num_test_cases": 22,
            "avg_precision": 0.85,
            "avg_recall": 0.78,
            "avg_f1": 0.81,
            "avg_mrr": 0.88
        },
        "individual_results": [
            {
                "query": "Mennyit térít a Uniqua Basic Casco jégkárra?",
                "precision": 0.8,
                "recall": 0.8,
                "f1": 0.8,
                "mrr": 1.0,
                "num_results": 5,
                "retrieved_docs": ["doc_1", "doc_2"]
            }
        ]
    }

def get_mock_prompt_results():
    """Mock Prompt evaluation results"""
    return {
        "num_test_cases": 18,
        "avg_context_relevance": 4.2,
        "avg_answer_quality": 4.5,
        "hallucination_rate": 5.6,
        "individual_results": [
            {
                "query": "Milyen esetekben nem fizet az Allianz?",
                "response": "Az Allianz nem fizet szándékos károkozás, ittas vezetés...",
                "context_relevance": {
                    "relevance_score": 5,
                    "reasoning": "A kontextus tökéletesen releváns"
                },
                "hallucination_check": {
                    "has_hallucination": False,
                    "severity": "nincs",
                    "confidence": 0.95
                },
                "answer_quality": {
                    "accuracy": 5,
                    "completeness": 4,
                    "clarity": 5,
                    "relevance": 5,
                    "overall_score": 5,
                    "feedback": "Kiváló válasz"
                }
            }
        ]
    }

def get_mock_application_results():
    """Mock Application evaluation results"""
    return {
        "user_journeys": [
            {
                "journey_name": "Kárbejelentési folyamat",
                "total_steps": 2,
                "total_latency_ms": 4500,
                "avg_step_latency_ms": 2250,
                "avg_element_coverage": 0.85,
                "steps": [
                    {
                        "step_number": 1,
                        "query": "Hogyan kell bejelenteni kárt?",
                        "latency_ms": 2100,
                        "element_coverage": 1.0,
                        "found_elements": ["bejelentés", "határidő"],
                        "num_sources": 4,
                        "response_length": 450
                    }
                ]
            }
        ],
        "response_quality": {
            "num_test_cases": 3,
            "avg_response_length": 520,
            "avg_num_sources": 3.5,
            "avg_source_relevance": 0.78,
            "latency": {
                "avg_ms": 2100,
                "p50_ms": 2000,
                "p95_ms": 3200,
                "p99_ms": 3500
            }
        },
        "user_satisfaction": {
            "num_test_cases": 3,
            "avg_satisfaction_percentage": 75,
            "satisfaction_distribution": {
                "very_satisfied": 1,
                "satisfied": 1,
                "neutral": 1,
                "unsatisfied": 0
            }
        }
    }
