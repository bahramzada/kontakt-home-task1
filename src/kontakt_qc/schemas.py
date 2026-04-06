from dataclasses import dataclass
from typing import Any


@dataclass
class Segment:
    speaker: str
    text: str
    start: float
    end: float


@dataclass
class CriterionResult:
    score: int
    reasoning: str
    probability: str
    evidence_snippet: str


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Payload obyekt olmalıdır."]

    if not payload.get("call_id"):
        errors.append("call_id boş ola bilməz.")

    segments = payload.get("segments")
    if not isinstance(segments, list):
        errors.append("segments massiv olmalıdır.")
        return errors

    if len(segments) == 0:
        errors.append("segments boş ola bilməz.")
        return errors

    for idx, seg in enumerate(segments):
        if not isinstance(seg, dict):
            errors.append(f"segments[{idx}] obyekt deyil.")
            continue

        for key in ("speaker", "text", "start", "end"):
            if key not in seg:
                errors.append(f"segments[{idx}] daxilində '{key}' yoxdur.")

        if "text" in seg and (seg.get("text") is None or str(seg.get("text")).strip() == ""):
            errors.append(f"segments[{idx}] text boşdur.")

        if "start" in seg and "end" in seg:
            try:
                start = float(seg["start"])
                end = float(seg["end"])
                if end < start:
                    errors.append(f"segments[{idx}] üçün end < start ola bilməz.")
            except (TypeError, ValueError):
                errors.append(f"segments[{idx}] start/end ədəd olmalıdır.")
    return errors
