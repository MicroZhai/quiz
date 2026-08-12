from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / 'questions.json'
QJS = ROOT / 'questions.js'
SW = ROOT / 'service-worker.js'
STATUS = ROOT / 'audit' / 'FINAL_STATUS.md'
SOURCE_BANK = 'metal_heat_treatment_2000_reviewed_2026'


def norm(s: str) -> str:
    return re.sub(r'\s+', '', str(s or '')).lower()


def sig(q: dict) -> tuple:
    return (q.get('type'), norm(q.get('question')), tuple(norm(x) for x in (q.get('options') or [])), norm(q.get('answer')))


def main() -> int:
    errors: list[str] = []
    all_q = json.loads(QUESTIONS.read_text(encoding='utf-8'))
    imported = [q for q in all_q if q.get('source_bank') == SOURCE_BANK]
    source_indices = [int(q.get('source_index')) for q in imported if q.get('source_index') is not None]

    ids = [int(q['id']) for q in all_q]
    if len(ids) != len(set(ids)):
        errors.append('全题库ID不唯一')

    seen = set(); duplicate_ids = []
    for q in all_q:
        s = sig(q)
        if s in seen: duplicate_ids.append(q.get('id'))
        seen.add(s)
    if duplicate_ids:
        errors.append(f'仍存在完整重复题: {duplicate_ids[:20]}')

    if len(imported) < 1990:
        errors.append(f'审校2000题实际入库仅 {len(imported)}，低于预期')
    if len(source_indices) != len(set(source_indices)):
        errors.append('新题库source_index重复')
    missing_source = sorted(set(range(1, 2001)) - set(source_indices))

    for q in imported:
        if not str(q.get('explanation') or '').strip():
            errors.append(f"ID {q.get('id')} 无解析")
        if q.get('type') == 'shortanswer' and not str(q.get('explanation') or '').startswith('参考答案要点：'):
            errors.append(f"ID {q.get('id')} 简答题没有参考答案要点")
        if q.get('source_level') == '强化练习' and int(q.get('source_index', 0)) != 2000:
            exp = str(q.get('explanation') or '')
            if '正确' not in exp or '错误' not in exp:
                errors.append(f"ID {q.get('id')} 强化题不是逐项解析")
        if int(q.get('source_index', 0)) == 2000:
            if any('题库完成说明' in str(x) or '本文件共' in str(x) for x in q.get('options', [])):
                errors.append('S2000仍含Markdown尾注')

    qjs = QJS.read_text(encoding='utf-8')
    header = re.search(r'总题数：(\d+)', qjs)
    if not header or int(header.group(1)) != len(all_q):
        errors.append('questions.js题数与questions.json不一致')

    sw = SW.read_text(encoding='utf-8')
    if f'q{len(all_q)}-reviewed-v1' not in sw:
        errors.append('PWA缓存版本未绑定当前题数')

    counts = Counter(q.get('type') for q in imported)
    levels = Counter(q.get('source_level') for q in imported)
    statuses = Counter(q.get('review_status') for q in imported)

    lines = [
        '# 刷题学习题库最终验收', '',
        f'**状态：{"PASS" if not errors else "FAIL"}**', '',
        f'- 正式总题数：**{len(all_q)}**',
        f'- 本次审校题库入库：**{len(imported)}**',
        f'- 来源索引缺失：**{len(missing_source)}**' + (f'（{missing_source[:30]}）' if missing_source else ''),
        f'- 完整重复题：**{len(duplicate_ids)}**',
        f'- 无解析新题：**{sum(1 for q in imported if not str(q.get("explanation") or "").strip())}**', '',
        '## 新题型', '',
    ]
    for k,v in sorted(counts.items()): lines.append(f'- {k}: {v}')
    lines += ['', '## 等级', '']
    for k,v in levels.items(): lines.append(f'- {k}: {v}')
    lines += ['', '## 审校状态', '']
    for k,v in statuses.items(): lines.append(f'- {k}: {v}')
    lines += ['', '## PWA', '', f'- questions.js题数：{header.group(1) if header else "未识别"}', f'- Service Worker缓存版本匹配：{"是" if f"q{len(all_q)}-reviewed-v1" in sw else "否"}', '']
    if errors:
        lines += ['## 错误', ''] + [f'- {e}' for e in errors]
    else:
        lines += ['## 结论', '', '- 题库数据、解析、去重、生成文件和PWA缓存版本全部通过独立验收。']
    STATUS.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
