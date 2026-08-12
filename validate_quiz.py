"""Validate quiz data and static entry consistency."""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).parent
VALID_TYPES = {"choice", "truefalse", "fill", "shortanswer", "calculation"}


def load_questions() -> list[dict]:
    path = BASE / "questions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("questions.json 必须是非空数组")
    return data


def choice_labels(q: dict) -> list[str]:
    options = q.get("options") or []
    labels = q.get("option_labels") or [chr(65 + i) for i in range(len(options))]
    return [str(x).upper() for x in labels]


def validate_data(qs: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ids = set()
    for i, q in enumerate(qs, 1):
        tag = f"第 {i} 条"
        qid = q.get("id")
        if qid in ids:
            errors.append(f"{tag}: 重复 id={qid}")
        ids.add(qid)
        if qid is None:
            errors.append(f"{tag}: 缺少 id")
        if not str(q.get("question", "")).strip():
            errors.append(f"{tag}: 题干为空")
        typ = q.get("type")
        if typ not in VALID_TYPES:
            errors.append(f"{tag}: 未支持题型 {typ!r}")
            continue
        if not q.get("topic"):
            warnings.append(f"{tag}: 缺少 topic")
        if not q.get("knowledge_point"):
            warnings.append(f"{tag}: 缺少 knowledge_point")

        if typ == "choice":
            options = q.get("options") or []
            if len(options) < 2:
                errors.append(f"{tag}: 选择题选项少于 2 个")
            labels = choice_labels(q)
            if len(labels) != len(options):
                errors.append(f"{tag}: option_labels 与 options 数量不一致")
            raw_answer = str(q.get("answer", "")).upper()
            picked = [label for label in labels if label in raw_answer]
            if not picked:
                errors.append(f"{tag}: 选择题答案未匹配任何选项")
        elif typ == "truefalse":
            if str(q.get("answer", "")).strip() not in {"√", "×"}:
                warnings.append(f"{tag}: 判断题答案不是标准 √ / ×")
        else:
            if not str(q.get("answer", "")).strip() and not str(q.get("explanation", "")).strip():
                errors.append(f"{tag}: {typ} 同时缺少 answer 与 explanation")
    return errors, warnings


def validate_entries() -> list[str]:
    errors: list[str] = []
    quiz = BASE / "quiz.html"
    index = BASE / "index.html"
    if not quiz.exists() or not index.exists():
        return ["缺少 quiz.html 或 index.html"]
    index_html = index.read_text(encoding="utf-8")
    if "quiz.html" not in index_html:
        errors.append("index.html 未指向 quiz.html")
    html = quiz.read_text(encoding="utf-8")
    for required in ["data-nav=\"home\"", "data-nav=\"practice\"", "data-nav=\"mistakes\"", "data-nav=\"profile\"", "questions.js"]:
        if required not in html:
            errors.append(f"quiz.html 缺少关键入口: {required}")
    if re.search(r"[🔥🧪📖📜📐📝🎲🚀]", html):
        errors.append("quiz.html 仍包含旧版核心 Emoji 图标")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-only", action="store_true")
    args = ap.parse_args()
    try:
        qs = load_questions()
    except Exception as exc:
        print(f"[ERROR] 无法读取题库: {exc}")
        return 1
    errors, warnings = validate_data(qs)
    if not args.data_only:
        errors.extend(validate_entries())
    counts = Counter(q.get("type") for q in qs)
    print(f"[INFO] 题目总数: {len(qs)}")
    print("[INFO] 题型: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for msg in warnings[:20]:
        print(f"[WARN] {msg}")
    if len(warnings) > 20:
        print(f"[WARN] 另有 {len(warnings)-20} 条警告未展开")
    for msg in errors:
        print(f"[ERROR] {msg}")
    if errors:
        print(f"[FAIL] {len(errors)} 个错误，{len(warnings)} 个警告")
        return 1
    print(f"[OK] 校验通过，{len(warnings)} 个警告")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
