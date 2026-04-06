from kontakt_qc.pii import mask_pii


def test_mask_pii():
    text = "Kart 1234123412341234, nömrə 0501234567"
    masked = mask_pii(text)
    assert "1234123412341234" not in masked
    assert "0501234567" not in masked
    assert "[MASKED_CARD]" in masked
    assert "[MASKED_PHONE]" in masked
