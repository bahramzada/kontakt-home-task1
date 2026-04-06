import json
import logging
from typing import Any

from .config import load_settings
from .llm_client import LLMClient
from .pii import mask_pii
from .rules import CRITERIA, evaluate_rules
from .schemas import validate_payload

logger = logging.getLogger(__name__)


def _build_transcript(segments: list[dict], mask_sensitive: bool = False) -> str:
    lines = []
    for seg in segments:
        text = str(seg.get("text", ""))
        if mask_sensitive:
            text = mask_pii(text)
        lines.append(f"[{seg.get('start')}-{seg.get('end')}] {seg.get('speaker')}: {text}")
    return "\n".join(lines)


def _text_exists_in_transcript(evidence: str, transcript: str) -> bool:
    if not evidence:
        return False
    evidence_l = evidence.lower().replace("  ", " ")
    transcript_l = transcript.lower().replace("  ", " ")
    # Hallucination müdafiəsi: LLM dəlili transkriptdə yoxdursa istifadə edilmir.
    return evidence_l[:80] in transcript_l or evidence_l in transcript_l


def _merge(rule_result: dict[str, Any], llm_result: dict[str, Any], transcript: str) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key in CRITERIA:
        rr = rule_result[key]
        raw = llm_result.get(key, {}) if isinstance(llm_result, dict) else {}
        llm_score = raw.get("score")
        llm_reason = str(raw.get("reasoning", "")).strip()
        llm_evidence = str(raw.get("evidence_snippet", "")).strip()

        use_llm = isinstance(llm_score, int) and 0 <= llm_score <= 3 and _text_exists_in_transcript(llm_evidence, transcript)
        if use_llm:
            final_score = round(0.7 * int(rr["score"]) + 0.3 * llm_score)
            merged[key] = {
                "score": max(0, min(3, final_score)),
                "reasoning": f"{rr['reasoning']} | LLM: {llm_reason}",
                "probability": rr["probability"],
                "evidence_snippet": rr["evidence_snippet"],
            }
        else:
            merged[key] = rr
    return merged


def evaluate_call(payload: dict[str, Any], force_no_llm: bool = False) -> dict[str, Any]:
    errors = validate_payload(payload)
    if errors:
        logger.warning("Validasiya xətası: %s", errors)
        return {
            "call_id": payload.get("call_id", "unknown"),
            "status": "error",
            "errors": errors,
        }

    call_id = payload["call_id"]
    segments = payload["segments"]
    duration = float(segments[-1]["end"]) - float(segments[0]["start"])

    rules = evaluate_rules(segments)
    transcript_raw = _build_transcript(segments, mask_sensitive=False)

    if duration < 0.1:
        logger.warning("Çox qısa audio/transkript (%s), LLM keçildi.", duration)
        return {"call_id": call_id, "status": "ok", "criteria": rules, "meta": {"llm_used": False, "reason": "short_audio"}}

    settings = load_settings()
    if force_no_llm or not settings.openrouter_api_key:
        return {"call_id": call_id, "status": "ok", "criteria": rules, "meta": {"llm_used": False, "reason": "api_key_missing_or_forced"}}

    try:
        llm_client = LLMClient(settings)
        masked_transcript = _build_transcript(segments, mask_sensitive=True)
        llm_res = llm_client.evaluate(call_id=call_id, transcript=masked_transcript)
        merged = _merge(rules, llm_res, transcript_raw)
        return {"call_id": call_id, "status": "ok", "criteria": merged, "meta": {"llm_used": True, "model": settings.openrouter_model}}
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM mərhələsində xəta baş verdi, rule-based nəticə qaytarılır: %s", exc)
        return {"call_id": call_id, "status": "ok", "criteria": rules, "meta": {"llm_used": False, "reason": "llm_error_fallback"}}


def pretty_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
