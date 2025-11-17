from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.evaluation.rag_eval import run_rag_evaluation
from app.evaluation.prompt_eval import run_prompt_evaluation
from app.evaluation.app_eval import run_application_evaluation
from app.evaluation.mock_results import (
    get_mock_rag_results,
    get_mock_prompt_results,
    get_mock_application_results
)

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

# Set to True to use mock results (no API calls)
USE_MOCK = False  # Using real API now


@router.post("/rag")
async def run_rag_eval(test_file: Optional[str] = "evaluation_tests/rag_test_cases.json", mock: bool = USE_MOCK):
    """Run RAG-level evaluation (retrieval quality, precision, recall, MRR)"""
    try:
        if mock:
            return get_mock_rag_results()
        results = run_rag_evaluation(test_file)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompt")
async def run_prompt_eval(test_file: Optional[str] = "evaluation_tests/prompt_test_cases.json", mock: bool = USE_MOCK):
    """Run Prompt-level evaluation (context relevance, hallucination, LLM-as-Judge)"""
    try:
        if mock:
            return get_mock_prompt_results()
        results = run_prompt_evaluation(test_file)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/application")
async def run_app_eval(test_file: Optional[str] = "evaluation_tests/app_test_cases.json", mock: bool = USE_MOCK):
    """Run Application-level evaluation (user journey, response quality, satisfaction)"""
    try:
        if mock:
            return get_mock_application_results()
        results = run_application_evaluation(test_file)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full")
async def run_full_eval():
    """Run complete 3-level evaluation framework"""
    try:
        results = {
            "rag_evaluation": run_rag_evaluation(),
            "prompt_evaluation": run_prompt_evaluation(),
            "application_evaluation": run_application_evaluation()
        }
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_evaluation_summary():
    """Get summary of all evaluation results"""
    return {
        "evaluation_framework": {
            "rag_level": {
                "description": "Retrieval quality: precision, recall, MRR",
                "min_test_cases": 20,
                "endpoint": "/api/evaluation/rag"
            },
            "prompt_level": {
                "description": "Context relevance, hallucination detection, LLM-as-Judge",
                "min_test_cases": 15,
                "endpoint": "/api/evaluation/prompt"
            },
            "application_level": {
                "description": "User journey, response quality, latency, satisfaction",
                "min_test_cases": 10,
                "endpoint": "/api/evaluation/application"
            }
        },
        "total_min_test_cases": 45
    }
