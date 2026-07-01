"""
Fix broken options arrays in questions.json.
Handles: merged options, missing options, out-of-order labels.
"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, 'questions.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(os.path.join(BASE, '复习题整合.md'), 'r', encoding='utf-8') as f:
    md_text = f.read()

def extract_choice_options_from_text(txt):
    """
    Given a question text that may contain inline options like
    '...（ ）。 A、opt1 B、opt2 C、opt3'
    extract the options and their labels.
    Returns (options_list, labels_list) or (None, None)
    """
    # Find where options start: after ）or 。, followed by label pattern
    # Try to find the start of options section
    m = re.search(r'(?:）|。)\s*([A-D])[、，.]', txt)
    if not m:
        m = re.search(r'(?:）|。)\s*([A-D])\s', txt)  # e.g. "） A降低"
    if not m:
        # Try without ）prefix: just find the first option marker
        m = re.search(r'\s+([A-D])[、，.]\s*\S', txt)

    if not m:
        return None, None

    pos = m.start()
    # Find the start of the option text (skip the ）or 。)
    # Backtrack to find the actual content boundary
    if txt[pos] in '））':
        pos += 1
    elif txt[pos] in '。':
        pos += 1
    pos = pos + m.group(0).index(m.group(1))

    opt_text = txt[pos:].strip()

    # Split at all [A-D][、，. ] boundaries
    # First, find all split positions
    parts = re.split(r'\s*(?=[A-D][、，.])\s*', opt_text)
    # Also handle: "A降低 B没变化" (no separator after letter)
    if len(parts) <= 1:
        parts = re.split(r'\s*(?=[A-D]\s)', opt_text)

    options = []
    labels = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m2 = re.match(r'([A-D])\s*[、，.]?\s*(.+)', part, re.DOTALL)
        if m2:
            labels.append(m2.group(1))
            opt = m2.group(2).strip()
            # Remove trailing numbers/junk
            opt = re.sub(r'\s+\d+\.?\s*$', '', opt)
            options.append(opt)

    if len(options) >= 2:
        return options, labels
    return None, None


def find_md_options(q_id, q_section):
    """Try to find a question's original options from the MD file."""
    # This is a fallback - search the MD for the question number and section
    # Not perfectly reliable due to duplicates
    return None, None


def reorder_options(options, labels, answer):
    """
    Reorder options to standard A,B,C,D... order.
    Returns (new_options, new_labels, new_answer)
    """
    if not labels:
        return options, labels, answer

    # Check if labels are already in order
    expected = [chr(65+i) for i in range(len(labels))]
    if labels == expected:
        return options, labels, answer

    # Reorder: sort by label
    pairs = sorted(zip(labels, options), key=lambda x: x[0])
    new_labels = [p[0] for p in pairs]
    new_options = [p[1] for p in pairs]

    # Remap answer: find which position the answer label moved to
    if answer and answer in labels:
        old_idx = labels.index(answer)
        old_content = options[old_idx]
        new_idx = new_options.index(old_content)
        new_answer = new_labels[new_idx]
    else:
        new_answer = answer

    return new_options, new_labels, new_answer


