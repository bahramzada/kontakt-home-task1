import re


# Transkript LLM-ə getməzdən əvvəl PII maskalanır.
def mask_pii(text: str) -> str:
    masked = re.sub(r"\b\d{16}\b", "[MASKED_CARD]", text)
    masked = re.sub(r"\b(?:AZE|AA)\w{6,}\b", "[MASKED_FIN]", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b0\d{9}\b", "[MASKED_PHONE]", masked)
    return masked
