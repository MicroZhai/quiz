from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "热处理题库" / "金属热处理工考工晋级大题库_答案随题版_2000题.md"
EXISTING = ROOT / "questions.json"
OUTDIR = ROOT / "audit"


def norm(text: str) -> str:
    text = str(text or "").lower()
    text = text.replace("fe₃c", "fe3c")
    text = re.sub(r"\*+|`+", "", text)
    text = re.sub(r"[\s\\>]+", "", text)
    text = re.sub(r"[，。；：、,.!?！？;:\"'“”‘’（）()\[\]【】<>《》—－-]", "", text)
    return text


def clean_md(text: str) -> str:
    text = re.sub(r"(?m)^\s*>\s?", "", str(text or ""))
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def type_from_section(section: str, answer_raw: str, has_options: bool) -> str:
    s = section or ""
    if "判断" in s or answer_raw.strip() in {"√", "×"}:
        return "truefalse"
    if "选择" in s or has_options:
        return "choice"
    if "填空" in s:
        return "fill"
    if "计算" in s:
        return "calculation"
    if "简答" in s or "问答" in s or "案例" in s:
        return "shortanswer"
    return "shortanswer"


def parse_choice_answer(raw: str, labels: list[str]) -> str:
    raw = raw.strip().upper()
    head = re.split(r"[，,。；;：:]", raw, maxsplit=1)[0].strip()
    found = [x for x in labels if re.search(rf"(?<![A-Z]){re.escape(x)}(?![A-Z])", head)]
    if found:
        return "".join(found)
    if head in labels:
        return head
    compact = re.sub(r"[^A-Z]", "", head)
    if compact and all(ch in labels for ch in compact):
        return "".join(dict.fromkeys(compact))
    return head


def find_answer(raw: str):
    patterns = [
        r"\*\*【答案[：:](.*?)】\*\*",
        r"\*\*【参考答案[：:]?(.*?)】\*\*",
        r"\*\*【参考答案】(.*?)\*\*",
    ]
    for pat in patterns:
        m = re.search(pat, raw, re.S)
        if m:
            return m
    return None


def parse_blocks(text: str) -> list[dict]:
    lines = text.splitlines()
    level = ""
    section = ""
    blocks: list[dict] = []
    current: list[str] | None = None
    current_no: int | None = None
    current_level = ""
    current_section = ""

    def flush() -> None:
        nonlocal current, current_no
        if current is None or current_no is None:
            return
        raw = "\n".join(current).strip()
        answer_match = find_answer(raw)
        if not answer_match:
            blocks.append({
                "source_no": current_no,
                "level": current_level,
                "section": current_section,
                "raw": raw,
                "parse_error": "缺少答案标记",
            })
            current = None
            current_no = None
            return

        answer_raw = clean_md(answer_match.group(1))
        body = (raw[: answer_match.start()] + raw[answer_match.end() :]).strip()
        body = re.sub(r"^\d+\\?\.\s*", "", body).strip()
        body = re.sub(r"(?m)^\s*>\s?", "", body)

        opt_matches = list(re.finditer(r"(?<!\w)([A-H])\.\s*", body))
        options: list[str] = []
        labels: list[str] = []
        question_text = body
        if opt_matches:
            question_text = body[: opt_matches[0].start()].strip()
            for idx, m in enumerate(opt_matches):
                end = opt_matches[idx + 1].start() if idx + 1 < len(opt_matches) else len(body)
                option_text = clean_md(body[m.end() : end])
                labels.append(m.group(1))
                options.append(option_text)

        qtype = type_from_section(current_section, answer_raw, bool(options))
        answer = answer_raw
        if qtype == "choice":
            answer = parse_choice_answer(answer_raw, labels)
        elif qtype == "truefalse":
            answer = "√" if "√" in answer_raw else "×" if "×" in answer_raw else answer_raw

        blocks.append({
            "source_no": current_no,
            "level": current_level,
            "section": current_section,
            "type": qtype,
            "question": clean_md(question_text),
            "options": options,
            "option_labels": labels,
            "answer": answer,
            "answer_raw": answer_raw,
            "raw": raw,
        })
        current = None
        current_no = None

    for line in lines:
        if line.startswith("## ") and not line.startswith("### "):
            flush()
            level = line[3:].strip()
            continue
        if line.startswith("### "):
            flush()
            section = line[4:].strip()
            continue
        m = re.match(r"^(\d+)\\?\.\s+", line)
        if m:
            flush()
            current_no = int(m.group(1))
            current_level = level
            current_section = section
            current = [line]
        elif current is not None:
            current.append(line)

    flush()
    return blocks


