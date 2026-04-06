import argparse
import json
import logging
from pathlib import Path

from kontakt_qc.engine import evaluate_call, pretty_json
from kontakt_qc.evaluation import evaluate_dataset


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def run_evaluate(input_file: str) -> int:
    payload = json.loads(Path(input_file).read_text(encoding="utf-8"))
    result = evaluate_call(payload)
    print(pretty_json(result))
    return 0 if result.get("status") == "ok" else 1


def run_eval_dataset(dataset_file: str) -> int:
    report = evaluate_dataset(dataset_file)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Kontakt Home zəng keyfiyyəti evaluatoru")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("evaluate", help="Tək zəng üçün qiymətləndirmə")
    p1.add_argument("--input", required=True, help="JSON input faylı")

    p2 = sub.add_parser("eval-dataset", help="Dataset üzrə qiymətləndirmə")
    p2.add_argument("--dataset", required=True, help="Eval dataset JSON faylı")

    args = parser.parse_args()
    if args.command == "evaluate":
        return run_evaluate(args.input)
    return run_eval_dataset(args.dataset)


if __name__ == "__main__":
    raise SystemExit(main())
