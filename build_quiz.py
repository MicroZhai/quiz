"""
build_quiz.py — 幂等的构建脚本
================================
从 questions.json + knowledge_points.json 生成 questions.js
每次运行从零生成，永不会产生重复内容。

数据流：
  questions.json ─────────┐
  knowledge_points.json ──┤
                           ├──→ questions.js（含全部数据+辅助函数）
                           └──→ index.html（= quiz.html 的副本）

quiz.html 是静态文件，永不被本脚本修改。
"""
import json, shutil
from pathlib import Path

BASE = Path(__file__).parent

# ============================================================
# 1. 读取数据源
# ============================================================
with open(BASE / 'questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

with open(BASE / 'knowledge_points.json', 'r', encoding='utf-8') as f:
    kp_list = json.load(f)

with open(BASE / 'knowledge_system.json', 'r', encoding='utf-8') as f:
    ks_data = json.load(f)

# ============================================================
# 2. 构建 KP_MAP（按 key 索引的知识点字典）
# ============================================================
kp_map_entries = []
for kp in kp_list:
    kp_map_entries.append(f'KP_MAP["{kp["key"]}"] = {json.dumps(kp, ensure_ascii=False)};')

# ============================================================
# 3. 生成 questions.js
# ============================================================
js_lines = []
js_lines.append('// ====== 热处理考试题库（自动生成）======')
js_lines.append(f'// 总题数：{len(questions)}')
js_lines.append(f'// 生成时间：自动生成，源数据来自 questions.json')
js_lines.append('')

# --- 题库数据 ---
questions_json = json.dumps(questions, ensure_ascii=False)
js_lines.append(f'window.ALL_QUESTIONS = {questions_json};')
js_lines.append('')

# --- 知识点数据 ---
kp_json = json.dumps(kp_list, ensure_ascii=False, indent=2)
js_lines.append(f'const KNOWLEDGE_POINTS = {kp_json};')
js_lines.append('')

# --- 知识体系数据 ---
ks_json = json.dumps(ks_data, ensure_ascii=False, indent=2)
js_lines.append(f'window.KNOWLEDGE_SYSTEM = {ks_json};')
js_lines.append('')

# --- 知识点查找表 ---
js_lines.append('const KP_MAP = {};')
js_lines.extend(kp_map_entries)
js_lines.append('')

# --- 工具函数 ---
js_lines.append('''function getKPInfo(question) {
  const key = question.knowledge_point_key || '';
  if (KP_MAP[key]) return KP_MAP[key];
  // Try matching by name
  const name = question.knowledge_point || '';
  for (const kp of KNOWLEDGE_POINTS) {
    if (kp.name === name) return kp;
  }
  return null;
}''')

js_content = '\n'.join(js_lines)

with open(BASE / 'questions.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f'[OK] Generated questions.js ({len(js_content):,} chars, {len(questions)} questions, {len(kp_list)} KPs, {len(ks_data.get("parts", []))} parts)')

# ============================================================
# 4. 复制 quiz.html -> index.html
# ============================================================
shutil.copy2(BASE / 'quiz.html', BASE / 'index.html')
print(f'[OK] Copied quiz.html -> index.html')

print(f'\n[DONE] Build complete. Open quiz.html in browser to verify.')
