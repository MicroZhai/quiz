"""
Build enhanced quiz.html with:
1. Top tab navigation: 刷题 / 复习 / 学习建议
2. Review mode with knowledge point grouping
3. Study guide page
4. Knowledge point explanations in quiz feedback
5. Embedded knowledge_points.json data
"""
import json
from pathlib import Path

BASE = Path(r'c:\Users\Zhai\Desktop\热处理复习资料')

# Read source files
with open(BASE / 'quiz.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(BASE / 'knowledge_points.json', 'r', encoding='utf-8') as f:
    kp_data = json.load(f)

# Build knowledge points JS object
kp_js = 'const KNOWLEDGE_POINTS = ' + json.dumps(kp_data, ensure_ascii=False, indent=2) + ';'

# Build knowledge point lookup map JS
kp_lookup_lines = ['const KP_MAP = {};']
for kp in kp_data:
    kp_lookup_lines.append(f'KP_MAP["{kp["key"]}"] = {json.dumps(kp, ensure_ascii=False)};')
kp_lookup_js = '\n'.join(kp_lookup_lines)

kp_script = f'''
<!-- ===== Knowledge Points Data ===== -->
<script>
{kp_js}
{kp_lookup_js}

function getKPInfo(question) {{
  const key = question.knowledge_point_key || '';
  if (KP_MAP[key]) return KP_MAP[key];
  // Try matching by name
  const name = question.knowledge_point || '';
  for (const kp of KNOWLEDGE_POINTS) {{
    if (kp.name === name) return kp;
  }}
  return null;
}}
</script>
'''

# Insert knowledge points script after questions.js
html = html.replace(
    '<script src="questions.js"></script>',
    '<script src="questions.js"></script>\n' + kp_script
)

# ====== NEW CSS ======
new_css = '''
/* ===== Top Tab Bar ===== */
.tab-bar { display:flex; background:#fff; border-radius:12px; margin-bottom:16px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.tab-bar .tab-item { flex:1; text-align:center; padding:14px 8px; cursor:pointer; font-size:15px; font-weight:600; color:#666; transition:all .2s; border-bottom:3px solid transparent; }
.tab-bar .tab-item:hover { color:#1a73e8; background:#f8f9ff; }
.tab-bar .tab-item.active { color:#1a73e8; border-bottom-color:#1a73e8; background:#e8f0fe; }

/* ===== Review Mode ===== */
.review-layout { display:flex; gap:12px; }
.review-sidebar { width:180px; flex-shrink:0; }
.review-sidebar .kp-nav { background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.08); position:sticky; top:8px; max-height:calc(100vh - 40px); overflow-y:auto; }
.review-sidebar .kp-nav-item { display:block; width:100%; text-align:left; padding:10px 14px; border:none; background:transparent; cursor:pointer; font-size:13px; color:#555; border-left:3px solid transparent; transition:all .15s; }
.review-sidebar .kp-nav-item:hover { background:#f8f9ff; color:#1a73e8; }
.review-sidebar .kp-nav-item.active { background:#e8f0fe; color:#1a73e8; border-left-color:#1a73e8; font-weight:600; }
.review-sidebar .kp-nav-item .kp-count { font-size:11px; color:#999; float:right; }
.review-main { flex:1; min-width:0; }
.review-kp-section { margin-bottom:20px; }
.review-kp-header { background:linear-gradient(135deg,#1a73e8,#1557b0); color:#fff; padding:14px 18px; border-radius:10px 10px 0 0; cursor:pointer; display:flex; justify-content:space-between; align-items:center; }
.review-kp-header h3 { font-size:16px; margin:0; }
.review-kp-explanation { background:#e8f0fe; padding:14px 18px; font-size:14px; line-height:1.8; color:#333; border-left:4px solid #1a73e8; display:none; }
.review-kp-explanation.show { display:block; }
.review-kp-explanation .kp-section-label { font-size:12px; color:#1a73e8; font-weight:600; margin-top:6px; }
.review-qcard { background:#fff; padding:14px 18px; border-bottom:1px solid #f0f0f0; transition:background .15s; }
.review-qcard:hover { background:#fafbff; }
.review-qcard:last-child { border-radius:0 0 10px 10px; }
.review-qcard .rq-meta { font-size:11px; color:#999; margin-bottom:4px; }
.review-qcard .rq-text { font-size:15px; line-height:1.7; }
.review-qcard .rq-answer { display:inline-block; background:#e6f4ea; color:#0d904f; padding:2px 10px; border-radius:4px; font-weight:700; font-size:14px; margin-left:6px; }
.review-qcard .rq-answer.wrong-ans { background:#fce8e6; color:#d93025; }
.review-qcard .rq-options { font-size:13px; color:#666; margin-top:4px; padding-left:8px; border-left:2px solid #e0e0e0; }
.review-qcard .rq-explanation { font-size:13px; color:#666; margin-top:6px; padding:8px 12px; background:#f8f9fa; border-radius:6px; line-height:1.6; }

/* ===== Study Guide ===== */
.guide-section { background:#fff; border-radius:10px; padding:18px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.guide-section h3 { margin-bottom:8px; font-size:17px; }
.guide-section p, .guide-section li { font-size:14px; line-height:1.8; color:#555; }
.guide-section ol, .guide-section ul { padding-left:20px; }
.guide-highlight { background:linear-gradient(135deg,#fff3e0,#ffe0b2); padding:14px 18px; border-radius:8px; border-left:4px solid #e65100; margin:10px 0; }
.guide-highlight.green { background:linear-gradient(135deg,#e8f5e9,#c8e6c9); border-left-color:#0d904f; }

/* ===== KP Explanation in Quiz ===== */
.kp-hint { font-size:13px; color:#1a73e8; margin-top:8px; padding:10px 14px; background:#e8f0fe; border-radius:8px; line-height:1.6; cursor:pointer; }
.kp-hint strong { cursor:pointer; }
.kp-hint .kp-detail { display:none; margin-top:6px; color:#333; font-weight:normal; }
.kp-hint .kp-detail.show { display:block; }

/* Mobile responsive */
@media (max-width:640px) {
  .review-layout { flex-direction:column; }
  .review-sidebar { width:100%; }
  .review-sidebar .kp-nav { display:flex; flex-wrap:nowrap; overflow-x:auto; max-height:none; position:static; gap:2px; padding:6px; }
  .review-sidebar .kp-nav-item { flex-shrink:0; white-space:nowrap; border-left:none; border-bottom:2px solid transparent; padding:8px 12px; font-size:12px; }
  .review-sidebar .kp-nav-item.active { border-left:none; border-bottom-color:#1a73e8; }
  .tab-bar .tab-item { font-size:13px; padding:12px 6px; }
}
'''

# Insert new CSS before </style>
html = html.replace('</style>', new_css + '\n</style>')

# ====== MODIFY RENDER FUNCTION ======
# Add new screen modes
old_render = '''function render() {
  const app = document.getElementById('app');
  if (screen === 'home') app.innerHTML = renderHome();
  else if (screen === 'quiz') app.innerHTML = renderQuiz();
  else if (screen === 'mistakes') app.innerHTML = renderMistakes();
  else if (screen === 'exam') app.innerHTML = renderExamPaper();
  bindEvents();
}'''

new_render = '''function render() {
  const app = document.getElementById('app');
  if (screen === 'home') app.innerHTML = renderHome();
  else if (screen === 'quiz') app.innerHTML = renderQuiz();
  else if (screen === 'mistakes') app.innerHTML = renderMistakes();
  else if (screen === 'exam') app.innerHTML = renderExamPaper();
  else if (screen === 'review') app.innerHTML = renderReview();
  else if (screen === 'studyguide') app.innerHTML = renderStudyGuide();
  bindEvents();
}'''

html = html.replace(old_render, new_render)

# ====== ADD TOP TAB BAR TO renderHome() ======
# Insert tab bar right after the header div in renderHome
old_header_end = '''<p>题库 ${totalQ} 题 | 已做 ${totalDone} 题 | 正确率 ${rate}%</p>
    </div>

    <div class="stats">'''

new_header_end = '''<p>题库 ${totalQ} 题 | 已做 ${totalDone} 题 | 正确率 ${rate}%</p>
    </div>

    <div class="tab-bar">
      <div class="tab-item active" data-tab="home">🧪 刷题</div>
      <div class="tab-item" data-tab="review">📖 复习资料</div>
      <div class="tab-item" data-tab="studyguide">📋 学习建议</div>
    </div>

    <div class="stats">'''

html = html.replace(old_header_end, new_header_end)

# ====== ADD REVIEW AND STUDYGUIDE RENDER FUNCTIONS ======
# Insert before the "// ========== EVENT BINDING ==========" comment
new_functions = '''
// ========== REVIEW MODE ==========
let reviewActiveKP = null;

function renderReview() {
  // Group questions by knowledge point
  const groups = {};
  QUESTIONS.forEach(q => {
    const kp = q.knowledge_point || '综合/未分类';
    if (!groups[kp]) groups[kp] = [];
    groups[kp].push(q);
  });

  // Sort groups: most questions first
  const sortedKP = Object.entries(groups).sort((a, b) => b[1].length - a[1].length);

  // Build sidebar
  const sidebarHtml = sortedKP.map(([name, qs], i) => {
    const activeCls = (reviewActiveKP === name || (reviewActiveKP === null && i === 0)) ? ' active' : '';
    return `<button class="kp-nav-item${activeCls}" data-kp="${escapeHtml(name)}">
      ${name} <span class="kp-count">${qs.length}</span>
    </button>`;
  }).join('');

  // Build main content - show active KP or first
  const activeName = reviewActiveKP || (sortedKP.length > 0 ? sortedKP[0][0] : '');
  const activeQs = groups[activeName] || [];

  // Find KP info
  let kpInfo = null;
  for (const kp of KNOWLEDGE_POINTS) {
    if (kp.name === activeName) { kpInfo = kp; break; }
  }

  let mainHtml = '';
  if (kpInfo) {
    mainHtml += `
    <div class="review-kp-section">
      <div class="review-kp-header" id="kpHeader">
        <h3>📌 ${kpInfo.name} (${activeQs.length}题)</h3>
        <span style="font-size:12px;opacity:0.8">点击展开解析 ▼</span>
      </div>
      <div class="review-kp-explanation" id="kpExplanation">
        <div style="font-weight:600;color:#1a73e8;margin-bottom:4px">📖 知识点解析</div>
        <div>${kpInfo.explanation}</div>
        ${kpInfo.key_concepts ? `<div class="kp-section-label">🔑 核心概念：${kpInfo.key_concepts.join('、')}</div>` : ''}
        ${kpInfo.exam_focus ? `<div class="kp-section-label">⚠️ 考试重点：${kpInfo.exam_focus}</div>` : ''}
      </div>
      ${activeQs.map(q => renderReviewQuestion(q)).join('')}
    </div>`;
  } else {
    mainHtml = `
    <div class="review-kp-section">
      <div class="review-kp-header">
        <h3>📌 ${activeName} (${activeQs.length}题)</h3>
      </div>
      ${activeQs.map(q => renderReviewQuestion(q)).join('')}
    </div>`;
  }

  return `
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
      <button class="btn btn-sm btn-outline" data-action="back">← 返回</button>
      <span style="font-size:14px;color:#666">📖 复习资料 · 按知识点分组</span>
    </div>
    <div class="tab-bar">
      <div class="tab-item" data-tab="home">🧪 刷题</div>
      <div class="tab-item active" data-tab="review">📖 复习资料</div>
      <div class="tab-item" data-tab="studyguide">📋 学习建议</div>
    </div>
    <div class="review-layout">
      <div class="review-sidebar">
        <div class="kp-nav">${sidebarHtml}</div>
      </div>
      <div class="review-main" id="reviewMain">
        ${mainHtml}
      </div>
    </div>
  `;
}

function renderReviewQuestion(q) {
  // Clean question text
  let dq = q.question;
  const optM = dq.match(/\s{2,}[A-D][、\.]/);
  if (optM && q.options && q.options.length > 0) {
    dq = dq.substring(0, optM.index).trim();
  }

  let answerHtml = '';
  let optionsHtml = '';

  if (q.type === 'choice') {
    answerHtml = `<span class="rq-answer">${q.answer || '?'}</span>`;
    if (q.options && q.options.length > 0) {
      optionsHtml = `<div class="rq-options">${q.options.map((o, i) => {
        const label = q.option_labels && q.option_labels[i] ? q.option_labels[i] : String.fromCharCode(65+i);
        const isCorrect = label === q.answer;
        return `<span style="${isCorrect ? 'color:#0d904f;font-weight:700' : ''}">${label}. ${o}</span>`;
      }).join(' &nbsp;|&nbsp; ')}</div>`;
    }
  } else if (q.type === 'truefalse') {
    const isCorrect = q.answer === '√';
    answerHtml = isCorrect ? '<span class="rq-answer">✓ 正确</span>' : '<span class="rq-answer wrong-ans">✗ 错误</span>';
  } else if (q.type === 'fill') {
    answerHtml = q.answer ? `<span class="rq-answer">${escapeHtml(q.answer)}</span>` : '<span class="rq-answer" style="background:#fff3e0;color:#e65100">答案缺失</span>';
  }

  // Explanation (for shortanswer/calculation)
  let explanationHtml = '';
  if (q.explanation) {
    explanationHtml = `<div class="rq-explanation"><strong>📝 解析/答案：</strong><br>${q.explanation.replace(/\\n/g, '<br>')}</div>`;
  }

  const typeBadge = getTypeName(q.type);

  return `
    <div class="review-qcard">
      <div class="rq-meta">[${typeBadge}] · ${q.topic || ''} ${answerHtml}</div>
      <div class="rq-text">${dq}</div>
      ${optionsHtml}
      ${explanationHtml}
    </div>
  `;
}

// ========== STUDY GUIDE ==========
function renderStudyGuide() {
  // Count questions per topic
  const topicCounts = {};
  const typeCounts = {};
  QUESTIONS.forEach(q => {
    topicCounts[q.topic] = (topicCounts[q.topic] || 0) + 1;
    typeCounts[q.type] = (typeCounts[q.type] || 0) + 1;
  });

  // Count per knowledge point
  const kpCounts = {};
  QUESTIONS.forEach(q => {
    const kp = q.knowledge_point || '综合/未分类';
    kpCounts[kp] = (kpCounts[kp] || 0) + 1;
  });
  const sortedKPs = Object.entries(kpCounts).sort((a, b) => b[1] - a[1]);

  // Weak areas from mistakes
  const mistakeKP = {};
  Object.keys(state.mistakes).forEach(id => {
    const q = QUESTIONS.find(qq => qq.id === parseInt(id));
    if (q) {
      const kp = q.knowledge_point || '综合/未分类';
      mistakeKP[kp] = (mistakeKP[kp] || 0) + 1;
    }
  });
  const sortedMistakeKP = Object.entries(mistakeKP).sort((a, b) => b[1] - a[1]);

  return `
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
      <button class="btn btn-sm btn-outline" data-action="back">← 返回</button>
      <span style="font-size:14px;color:#666">📋 学习建议</span>
    </div>
    <div class="tab-bar">
      <div class="tab-item" data-tab="home">🧪 刷题</div>
      <div class="tab-item" data-tab="review">📖 复习资料</div>
      <div class="tab-item active" data-tab="studyguide">📋 学习建议</div>
    </div>

    <div class="guide-section">
      <h3>🎯 总体情况</h3>
      <p>题库共 <strong>${QUESTIONS.length}</strong> 题，覆盖 <strong>${Object.keys(topicCounts).length}</strong> 个知识模块、<strong>${sortedKPs.length}</strong> 个知识点。</p>
      <p>题型分布：${Object.entries(typeCounts).map(([t,c]) => getTypeName(t)+' '+c+'题').join(' | ')}</p>
    </div>

    <div class="guide-section">
      <h3>🗺️ 推荐学习路径</h3>
      <ol>
        <li><strong>第一步：通读知识点解析</strong>（约30分钟）<br>在「📖 复习资料」中，从上到下浏览每个知识点的核心解析和考试重点，对整体框架有清晰认识。</li>
        <li><strong>第二步：按知识点逐个攻克</strong><br>选择一个知识点（建议从题量多的开始），先看解析→看该知识点的所有题目→在刷题模式筛选该知识点集中练习。</li>
        <li><strong>第三步：重点突破薄弱环节</strong><br>查看下方「薄弱环节」，针对错题集中的知识点重点复习，确保每个知识点的正确率达到80%以上。</li>
        <li><strong>第四步：模拟考试检验</strong><br>用「综合复习」的86题或模拟考试模式检验整体掌握程度，目标是90分以上。</li>
        <li><strong>第五步：考前冲刺</strong><br>重做全部错题，浏览复习资料中标记的高频考点，确保计算题每题都亲手算过。</li>
      </ol>
    </div>

    <div class="guide-section">
      <h3>📊 知识点题量分布（按重要性排序）</h3>
      <div style="max-height:300px;overflow-y:auto">
        ${sortedKPs.map(([name, count]) => {
          const pct = (count / QUESTIONS.length * 100).toFixed(1);
          const barW = Math.max(pct * 8, 2);
          return `<div style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:13px">
            <span style="width:130px;text-align:right;flex-shrink:0">${name}</span>
            <div style="flex:1;background:#e8f0fe;border-radius:4px;height:18px;position:relative">
              <div style="background:linear-gradient(90deg,#1a73e8,#4a9af5);height:100%;border-radius:4px;width:${barW}px;min-width:${count>0?'2px':'0'}"></div>
            </div>
            <span style="width:40px;text-align:right;flex-shrink:0;font-weight:600">${count}</span>
          </div>`;
        }).join('')}
      </div>
    </div>

    ${sortedMistakeKP.length > 0 ? `
    <div class="guide-section">
      <h3>⚠️ 薄弱环节（错题按知识点统计）</h3>
      <p style="font-size:13px;color:#999;margin-bottom:8px">以下知识点错题较多，建议优先复习：</p>
      ${sortedMistakeKP.map(([name, count]) => `
        <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;margin:4px 0;background:#fff3e0;border-radius:6px;font-size:14px">
          <span style="color:#e65100;font-weight:600">${count}题</span>
          <span>${name}</span>
          <button class="btn btn-sm btn-outline" data-action="review-kp" data-kp="${escapeHtml(name)}" style="margin-left:auto;font-size:11px;padding:4px 10px">去复习 →</button>
        </div>
      `).join('')}
    </div>` : `
    <div class="guide-section">
      <h3>✅ 暂无错题数据</h3>
      <p>开始刷题后，这里会显示你的薄弱环节分析。</p>
    </div>`}

    <div class="guide-highlight">
      <h4 style="color:#e65100;margin-bottom:6px">💡 高分技巧</h4>
      <ul>
        <li><strong>判断题要追问"为什么错"</strong>：不能只看✓/✗，要理解错误表述错在哪里</li>
        <li><strong>选择题要理解每个选项</strong>：为什么选A不选B？干扰项为什么错？</li>
        <li><strong>计算题每题独立算2遍</strong>：这是最稳拿分的题型，不要只看不练</li>
        <li><strong>同类题对比记忆</strong>：同一知识点可能有多种问法，放在一起对比效率最高</li>
        <li><strong>利用碎片时间</strong>：手机上随时刷10-20题，保持手感</li>
      </ul>
    </div>

    <div class="guide-highlight green">
      <h4 style="color:#0d904f;margin-bottom:6px">📈 目标：100分</h4>
      <ul>
        <li>选择题+判断题（共524题，占77%）：基础分，力争全对</li>
        <li>填空题（120题）：关键词准确，60%模糊匹配即可得分</li>
        <li>简答题（15题）+ 计算题（20题）：理解为主，背诵关键公式</li>
        <li>考前确保错题本清零 → 意味着所有题都至少答对过一次</li>
      </ul>
    </div>
  `;
}
'''

# Insert before "// ========== EVENT BINDING =========="
html = html.replace(
    '// ========== EVENT BINDING ==========',
    new_functions + '\n// ========== EVENT BINDING =========='
)

# ====== ADD TAB EVENT HANDLING IN bindEvents ======
# After "// Home screen" section, add tab handling
old_home_screen = '''  // Home screen
  document.querySelectorAll('[data-action]').forEach(el => {'''

new_home_screen = '''  // Tab bar
  document.querySelectorAll('[data-tab]').forEach(el => {
    el.addEventListener('click', function() {
      const tab = this.dataset.tab;
      if (tab === 'home') { screen = 'home'; render(); }
      else if (tab === 'review') { screen = 'review'; reviewActiveKP = null; render(); }
      else if (tab === 'studyguide') { screen = 'studyguide'; render(); }
    });
  });

  // Review KP nav
  document.querySelectorAll('[data-kp]').forEach(el => {
    el.addEventListener('click', function() {
      const kpName = this.dataset.kp;
      if (this.dataset.action === 'review-kp') {
        screen = 'review';
        reviewActiveKP = kpName;
        render();
      } else {
        // KP nav item in sidebar
        reviewActiveKP = kpName;
        // Just update the main area
        const groups = {};
        QUESTIONS.forEach(q => {
          const k = q.knowledge_point || '综合/未分类';
          if (!groups[k]) groups[k] = [];
          groups[k].push(q);
        });
        const activeQs = groups[kpName] || [];
        let kpInfo = null;
        for (const kp of KNOWLEDGE_POINTS) {
          if (kp.name === kpName) { kpInfo = kp; break; }
        }
        const mainDiv = document.getElementById('reviewMain');
        if (mainDiv) {
          let html = '';
          if (kpInfo) {
            html += `<div class="review-kp-section">
              <div class="review-kp-header" id="kpHeader">
                <h3>📌 ${kpInfo.name} (${activeQs.length}题)</h3>
                <span style="font-size:12px;opacity:0.8">点击展开解析 ▼</span>
              </div>
              <div class="review-kp-explanation" id="kpExplanation">
                <div style="font-weight:600;color:#1a73e8;margin-bottom:4px">📖 知识点解析</div>
                <div>${kpInfo.explanation}</div>
                ${kpInfo.key_concepts ? `<div class="kp-section-label">🔑 核心概念：${kpInfo.key_concepts.join('、')}</div>` : ''}
                ${kpInfo.exam_focus ? `<div class="kp-section-label">⚠️ 考试重点：${kpInfo.exam_focus}</div>` : ''}
              </div>
              ${activeQs.map(q => renderReviewQuestion(q)).join('')}
            </div>`;
          } else {
            html = `<div class="review-kp-section">
              <div class="review-kp-header"><h3>📌 ${kpName} (${activeQs.length}题)</h3></div>
              ${activeQs.map(q => renderReviewQuestion(q)).join('')}
            </div>`;
          }
          mainDiv.innerHTML = html;
          // Update active state
          document.querySelectorAll('.kp-nav-item').forEach(item => item.classList.remove('active'));
          const clicked = document.querySelector(`.kp-nav-item[data-kp="${kpName.replace(/"/g, '&quot;')}"]`);
          if (clicked) clicked.classList.add('active');
          // Bind kp header toggle
          bindReviewHeader();
        } else {
          render();
        }
      }
    });
  });

  // KP explanation toggle in review
  bindReviewHeader();

  // Home screen
  document.querySelectorAll('[data-action]').forEach(el => {'''

html = html.replace(old_home_screen, new_home_screen)

# ====== ADD KP EXPLANATION TO QUIZ FEEDBACK ======
# After the choice correct feedback
old_choice_fb = '''        fb.innerHTML = `<div class="feedback correct">✅ 正确！</div>`;'''
new_choice_fb = '''        fb.innerHTML = `<div class="feedback correct">✅ 正确！</div>${getKPHint(q)}`;'''
html = html.replace(old_choice_fb, new_choice_fb)

old_choice_wrong = '''        fb.innerHTML = `<div class="feedback wrong">❌ 错误！正确答案是 <strong>${q.answer}</strong></div>`;'''
new_choice_wrong = '''        fb.innerHTML = `<div class="feedback wrong">❌ 错误！正确答案是 <strong>${q.answer}</strong></div>${getKPHint(q)}`;'''
html = html.replace(old_choice_wrong, new_choice_wrong)

# TF feedback
old_tf_correct = '''        fb.innerHTML = `<div class="feedback correct">✅ 正确！</div>`;'''
# (already replaced above, need to find the TF-specific one)
# The TF section has same pattern. Let me find the specific TF context
old_tf_wrong = '''        fb.innerHTML = `<div class="feedback wrong">❌ 错误！正确答案是 <strong>${q.answer === '√' ? '正确 (√)' : '错误 (×)'}</strong></div>`;'''
new_tf_wrong = '''        fb.innerHTML = `<div class="feedback wrong">❌ 错误！正确答案是 <strong>${q.answer === '√' ? '正确 (√)' : '错误 (×)'}</strong></div>${getKPHint(q)}`;'''
html = html.replace(old_tf_wrong, new_tf_wrong)

# Fill feedback
old_fill_correct = '''    fb.innerHTML = `<div class="feedback correct">✅ 正确！</div><div class="answer-reveal">你的答案: ${input.value}<br>标准答案: ${q.answer}</div>`;'''
new_fill_correct = '''    fb.innerHTML = `<div class="feedback correct">✅ 正确！</div><div class="answer-reveal">你的答案: ${input.value}<br>标准答案: ${q.answer}</div>${getKPHint(q)}`;'''
html = html.replace(old_fill_correct, new_fill_correct)

old_fill_wrong = '''    fb.innerHTML = `<div class="feedback wrong">❌ 不完全正确</div><div class="answer-reveal">你的答案: ${input.value}<br><strong>标准答案: ${q.answer}</strong></div>`;'''
new_fill_wrong = '''    fb.innerHTML = `<div class="feedback wrong">❌ 不完全正确</div><div class="answer-reveal">你的答案: ${input.value}<br><strong>标准答案: ${q.answer}</strong></div>${getKPHint(q)}`;'''
html = html.replace(old_fill_wrong, new_fill_wrong)

# Open question self-check feedback
old_self_correct = '''        fb.innerHTML = `<div class="feedback correct">✅ 已记录：答对了！</div>`;'''
new_self_correct = '''        fb.innerHTML = `<div class="feedback correct">✅ 已记录：答对了！</div>${getKPHint(q)}`;'''
html = html.replace(old_self_correct, new_self_correct)

old_self_wrong = '''        fb.innerHTML = `<div class="feedback wrong">📝 已加入错题本，继续加油！</div>`;'''
new_self_wrong = '''        fb.innerHTML = `<div class="feedback wrong">📝 已加入错题本，继续加油！</div>${getKPHint(q)}`;'''
html = html.replace(old_self_wrong, new_self_wrong)

# ====== ADD getKPHint() AND bindReviewHeader() FUNCTIONS ======
# Insert before the "// ========== INIT ==========" comment
helper_functions = '''
// ========== KP HELPER ==========
function getKPHint(q) {
  const kpInfo = getKPInfo(q);
  if (!kpInfo) return '';
  return `
    <div class="kp-hint" onclick="this.querySelector('.kp-detail').classList.toggle('show')">
      <strong>📌 ${kpInfo.name}</strong> — 点击查看知识点解析
      <div class="kp-detail">${kpInfo.explanation}</div>
    </div>`;
}

function bindReviewHeader() {
  const kpHeader = document.getElementById('kpHeader');
  if (kpHeader) {
    kpHeader.addEventListener('click', function() {
      const exp = document.getElementById('kpExplanation');
      if (exp) exp.classList.toggle('show');
    });
  }
}
'''

html = html.replace(
    '// ========== INIT ==========',
    helper_functions + '\n// ========== INIT =========='
)

# ====== WRITE OUTPUT ======
output_path = BASE / 'quiz.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"[DONE] Written quiz.html ({len(html)} chars)")
print(f"Output: {output_path}")
