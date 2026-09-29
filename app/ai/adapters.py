"""LLM Adapter Pattern for Minimax, OpenAI, and Deterministic Mock."""

import json
import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("LLMAdapters")


class BaseLLMAdapter(ABC):
    """Abstract interface for LLM coaching generation."""

    @abstractmethod
    async def generate_coaching_rationale(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> str:
        """Generate high-level coaching prose explaining the autoregulation."""
        pass

    @abstractmethod
    async def stream_coaching_tokens(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> AsyncIterator[str]:
        """Yield real-time coaching text tokens."""
        pass


class MinimaxAdapter(BaseLLMAdapter):
    """Minimax LLM adapter via OpenAI-compatible REST API."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _build_prompt(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> List[Dict[str, str]]:
        system_prompt = (
            "You are the Specialized Hypertrophy & Sports Performance Agent for IronGraph-Engine. "
            "Ground your rationale in evidence-based exercise physiology (Schoenfeld, Israetel, Beardsley). "
            "Explain clearly why exercises were substituted (e.g. lowering spinal axial stress), "
            "how load or RIR was autoregulated for recovery, and how time-density intensifiers (APS, Myo-reps) "
            "secured effective mechanical tension under time and sleep constraints. Be concise, punchy, and encouraging."
        )
        user_prompt = f"""
Lifter: {lifter_name}
Daily Drawbacks:
- Sleep: {drawbacks.get('sleep_hours')} hours
- Available Time: {drawbacks.get('available_minutes')} minutes
- Symptoms: {drawbacks.get('localized_pain_symptoms')}
- Blocked Equipment: {drawbacks.get('occupied_equipment')}

Adapted Program:
{json.dumps(adapted_exercises, indent=2)}

Effective Volume Delta: {volume_delta} sets.

Provide concise (2-3 paragraphs) scientific coaching commentary explaining this adapted session.
"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    async def generate_coaching_rationale(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> str:
        messages = self._build_prompt(lifter_name, drawbacks, adapted_exercises, volume_delta)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def stream_coaching_tokens(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> AsyncIterator[str]:
        messages = self._build_prompt(lifter_name, drawbacks, adapted_exercises, volume_delta)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "stream": True
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue


class MockLLMAdapter(BaseLLMAdapter):
    """Deterministic scientific mock adapter for testing and offline execution."""

    async def generate_coaching_rationale(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> str:
        sleep = drawbacks.get("sleep_hours", 7.0)
        time_avail = drawbacks.get("available_minutes", 60)
        symptoms = drawbacks.get("localized_pain_symptoms", [])

        prose = [
            f"Autoregulation applied for {lifter_name}."
        ]
        if sleep < 5.5:
            prose.append(
                f"Sleep was constrained ({sleep}h); heavy spinal axial loading was eliminated to manage CNS strain while loads were scaled by the recovery factor."
            )
        if symptoms:
            prose.append(
                f"Active joint symptoms ({', '.join(symptoms)}) triggered deterministic biomechanical substitution to high-SFR, stabilized alternatives."
            )
        if time_avail <= 40:
            prose.append(
                f"To compress training into {time_avail} minutes without dropping mechanical tension, Antagonist Paired Sets (APS) and rest-pause intervals were incorporated."
            )
        prose.append(
            f"Preserved {len(adapted_exercises)} core movements maintaining high-threshold motor unit stimulus and full hypertrophic stimulus."
        )
        return " ".join(prose)

    async def stream_coaching_tokens(
        self,
        lifter_name: str,
        drawbacks: Dict[str, Any],
        adapted_exercises: List[Dict[str, Any]],
        volume_delta: int
    ) -> AsyncIterator[str]:
        full_text = await self.generate_coaching_rationale(
            lifter_name, drawbacks, adapted_exercises, volume_delta
        )
        # Split into readable sentence chunks
        chunks = full_text.split(". ")
        for i, chunk in enumerate(chunks):
            suffix = ". " if i < len(chunks) - 1 else ""
            yield chunk + suffix


class LLMAdapterFactory:
    """Factory to instantiate LLM provider."""

    @staticmethod
    def get_adapter() -> BaseLLMAdapter:
        if settings.LLM_PRIMARY_PROVIDER == "minimax" and settings.MINIMAX_API_KEY:
            logger.info("Initializing MinimaxAdapter")
            return MinimaxAdapter(
                api_key=settings.MINIMAX_API_KEY,
                base_url=settings.MINIMAX_BASE_URL,
                model=settings.MINIMAX_MODEL
            )
        logger.info("Using MockLLMAdapter for deterministic testing")
        return MockLLMAdapter()
