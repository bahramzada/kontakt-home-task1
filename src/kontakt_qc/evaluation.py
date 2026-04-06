import json
from pathlib import Path
from typing import Any

from .engine import evaluate_call
from .rules import CRITERIA


def evaluate_dataset(dataset_path: str) -> dict[str, Any]:
    data = json.loads(Path(dataset_path).read_text(encoding="utf-8"))

    exact_hits = {k: 0 for k in CRITERIA}
    abs_error = {k: 0 for k in CRITERIA}

    for item in data:
        pred = evaluate_call(item["input"], force_no_llm=True)
        criteria = pred["criteria"]
        expected = item["expected_output"]
        for k in CRITERIA:
            p = int(criteria[k]["score"])
            e = int(expected[k]["score"])
            if p == e:
                exact_hits[k] += 1
            abs_error[k] += abs(p - e)

    n = len(data)
    return {
        "count": n,
        "exact_match_rate": {k: round(exact_hits[k] / n, 4) for k in CRITERIA},
        "mae": {k: round(abs_error[k] / n, 4) for k in CRITERIA},
        "overall_exact": round(sum(exact_hits.values()) / (n * len(CRITERIA)), 4),
        "overall_mae": round(sum(abs_error.values()) / (n * len(CRITERIA)), 4),
    }
