"""
Prompt Level Evaluation
Tests context relevance, hallucination detection, LLM-as-Judge
"""

from typing import List, Dict
from openai import OpenAI
from app.core.config import get_settings
from app.core.rag import RAGPipeline
import json


class PromptEvaluator:
    """Evaluate prompt quality and LLM responses"""

    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.rag = RAGPipeline()

    def evaluate_context_relevance(
        self,
        query: str,
        context: str,
        response: str
    ) -> Dict:
        """
        Use LLM-as-Judge to evaluate if context was relevant to the response
        """
        judge_prompt = f"""Értékeld, hogy a megadott kontextus mennyire releváns volt a kérdéshez és a válaszhoz.

Kérdés: {query}

Kontextus:
{context}

Válasz:
{response}

Értékeld 1-5 skálán:
1 - Teljesen irreleváns
2 - Kissé releváns
3 - Közepesen releváns
4 - Nagyon releváns
5 - Tökéletesen releváns

Add meg a pontszámot és egy rövid indoklást JSON formátumban:
{{"score": <1-5>, "reasoning": "<indoklás>"}}"""

        judge_response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=150  # Limit tokens for faster response
        )

        try:
            result = json.loads(judge_response.choices[0].message.content)
            return {
                "relevance_score": result.get("score", 0),
                "reasoning": result.get("reasoning", ""),
                "query": query
            }
        except:
            return {"relevance_score": 0, "reasoning": "Parse error", "query": query}

    def detect_hallucination(
        self,
        query: str,
        context: str,
        response: str
    ) -> Dict:
        """
        Use LLM-as-Judge to detect if the response contains hallucinations
        (information not present in the context)
        """
        judge_prompt = f"""Ellenőrizd, hogy a válasz tartalmaz-e olyan információt, ami NINCS a megadott kontextusban.

Kérdés: {query}

Kontextus:
{context}

Válasz:
{response}

Értékeld:
- Van-e hallucináció? (igen/nem)
- Ha igen, mely részek hallucinációk?
- Mennyire súlyos? (enyhe/közepes/súlyos)

JSON formátumban:
{{
    "has_hallucination": <true/false>,
    "hallucinated_parts": ["<részlet1>", "<részlet2>"],
    "severity": "<enyhe/közepes/súlyos/nincs>",
    "confidence": <0-1>
}}"""

        judge_response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=150  # Limit tokens for faster response
        )

        try:
            result = json.loads(judge_response.choices[0].message.content)
            return {
                "has_hallucination": result.get("has_hallucination", False),
                "hallucinated_parts": result.get("hallucinated_parts", []),
                "severity": result.get("severity", "nincs"),
                "confidence": result.get("confidence", 0),
                "query": query
            }
        except:
            return {
                "has_hallucination": None,
                "error": "Parse error",
                "query": query
            }

    def evaluate_answer_quality(
        self,
        query: str,
        response: str,
        expected_answer: str = None
    ) -> Dict:
        """
        Use LLM-as-Judge to evaluate overall answer quality
        """
        judge_prompt = f"""Értékeld a választ az alábbi szempontok szerint:

Kérdés: {query}

Válasz:
{response}
"""

        if expected_answer:
            judge_prompt += f"""
Elvárt válasz:
{expected_answer}
"""

        judge_prompt += """
Értékeld a következő szempontok szerint (1-5 skálán):
1. Pontosság - Helyes információkat tartalmaz?
2. Teljességhatár - Teljes választ ad?
3. Világosság - Érthető és jól strukturált?
4. Relevancia - A kérdésre válaszol?

JSON formátumban:
{
    "accuracy": <1-5>,
    "completeness": <1-5>,
    "clarity": <1-5>,
    "relevance": <1-5>,
    "overall_score": <1-5>,
    "feedback": "<rövid visszajelzés>"
}"""

        judge_response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=150  # Limit tokens for faster response
        )

        try:
            result = json.loads(judge_response.choices[0].message.content)
            return {
                "accuracy": result.get("accuracy", 0),
                "completeness": result.get("completeness", 0),
                "clarity": result.get("clarity", 0),
                "relevance": result.get("relevance", 0),
                "overall_score": result.get("overall_score", 0),
                "feedback": result.get("feedback", ""),
                "query": query
            }
        except:
            return {"overall_score": 0, "error": "Parse error", "query": query}

    def evaluate_single_turn(
        self,
        test_case: Dict
    ) -> Dict:
        """
        Evaluate a single-turn conversation

        test_case format:
        {
            "query": "Kérdés",
            "expected_answer": "Elvárt válasz (opcionális)",
            "context": "Kontextus (opcionális - ha nincs, RAG generálja)"
        }
        """
        query = test_case["query"]

        # Get RAG response if context not provided
        if "context" not in test_case:
            rag_result = self.rag.generate_response(query)
            response = rag_result["answer"]
            context = "\n\n".join([s.get("chunk_text", "") for s in rag_result["sources"]])
        else:
            # Use provided context and response
            context = test_case["context"]
            response = test_case.get("response", "")

        # Run evaluations
        relevance = self.evaluate_context_relevance(query, context, response)
        hallucination = self.detect_hallucination(query, context, response)
        quality = self.evaluate_answer_quality(
            query,
            response,
            test_case.get("expected_answer")
        )

        return {
            "query": query,
            "response": response,
            "context_relevance": relevance,
            "hallucination_check": hallucination,
            "answer_quality": quality
        }


def run_prompt_evaluation(test_file: str = "evaluation_tests/prompt_test_cases.json") -> Dict:
    """
    Run complete prompt-level evaluation

    Test file format:
    {
        "single_turn_tests": [
            {
                "query": "...",
                "expected_answer": "..." (optional)
            },
            ...
        ]
    }
    """
    evaluator = PromptEvaluator()

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"Test file not found: {test_file}"}

    results = []

    for test_case in test_data.get("single_turn_tests", []):
        result = evaluator.evaluate_single_turn(test_case)
        results.append(result)

    # Aggregate scores
    avg_relevance = sum(r["context_relevance"]["relevance_score"] for r in results) / len(results) if results else 0
    avg_quality = sum(r["answer_quality"]["overall_score"] for r in results) / len(results) if results else 0
    hallucination_rate = sum(1 for r in results if r["hallucination_check"].get("has_hallucination")) / len(results) if results else 0

    return {
        "num_test_cases": len(results),
        "avg_context_relevance": round(avg_relevance, 2),
        "avg_answer_quality": round(avg_quality, 2),
        "hallucination_rate": round(hallucination_rate * 100, 1),  # Percentage
        "individual_results": results
    }
