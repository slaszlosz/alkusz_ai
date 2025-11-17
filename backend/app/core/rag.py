from typing import List, Dict, Optional, Iterator
from openai import OpenAI
from app.services.vector_store import VectorStore
from app.core.config import get_settings
from app.core.metrics import metrics_tracker
import time
import tiktoken


class RAGPipeline:
    """Retrieval Augmented Generation pipeline"""

    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.vector_store = VectorStore()
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        self.system_prompt = """Te egy vállalati tudásbázis asszisztens vagy, aki magyar nyelven válaszol kérdésekre.

A feladatod, hogy a rendelkezésedre bocsátott dokumentumok alapján pontos és részletes válaszokat adj.

Fontos szabályok:
- Csak a megadott kontextus alapján válaszolj
- Ha nem találsz releváns információt a dokumentumokban, jelezd ezt
- Mindig hivatkozz a forrásokra
- Válaszolj magyarul, világosan és érthetően
- Ha számokat vagy konkrét adatokat mondasz, légy precíz
"""

    def generate_response(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        category: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Generate response using RAG pipeline with metrics tracking
        Returns: {answer, sources, metrics}
        """
        start_time = time.time()

        # 1. Retrieve relevant chunks
        retrieval_start = time.time()
        results = self.vector_store.search(
            query=query,
            n_results=5,
            category=category
        )
        retrieval_latency = time.time() - retrieval_start

        # 2. Build context from retrieved chunks
        context = self._build_context(results)

        # 3. Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges

        # Add current query with context
        user_message = f"""Kontextus a dokumentumokból:
{context}

Kérdés: {query}

Válaszolj a kérdésre a fenti kontextus alapján. Ha hivatkozol információkra, jelezd melyik dokumentumból származnak."""

        messages.append({"role": "user", "content": user_message})

        # Count input tokens
        input_tokens = sum(len(self.tokenizer.encode(msg["content"])) for msg in messages)

        # 4. Generate response
        model = "gpt-4o-mini"
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )

        answer = response.choices[0].message.content
        output_tokens = response.usage.completion_tokens if response.usage else len(self.tokenizer.encode(answer))

        total_latency = time.time() - start_time

        # 5. Format sources
        sources = self._format_sources(results)

        # 6. Log metrics
        metrics_tracker.log_query(
            query=query,
            response=answer,
            sources=sources,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_latency=total_latency,
            retrieval_latency=retrieval_latency,
            conversation_id=conversation_id
        )

        return {
            "answer": answer,
            "sources": sources,
            "metrics": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_latency_ms": round(total_latency * 1000, 1),
                "retrieval_latency_ms": round(retrieval_latency * 1000, 1)
            }
        }

    def generate_response_stream(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        category: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Iterator[str]:
        """
        Generate streaming response using RAG pipeline
        Yields chunks of the response
        """
        start_time = time.time()
        first_token_time = None

        # 1. Retrieve relevant chunks
        retrieval_start = time.time()
        results = self.vector_store.search(
            query=query,
            n_results=5,
            category=category
        )
        retrieval_latency = time.time() - retrieval_start

        # 2. Build context
        context = self._build_context(results)

        # 3. Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        if conversation_history:
            messages.extend(conversation_history[-6:])

        user_message = f"""Kontextus a dokumentumokból:
{context}

Kérdés: {query}

Válaszolj a kérdésre a fenti kontextus alapján. Ha hivatkozol információkra, jelezd melyik dokumentumból származnak."""

        messages.append({"role": "user", "content": user_message})

        input_tokens = sum(len(self.tokenizer.encode(msg["content"])) for msg in messages)

        # 4. Stream response
        model = "gpt-4o-mini"
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            stream=True
        )

        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.time()

                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        # 5. Calculate metrics
        total_latency = time.time() - start_time
        first_token_latency = first_token_time - start_time if first_token_time else None
        output_tokens = len(self.tokenizer.encode(full_response))

        sources = self._format_sources(results)

        # 6. Log metrics
        metrics_tracker.log_query(
            query=query,
            response=full_response,
            sources=sources,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_latency=total_latency,
            first_token_latency=first_token_latency,
            retrieval_latency=retrieval_latency,
            conversation_id=conversation_id
        )

    def _build_context(self, results: List[Dict]) -> str:
        """Build context string from search results"""
        if not results:
            return "Nem található releváns információ a dokumentumokban."

        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            text = result['text']
            context_parts.append(
                f"[{i}] Forrás: {metadata['filename']}, {metadata['page']}. oldal\n{text}\n"
            )

        return "\n".join(context_parts)

    def _format_sources(self, results: List[Dict]) -> List[Dict]:
        """Format sources for frontend display"""
        sources = []
        seen = set()

        for result in results:
            metadata = result['metadata']
            # Unique key: filename + page
            key = f"{metadata['doc_id']}_{metadata['page']}"

            if key not in seen:
                seen.add(key)
                sources.append({
                    "doc_id": metadata['doc_id'],
                    "filename": metadata['filename'],
                    "page": metadata['page'],
                    "chunk_text": result['text'][:200] + "...",  # Preview
                    "relevance_score": round(result['score'], 3)
                })

        return sources
