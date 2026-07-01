"""
json_to_md.py — 从 questions.json 反向生成 复习题整合.md
========================================================
数据流：questions.json → 复习题整合.md
JSON 是单一数据源，Markdown 是生成的阅读文档。

生成格式：
  ## 一、热处理基础知识
  ### 选择题
  1、题干（ D ）
  A、选项1 B、选项2 C、选项3 D、选项4

  ### 判断题
  (√) 1、题目内容

  ### 填空题
  1、题目 ______
     答：答案

  ### 简答题
  1、题目
     答：答案

  ### 计算题
  1、题目
     解：...
     答：...
"""
import json
from pathlib import Path
from collections import OrderedDict

BASE = Path(__file__).parent

with open(BASE / 'questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# ============================================================
# Section ordering and names
# ============================================================
SECTION_ORDER = [
    '热处理基础知识',
    '热处理设备与工艺',
    '质量管理',
    '仪表知识',
    '综合复习',
]

SECTION_TITLES = {
    '热处理基础知识': '一、热处理基础知识',
    '热处理设备与工艺': '二、热处理设备与工艺',
    '质量管理': '三、质量管理',
    '仪表知识': '四、仪表知识',
    '综合复习': '五、综合复习',
}

TYPE_ORDER = ['choice', 'truefalse', 'fill', 'shortanswer', 'calculation']
TYPE_NAMES = {
    'choice': '选择题',
    'truefalse': '判断题',
    'fill': '填空题',
    'shortanswer': '简答题',
    'calculation': '计算题',
}

# ============================================================
# Group questions by section → type
# ============================================================
groups = OrderedDict()
for section in SECTION_ORDER:
    groups[section] = OrderedDict()
    for t in TYPE_ORDER:
        groups[section][t] = []

for q in questions:
    topic = q.get('topic', '')
    qtype = q.get('type', '')
    if topic in groups and qtype in groups[topic]:
        groups[topic][qtype].append(q)

# ============================================================
# Generate Markdown
# ============================================================
lines = []
lines.append('# 热处理考试复习题整合')
lines.append('')
lines.append('> 本文档由 `json_to_md.py` 从 `questions.json` 自动生成。')
lines.append(f'> 总题数：{len(questions)} 题')
lines.append('')
lines.append('---')
lines.append('')

# Table of contents
lines.append('## 目录')
lines.append('')
for section in SECTION_ORDER:
    sec_title = SECTION_TITLES.get(section, section)
    lines.append(f'- [{sec_title}](#{sec_title.replace("、", "").replace(" ", "-")})')
    for t in TYPE_ORDER:
        qs = groups[section][t]
        if qs:
            lines.append(f'  - [{TYPE_NAMES[t]}（{len(qs)}题）](#{sec_title.replace("、", "").replace(" ", "-")}-{TYPE_NAMES[t]})')
lines.append('')

# Generate each section
for section in SECTION_ORDER:
    sec_title = SECTION_TITLES.get(section, section)
    lines.append('---')
    lines.append('')
    lines.append(f'## {sec_title}')
    lines.append('')

    for t in TYPE_ORDER:
        qs = groups[section][t]
        if not qs:
            continue

        type_name = TYPE_NAMES[t]
        lines.append(f'### {type_name}')
        lines.append('')

        for i, q in enumerate(qs):
            qid = q.get('id', '?')
            question = q.get('question', '').strip()
            answer = q.get('answer', '').strip()
            options = q.get('options', [])
            option_labels = q.get('option_labels', [])
            explanation = q.get('explanation', '').strip()

            if t == 'choice':
                # Format: 1、题干（ D ）
                # Clean up trailing option markers from question text
                import re
                cleaned_q = re.sub(r'\s+[A-D][、.．].*$', '', question).strip()
                ans_str = f'（ {answer} ）' if answer else '（ ）'
                lines.append(f'{i+1}、{cleaned_q}{ans_str}')
                if options:
                    opts_parts = []
                    for j, opt in enumerate(options):
                        label = option_labels[j] if j < len(option_labels) else chr(65+j)
                        opts_parts.append(f'{label}、{opt}')
                    lines.append('')
                    lines.append(' '.join(opts_parts))
                lines.append('')

            elif t == 'truefalse':
                # Format: (√) 1、题目内容
                marker = f'({answer})' if answer in ('√', '×') else '( )'
                lines.append(f'{marker} {i+1}、{question}')
                lines.append('')

            elif t == 'fill':
                # Format: 1、题目 ______
                #    答：答案
                lines.append(f'{i+1}、{question}')
                if answer:
                    lines.append(f'   答：{answer}')
                else:
                    lines.append(f'   答：（答案缺失）')
                lines.append('')

            elif t == 'shortanswer':
                # Format: 1、题目
                #    答：答案（从explanation提取）
                lines.append(f'{i+1}、{question}')
                if explanation:
                    lines.append(f'   答：{explanation}')
                elif answer:
                    lines.append(f'   答：{answer}')
                else:
                    lines.append(f'   答：（答案缺失）')
                lines.append('')

            elif t == 'calculation':
                # Format: 1、题目
                #    解/答（从explanation提取）
                lines.append(f'{i+1}、{question}')
                if explanation:
                    lines.append(f'   {explanation}')
                elif answer:
                    lines.append(f'   答：{answer}')
                else:
                    lines.append(f'   答：（解析缺失）')
                lines.append('')

# ============================================================
# Write output
# ============================================================
content = '\n'.join(lines)

output_path = BASE / '复习题整合.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Count stats
total = sum(len(qs) for sec in groups.values() for qs in sec.values())
print(f'[OK] Generated 复习题整合.md ({len(content):,} chars, {content.count(chr(10)):,} lines)')
print(f'Questions written: {total}')

for section in SECTION_ORDER:
    sec_total = sum(len(qs) for qs in groups[section].values())
    type_counts = ', '.join(f'{TYPE_NAMES[t]}: {len(groups[section][t])}' for t in TYPE_ORDER if groups[section][t])
    print(f'  {SECTION_TITLES[section]}: {sec_total}题 ({type_counts})')
