from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARSED = ROOT / 'audit' / 'parsed_2000.json'
REVIEWS = ROOT / 'audit' / 'reviews'
QUESTIONS = ROOT / 'questions.json'
REPORT = ROOT / 'audit' / 'FINAL_IMPORT_REPORT.md'
SOURCE_BANK = 'metal_heat_treatment_2000_reviewed_2026'
SOURCE_NAME = '金属热处理工考工晋级大题库（2000题审校版）'


def norm(s: str) -> str:
    s = str(s or '').lower().replace('fe₃c', 'fe3c')
    s = re.sub(r'[\s\\>*`]+', '', s)
    s = re.sub(r'[，。；：、,.!?！？;:\"\'“”‘’（）()\[\]【】<>《》—－-]', '', s)
    return s


def signature(q: dict) -> str:
    return '|'.join([
        str(q.get('type', '')),
        norm(q.get('question', '')),
        '||'.join(norm(x) for x in q.get('options', []) or []),
        norm(q.get('answer', '')),
    ])


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_reviews() -> dict[int, dict]:
    reviews: dict[int, dict] = {}
    patterns = ['judgment_*.json', 'choice_*.json', 'shortanswer_*.json', 'composite_unresolved_*.json']
    for pattern in patterns:
        for path in sorted(REVIEWS.glob(pattern)):
            for item in load_json(path):
                idx = int(item['source_index'])
                if idx in reviews:
                    raise ValueError(f'重复审校记录 source_index={idx}: {path}')
                reviews[idx] = item
    return reviews


def load_fixes() -> dict[int, dict]:
    path = REVIEWS / 'question_fixes.json'
    if not path.exists():
        return {}
    return {int(x['source_index']): x for x in load_json(path)}


def level_short(level: str) -> str:
    if '初级' in level: return '初级工'
    if '中级' in level: return '中级工'
    if '高级工' in level: return '高级工'
    if '技师' in level: return '技师/高级技师'
    if '第五部分' in level: return '强化练习'
    return '综合'


def difficulty(level: str) -> int:
    if '初级' in level: return 1
    if '中级' in level: return 2
    if '高级工' in level: return 3
    if '技师' in level: return 4
    if '第五部分' in level: return 3
    return 2


def topic_for(kp: str, question: str = '') -> str:
    text = f'{kp} {question}'
    instrument = ['热电偶','测温','炉温均匀','系统准确','辐射测温','温度记录','计量','温控','硬度计']
    quality = ['质量','硬度检验','金相','SPC','MSA','GRR','FMEA','8D','5Why','鱼骨','过程能力','追溯','检验','返修','文件','变更','数据','审核','培训','供应商','客户','首件','控制计划','反应计划','失效','根因','统计','DOE','工艺验证','资格','知识管理','持续改进','偏差评审','抽样']
    equipment = ['设备','炉门','风机','真空炉','淬火槽','感应器','盐浴','吊装','安全','工装','装炉','冷却系统','备件','维护','产能','节能','氨气','油火灾']
    if any(k in text for k in instrument): return '仪表知识'
    if any(k in text for k in quality): return '质量管理'
    if any(k in text for k in equipment): return '热处理设备与工艺'
    if any(k in text for k in ['渗碳','渗氮','感应','火焰','淬火介质','真空热处理','化学热处理']): return '热处理设备与工艺'
    return '热处理基础知识'


def kp_key(kp: str) -> str:
    rules = [
        ('退火', 'annealing'), ('正火', 'normalizing'), ('调质', 'tempering'), ('回火', 'tempering'),
        ('淬透', 'quenching'), ('淬硬', 'quenching'), ('淬火', 'quenching'),
        ('TTT', 'ttt_cct_diagram'), ('CCT', 'ttt_cct_diagram'),
        ('奥氏体', 'austenite_transformation'), ('Ms', 'martensite_transformation'), ('Mf', 'martensite_transformation'),
        ('马氏体', 'martensite_transformation'), ('残余奥氏体', 'martensite_transformation'), ('冷处理', 'martensite_transformation'),
        ('珠光体', 'pearlite_bainite'), ('贝氏体', 'pearlite_bainite'),
        ('渗碳', 'surface_chemical_heat_treatment'), ('渗氮', 'surface_chemical_heat_treatment'), ('感应', 'surface_chemical_heat_treatment'), ('火焰', 'surface_chemical_heat_treatment'),
        ('牌号', 'steel_classification'), ('20钢', 'steel_classification'), ('45钢', 'steel_classification'), ('40Cr', 'steel_classification'), ('65Mn', 'steel_classification'), ('GCr15', 'steel_classification'), ('20CrMnTi', 'steel_classification'), ('38CrMoAl', 'steel_classification'), ('T10', 'steel_classification'), ('Cr12MoV', 'steel_classification'), ('W18Cr4V', 'steel_classification'), ('W6Mo5Cr4V2', 'steel_classification'), ('60Si2Mn', 'steel_classification'),
        ('合金元素', 'alloy_elements'), ('硼', 'alloy_elements'), ('力学', 'mechanical_properties'), ('硬度', 'mechanical_properties'),
    ]
    for token, key in rules:
        if token in kp: return key
    return 'reviewed_import'


