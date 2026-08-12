from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / 'questions.json'
SOURCE_BANK = 'metal_heat_treatment_2000_reviewed_2026'


def norm(s: str) -> str:
    return re.sub(r'\s+', '', str(s or '')).lower()


def full_sig(q: dict) -> tuple:
    return (
        q.get('type'), norm(q.get('question')),
        tuple(norm(x) for x in q.get('options', []) or []), norm(q.get('answer'))
    )


def main() -> int:
    all_q = json.loads(QUESTIONS.read_text(encoding='utf-8'))
    imported = [q for q in all_q if q.get('source_bank') == SOURCE_BANK]
    errors = []

    if not imported:
        errors.append('没有发现已导入的2000题审校题库')

    ids = [q.get('id') for q in all_q]
    if len(ids) != len(set(ids)):
        errors.append('全题库存在重复ID')

    sigs = set()
    duplicate_ids = []
    for q in all_q:
        sig = full_sig(q)
        if sig in sigs:
            duplicate_ids.append(q.get('id'))
        sigs.add(sig)
    if duplicate_ids:
        errors.append(f'全题库存在完整重复题: {duplicate_ids[:20]}')

    for q in imported:
        qid = q.get('id')
        for required in ('question', 'answer', 'explanation', 'source_index', 'source_level', 'review_status'):
            if q.get(required) in (None, ''):
                errors.append(f'ID {qid}: 缺少 {required}')
        if q.get('type') == 'choice':
            options = q.get('options') or []
            labels = q.get('option_labels') or []
            answer = str(q.get('answer') or '')
            if len(options) < 2 or len(options) != len(labels):
                errors.append(f'ID {qid}: 选择题选项结构异常')
            if not answer or any(ch not in labels for ch in answer if ch.isalpha()):
                errors.append(f'ID {qid}: 选择题答案无法匹配选项')
        if q.get('source_level') == '强化练习' and q.get('source_index') != 2000:
            exp = str(q.get('explanation') or '')
            if '正确' not in exp or '错误' not in exp:
                errors.append(f'ID {qid}: 强化辨析题未包含逐项真假解析')
        if q.get('type') == 'shortanswer' and not str(q.get('explanation') or '').startswith('参考答案要点：'):
            errors.append(f'ID {qid}: 简答题未按参考答案要点格式整理')
        if q.get('source_index') == 2000:
            d = (q.get('options') or ['','','',''])[-1]
            if '题库完成说明' in d or '本文件共' in d:
                errors.append('最后一道强化题仍包含Markdown尾注')

    counts = Counter(q.get('type') for q in imported)
    levels = Counter(q.get('source_level') for q in imported)
    statuses = Counter(q.get('review_status') for q in imported)
    print('[INFO] total:', len(all_q))
    print('[INFO] imported:', len(imported))
    print('[INFO] imported types:', dict(counts))
    print('[INFO] imported levels:', dict(levels))
    print('[INFO] review status:', dict(statuses))
    if errors:
        for e in errors[:100]: print('[ERROR]', e)
        print(f'[FAIL] {len(errors)} errors')
        return 1
    print('[OK] reviewed 2000-bank integration validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
