from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARSED = ROOT / 'audit' / 'parsed_2000.json'
EXISTING = ROOT / 'questions.json'
OUT = ROOT / 'audit' / 'review_batches'


def norm(s: str) -> str:
    s = str(s or '').lower().replace('fe₃c', 'fe3c')
    s = re.sub(r'[\s\\>*`]+', '', s)
    s = re.sub(r'[，。；：、,.!?！？;:\"\'“”‘’（）()\[\]【】<>《》—－-]', '', s)
    return s


def grams(s: str, n: int = 3) -> set[str]:
    s = norm(s)
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i+n] for i in range(len(s)-n+1)}


def canonical(q: dict) -> str:
    text = q.get('question', '')
    if q.get('type') == 'choice':
        labels = q.get('option_labels') or []
        options = q.get('options') or []
        answer = str(q.get('answer') or '')
        ans_text = []
        for label, option in zip(labels, options):
            if label in answer:
                ans_text.append(option)
        if ans_text:
            text += ' ' + ' '.join(ans_text)
    return text


def similarity(a: dict, b: dict) -> float:
    ca, cb = canonical(a), canonical(b)
    na, nb = norm(ca), norm(cb)
    if not na or not nb:
        return 0.0
    ga, gb = grams(ca), grams(cb)
    dice = (2 * len(ga & gb) / (len(ga) + len(gb))) if ga and gb else 0.0
    seq = SequenceMatcher(None, na, nb, autojunk=False).ratio()
    type_bonus = 0.04 if a.get('type') == b.get('type') else 0.0
    return min(1.0, 0.58 * dice + 0.38 * seq + type_bonus)


def best_match(q: dict, existing: list[dict]) -> tuple[float, dict | None]:
    best_score = 0.0
    best = None
    qchars = set(norm(canonical(q)))
    for e in existing:
        echars = set(norm(canonical(e)))
        if not qchars or not echars:
            continue
        # Cheap prefilter: enough shared characters to be worth a full comparison.
        overlap = len(qchars & echars) / max(1, min(len(qchars), len(echars)))
        if overlap < 0.38:
            continue
        score = similarity(q, e)
        if score > best_score:
            best_score, best = score, e
    return best_score, best


def write_batches(name: str, items: list[dict], size: int = 40) -> None:
    for i in range(0, len(items), size):
        batch = items[i:i+size]
        num = i // size + 1
        lines = [f'# {name} · 批次 {num}', '', f'本批 {len(batch)} 题。审校时需要给出：结论（通过/修正/暂缓）、正确答案、学习型解析、知识点、依据类型。', '']
        for q in batch:
            lines.append(f"## S{q['source_index']} · {q.get('level','')} · {q.get('section','')} · 原题号 {q.get('source_no','')}")
            lines.append('')
            lines.append(q.get('question',''))
            lines.append('')
            if q.get('options'):
                for lab, opt in zip(q.get('option_labels') or [], q.get('options') or []):
                    lines.append(f'- {lab}. {opt}')
                lines.append('')
            lines.append(f"**原答案：{q.get('answer','')}**")
            if q.get('answer_raw') and q.get('type') == 'shortanswer':
                lines.append('')
                lines.append(f"**原参考答案：** {q.get('answer_raw')}")
            m = q.get('existing_match')
            if m:
                lines.append('')
                lines.append(f"**现有715题最相近：** ID {m['id']} · 相似度 {m['score']:.3f}")
                lines.append(f"- 题目：{m['question']}")
                if m.get('explanation'):
                    lines.append(f"- 已有解析：{m['explanation']}")
            lines.append('')
        (OUT / f'{name}_{num:02d}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.md'):
        old.unlink()
    parsed = json.loads(PARSED.read_text(encoding='utf-8'))
    existing = json.loads(EXISTING.read_text(encoding='utf-8'))

    # Only the original 1037 need full knowledge review. The fifth part is generated composite practice.
    original = [q for q in parsed if not str(q.get('level','')).startswith('第五部分')]
    composites = [q for q in parsed if str(q.get('level','')).startswith('第五部分')]

    high = medium = 0
    for q in original:
        score, match = best_match(q, existing)
        if match and score >= 0.54:
            q['existing_match'] = {
                'id': match.get('id'),
                'score': round(score, 4),
                'question': match.get('question'),
                'answer': match.get('answer'),
                'explanation': match.get('explanation'),
                'knowledge_point': match.get('knowledge_point'),
            }
            if score >= 0.78:
                high += 1
            else:
                medium += 1

    judgments = [q for q in original if q.get('type') == 'truefalse']
    choices = [q for q in original if q.get('type') == 'choice']
    shorts = [q for q in original if q.get('type') == 'shortanswer']
    unresolved_composites = [q for q in composites if q.get('audit_status') != 'auto_verified_composite']

    write_batches('judgment', judgments)
    write_batches('choice', choices)
    write_batches('shortanswer', shorts, 25)
    write_batches('composite_unresolved', unresolved_composites, 25)

    summary = {
        'original_count': len(original),
        'judgment': len(judgments),
        'choice': len(choices),
        'shortanswer': len(shorts),
        'composite_count': len(composites),
        'composite_auto_verified': len(composites) - len(unresolved_composites),
        'composite_unresolved': len(unresolved_composites),
        'existing_high_similarity': high,
        'existing_medium_similarity': medium,
        'batch_counts': {
            'judgment': math.ceil(len(judgments)/40),
            'choice': math.ceil(len(choices)/40),
            'shortanswer': math.ceil(len(shorts)/25),
            'composite_unresolved': math.ceil(len(unresolved_composites)/25) if unresolved_composites else 0,
        },
    }
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
