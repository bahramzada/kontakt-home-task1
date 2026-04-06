from kontakt_qc.engine import _merge


def test_merge_ignores_hallucinated_llm_evidence():
    rule = {
        "KR2.1": {"score": 2, "reasoning": "rule", "probability": "HIGH", "evidence_snippet": "[0-1] Operator: Salam"},
        "KR2.2": {"score": 2, "reasoning": "rule", "probability": "HIGH", "evidence_snippet": "[0-1] Operator: Salam"},
        "KR2.3": {"score": 2, "reasoning": "rule", "probability": "HIGH", "evidence_snippet": "[0-1] Operator: Salam"},
        "KR2.4": {"score": 2, "reasoning": "rule", "probability": "HIGH", "evidence_snippet": "[0-1] Operator: Salam"},
        "KR2.5": {"score": 2, "reasoning": "rule", "probability": "HIGH", "evidence_snippet": "[0-1] Operator: Salam"},
    }
    llm = {
        "KR2.1": {"score": 3, "reasoning": "50% endirim təklif etdi", "evidence_snippet": "[99-100] Operator: Sizə 50% endirim veririk"}
    }
    merged = _merge(rule, llm, "[0-1] Operator: Salam")
    assert merged["KR2.1"]["score"] == 2