def clean_truth_prefix(text: str) -> str:
    return re.sub(r'^(正确|错误)[。；：:\s]*', '', str(text or '').strip())


def composite_explanation(q: dict, parsed_by_norm: dict[str, list[dict]], reviews: dict[int, dict]) -> tuple[str, str, str]:
    labels = q.get('option_labels') or []
    options = q.get('options') or []
    truths = (q.get('auto_check') or {}).get('option_truth') or []
    parts = []
    selected_review = None
    bases = []
    for i, (label, opt) in enumerate(zip(labels, options)):
        truth = truths[i] if i < len(truths) else None
        candidates = parsed_by_norm.get(norm(opt), [])
        atomic_review = None
        for cand in candidates:
            if cand.get('type') == 'truefalse' and int(cand.get('source_index', -1)) in reviews:
                atomic_review = reviews[int(cand['source_index'])]
                break
        state = '正确' if truth is True else '错误' if truth is False else '需结合题意判断'
        if atomic_review:
            detail = clean_truth_prefix(atomic_review.get('explanation', ''))
            if label == q.get('answer'):
                selected_review = atomic_review
            if atomic_review.get('basis'):
                bases.append(atomic_review['basis'])
        else:
            detail = '该选项已通过题库内部逻辑校验。' if truth is not None else '该选项需结合其他已审知识点判断。'
        parts.append(f'{label}{state}：{detail}')
    intro = f"本题答案为{q.get('answer')}。"
    explanation = intro + '；'.join(parts)
    kp = (selected_review or {}).get('knowledge_point') or '综合辨析'
    basis = '；'.join(dict.fromkeys(bases)) if bases else '已审基础命题组合验证'
    return explanation, kp, basis


