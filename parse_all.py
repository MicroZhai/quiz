"""
解析5个热处理复习 .md 文件，提取所有题目，输出 questions.json
"""
import re
import json
import os
from pathlib import Path

BASE_DIR = Path(r'c:\Users\Zhai\Desktop\热处理复习资料')

# 文件 → 主题映射
FILE_TOPIC = {
    '一、热处理基础知识.md': '热处理基础知识',
    '二、热处理设备知识.md': '热处理设备与工艺',
    '四、质量管理知识.md': '质量管理',
    '五、仪表知识.md': '仪表知识',
    '复习资料.md': '综合复习',
}

# 章节标题模式
SECTION_PATTERNS = [
    (re.compile(r'^##\s*([一二三四五六七八九十]+)、(.+)'), 'md'),   # ## 一、选择题
    (re.compile(r'^\(([一二三四五六七八九十]+)\)(.+)'), 'paren'),   # (一)选择题
    (re.compile(r'^（([一二三四五六七八九十]+)）(.+)'), 'fparen'),  # （一）选择题 (全角括号)
    (re.compile(r'^([一二三四五六七八九十]+)\)(.+)'), 'rparen'),     # 三)填空题 (缺左括号)
    (re.compile(r'^([一二三四五六七八九十]+)、(.+)'), 'dun'),       # 一、选择题 (无括号)
]

SECTION_TYPE_MAP = {
    '选择题': 'choice',
    '判断题': 'truefalse',
    '填空题': 'fill',
    '简答题': 'shortanswer',
    '计算题': 'calculation',
    '作图题': 'drawing',
}

def detect_section(line):
    """检测行是否为章节标题，返回 (type_key, title) 或 None"""
    for pattern, style in SECTION_PATTERNS:
        m = pattern.match(line.strip())
        if m:
            title = (m.group(1) + '、' + m.group(2)).strip()
            for key, stype in SECTION_TYPE_MAP.items():
                if key in title:
                    return stype, title
    return None

def extract_choice_answer(text):
    """从题干中提取选择题答案 (A-D)"""
    m = re.search(r'\(\s*([A-D])\s*\)', text)
    return m.group(1) if m else None

def extract_truefalse_answer(line):
    """从判断题行提取答案"""
    m = re.search(r'\(\s*([√×Xx])\s*\)', line)
    if m:
        ans = m.group(1)
        if ans in ('X', 'x'):
            return '×'
        return ans
    return None

def parse_choice_questions(lines, start_idx, end_idx):
    """解析选择题"""
    questions = []
    # 先合并：如果一行不以编号开头，可能是上一题的延续
    merged = []
    i = start_idx
    while i < end_idx:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # 检测是否为新题目开始
        if re.match(r'^\d{1,3}[、\.]', line):
            merged.append(line)
        elif merged:
            merged[-1] += ' ' + line
        i += 1

    for line in merged:
        # 提取编号
        m = re.match(r'^(\d{1,3})[、\.]\s*(.+)', line, re.DOTALL)
        if not m:
            continue
        qtext = m.group(2).strip()

        # 提取答案
        answer = extract_choice_answer(qtext)

        # 去除答案标记，清理题干
        question = re.sub(r'\(\s*[A-D]\s*\)', '（）', qtext)
        question = question.strip()

        # 提取选项（从题干后的部分）
        options = []
        # 尝试从行中提取 A、B、C、D 选项
        # 多种模式：A、text B、text 或 A.text B.text 或 A text B text
        opt_patterns = [
            r'([A-D])[、\.]\s*(.+?)(?=\s+[A-D][、\.\s]|$)',
            r'([A-D])\s+(.+?)(?=\s+[A-D]\s+|$)',
        ]
        for pat in opt_patterns:
            found = re.findall(pat, qtext)
            if len(found) >= 2:
                options = [(label, text.strip()) for label, text in found]
                break

        # 如果没找到4个选项，可能是选项在下一行——这里简化处理
        # 对于文件3（复习资料）的格式：选项和题干同行但用空格分隔
        if not options:
            # fallback: 搜索 "A." 或 "A、" 模式
            part_match = re.search(r'[A-D][、\.]', qtext)
            if part_match:
                parts = re.split(r'\s{2,}(?=[A-D][、\.])', qtext)
                if len(parts) >= 2:
                    # 第一部分是题干
                    question = parts[0].strip()
                    question = re.sub(r'\(\s*[A-D]\s*\)', '（）', question)
                    for p in parts[1:]:
                        pm = re.match(r'([A-D])[、\.]\s*(.+)', p.strip())
                        if pm:
                            options.append((pm.group(1), pm.group(2).strip()))

        opt_texts = [t for _, t in options]
        opt_labels = [l for l, _ in options]

        questions.append({
            'type': 'choice',
            'question': question,
            'options': opt_texts,
            'option_labels': opt_labels,
            'answer': answer if answer else '',
            'explanation': '',
        })
    return questions


