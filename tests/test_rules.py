from kontakt_qc.engine import evaluate_call


def test_good_call_scores_high():
    payload = {
        "call_id": "good1",
        "segments": [
            {"speaker": "Operator", "text": "Salam, buyurun, necə kömək edə bilərəm?", "start": 0.0, "end": 2.0},
            {"speaker": "Customer", "text": "İnternet paket qiymətini soruşuram.", "start": 2.2, "end": 3.5},
            {
                "speaker": "Operator",
                "text": "Əlbəttə, 100 mbps paket aylıq 35 manatdır. Sifariş üçün ünvan və əlaqə nömrənizi qeyd edim?",
                "start": 3.7,
                "end": 8.5,
            },
            {"speaker": "Customer", "text": "Bəli, qeyd edin.", "start": 8.7, "end": 9.2},
            {"speaker": "Operator", "text": "Təşəkkür edirəm, sifariş qeydə alındı. Yaxşı gün!", "start": 9.4, "end": 12.0},
        ],
    }
    result = evaluate_call(payload, force_no_llm=True)
    c = result["criteria"]
    assert c["KR2.1"]["score"] >= 2
    assert c["KR2.3"]["score"] >= 2
    assert c["KR2.4"]["score"] >= 2
    assert c["KR2.5"]["score"] >= 2
