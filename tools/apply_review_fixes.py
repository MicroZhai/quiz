from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / 'questions.json'
FIXES = ROOT / 'audit' / 'reviews' / 'question_fixes.json'
SOURCE_BANK = 'metal_heat_treatment_2000_reviewed_2026'


def main() -> None:
    questions = json.loads(QUESTIONS.read_text(encoding='utf-8'))
    fixes = {int(x['source_index']): x for x in json.loads(FIXES.read_text(encoding='utf-8'))}
    changed = 0
    for q in questions:
        if q.get('source_bank') != SOURCE_BANK:
            continue
        idx = int(q.get('source_index', -1))
        fix = fixes.get(idx)
        if fix:
            for field in ('question', 'options', 'option_labels', 'answer'):
                if field in fix:
                    q[field] = fix[field]
            if fix.get('explanation'):
                q['explanation'] = fix['explanation']
            q['review_status'] = 'fixed'
            changed += 1

        # Existing UI reveals explanation for open questions before self-rating.
        # Keep the learning rationale, but place the reviewed scoring answer first.
        if q.get('type') == 'shortanswer':
            answer = str(q.get('answer') or '').strip()
            explanation = str(q.get('explanation') or '').strip()
            if answer and not explanation.startswith('参考答案要点：'):
                q['explanation'] = f'参考答案要点：{answer}\n\n解析：{explanation}'

    QUESTIONS.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'[OK] applied reviewed fixes: {changed}; formatted short-answer references')


if __name__ == '__main__':
    main()