# Process all choice questions
fixed_count = 0
for q in data:
    if q['type'] != 'choice':
        continue

    txt = q['question']
    opts = q.get('options', [])
    labels = q.get('option_labels', [])
    ans = q.get('answer', '')

    # Step 1: Try to extract options from question text (if still has embedded)
    if not opts or any(re.search(r'[A-D][、，.]', o) for o in opts):
        new_opts, new_labels = extract_choice_options_from_text(txt)
        if new_opts:
            opts = new_opts
            labels = new_labels

    # Step 2: Split merged options (text containing embedded labels)
    new_opts = []
    for opt in (opts or []):
        # Split at embedded [A-D][、，.] positions
        sub_parts = re.split(r'(?=[A-D][、，.])', opt)
        for sp in sub_parts:
            sp = sp.strip()
            if not sp:
                continue
            # Strip leading label
            content = re.sub(r'^[A-D][、，.]\s*', '', sp).strip()
            if content:
                new_opts.append(content)

    if new_opts and (len(new_opts) != len(opts or []) or new_opts != opts):
        opts = new_opts
        # Rebuild labels
        labels = [chr(65+i) for i in range(len(opts))]

        # Remap answer if needed
        if ans and ans not in labels:
            # Try to find answer by index
            try:
                old_ans_idx = ord(ans) - 65
                if 0 <= old_ans_idx < len(opts):
                    ans = labels[old_ans_idx]
            except:
                pass

    # Step 3: Strip extracted option A from question text suffix
    # Some questions have option A's content appended to the question:
    # e.g. "...是（ ）。 A、2A70" where A's content follows the question
    m_a = re.search(r'(?:（\s*）|。)\s*(A)[、，.]\s*(.+?)$', txt)
    if m_a and opts and not any(lbl == 'A' for lbl in labels):
        opt_a_content = m_a.group(2).strip()
        opts.insert(0, opt_a_content)
        txt = txt[:m_a.start()].rstrip()
        if txt.endswith('（ ）'):
            pass  # keep the empty brackets
        elif not txt.endswith('）') and not txt.endswith('。'):
            txt = txt.rstrip() + '（ ）'
        q['question'] = txt

    # Step 4: Extract options from question text for questions with empty options
    if not opts:
        new_opts, new_labels = extract_choice_options_from_text(txt)
        if new_opts:
            opts = new_opts
            labels = new_labels
            # Also strip options from question text
            m = re.search(r'\s+([A-D])[、，.]\s*\S', txt)
            if m:
                tail = txt[m.start():]
                tail_markers = len(re.findall(r'\s+[A-D][、，.\s]', tail))
                if tail_markers >= 2:
                    txt = txt[:m.start()].rstrip()
                    q['question'] = txt

    # Step 5: ALWAYS rebuild labels to standard A,B,C,D...
    if opts:
        labels = [chr(65 + i) for i in range(len(opts))]

        # Remove duplicate options (keep first occurrence)
        seen = set()
        unique_opts = []
        for o in opts:
            if o not in seen:
                seen.add(o)
                unique_opts.append(o)
        if len(unique_opts) < len(opts):
            opts = unique_opts
            labels = [chr(65 + i) for i in range(len(opts))]

    # Step 6: Reorder to standard labels
    if opts and labels:
        opts, labels, ans = reorder_options(opts, labels, ans)

    if opts:
        q['options'] = opts
        q['option_labels'] = labels
        if ans:
            q['answer'] = ans
        fixed_count += 1

    # Step 7: Ensure question text doesn't have inline options
    m = re.search(r'\s+([A-D])[、，.]\s*\S', txt)
    if m:
        tail = txt[m.start():]
        tail_markers = len(re.findall(r'\s+[A-D][、，.\s]', tail))
        if tail_markers >= 2:
            txt = txt[:m.start()].rstrip()
            q['question'] = txt

print(f'Processed {fixed_count} choice questions')

# Final validation
issues = []
for q in data:
    if q['type'] != 'choice':
        continue
    opts = q.get('options', [])
    labels = q.get('option_labels', [])
    ans = q.get('answer', '')

    if not opts:
        issues.append(f'#{q["id"]}: EMPTY options, ans={ans}, q={q["question"][:60]}')
        continue

    # Check labels are A,B,C...
    expected = [chr(65+i) for i in range(len(opts))]
    if labels != expected:
        issues.append(f'#{q["id"]}: bad labels {labels} vs expected {expected}')

    # Check answer in labels
    if ans and ans not in labels:
        issues.append(f'#{q["id"]}: answer {ans} not in labels {labels}, opts={opts}')

    # Check for embedded labels in option text
    for i, opt in enumerate(opts):
        if re.search(r'[A-D][、，.]', opt):
            issues.append(f'#{q["id"]}: embedded label in opt[{i}]: "{opt[:60]}"')
            break

if issues:
    print(f'\n{len(issues)} remaining issues:')
    for iss in issues:
        print(f'  {iss}')
else:
    print('ALL CLEAN! ✅')

# Save
with open(os.path.join(BASE, 'questions.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Regenerate questions.js
js_path = os.path.join(BASE, 'questions.js')
js = 'window.ALL_QUESTIONS = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';'
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print(f'\nSaved questions.json + questions.js')
