"""
build_quiz.py — 幂等题库构建脚本
================================
从 questions.json + knowledge_points.json + knowledge_system.json 生成 questions.js。
quiz.html 为静态应用文件；index.html 为 GitHub Pages 的轻量跳转入口，构建脚本不再复制页面。
"""
import json
from pathlib import Path

BASE = Path(__file__).parent

with open(BASE / 'questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)
with open(BASE / 'knowledge_points.json', 'r', encoding='utf-8') as f:
    kp_list = json.load(f)
with open(BASE / 'knowledge_system.json', 'r', encoding='utf-8') as f:
    ks_data = json.load(f)

kp_map_entries = [
    f'KP_MAP["{kp["key"]}"] = {json.dumps(kp, ensure_ascii=False)};'
    for kp in kp_list
]

js_lines = [
    '// ====== 热处理考试题库（自动生成）======',
    f'// 总题数：{len(questions)}',
    '// 生成时间：自动生成，源数据来自 questions.json',
    '',
    f'window.ALL_QUESTIONS = {json.dumps(questions, ensure_ascii=False)};',
    '',
    f'const KNOWLEDGE_POINTS = {json.dumps(kp_list, ensure_ascii=False, indent=2)};',
    '',
    f'window.KNOWLEDGE_SYSTEM = {json.dumps(ks_data, ensure_ascii=False, indent=2)};',
    '',
    'const KP_MAP = {};',
    *kp_map_entries,
    '',
    '''function getKPInfo(question) {
  const key = question.knowledge_point_key || '';
  if (KP_MAP[key]) return KP_MAP[key];
  const name = question.knowledge_point || '';
  for (const kp of KNOWLEDGE_POINTS) {
    if (kp.name === name) return kp;
  }
  return null;
}''',
]

js_content = '\n'.join(js_lines)
with open(BASE / 'questions.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f'[OK] Generated questions.js ({len(js_content):,} chars, {len(questions)} questions, {len(kp_list)} KPs, {len(ks_data.get("parts", []))} parts)')
print('[DONE] Build complete. Open quiz.html to verify.')