def detect_intent(question: str) -> str | None:
    q = norm(question)
    negative = ["错误的是", "错误的一项", "不正确的是", "不正确的一项", "表述不正确", "说法错误"]
    positive = ["正确的是", "正确的一项", "表述正确", "说法正确"]
    if any(norm(x) in q for x in negative):
        return "false"
    if any(norm(x) in q for x in positive):
        return "true"
    return None


def main() -> int:
    OUTDIR.mkdir(exist_ok=True)
    source_questions = parse_blocks(SOURCE.read_text(encoding="utf-8"))
    existing = json.loads(EXISTING.read_text(encoding="utf-8"))

    existing_by_norm: dict[str, list[dict]] = defaultdict(list)
    for q in existing:
        existing_by_norm[norm(q.get("question", ""))].append(q)

    truth: dict[str, set[bool]] = defaultdict(set)
    truth_examples: dict[str, str] = {}
    for q in source_questions:
        if q.get("type") == "truefalse" and q.get("question") and q.get("answer") in {"√", "×"}:
            k = norm(q["question"])
            truth[k].add(q["answer"] == "√")
            truth_examples[k] = q["question"]
    for q in existing:
        if q.get("type") == "truefalse" and q.get("answer") in {"√", "×"}:
            k = norm(q.get("question", ""))
            truth[k].add(q["answer"] == "√")
            truth_examples[k] = q.get("question", "")

    conflicting_truth = {k: vals for k, vals in truth.items() if len(vals) > 1}
    stats = Counter()
    issues: list[dict] = []
    parsed: list[dict] = []

    for idx, q in enumerate(source_questions, 1):
        stats["parsed"] += 1
        if q.get("parse_error"):
            stats["parse_error"] += 1
            issues.append({"kind": "parse_error", "index": idx, **q})
            parsed.append(q)
            continue

        stats[f"type:{q['type']}"] += 1
        qn = norm(q.get("question", ""))
        duplicate_ids = [x.get("id") for x in existing_by_norm.get(qn, [])]
        if duplicate_ids:
            stats["exact_duplicate_existing"] += 1

        status = "needs_review"
        flags: list[str] = []
        auto = None

        if not q.get("question"):
            flags.append("空题干")
        if q["type"] == "choice":
            labels = q.get("option_labels") or []
            options = q.get("options") or []
            if len(options) < 2:
                flags.append("选择题选项少于2个")
            if q.get("answer") and any(ch not in labels for ch in q["answer"] if ch.isalpha()):
                flags.append("答案字母不在选项中")
            if len({norm(x) for x in options}) != len(options):
                flags.append("存在重复选项")

            intent = detect_intent(q.get("question", ""))
            if intent and options:
                option_truth: list[bool | None] = []
                for opt in options:
                    vals = truth.get(norm(opt))
                    if vals and len(vals) == 1:
                        option_truth.append(next(iter(vals)))
                    else:
                        option_truth.append(None)
                known = sum(v is not None for v in option_truth)
                wanted = intent == "true"
                matches = [labels[i] for i, v in enumerate(option_truth) if v is wanted]
                if known == len(options):
                    if len(matches) == 1:
                        inferred = matches[0]
                        auto = {"intent": intent, "option_truth": option_truth, "inferred_answer": inferred, "source_answer": q.get("answer")}
                        if q.get("answer") == inferred:
                            status = "auto_verified_composite"
                            stats["auto_verified_composite"] += 1
                        else:
                            flags.append(f"组合题答案冲突: 推断{inferred}/原答案{q.get('answer')}")
                            stats["composite_answer_conflict"] += 1
                    else:
                        flags.append(f"组合题非唯一答案: 符合项={matches}")
                        stats["composite_non_unique"] += 1
                elif known:
                    auto = {"intent": intent, "option_truth": option_truth, "known_options": known}
                    stats["composite_partial_known"] += 1

        if q["type"] == "truefalse":
            vals = truth.get(qn)
            if vals and len(vals) == 1 and ((q.get("answer") == "√") == next(iter(vals))):
                status = "internally_consistent"
            if qn in conflicting_truth:
                flags.append("同一判断命题存在相反答案")

        if duplicate_ids:
            status = "duplicate_existing"
        if flags:
            status = "problem"
            for flag in flags:
                issues.append({"kind": "question_problem", "index": idx, "source_no": q.get("source_no"), "level": q.get("level"), "section": q.get("section"), "question": q.get("question"), "flag": flag})

        parsed.append({
            "source_index": idx,
            "source_no": q.get("source_no"),
            "level": q.get("level"),
            "section": q.get("section"),
            "type": q.get("type"),
            "question": q.get("question"),
            "options": q.get("options", []),
            "option_labels": q.get("option_labels", []),
            "answer": q.get("answer"),
            "answer_raw": q.get("answer_raw"),
            "duplicate_existing_ids": duplicate_ids,
            "audit_status": status,
            "flags": flags,
            "auto_check": auto,
            "source": "金属热处理工考工晋级大题库_答案随题版_2000题",
        })
        stats[f"status:{status}"] += 1

    internal_groups: dict[str, list[int]] = defaultdict(list)
    for q in parsed:
        if q.get("question"):
            internal_groups[norm(q["question"])].append(q.get("source_index"))
    internal_dups = {k: v for k, v in internal_groups.items() if len(v) > 1}
    stats["internal_duplicate_groups"] = len(internal_dups)
    stats["internal_duplicate_extra_questions"] = sum(len(v) - 1 for v in internal_dups.values())

    level_counts = Counter(q.get("level", "") for q in parsed)
    section_counts = Counter((q.get("level", ""), q.get("section", "")) for q in parsed)
    audit = {
        "source_file": str(SOURCE.relative_to(ROOT)),
        "existing_question_count": len(existing),
        "stats": dict(stats),
        "level_counts": dict(level_counts),
        "section_counts": [{"level": level, "section": section, "count": count} for (level, section), count in section_counts.items()],
        "conflicting_truth_count": len(conflicting_truth),
        "conflicting_truth_examples": [truth_examples[k] for k in list(conflicting_truth)[:100]],
        "internal_duplicate_groups": list(internal_dups.values())[:500],
        "issue_count": len(issues),
        "issues": issues,
    }

    (OUTDIR / "parsed_2000.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTDIR / "audit_2000.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# 2000题结构审校报告", "",
        "> 本报告只做结构、重复和内部逻辑审校；它不是最终知识正确性结论。正式入库还必须经过权威资料核对与解析补全。", "",
        "## 总览", "",
        f"- 原文件解析题数：**{stats['parsed']}**",
        f"- 现有正式题库：**{len(existing)}**",
        f"- 与现有题库文字完全重复：**{stats['exact_duplicate_existing']}**",
        f"- 2000题内部重复组：**{stats['internal_duplicate_groups']}**",
        f"- 可由既有判断命题自动验证的组合题：**{stats['auto_verified_composite']}**",
        f"- 组合题答案冲突：**{stats['composite_answer_conflict']}**",
        f"- 组合题非唯一答案：**{stats['composite_non_unique']}**",
        f"- 同一判断命题出现相反答案：**{len(conflicting_truth)}**",
        f"- 结构/逻辑问题记录：**{len(issues)}**", "",
        "## 题型", "",
    ]
    for typ in ["choice", "truefalse", "fill", "shortanswer", "calculation"]:
        md.append(f"- {typ}: {stats[f'type:{typ}']}")
    md.extend(["", "## 等级", ""])
    for level, count in level_counts.items():
        md.append(f"- {level}: {count}")
    md.extend(["", "## 下一轮规则", "", "1. duplicate_existing：优先沿用现有715题及其解析，不重复入库。", "2. auto_verified_composite：仍需抽查知识依据，但已通过唯一答案内部逻辑检查。", "3. problem：必须人工/权威资料核对，未解决前禁止进入正式刷题池。", "4. needs_review / internally_consistent：进入知识正确性与解析补全流程。", "", "## 问题样例（前100条）", ""])
    for issue in issues[:100]:
        md.append(f"- `{issue.get('level','')} / {issue.get('section','')} / #{issue.get('source_no','')}` {issue.get('flag') or issue.get('parse_error')}: {issue.get('question','')}")
    (OUTDIR / "AUDIT_2000.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(audit["stats"], ensure_ascii=False, indent=2))
    print(f"parsed={len(parsed)}, issues={len(issues)}, conflicts={len(conflicting_truth)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
