from collections import Counter
from dataclasses import asdict
from typing import Iterable

from .schemas import CriterionResult

CRITERIA = ["KR2.1", "KR2.2", "KR2.3", "KR2.4", "KR2.5"]


def _join_text(segments: list[dict]) -> str:
    return " ".join(str(s.get("text", "")) for s in segments)


def _op_segments(segments: list[dict]) -> list[dict]:
    return [s for s in segments if str(s.get("speaker", "")).lower() == "operator"]


def _evidence(segments: list[dict], keywords: Iterable[str]) -> str:
    kws = [k.lower() for k in keywords]
    found = []
    for s in segments:
        txt = str(s.get("text", ""))
        if any(k in txt.lower() for k in kws):
            found.append(f"[{s.get('start')}-{s.get('end')}] {s.get('speaker')}: {txt}")
        if len(found) == 2:
            break
    return " ".join(found) if found else "Aydın dəlil tapılmadı."


def _probability(conf: float) -> str:
    if conf >= 0.8:
        return "HIGH"
    if conf >= 0.5:
        return "MEDIUM"
    return "LOW"


def _safe_score(x: int) -> int:
    return max(0, min(3, int(x)))


def _kr21(segments: list[dict]) -> CriterionResult:
    ops = _op_segments(segments)
    text = _join_text(ops).lower()
    cues = ["kömək", "həll", "baxaq", "yoxlayaq", "təklif", "dəstək", "kömək edə bilərəm"]
    proactive = sum(1 for c in cues if c in text)
    q_count = sum(1 for s in ops if "?" in str(s.get("text", "")))
    score = 1 + (1 if proactive >= 1 else 0) + (1 if proactive >= 2 and q_count >= 1 else 0)
    reasoning = "Operator aktiv dəstək və operativ yanaşma göstərir." if score >= 3 else "Operator qismən kömək göstərir, amma aktivlik tam deyil."
    return CriterionResult(_safe_score(score), reasoning, _probability(min(1.0, proactive / 3)), _evidence(segments, cues))


def _kr22(segments: list[dict]) -> CriterionResult:
    ops = _op_segments(segments)
    op_texts = [str(s.get("text", "")).lower() for s in ops]
    repeats = 0
    if op_texts:
        counts = Counter(op_texts)
        repeats = sum(v - 1 for v in counts.values() if v > 1)
    bad = any(w in " ".join(op_texts) for w in ["təkrar", "yenidən deyin", "başa düşmədim"])
    score = 3
    if repeats >= 2 or bad:
        score = 1
    elif repeats == 1:
        score = 2
    reasoning = "Müştərinin tələbatı düzgün formalaşdırılıb, artıq təkrar yoxdur." if score == 3 else "Tələbatın formalaşdırılmasında təkrar və ya axıcılıq problemi var."
    return CriterionResult(score, reasoning, _probability(0.85 if score == 3 else 0.55), _evidence(segments, ["təkrar", "dəqiqləşdir", "buyurun", "kömək"]))


def _kr23(segments: list[dict]) -> CriterionResult:
    ops_text = _join_text(_op_segments(segments)).lower()
    detail_markers = ["manat", "mbps", "kanal", "%", "saat", "gün", "24", "qiymət", "tarif"]
    detail_count = sum(1 for d in detail_markers if d in ops_text)
    uncertain = any(u in ops_text for u in ["bilmirəm", "dəqiq deyil", "əmin deyiləm"])
    score = 1
    if detail_count >= 2 and not uncertain:
        score = 3
    elif detail_count >= 1:
        score = 2
    reasoning = "Məlumat dolğun və dəqiq təqdim olunur." if score >= 3 else "Məlumat qismən təqdim olunub və ya detallıq zəifdir."
    return CriterionResult(score, reasoning, _probability(min(1.0, 0.4 + detail_count * 0.2)), _evidence(_op_segments(segments), detail_markers))


def _kr24(segments: list[dict]) -> CriterionResult:
    ops_text = _join_text(_op_segments(segments)).lower()
    reg_cues = ["qeyd", "sifariş", "müraciət", "ünvan", "əlaqə", "yönləndir", "texnik"]
    hit = sum(1 for c in reg_cues if c in ops_text)
    score = 1 if hit == 0 else (2 if hit <= 2 else 3)
    reasoning = "Müraciət düzgün yönləndirilib və qeydiyyat tamamlanıb." if score == 3 else "Yönləndirmə/qeydiyyat qismən edilib."
    return CriterionResult(score, reasoning, _probability(min(1.0, hit / 4)), _evidence(_op_segments(segments), reg_cues))


def _kr25(segments: list[dict]) -> CriterionResult:
    ops_text = _join_text(_op_segments(segments)).lower()
    polite = ["salam", "buyurun", "təşəkkür", "xahiş edirəm", "yaxşı gün"]
    bad = ["mikro donub", "internet zəifdir", "şəxsən mən", "məncə", "boş verin", "gözlə"]
    bad_hit = any(b in ops_text for b in bad)
    polite_hit = sum(1 for p in polite if p in ops_text)
    score = 3 if (polite_hit >= 2 and not bad_hit) else (2 if not bad_hit else 0)
    reasoning = "Peşəkar ünsiyyət və etiket qaydaları qorunub." if score >= 2 else "Peşəkarlıq qaydalarını pozan ifadələr var."
    conf = 0.9 if score == 3 else (0.6 if score == 2 else 0.95)
    return CriterionResult(score, reasoning, _probability(conf), _evidence(_op_segments(segments), polite + bad))


def evaluate_rules(segments: list[dict]) -> dict[str, dict]:
    return {
        "KR2.1": asdict(_kr21(segments)),
        "KR2.2": asdict(_kr22(segments)),
        "KR2.3": asdict(_kr23(segments)),
        "KR2.4": asdict(_kr24(segments)),
        "KR2.5": asdict(_kr25(segments)),
    }
