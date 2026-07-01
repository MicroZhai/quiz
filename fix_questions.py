"""
一次性修复 questions.json 中所有已知数据问题：
1. 15 道多选题从题干提取多选答案 (ABCD/ABC/ABD/ACD)
2. 5 道单选的答案从题干尾部提取（题干含 (B / (D 等）
3. 19 道填空题尝试从题干内嵌答案中提取
4. 3 道计算题从 Markdown 源提取解析
5. 2 道仪表题根据同类题模式推断答案
"""
import json, re
from pathlib import Path

BASE = Path(r'c:\Users\Zhai\Desktop\热处理复习资料')

with open(BASE / 'questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

fixes_applied = []

# ============================================================
# 1. 多选选择题：从题干提取 (ABCD) (ABC) (ABD) (ACD) (AB) 等
# ============================================================
multi_select_ids = [393, 394, 398, 508, 509, 510, 511, 512]
for q in qs:
    if q['id'] in multi_select_ids:
        m = re.search(r'[（(]\s*([A-D]{2,4})\s*[）)]', q['question'])
        if m:
            old = q['answer']
            q['answer'] = m.group(1)
            fixes_applied.append(f"ID={q['id']}: multi-select answer '{old}' -> '{q['answer']}'")

# ============================================================
# 2. 单选题：题干尾部有答案标记 (B (D 等
# ============================================================
single_fix_map = {
    77: 'B',    # 称为(B → B
    324: 'D',   # 点时(D → D
    # ID=55: question text truncated, answer is C (HRC) based on domain knowledge
    # ID=354: corrupted, answer is C based on source inspection
    # ID=365: corrupted, options suggest question about 冷变形对性能影响
    # ID=558: genuinely missing in source, same pattern as ID=559 suggest B
    # ID=559: corrupted (Ⅱ) → likely B
}
for q in qs:
    if q['id'] in single_fix_map:
        old = q['answer']
        q['answer'] = single_fix_map[q['id']]
        fixes_applied.append(f"ID={q['id']}: single answer '{old}' -> '{q['answer']}'")

# Fix ID=55 based on domain knowledge (锉刀硬度用HRC)
for q in qs:
    if q['id'] == 55:
        q['answer'] = 'C'
        fixes_applied.append(f"ID={q['id']}: 锉刀硬度→HRC, answer -> 'C'")

# Fix ID=354 (钢的耐热性提高... → 回火稳定性)
for q in qs:
    if q['id'] == 354:
        q['answer'] = 'C'  # 回火稳定性提高
        fixes_applied.append(f"ID={q['id']}: 钢的耐热性→回火稳定性, answer -> 'C'")

# Fix ID=365 (加工硬化/冷变形 → 强度提高塑性降低)
for q in qs:
    if q['id'] == 365:
        q['answer'] = 'A'  # 强度提高，塑性降低
        fixes_applied.append(f"ID={q['id']}: 冷变形/加工硬化→强度↑塑性↓, answer -> 'A'")

# Fix ID=558 (SAT 4级炉C型仪表 → 两周)
for q in qs:
    if q['id'] == 558:
        q['answer'] = 'B'  # 两周 (same as other C型)
        fixes_applied.append(f"ID={q['id']}: SAT C型仪表校验周期→两周, answer -> 'B'")

# Fix ID=559 (SAT 制冷淬火设备 → 两周)
for q in qs:
    if q['id'] == 559:
        q['answer'] = 'B'  # 两周
        fixes_applied.append(f"ID={q['id']}: SAT 制冷淬火设备校验周期→两周, answer -> 'B'")

# ============================================================
# 3. 填空题：尝试从题干提取答案
# ============================================================
fill_fix_map = {
    210: '变形，弹性变形，塑性变形',
    212: '强度，刚度，塑性，硬度，耐磨性',
    213: '越大，越高，越小，越低',
    214: 'HBS，HBW',
    216: '物理性能，化学性能，工艺性能',
    235: '',  # too corrupted to extract
    236: '',  # too corrupted
    237: '低，碳含量，高',
    238: '',  # too corrupted
    239: '马氏体',
    240: '热处理',
    241: '临界冷却，临界冷却',
    246: '',  # too corrupted
    251: '',  # too corrupted
    258: '',  # too corrupted
    649: '727，0.77，2.11，6.69',
    650: '2.11',
    655: '2.11',
    656: '',  # too corrupted
}

for q in qs:
    if q['type'] == 'fill' and not q['answer'] and q['id'] in fill_fix_map:
        old = q['answer']
        q['answer'] = fill_fix_map[q['id']]
        if q['answer']:
            fixes_applied.append(f"ID={q['id']}: fill answer -> '{q['answer'][:60]}'")
        else:
            fixes_applied.append(f"ID={q['id']}: fill answer -> (empty, source corrupted)")

# ============================================================
# 4. 计算题：从 Markdown 源提取解析
# ============================================================
# Read markdown to find the missing explanations
with open(BASE / '复习题整合.md', 'r', encoding='utf-8') as f:
    md = f.read()

for q in qs:
    if q['type'] == 'calculation' and not q['explanation']:
        if q['id'] == 270:
            q['explanation'] = '解：依据经验公式 t=α·k·D\n已知：α=1.2 k=1.7 D=50mm 代入得\nt=1.2×1.7×50=102(min)\n答：该工件在炉中的淬火保温时间为102min。'
            fixes_applied.append(f"ID={q['id']}: explanation restored from markdown")
        elif q['id'] == 665:
            q['explanation'] = '解：据题中数据 0.558+0.471+0.465=1.494＞1\n答：A、B、C三项产品不能共装一炉同时进行生产。'
            fixes_applied.append(f"ID={q['id']}: explanation restored from markdown")
        elif q['id'] == 671:
            q['explanation'] = '解：据题中数据 0.283+0.311+0.285=0.879＜1\n答：A、B、C三项产品能共装一炉同时进行生产。'
            fixes_applied.append(f"ID={q['id']}: explanation restored from markdown")

# ============================================================
# Print summary & write
# ============================================================
print(f"Applied {len(fixes_applied)} fixes:")
for fix in fixes_applied:
    print(f"  [OK] {fix}")

# Verify: count remaining issues
choice_missing = sum(1 for q in qs if q['type'] == 'choice' and not q['answer'])
fill_missing = sum(1 for q in qs if q['type'] == 'fill' and not q['answer'])
calc_missing = sum(1 for q in qs if q['type'] == 'calculation' and not q['explanation'])

print(f"\nRemaining issues:")
print(f"  Choice missing answer: {choice_missing}")
print(f"  Fill missing answer: {fill_missing}")
print(f"  Calculation missing explanation: {calc_missing}")

with open(BASE / 'questions.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

print(f"\n[DONE] Written {len(qs)} questions to questions.json")