def main() -> int:
    parsed = load_json(PARSED)
    reviews = load_reviews()
    fixes = load_fixes()
    parsed_map = {int(q['source_index']): q for q in parsed if q.get('source_index') is not None}

    original_indices = {idx for idx, q in parsed_map.items() if not str(q.get('level','')).startswith('第五部分')}
    missing_original = sorted(original_indices - reviews.keys())
    if missing_original:
        raise ValueError(f'原始1037题仍有未审校项: {missing_original[:20]} (共{len(missing_original)})')

    composite = [q for q in parsed if str(q.get('level','')).startswith('第五部分')]
    unresolved = [int(q['source_index']) for q in composite if q.get('audit_status') != 'auto_verified_composite']
    missing_unresolved = [i for i in unresolved if i not in reviews]
    if missing_unresolved:
        raise ValueError(f'强化题未决项缺少人工审校: {missing_unresolved}')

    existing_all = load_json(QUESTIONS)
    base = [q for q in existing_all if q.get('source_bank') != SOURCE_BANK]
    next_id = max(int(q.get('id', 0)) for q in base) + 1
    seen = {signature(q) for q in base}

    parsed_by_norm: dict[str, list[dict]] = defaultdict(list)
    for q in parsed:
        parsed_by_norm[norm(q.get('question',''))].append(q)

    imported = []
    skipped_duplicates = []
    held = []
    fixed_count = 0
    composite_count = 0

    for q in parsed:
        idx = int(q['source_index'])
        review = reviews.get(idx)
        fix = fixes.get(idx)

        if review and review.get('verdict') == 'hold':
            held.append(idx)
            continue

        nq = {
            'type': q.get('type'),
            'question': q.get('question'),
            'options': q.get('options') or [],
            'option_labels': q.get('option_labels') or [],
            'answer': q.get('answer'),
        }
        basis = ''
        if fix:
            fixed_count += 1
            if fix.get('question'): nq['question'] = fix['question']
            if fix.get('answer'): nq['answer'] = fix['answer']
            explanation = fix.get('explanation') or (review or {}).get('explanation') or ''
            kp = (review or {}).get('knowledge_point') or '综合'
            basis = (review or {}).get('basis') or ''
        elif str(q.get('level','')).startswith('第五部分'):
            composite_count += 1
            if review:
                nq['answer'] = review.get('answer', nq['answer'])
                explanation = review.get('explanation', '')
                kp = review.get('knowledge_point', '综合辨析')
                basis = review.get('basis', '')
            else:
                explanation, kp, basis = composite_explanation(q, parsed_by_norm, reviews)
        else:
            if not review:
                raise ValueError(f'缺少审校记录 source_index={idx}')
            if review.get('answer') not in (None, ''):
                nq['answer'] = review['answer']
            explanation = review.get('explanation', '')
            kp = review.get('knowledge_point') or '综合'
            basis = review.get('basis', '')

        if nq['type'] == 'shortanswer' and review:
            # answer is the self-check reference; explanation adds the learning rationale.
            nq['answer'] = review.get('answer') or nq.get('answer') or ''

        if not str(explanation).strip():
            raise ValueError(f'入库题缺少解析 source_index={idx}')

        level = level_short(q.get('level',''))
        topic = topic_for(kp, nq['question'])
        item = {
            'type': nq['type'],
            'question': nq['question'],
            'options': nq['options'],
            'option_labels': nq['option_labels'],
            'answer': nq['answer'],
            'explanation': explanation,
            'section': f"{level} · {q.get('section','').strip()}",
            'topic': topic,
            'id': next_id,
            'knowledge_point': kp,
            'knowledge_point_key': kp_key(kp),
            'difficulty': difficulty(q.get('level','')),
            'source': SOURCE_NAME,
            'source_bank': SOURCE_BANK,
            'source_index': idx,
            'source_no': q.get('source_no'),
            'source_level': level,
            'review_status': 'fixed' if fix else 'reviewed' if not str(q.get('level','')).startswith('第五部分') else 'composite_verified',
        }
        if basis:
            item['review_basis'] = basis

        sig = signature(item)
        if sig in seen:
            skipped_duplicates.append(idx)
            continue
        seen.add(sig)
        imported.append(item)
        next_id += 1

    merged = base + imported
    # Safety checks before writing.
    ids = [int(q['id']) for q in merged]
    if len(ids) != len(set(ids)):
        raise ValueError('合并后出现重复ID')
    missing_expl = [q['id'] for q in imported if not str(q.get('explanation','')).strip()]
    if missing_expl:
        raise ValueError(f'新题缺少解析: {missing_expl[:10]}')
    bad_choices = []
    for q in imported:
        if q['type'] == 'choice':
            labels = q.get('option_labels') or []
            answer = str(q.get('answer',''))
            if not q.get('options') or not answer or any(ch not in labels for ch in answer if ch.isalpha()):
                bad_choices.append(q['id'])
    if bad_choices:
        raise ValueError(f'选择题答案/选项异常: {bad_choices[:20]}')

    QUESTIONS.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    by_type = Counter(q['type'] for q in imported)
    by_level = Counter(q['source_level'] for q in imported)
    by_topic = Counter(q['topic'] for q in imported)
    report = [
        '# 2000题审校与正式入库报告', '',
        '## 结论', '',
        f'- 原始资料题数：**{len(parsed)}**',
        f'- 原正式题库：**{len(base)}**',
        f'- 本次新增正式题：**{len(imported)}**',
        f'- 全部正式题库：**{len(merged)}**',
        f'- 因完整内容重复跳过：**{len(skipped_duplicates)}**',
        f'- 暂缓入库：**{len(held)}**',
        f'- 修正后入库：**{fixed_count}**',
        f'- 强化辨析题入库：**{sum(1 for q in imported if q["source_level"] == "强化练习")}**', '',
        '## 审校覆盖', '',
        f'- 原始题人工知识审校：**{len(original_indices)}/{len(original_indices)}**',
        f'- 强化题自动唯一答案验证：**{sum(1 for q in composite if q.get("audit_status") == "auto_verified_composite")}**',
        f'- 强化题人工补充审校：**{len(unresolved)}**', '',
        '## 新增题型', '',
    ]
    for k, v in sorted(by_type.items()): report.append(f'- {k}: {v}')
    report.extend(['', '## 新增等级', ''])
    for k, v in by_level.items(): report.append(f'- {k}: {v}')
    report.extend(['', '## 新增主题', ''])
    for k, v in by_topic.items(): report.append(f'- {k}: {v}')
    report.extend(['', '## 重复/暂缓明细', '', f'- 重复 source_index: {skipped_duplicates or "无"}', f'- 暂缓 source_index: {held or "无"}', '', '## 说明', '', '- 原1037题必须有人工知识审校记录和学习型解析才允许进入正式题库。', '- 962道自动验证强化题通过已审判断命题反向验证每个选项真假并生成逐项解析。', '- 自动规则无法确认的强化题必须有人工审校记录。', '- `question_fixes.json` 中的歧义题以修订题干覆盖原题后再入库。', '- 再次运行脚本会先移除本来源上次导入结果，再按当前审校记录幂等重建，不会重复累加。', ''])
    REPORT.write_text('\n'.join(report), encoding='utf-8')

    print(json.dumps({
        'base': len(base), 'source': len(parsed), 'imported': len(imported), 'merged': len(merged),
        'duplicates': len(skipped_duplicates), 'held': len(held), 'fixed': fixed_count,
        'by_type': dict(by_type), 'by_level': dict(by_level)
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
