"""
apply_explanations.py — 将逐题解析批量写入 questions.json

用法：
  1. 编辑同目录下的 explanations_data.json，按 {id: "解析文本"} 格式添加
  2. 运行: python apply_explanations.py
  3. 自动更新 questions.json → 运行 build_quiz.py → 运行 json_to_md.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # 1. 读取数据
    questions_path = os.path.join(BASE, 'questions.json')
    exp_path = os.path.join(BASE, 'explanations_data.json')

    if not os.path.exists(exp_path):
        print("[ERROR] explanations_data.json not found")
        sys.exit(1)

    questions = load_json(questions_path)
    explanations = load_json(exp_path)

    # 2. 建立 id → index 映射
    id_to_idx = {}
    for i, q in enumerate(questions):
        qid = str(q.get('id', ''))
        id_to_idx[qid] = i

    # 3. 写入解析
    updated = 0
    overwritten = 0
    skipped = []
    for qid_str, exp_text in explanations.items():
        if qid_str in id_to_idx:
            idx = id_to_idx[qid_str]
            old = questions[idx].get('explanation', '')
            questions[idx]['explanation'] = exp_text
            if old and old.strip() and old != exp_text:
                overwritten += 1
            updated += 1
        else:
            skipped.append(qid_str)

    # 4. 保存
    save_json(questions_path, questions)
    print(f"[OK] Wrote {updated} explanations to questions.json")
    if overwritten:
        print(f"     ({overwritten} overwritten)")

    if skipped:
        print(f"[WARN] Skipped {len(skipped)} unknown IDs: {skipped}")

    # 5. 统计
    total = len(questions)
    has_exp = sum(1 for q in questions if q.get('explanation', '').strip())
    empty = total - has_exp
    print(f"[STATS] {total} total, {has_exp} with explanation, {empty} remaining ({empty/total*100:.1f}%)")

    # 6. 运行构建
    print("\n[BUILD] Running build_quiz.py ...")
    os.chdir(BASE)
    ret = os.system('python build_quiz.py')
    if ret != 0:
        print("[WARN] build_quiz.py returned non-zero")

    print("[BUILD] Running json_to_md.py ...")
    ret = os.system('python json_to_md.py')
    if ret != 0:
        print("[WARN] json_to_md.py returned non-zero")

    print("\n[DONE] All complete!")

if __name__ == '__main__':
    main()