def parse_truefalse_questions(lines, start_idx, end_idx):
    """解析判断题"""
    questions = []

    # 预处理：合并跨行括号（复习资料的格式问题）
    merged_lines = []
    i = start_idx
    while i < end_idx:
        line = lines[i].rstrip('\n')
        stripped = line.strip()
        # 跨行括号：一行是 "(   √" 下一行是 ")1."
        if re.match(r'^\(\s*[√×Xx]?\s*$', stripped) and i + 1 < end_idx:
            next_line = lines[i + 1].strip()
            if re.match(r'^\)?\d{1,3}[、\.]', next_line):
                merged_lines.append(line + ' ' + next_line)
                i += 2
                continue
            # 下一行以 ) 开始
            if next_line.startswith(')'):
                merged_lines.append(line + next_line)
                i += 2
                continue
        merged_lines.append(line)
        i += 1

    full_text = '\n'.join(merged_lines)

    # 拆分题目：每个题目以 (答案)编号 开始
    # 模式: 可选的 ( 答案 ) 然后是数字编号
    pattern = r'(?:\(\s*([√×Xx]?)\s*\))\s*(\d{1,3})[、\.，,]\s*'
    parts = list(re.finditer(pattern, full_text))

    for j, match in enumerate(parts):
        answer_raw = match.group(1)
        qnum = match.group(2)
        start = match.end()
        end = parts[j + 1].start() if j + 1 < len(parts) else len(full_text)
        qtext = full_text[start:end].strip()
        # 清理
        qtext = re.sub(r'\s+', ' ', qtext).strip()

        # 标准化答案
        if answer_raw in ('X', 'x'):
            answer = '×'
        elif answer_raw == '√':
            answer = '√'
        elif not answer_raw:
            answer = ''
        else:
            answer = answer_raw

        questions.append({
            'type': 'truefalse',
            'question': qtext,
            'answer': answer,
            'explanation': '',
        })

    return questions


def parse_fill_questions(lines, start_idx, end_idx):
    """解析填空题"""
    questions = []
    combined_text = '\n'.join(lines[start_idx:end_idx])

    # 按编号分割
    # 支持: 01、  1、  1.
    pattern = r'(?:^|\n)(\d{1,3})[、\.]\s*'
    parts = list(re.finditer(pattern, combined_text))

    for j, match in enumerate(parts):
        qnum = match.group(1)
        start = match.end()
        end = parts[j + 1].start() if j + 1 < len(parts) else len(combined_text)
        qtext = combined_text[start:end].strip()

        # 提取答案：末尾括号中的内容
        # 支持 (答案) 和 （答案）
        answer = ''
        ans_m = re.search(r'[（(]([^）)]+)[）)]\s*$', qtext)
        if ans_m:
            answer = ans_m.group(1).strip()
            qtext = qtext[:ans_m.start()].strip()

        # 清理文本
        qtext = re.sub(r'\s+', ' ', qtext).strip()

        # 标准化空白标记为 ______
        qtext = re.sub(r'_+', '______', qtext)
        # 如果没有任何空白标记，在合适位置加
        if '______' not in qtext and '___' not in qtext:
            qtext += ' ______'

        questions.append({
            'type': 'fill',
            'question': qtext,
            'answer': answer,
            'explanation': '',
        })

    return questions


def parse_shortanswer_questions(lines, start_idx, end_idx):
    """解析简答题"""
    questions = []
    combined_text = '\n'.join(lines[start_idx:end_idx])

    # 按 "答：" 分割
    # 先按编号找题目
    pattern = r'(?:^|\n)\s*(\d{1,3})[、\.]\s*'
    parts = list(re.finditer(pattern, combined_text))

    for j, match in enumerate(parts):
        qnum = match.group(1)
        start = match.end()
        end = parts[j + 1].start() if j + 1 < len(parts) else len(combined_text)
        block = combined_text[start:end].strip()

        # 分离题目和答案
        question = block
        explanation = ''

        # 找 "答：" 标记
        ans_idx = block.find('答：')
        if ans_idx >= 0:
            question = block[:ans_idx].strip()
            explanation = block[ans_idx + 2:].strip()

        # 清理OCR杂项
        question = re.sub(r'^[\w\d\s]{1,3}(?=[^\w\d\s]{2})', '', question).strip()

        # 清理文本
        question = re.sub(r'\s+', ' ', question).strip()
        explanation = re.sub(r'\s+', ' ', explanation).strip()

        questions.append({
            'type': 'shortanswer',
            'question': question,
            'answer': '',
            'explanation': explanation,
        })

    return questions


def parse_calculation_questions(lines, start_idx, end_idx):
    """解析计算题"""
    questions = []
    combined_text = '\n'.join(lines[start_idx:end_idx])

    pattern = r'(?:^|\n)\s*(\d{1,3})[、\.]\s*'
    parts = list(re.finditer(pattern, combined_text))

    for j, match in enumerate(parts):
        qnum = match.group(1)
        start = match.end()
        end = parts[j + 1].start() if j + 1 < len(parts) else len(combined_text)
        block = combined_text[start:end].strip()

        question = block
        explanation = ''

        # 找 "解：" 标记
        jie_idx = block.find('解：')
        if jie_idx >= 0:
            question = block[:jie_idx].strip()
            explanation = block[jie_idx:].strip()

        # 清理
        question = re.sub(r'\s+', ' ', question).strip()
        explanation = re.sub(r'\s+', ' ', explanation).strip()

        questions.append({
            'type': 'calculation',
            'question': question,
            'answer': '',
            'explanation': explanation,
        })

    return questions


