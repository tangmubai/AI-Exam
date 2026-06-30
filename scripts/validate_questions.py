"""Sanity checks for the generated offline question bank."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "questions.js"
RUNNING_HEADER_RE = re.compile(
    r"(人工智能与循环神经网络|大模型介绍|强化学习题库)\s+\d{1,3}"
)
BROKEN_FORMULA_RE = re.compile(r"[\ufffc\ufffd\uffff]|\bT\s+(?:ransformer|oken|arget|ask)|BAR\s+T")


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8").strip()
    prefix = "window.QUESTION_BANK = "
    if not raw.startswith(prefix) or not raw.endswith(";"):
        raise SystemExit("questions.js has an unexpected wrapper")
    bank = json.loads(raw[len(prefix) : -1])
    questions = bank["questions"]
    errors: list[str] = []
    seen: set[str] = set()

    for index, question in enumerate(questions):
        label = f"#{index + 1} {question['id']}"
        if question["id"] in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(question["id"])
        for field in ("document", "prompt", "answer", "type"):
            if not str(question.get(field, "")).strip():
                errors.append(f"{label}: empty {field}")
        combined_text = "\n".join(
            [
                str(question.get("prompt", "")),
                str(question.get("answer", "")),
                str(question.get("explanation", "")),
                "\n".join(str(option.get("text", "")) for option in question.get("options", [])),
            ]
        )
        if RUNNING_HEADER_RE.search(combined_text):
            errors.append(f"{label}: likely running header leaked into question text")
        if BROKEN_FORMULA_RE.search(combined_text):
            errors.append(f"{label}: likely broken formula/text extraction artifact")
        if question["page"] < 1:
            errors.append(f"{label}: invalid page")
        if question["type"] == "选择题":
            keys = [option["key"] for option in question["options"]]
            if len(keys) < 2:
                errors.append(f"{label}: choice question has {len(keys)} options")
            answer_keys = re.findall(r"[A-H]", question["answer"].upper())
            if not answer_keys or any(key not in keys for key in answer_keys):
                errors.append(
                    f"{label}: answer {question['answer']!r} does not match options {keys}"
                )
        if re.search(r"(?:答案|解析|解答)\s*[：:]", question["prompt"]):
            errors.append(f"{label}: prompt contains an answer marker")

    print(f"Documents: {len(bank['documents'])}")
    print(f"Questions: {len(questions)}")
    print(f"Unique IDs: {len(seen)}")
    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors[:50]:
            print(" -", error)
        raise SystemExit(1)
    print("Validation passed.")


if __name__ == "__main__":
    main()
