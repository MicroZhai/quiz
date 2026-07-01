"""
从 复习题整合.md 解析题目，输出 questions.json 和 questions.js
"""
import re, json
from pathlib import Path

BASE = Path(r'c:\Users\Zhai\Desktop\热处理复习资料')
MD_FILE = BASE / '复习题整合.md'

SECTION_TOPIC = {
    '一、热处理基础知识': '热处理基础知识',
    '二、热处理设备知识': '热处理设备与工艺',
    '三、热处理工艺知识': '热处理设备与工艺',
    '四、质量管理知识': '质量管理',
    '五、仪表知识': '仪表知识',
    '六、综合复习': '综合复习',
}

def extract_choice_answer(qtext):
    """从题干提取选择题答案"""
    m = re.search(r'[（(]\s*([A-D])\s*[）)]', qtext)
    return m.group(1) if m else None

def parse_all():
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    questions = []
    current_h2 = ''
    current_h3 = ''
    current_topic = ''

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # H2 标题
        m2 = re.match(r'^##\s+(.+)', s)
        if m2:
            current_h2 = m2.group(1)
            if '目录' not in current_h2 and '📑' not in current_h2:
                current_topic = SECTION_TOPIC.get(current_h2, current_h2)
            current_h3 = ''
            i += 1
            continue

        # H3 标题 → 题型
        m3 = re.match(r'^###\s+(.+)', s)
        if m3:
            current_h3 = m3.group(1)
            i += 1
            continue

        # ---- 选择题 ----
        if current_h3 == '选择题':
            mq = re.match(r'^(\d{1,3})[、\.]\s*(.+)', s)
            if mq:
                qtext = mq.group(2).strip()

                # 收集选项行
                j = i + 1
                extra_lines = []
                while j < len(lines):
                    ns = lines[j].strip()
                    if not ns:
                        extra_lines.append(lines[j])
                        j += 1
                        continue
                    if re.match(r'^\d{1,3}[、\.]', ns) or re.match(r'^#{1,3}\s', ns):
                        break
                    extra_lines.append(lines[j])
                    j += 1

                full_opts = '\n'.join(extra_lines)
                answer = extract_choice_answer(qtext)

                # 清理题干中的答案标记
                question = re.sub(r'[（(]\s*[A-D]\s*[）)]', '（ ）', qtext)
                question = re.sub(r'（\s*）', '（ ）', question)

                # 提取选项
                options = []
                opt_labels = []
                opt_parts = re.findall(r'([A-D])[、\.]\s*(.+?)(?=\s+[A-D][、\.]|$)', full_opts)
                if not opt_parts:
                    opt_parts = re.findall(r'([A-D])\s+(.+?)(?=\s+[A-D]\s+|$)', full_opts)
                for label, text in opt_parts:
                    opt_labels.append(label)
                    options.append(text.strip())

                questions.append({
                    'type': 'choice',
                    'question': question,
                    'options': options,
                    'option_labels': opt_labels,
                    'answer': answer if answer else '',
                    'explanation': '',
                    'topic': current_topic,
                    'section': current_h2,
                })
                i = j
                continue

        # ---- 判断题 ----
        if current_h3 == '判断题':
            # 行格式: (√) 01、题目 或 (×) 01、题目
            mq = re.match(r'\(\s*([√×]?)\s*\)\s*(\d{1,3})[、，\.]\s*(.+)', s)
            if mq:
                ans = mq.group(1) or ''
                qtext = mq.group(3).strip()
                questions.append({
                    'type': 'truefalse',
                    'question': qtext,
                    'answer': ans,
                    'explanation': '',
                    'topic': current_topic,
                    'section': current_h2,
                })
            i += 1
            continue

        # ---- 填空题 ----
        if current_h3 == '填空题':
            mq = re.match(r'^(\d{1,3})[、\.]\s*(.+)', s)
            if mq:
                qtext = mq.group(2).strip()
                answer = ''
                # 下一行可能是 答：...
                if i+1 < len(lines):
                    ns = lines[i+1].strip()
                    m_ans = re.match(r'^答：(.+)', ns)
                    if m_ans:
                        answer = m_ans.group(1).strip()
                        i += 1  # 跳过答案行

                qtext = re.sub(r'_{2,}', '______', qtext)
                if '______' not in qtext:
                    qtext += ' ______'

                questions.append({
                    'type': 'fill',
                    'question': qtext,
                    'answer': answer,
                    'explanation': '',
                    'topic': current_topic,
                    'section': current_h2,
                })
            i += 1
            continue

        # ---- 简答题 ----
        if current_h3 == '简答题':
            mq = re.match(r'^(\d{1,3})[、\.]\s*(.+)', s)
            if mq:
                qtext = mq.group(2).strip()
                explanation = ''
                # 收集后续行直到遇到 答：
                j = i + 1
                while j < len(lines):
                    ns = lines[j].strip()
                    if re.match(r'^答：', ns):
                        explanation = ns[2:].strip()
                        j += 1
                        break
                    if re.match(r'^\d{1,3}[、\.]', ns) or re.match(r'^#{1,3}\s', ns):
                        break
                    j += 1

                questions.append({
                    'type': 'shortanswer',
                    'question': qtext,
                    'answer': '',
                    'explanation': explanation,
                    'topic': current_topic,
                    'section': current_h2,
                })
                i = j
                continue

        # ---- 计算题 ----
        if current_h3 == '计算题':
            mq = re.match(r'^(\d{1,3})[、\.]\s*(.+)', s)
            if mq:
                qtext = mq.group(2).strip()
                explanation = ''
                j = i + 1
                while j < len(lines):
                    ns = lines[j].strip()
                    if re.match(r'^答：|^解：', ns):
                        explanation += ns + '\n'
                        j += 1
                        continue
                    if re.match(r'^\d{1,3}[、\.]', ns) or re.match(r'^#{1,3}\s', ns):
                        break
                    j += 1
                explanation = explanation.strip()

                questions.append({
                    'type': 'calculation',
                    'question': qtext,
                    'answer': '',
                    'explanation': explanation,
                    'topic': current_topic,
                    'section': current_h2,
                })
                i = j
                continue

        i += 1

    # Dedup
    seen = set()
    unique = []
    for q in questions:
        key = q['question'][:50].strip()
        if key in seen:
            continue
        seen.add(key)
        q['id'] = len(unique) + 1
        unique.append(q)

    # Output
    json_path = BASE / 'questions.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    js_path = BASE / 'questions.js'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('window.ALL_QUESTIONS = ' + json.dumps(unique, ensure_ascii=False, indent=2) + ';')

    # Stats
    from collections import Counter
    types = Counter(q['type'] for q in unique)
    print(f'Total: {len(unique)} questions')
    for t, n in types.items():
        with_ans = sum(1 for q in unique if q['type'] == t and q.get('answer'))
        print(f'  {t}: {n} (with answer: {with_ans})')

if __name__ == '__main__':
    parse_all()
