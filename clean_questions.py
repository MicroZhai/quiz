"""
Clean question text in questions.json:
1. 选择题: strip inline options (A、... B、...) from question text
2. 填空题: strip inline answers in parentheses from question text
3. 判断题: remove (√)/(×) markers from question text

After cleaning, regenerates questions.js.
"""
import json
import re
import os

def clean_choice_question(q):
    """Strip inline options from choice question text."""
    txt = q['question']
    options = q.get('options', [])

    # Try multiple patterns to find where options start
    # Pattern: whitespace + letter A-D + separator (、or . or space) + content
    # The options section always starts at the FIRST option marker that is followed
    # by at least one more option marker

    # Find all candidate option-marker positions
    # Matches: " A、xxx", "A. xxx", " A降低", "A.温度", etc.
    opt_marker = re.compile(r'(?:(?<=\s)|(?<=）)|(?<=。)|(?<=…)|(?<=\.))\s*([A-D])([、，.\s])(\s*)')

    matches = list(opt_marker.finditer(txt))

    if len(matches) < 2:
        # Need at least 2 option markers to identify an options section
        # Try more aggressive pattern: A-D followed directly by Chinese/letter
        opt_marker2 = re.compile(r'(?:(?<=\s)|(?<=）)|(?<=。)|(?<=…))\s*([A-D])([、，.]|\s|(?=[一-鿿A-Za-z]))')
        matches = list(opt_marker2.finditer(txt))

    if len(matches) >= 2:
        # Verify options: check that the text after the first marker
        # contains all or most of the actual options
        first_pos = matches[0].start()
        tail = txt[first_pos:]

        # Count option markers in tail
        tail_markers = len(list(opt_marker.finditer(tail)))

        if tail_markers >= min(2, len(options) if options else 2):
            txt = txt[:first_pos].rstrip()

    # Also handle case like "#11: ...（ ）A.温度 B.化学成分..."
    # Where option starts directly after ） without space
    if len(matches) < 2:
        m = re.search(r'(?:）|。)\s*([A-D])[、，.]', txt)
        if m:
            pos = m.start() + 1  # After ）or 。
            tail = txt[pos:].lstrip()
            tail_markers = list(opt_marker.finditer(tail))
            if tail_markers >= 2:
                # Found: everything after ）is options
                txt = txt[:pos]

    # For questions where options array is empty, try to extract options
    if not options:
        extracted = extract_options_from_text(q['question'], q.get('answer', ''))
        if extracted:
            q['options'] = extracted['options']
            q['option_labels'] = extracted['labels']

    q['question'] = txt.strip()
    return q

def extract_options_from_text(txt, answer):
    """Extract options from question text for questions missing options array."""
    # Find the options section
    m = re.search(r'(?:^|\s)([A-D])[、，.\s]+(.+?)(?:\s+[A-D][、，.\s]|\s*$)', txt)
    if not m:
        return None

    # Find all option-label + content pairs
    opt_pattern = re.compile(r'\s*([A-D])[、，.\s]+(.+?)(?=\s+[A-D][、，.\s]|\s*$)', re.DOTALL)
    matches = list(opt_pattern.finditer(txt))

    if len(matches) >= 2:
        options = []
        labels = []
        for m in matches:
            labels.append(m.group(1))
            options.append(m.group(2).strip().rstrip('.'))

        # Detect labels: A,B,C,D or A-Z
        if labels and labels[0] in 'ABCDEFGH':
            return {'options': options, 'labels': labels}

    return None

def clean_fill_question(q):
    """Strip inline answers in parentheses from fill question text."""
    txt = q['question']
    answer = q.get('answer', '')

    # Find Chinese parenthesized content that looks like an answer
    # Pattern: （...） containing Chinese, commas, or numbers
    # BUT preserve （ ） (empty brackets which are the quiz blank)
    # and preserve （X） where X is a single letter/number (might be formatting)

    def should_remove(match):
        content = match.group(1)
        # Don't remove empty brackets
        if not content.strip():
            return False
        # Don't remove single-character markers
        if len(content.strip()) <= 1:
            return False
        # Remove if content looks like an answer (has Chinese, numbers, commas)
        # These are typically things like （变形，弹性变形，塑性变形）
        return True

    # Remove inline answers: （...content...）
    txt = re.sub(r'（([^）]{2,60})）', lambda m: '' if should_remove(m) else m.group(0), txt)

    # Also handle half-width parens used for answers
    # e.g., (变形，弹性变形) but not (A) or ( )
    # Be more conservative here
    txt = re.sub(r'\(([^\)]{3,60})\)', lambda m: '' if re.search(r'[一-鿿]', m.group(1)) else m.group(0), txt)

    # Clean up double spaces
    txt = re.sub(r'  +', ' ', txt)

    # Clean up spaces before Chinese punctuation
    txt = re.sub(r'\s+（', '（', txt)
    txt = re.sub(r'\s+。', '。', txt)

    q['question'] = txt.strip()
    return q

def clean_truefalse_question(q):
    """Remove answer markers from truefalse question text."""
    txt = q['question']

    # Remove (√) and (×) markers from question text
    txt = re.sub(r'[（(]\s*[√×✓✗]\s*[）)]', '', txt)

    # Remove standalone √ × markers at start
    txt = re.sub(r'^[√×✓✗]\s*', '', txt)

    # For merged questions (multiple Qs in one), try to identify
    # Pattern: )数字、 or ）数字、
    # These are cases where questions got concatenated
    # We keep them as-is since splitting is risky without source data

    q['question'] = txt.strip()
    return q

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base, 'questions.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {'choice_cleaned': 0, 'fill_cleaned': 0, 'tf_cleaned': 0, 'options_extracted': 0}

    for q in data:
        orig = q['question']

        if q['type'] == 'choice':
            old_opts = bool(q.get('options'))
            q = clean_choice_question(q)
            if q['question'] != orig:
                stats['choice_cleaned'] += 1
            if not old_opts and q.get('options'):
                stats['options_extracted'] += 1

        elif q['type'] == 'fill':
            q = clean_fill_question(q)
            if q['question'] != orig:
                stats['fill_cleaned'] += 1

        elif q['type'] == 'truefalse':
            q = clean_truefalse_question(q)
            if q['question'] != orig:
                stats['tf_cleaned'] += 1

    # Save cleaned JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Cleaned questions.json:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Show some cleaned examples
    print("\n--- 选择题清理示例 ---")
    count = 0
    for q in data:
        if q['type'] == 'choice' and count < 3:
            print(f"#{q['id']}: {q['question'][:100]}...")
            if q.get('options'):
                print(f"  Options: {q['options']}")
            count += 1

    # Show fill cleaning examples
    print("\n--- 填空题清理示例 ---")
    count = 0
    for q in data:
        if q['type'] == 'fill' and count < 3:
            print(f"#{q['id']}: {q['question'][:120]}...")
            print(f"  Answer: {q.get('answer', '')[:80]}")
            count += 1

    # Generate questions.js
    js_path = os.path.join(base, 'questions.js')
    js_content = 'window.ALL_QUESTIONS = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"\nRegenerated questions.js ({len(data)} questions)")

if __name__ == '__main__':
    main()
