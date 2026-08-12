from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / 'questions.json'
REPORT = ROOT / 'audit' / 'DEDUP_EXISTING_REPORT.md'
IMPORTED_BANK = 'metal_heat_treatment_2000_reviewed_2026'


def norm(s: str) -> str:
    return re.sub(r'\s+', '', str(s or '')).lower()


def signature(q: dict) -> tuple:
    return (
        q.get('type'),
        norm(q.get('question')),
        tuple(norm(x) for x in (q.get('options') or [])),
        norm(q.get('answer')),
    )


def quality(q: dict) -> tuple[int, int, int]:
    """Prefer rows with explanation and richer learning metadata."""
    explanation = str(q.get('explanation') or '')
    kp = str(q.get('knowledge_point') or '')
    return (1 if explanation else 0, len(explanation), 1 if kp else 0)


def merge_into(keep: dict, duplicate: dict) -> list[str]:
    changes: list[str] = []
    if quality(duplicate) > quality(keep):
        if duplicate.get('explanation') and duplicate.get('explanation') != keep.get('explanation'):
            keep['explanation'] = duplicate['explanation']
            changes.append('采用更完整解析')
        if duplicate.get('knowledge_point') and not keep.get('knowledge_point'):
            keep['knowledge_point'] = duplicate['knowledge_point']
            changes.append('补知识点')
        if duplicate.get('knowledge_point_key') and not keep.get('knowledge_point_key'):
            keep['knowledge_point_key'] = duplicate['knowledge_point_key']
            changes.append('补知识点键')
        if duplicate.get('topic') and not keep.get('topic'):
            keep['topic'] = duplicate['topic']
            changes.append('补主题')
    return changes


def main() -> int:
    all_q = json.loads(QUESTIONS.read_text(encoding='utf-8'))
    # Remove any previous generated 2000-bank import first; integration will rebuild it idempotently.
    base = [q for q in all_q if q.get('source_bank') != IMPORTED_BANK]
    imported_removed = len(all_q) - len(base)

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for q in base:
        groups[signature(q)].append(q)

    removed_ids: set[int] = set()
    details: list[dict] = []
    for rows in groups.values():
        if len(rows) < 2:
            continue
        rows.sort(key=lambda q: int(q.get('id', 10**9)))
        keep = rows[0]
        removed = rows[1:]
        merged_changes = []
        for dup in removed:
            merged_changes.extend(merge_into(keep, dup))
            removed_ids.add(int(dup['id']))
        details.append({
            'keep_id': int(keep['id']),
            'removed_ids': [int(x['id']) for x in removed],
            'question': keep.get('question', ''),
            'merged_changes': sorted(set(merged_changes)),
        })

    cleaned = [q for q in base if int(q.get('id', -1)) not in removed_ids]
    QUESTIONS.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# 旧715题完全重复清理报告', '',
        f'- 清理前旧正式题库：**{len(base)}**',
        f'- 完全重复组：**{len(details)}**',
        f'- 删除重复副本：**{len(removed_ids)}**',
        f'- 清理后唯一题：**{len(cleaned)}**',
        f'- 运行前移除的旧版2000题导入结果：**{imported_removed}**（会由后续入库脚本重建）', '',
        '## 规则', '',
        '- “完全重复”要求题型、标准化题干、选项和答案全部相同。',
        '- 每组保留 ID 最小的一条，以尽量保持既有学习记录稳定。',
        '- 若重复副本解析更完整，则把更完整解析合并到保留题后再删除副本。', '',
        '## 明细', '',
    ]
    if not details:
        lines.append('- 无完全重复题。')
    for row in details:
        change = '；'.join(row['merged_changes']) if row['merged_changes'] else '无需合并字段'
        lines.append(f"- 保留 ID **{row['keep_id']}**；删除 {row['removed_ids']}；{change}；题目：{row['question']}")
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(json.dumps({
        'before': len(base),
        'duplicate_groups': len(details),
        'removed': len(removed_ids),
        'after': len(cleaned),
        'details': details,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