def parse_drawing_questions(lines, start_idx, end_idx):
    """解析作图题"""
    questions = []
    combined_text = ' '.join(lines[start_idx:end_idx])

    pattern = r'(\d{1,3})[、\.]\s*'
    parts = list(re.finditer(pattern, combined_text))

    for j, match in enumerate(parts):
        start = match.end()
        end = parts[j + 1].start() if j + 1 < len(parts) else len(combined_text)
        qtext = combined_text[start:end].strip()
        qtext = re.sub(r'\s+', ' ', qtext).strip()

        questions.append({
            'type': 'drawing',
            'question': qtext,
            'answer': '',
            'explanation': '请根据题目要求作图',
        })

    return questions


def parse_file(filepath):
    """解析单个 .md 文件，返回题目列表"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    questions = []

    # 检测章节边界
    sections = []
    for i, line in enumerate(lines):
        result = detect_section(line)
        if result:
            sections.append((i, result[0], result[1]))

    # 如果没检测到章节，整个文件作为一种题型
    if not sections:
        # fallback: 尝试按内容模式检测
        # 有大量 (A-D) 模式 → 选择题
        abcd_count = len(re.findall(r'\(\s*[A-D]\s*\)', content[:2000]))
        tf_count = len(re.findall(r'\(\s*[√×Xx]\s*\)', content[:2000]))
        if abcd_count > tf_count:
            questions = parse_choice_questions(lines, 0, len(lines))
        elif tf_count > 0:
            questions = parse_truefalse_questions(lines, 0, len(lines))
        return questions

    # 按章节解析
    for idx, (line_num, stype, title) in enumerate(sections):
        end_line = sections[idx + 1][0] if idx + 1 < len(sections) else len(lines)

        if stype == 'choice':
            qs = parse_choice_questions(lines, line_num + 1, end_line)
        elif stype == 'truefalse':
            qs = parse_truefalse_questions(lines, line_num + 1, end_line)
        elif stype == 'fill':
            qs = parse_fill_questions(lines, line_num + 1, end_line)
        elif stype == 'shortanswer':
            qs = parse_shortanswer_questions(lines, line_num + 1, end_line)
        elif stype == 'calculation':
            qs = parse_calculation_questions(lines, line_num + 1, end_line)
        elif stype == 'drawing':
            qs = parse_drawing_questions(lines, line_num + 1, end_line)
        else:
            qs = []

        for q in qs:
            q['section'] = title
        questions.extend(qs)

    return questions


def main():
    all_questions = []
    stats = {}

    for filename, topic in FILE_TOPIC.items():
        filepath = BASE_DIR / filename
        if not filepath.exists():
            print(f"[WARN] File not found: {filepath}")
            continue

        print(f"[PARSE] {filename}")
        questions = parse_file(str(filepath))

        for q in questions:
            q['topic'] = topic

        # 分配全局 ID
        for q in questions:
            q['id'] = len(all_questions) + 1
            all_questions.append(q)

        # 统计
        type_counts = {}
        for q in questions:
            t = q['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        stats[filename] = type_counts
        print(f"   -> Extracted {len(questions)} questions: {type_counts}")

    # Dedup by first 40 chars of question text
    print(f"\n[STAT] Before dedup: {len(all_questions)}")
    seen = set()
    unique = []
    dup_count = 0
    for q in all_questions:
        key = q['question'][:40].strip()
        if key in seen:
            dup_count += 1
            continue
        seen.add(key)
        q['id'] = len(unique) + 1
        unique.append(q)
    print(f"   After dedup: {len(unique)} questions (removed {dup_count} duplicates)")

    # Output JSON
    json_path = BASE_DIR / 'questions.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    # Output JS (for offline HTML loading)
    js_path = BASE_DIR / 'questions.js'
    js_content = 'window.ALL_QUESTIONS = ' + json.dumps(unique, ensure_ascii=False, indent=2) + ';'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"\n[DONE] Generated: {json_path}")
    print(f"        Generated: {js_path}")
    print(f"   Total: {len(unique)} questions")

    # Stats by type
    type_stats = {}
    topic_stats = {}
    for q in unique:
        t = q['type']
        type_stats[t] = type_stats.get(t, 0) + 1
        tp = q['topic']
        topic_stats[tp] = topic_stats.get(tp, 0) + 1
    print(f"   By type: {type_stats}")
    print(f"   By topic: {topic_stats}")

    # Answer coverage
    for t in ['choice', 'truefalse', 'fill']:
        qs = [q for q in unique if q['type'] == t]
        with_ans = [q for q in qs if q.get('answer')]
        print(f"   {t} answer coverage: {len(with_ans)}/{len(qs)}")


if __name__ == '__main__':
    main()
