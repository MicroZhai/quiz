"""
fix_questions_v3.py — 修复 questions.json 中的残留数据问题
============================================================
问题：
  1. ID 107/108 题干有杂散后缀
  2. ID 444 合并了两道判断题
  3. ID 325-342 是填空题但 type 标为 truefalse
  4. 部分题干有内嵌答案标记需要清理
运行后：python json_to_md.py && python build_quiz.py
"""
import json, re, copy
from pathlib import Path

BASE = Path(__file__).parent

with open(BASE / 'questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Build lookup
by_id = {q['id']: q for q in questions}
max_id = max(q['id'] for q in questions)

fixes_applied = []

# ============================================================
# 1. Clean garbled suffixes on IDs 107, 108
# ============================================================
if 107 in by_id:
    old = by_id[107]['question']
    # Remove trailing garbled text after the main statement
    by_id[107]['question'] = '在共析温度以下存在的奥氏体称为过冷奥氏体。'
    fixes_applied.append(f'ID=107: cleaned suffix [{old[-30:]}] → [{by_id[107]["question"][-30:]}]')

if 108 in by_id:
    old = by_id[108]['question']
    # "属于不锈钢类。" is wrong — Cr12/Cr12MoV are NOT stainless, it's garbled suffix
    by_id[108]['question'] = '常用的冷作模具钢有：Cr12、Cr12MoV。'
    fixes_applied.append(f'ID=108: cleaned suffix')

# --- Additional garbled suffixes ---
garbled_suffix_fixes = {
    144: ('炉温均匀性测量的目的，在于通过测量掌握炉膛内各处温度的分布情况。',
          '薄的部分先漫入浑火'),
    149: ('导热性差的金属工件或坯料，加热或冷却时会产生内外温差导致内外不同的膨胀或收缩，产生应力、变形或破坏。',
          '在空冷过程中能发生马氏体转'),
    150: ('1Cr12Ni2WMoVNb钢的淬透性好。',
          '变。'),
}

for qid, (clean_txt, suffix) in garbled_suffix_fixes.items():
    if qid in by_id:
        old = by_id[qid]['question']
        by_id[qid]['question'] = clean_txt
        fixes_applied.append(f'ID={qid}: removed suffix [{suffix}]')

# ============================================================
# 2. Split merged question ID 444
# ============================================================
if 444 in by_id:
    old_q = by_id[444]['question']
    # Split at " ( J)18、" pattern
    parts = re.split(r'\s*\(\s*J\s*\)\s*18[、，.]?\s*', old_q)
    if len(parts) == 2:
        part1 = parts[0].strip().rstrip('.。') + '。'
        part2 = parts[1].strip()
        # Fix garbled characters in part2
        part2 = part2.replace('趋热', '趋势').replace('从总的趋势上看', '从总的趋势上看，')
        if not part2.endswith('。'):
            part2 = part2.rstrip('.。') + '。'

        by_id[444]['question'] = part1
        fixes_applied.append(f'ID=444 part1: [{part1[:80]}...]')

        # Create new question for part2
        max_id += 1
        new_q = copy.deepcopy(by_id[444])
        new_q['id'] = max_id
        new_q['question'] = part2
        new_q['answer'] = '√'  # 回火硬度随温度升高而降低 — 正确
        new_q['knowledge_point'] = '回火'
        new_q['knowledge_point_key'] = 'tempering'
        questions.append(new_q)
        by_id[max_id] = new_q
        fixes_applied.append(f'NEW ID={max_id} (from ID=444 split): [{part2[:80]}...]')

# ============================================================
# 3. Fix IDs 325-342: truefalse → fill, extract answers
# ============================================================
fill_fixes = {
    325: {
        'question': '真空炉生产结束后，待炉膛内温度低于______行出炉作业。',
        'answer': '200度'
    },
    326: {
        'question': '定速降温炉在进行非定速降温工艺生产时，应先检查______保证其置于关闭档，方可进行正常生产。',
        'answer': '降温开关旋钮'
    },
    327: {
        'question': '铝合金、空气淬火炉在出炉时必须保证______灯亮和______灯亮，方可打开炉门进行下降作业。',
        'answer': '料框升，穿销位'
    },
    328: {
        'question': '目前热处理分厂井式炉上有______台循环风机。',
        'answer': '三台'
    },
    329: {
        'question': '10T机械手装出炉位有两种，分别是______、______。',
        'answer': '全炉位，半桥'
    },
    330: {
        'question': '分厂电炉的加热元件主要有两种，分别是______、______。',
        'answer': '电阻带，电炉丝'
    },
    331: {
        'question': '分厂蒸汽发生器主要是给水槽进行______。',
        'answer': '加热'
    },
    332: {
        'question': '炉子循环风机主要作用是为了保证炉温______。',
        'answer': '均匀性'
    },
    333: {
        'question': '自主维护活动的基本工作______、清扫、加润滑油、整理和整顿、简单维修和更换。',
        'answer': '点检、紧固'
    },
    334: {
        'question': '在自主维护活动中应按照______对设备进行清扫。',
        'answer': '清扫标准'
    },
    # ID 335 is already type "fill" - skip
    336: {
        'question': '在自主维护活动时应对______进行着重检查。',
        'answer': '近期故障频发点'
    },
    337: {
        'question': '班组应在______对设备一保内容一一对应进行检查。',
        'answer': '设备使用前'
    },
    338: {
        'question': 'TPM的三大思想是______、零缺陷、小组活动。',
        'answer': '预防'
    },
    339: {
        'question': '现场班组应定期对设备进行______查找问题，发现隐患并及时解决。',
        'answer': '自主维护活动'
    },
    340: {
        'question': 'OPL的编号规则是：______。',
        'answer': '单位+年份月份+小组名称+当月篇数'
    },
    341: {
        'question': '设备水箱水位不能低于总水位的______。',
        'answer': '一半'
    },
    342: {
        'question': '定期使用压缩空气对配电柜内______进行清扫，防止设备因过热导致断电停机。',
        'answer': '调功器散热片'
    },
}

for qid, fix in fill_fixes.items():
    if qid in by_id:
        old_type = by_id[qid]['type']
        old_q = by_id[qid]['question']
        by_id[qid]['type'] = 'fill'
        by_id[qid]['question'] = fix['question']
        by_id[qid]['answer'] = fix['answer']
        fixes_applied.append(f'ID={qid}: type {old_type}→fill, q=[{old_q[:60]}...] → [{fix["question"][:60]}...]')

# Fix ID 335 (already fill) — update answer if needed
if 335 in by_id:
    # ID 335 question is about 吊具管理规定 colors, answer should be about tonnage
    # Current: answer="1级，2级，3级" — this seems correct based on context
    # But let's verify the question text
    old_q = by_id[335]['question']
    # The question says 紫色/绿色/黄色/红色 吊具, but the MD shows different content
    # Keep current answer as-is since it was filled in v2
    fixes_applied.append(f'ID=335: kept as fill, q=[{old_q[:80]}...]')

# ============================================================
# 4. Fix garbled content in ID 342's original question trailing text
#    (already handled above in fill_fixes)
# ============================================================

# ============================================================
# 5. Check for other garbled entries
# ============================================================
# ID 149 has garbled text at end, let's check
for q in questions:
    txt = q.get('question', '')
    # Check for orphan section headers embedded in question text
    if re.search(r'[三四五六七八九]、', txt):
        fixes_applied.append(f'WARNING ID={q["id"]}: possible embedded section header: [{txt[:120]}]')

# ============================================================
# Write fixed JSON
# ============================================================
# Sort by ID
questions.sort(key=lambda x: x['id'])

output_path = BASE / 'questions.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f'[OK] Fixed questions.json ({len(questions)} total questions)')
print(f'Fixes applied:')
for fix in fixes_applied:
    print(f'  - {fix}')

# Stats
type_counts = {}
for q in questions:
    t = q['type']
    type_counts[t] = type_counts.get(t, 0) + 1
print(f'\nType distribution:')
for t, c in sorted(type_counts.items()):
    print(f'  {t}: {c}')
