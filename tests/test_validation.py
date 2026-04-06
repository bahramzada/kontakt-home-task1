from kontakt_qc.engine import evaluate_call


def test_empty_segments_returns_error():
    payload = {"call_id": "x", "segments": []}
    result = evaluate_call(payload, force_no_llm=True)
    assert result["status"] == "error"
    assert "segments boş ola bilməz." in result["errors"]


def test_short_audio_skips_llm():
    payload = {
        "call_id": "short1",
        "segments": [
            {"speaker": "Operator", "text": "Salam", "start": 0.0, "end": 0.05},
            {"speaker": "Customer", "text": "Salam", "start": 0.06, "end": 0.09},
        ],
    }
    result = evaluate_call(payload)
    assert result["status"] == "ok"
    assert result["meta"]["llm_used"] is False
    assert result["meta"]["reason"] == "short_audio"
