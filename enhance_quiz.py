"""
Enhance quiz.html with:
1. SM-2 spaced repetition algorithm
2. Learning stats dashboard
3. Smart review mode
"""
import re

with open('quiz.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. Add SM-2 state fields (after `let examTotalCount = 50`)
# ============================================================
old_state = '''let examTotalCount = 50;'''
new_state = '''let examTotalCount = 50;

// ===== SM-2 Spaced Repetition State =====
// reviewSchedule: { questionId: { n, ef, interval, lastReview, nextReview } }
// n = repetition count, ef = ease factor (>=1.3), interval = days
function getSchedule() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY + '_sm2');
    return raw ? JSON.parse(raw) : {};
  } catch(e) { return {}; }
}
function saveSchedule(sched) {
  localStorage.setItem(STORAGE_KEY + '_sm2', JSON.stringify(sched));
}

// SM-2 Algorithm: grade 0-5 (0=complete blackout, 5=perfect recall)
function sm2Grade(questionId, grade) {
  const sched = getSchedule();
  let card = sched[questionId] || { n: 0, ef: 2.5, interval: 0 };
  if (grade >= 3) {
    if (card.n === 0) card.interval = 1;
    else if (card.n === 1) card.interval = 6;
    else card.interval = Math.round(card.interval * card.ef);
    card.n++;
  } else {
    card.n = 0;
    card.interval = 1;
  }
  card.ef = Math.max(1.3, card.ef + (0.1 - (5-grade) * (0.08 + (5-grade) * 0.02)));
  const today = new Date().toISOString().split('T')[0];
  card.lastReview = today;
  card.nextReview = new Date(Date.now() + card.interval * 86400000).toISOString().split('T')[0];
  sched[questionId] = card;
  saveSchedule(sched);
  return card;
}

// Get cards due for review today
function getDueCards() {
  const sched = getSchedule();
  const today = new Date().toISOString().split('T')[0];
  const due = [];
  // Cards scheduled for review today or earlier
  for (const [qid, card] of Object.entries(sched)) {
    if (card.nextReview <= today) due.push(parseInt(qid));
  }
  // Cards that have been answered but never scheduled (from mistakes)
  const scheduledIds = new Set(Object.keys(sched).map(Number));
  const mistakeIds = Object.keys(state.mistakes).map(Number);
  for (const qid of mistakeIds) {
    if (!scheduledIds.has(qid)) due.push(qid);
  }
  return [...new Set(due)]; // dedup
}

// Get study streak (consecutive days with activity)
function getStreak() {
  const history = state.stats?.dailyActivity || {};
  const dates = Object.keys(history).sort().reverse();
  if (dates.length === 0) return 0;
  let streak = 0;
  const today = new Date();
  for (let i = 0; i < dates.length; i++) {
    const expected = new Date(today);
    expected.setDate(expected.getDate() - i);
    const expectedStr = expected.toISOString().split('T')[0];
    if (dates.includes(expectedStr)) streak++;
    else break;
  }
  return streak;
}

// Record daily activity
function recordActivity() {
  if (!state.stats.dailyActivity) state.stats.dailyActivity = {};
  const today = new Date().toISOString().split('T')[0];
  state.stats.dailyActivity[today] = (state.stats.dailyActivity[today] || 0) + 1;
}'''

html = html.replace(old_state, new_state)

# ============================================================
# 2. Add 'smartreview' to screen enum and render()
# ============================================================
old_screen = "let screen = 'home'; // home | quiz | mistakes | exam"
new_screen = "let screen = 'home'; // home | quiz | mistakes | exam | review | studyguide | smartreview"
html = html.replace(old_screen, new_screen)

old_render = '''function render() {
  const app = document.getElementById('app');
  if (screen === 'home') app.innerHTML = renderHome();
  else if (screen === 'quiz') app.innerHTML = renderQuiz();
  else if (screen === 'mistakes') app.innerHTML = renderMistakes();
  else if (screen === 'exam') app.innerHTML = renderExamPaper();
  else if (screen === 'review') app.innerHTML = renderReview();
  else if (screen === 'studyguide') app.innerHTML = renderStudyGuide();
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
  else if (screen === 'smartreview') app.innerHTML = renderSmartReview();
  bindEvents();
}'''

html = html.replace(old_render, new_render)

# ============================================================
# 3. Add stats card to home screen (after the first stats grid)
# ============================================================
# Insert after the closing </div> of the stats grid
old_stats_end = '''</div>
	    </div>

	    <div class="card">
	      <h3 style="margin-bottom:12px">📂 按主题筛选</h3>'''

new_stats_end = '''</div>
	    </div>

	    ${(() => {
	      const dueCards = getDueCards();
	      const streak = getStreak();
	      const kpStats = {};
	      Object.keys(state.mistakes).forEach(id => {
	        const q = QUESTIONS.find(qq => qq.id === parseInt(id));
	        if (q) {
	          const kp = q.knowledge_point || '综合';
	          kpStats[kp] = (kpStats[kp] || 0) + 1;
	        }
	      });
	      const topWeakKPs = Object.entries(kpStats).sort((a,b) => b[1]-a[1]).slice(0, 3);

	      return \`
	    <div class="card" style="background:linear-gradient(135deg,#f0f4ff,#e8f0fe);border-left:4px solid #1a73e8">
	      <h3 style="margin-bottom:10px">📊 学习统计</h3>
	      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px">
	        <div style="text-align:center;padding:8px">
	          <div style="font-size:24px;font-weight:700;color:#1a73e8">${dueCards.length}</div>
	          <div style="font-size:11px;color:#666">🎯 待复习</div>
	        </div>
	        <div style="text-align:center;padding:8px">
	          <div style="font-size:24px;font-weight:700;color:#0d904f">${streak}</div>
	          <div style="font-size:11px;color:#666">🔥 连续天数</div>
	        </div>
	        <div style="text-align:center;padding:8px">
	          <div style="font-size:24px;font-weight:700;color:#e65100">${Object.keys(state.mistakes).length}</div>
	          <div style="font-size:11px;color:#666">📝 错题数</div>
	        </div>
	        <div style="text-align:center;padding:8px">
	          <div style="font-size:24px;font-weight:700;color:#1a73e8">${rate}%</div>
	          <div style="font-size:11px;color:#666">✅ 正确率</div>
	        </div>
	      </div>
	      ${topWeakKPs.length > 0 ? \`
	        <div style="margin-top:10px;font-size:13px;color:#666">
	          <strong>⚠️ 薄弱知识点：</strong>
	          ${topWeakKPs.map(([kp, c]) => \`<span style="display:inline-block;margin:2px 4px;padding:2px 8px;background:#fff3e0;border-radius:10px;font-size:12px">\${kp} (\${c}题)</span>\`).join('')}
	        </div>
	      \` : ''}
	      ${dueCards.length > 0 ? \`<button class="btn btn-primary btn-sm mt-12" data-action="start-smart-review" style="width:100%">🎯 开始智能复习（\${dueCards.length}题待复习）</button>\` : \`<p style="font-size:12px;color:#999;margin-top:8px;text-align:center">✨ 暂无待复习卡片，去刷题吧！</p>\`}
	    </div>
	    \`;
	    })()}

	    <div class="card">
	      <h3 style="margin-bottom:12px">📂 按主题筛选</h3>'''

html = html.replace(old_stats_end, new_stats_end)

# ============================================================
# 4. Add smart review render function (before STUDY GUIDE section)
# ============================================================
old_study_guide = '// ========== STUDY GUIDE =========='

new_smart_review = '''// ========== SMART REVIEW (SM-2) ==========
let smartReviewQuestions = [];
let smartReviewIndex = 0;

function renderSmartReview() {
  if (smartReviewQuestions.length === 0) {
    const dueIds = getDueCards();
    smartReviewQuestions = dueIds.map(id => QUESTIONS.find(q => q.id === id)).filter(Boolean);
    smartReviewIndex = 0;
  }

  if (smartReviewQuestions.length === 0) {
    return `
      <div class="header"><h1>✨ 暂无待复习</h1></div>
      <div class="card text-center">
        <p style="font-size:16px;color:#666">所有题目都已安排好复习计划！</p>
        <p style="font-size:14px;color:#999;margin-top:8px">继续刷题可以巩固更多知识点。</p>
      </div>
      <button class="btn btn-primary btn-block" data-action="back">← 返回首页</button>
    `;
  }

  if (smartReviewIndex >= smartReviewQuestions.length) {
    // Review session complete
    const sched = getSchedule();
    const remainingDue = Object.values(sched).filter(c => c.nextReview <= new Date().toISOString().split('T')[0]).length;
    smartReviewQuestions = [];
    smartReviewIndex = 0;
    return `
      <div class="header"><h1>🎉 本轮复习完成！</h1></div>
      <div class="card text-center">
        <p style="font-size:16px;color:#0d904f">当前复习计划已完成。</p>
        ${remainingDue > 0 ? `<p style="font-size:14px;color:#e65100;margin-top:8px">仍有 ${remainingDue} 张卡片今日待复习</p>` : ''}
      </div>
      <button class="btn btn-primary btn-block" data-action="back">← 返回首页</button>
    `;
  }

  const q = smartReviewQuestions[smartReviewIndex];
  const card = getSchedule()[q.id];
  const progress = Math.round(smartReviewIndex / smartReviewQuestions.length * 100);

  return `
    <div class="header" style="background:linear-gradient(135deg,#7c3aed,#5b21b6)">
      <h1>🎯 智能复习</h1>
      <p>基于遗忘曲线的间隔重复 · SM-2 算法</p>
    </div>
    <div class="quiz-progress">
      <span>第 ${smartReviewIndex+1}/${smartReviewQuestions.length} 题</span>
      <span style="font-size:12px;color:#7c3aed">${card ? '间隔: '+card.interval+'天 · 容易度: '+card.ef.toFixed(1) : '新卡片'}</span>
    </div>
    <div class="progress-bar"><div class="progress-bar-fill" style="width:${progress}%;background:#7c3aed"></div></div>
    ${q.type === 'choice' ? renderChoiceQuestion(q) : ''}
    ${q.type === 'truefalse' ? renderTrueFalseQuestion(q) : ''}
    ${q.type === 'fill' ? renderFillQuestion(q) : ''}
    ${q.type === 'shortanswer' || q.type === 'calculation' ? renderOpenQuestion(q) : ''}
  `;
}

// ========== STUDY GUIDE =========='''

html = html.replace(old_study_guide, new_smart_review)

# ============================================================
# 5. Add SM-2 grading after answer feedback (modify correct/wrong handling)
# ============================================================
# After recording a correct answer, grade SM-2 with quality=4
old_correct_record = '''  if (correct) {
    state.stats.correct = (state.stats.correct || 0) + 1;
    delete state.mistakes[q.id];
  } else {
    state.mistakes[q.id] = true;
  }'''

new_correct_record = '''  if (correct) {
    state.stats.correct = (state.stats.correct || 0) + 1;
    delete state.mistakes[q.id];
    sm2Grade(q.id, 4); // SM-2: correct = good recall
  } else {
    state.mistakes[q.id] = true;
    sm2Grade(q.id, 2); // SM-2: wrong = failed recall
  }
  recordActivity();'''

html = html.replace(old_correct_record, new_correct_record)

# No need for separate wrong record replacement anymore
old_wrong_record = 'SKIP_THIS_REPLACEMENT'
new_wrong_record = 'SKIP_THIS_REPLACEMENT'

# ============================================================
# 6. Add smart review event handlers in bindEvents
# ============================================================
old_event_back = "if (action === 'back') { screen = 'home';"

new_event_back = "if (action === 'start-smart-review') { screen = 'smartreview'; smartReviewQuestions = []; smartReviewIndex = 0; render(); return; }\n    if (action === 'back') { screen = 'home';"

html = html.replace(old_event_back, new_event_back)

# ============================================================
# 7. Add smart review navigation in event handling
# ============================================================
# Find the "Next" button handling for smart review mode
old_next_btn = "if (action === 'next') {"

new_next_btn = '''if (action === 'next') {
      if (screen === 'smartreview') {
        smartReviewIndex++;
        render();
        return;
      }'''

html = html.replace(old_next_btn, new_next_btn)

# ============================================================
# 8. Add CSS for smart review
# ============================================================
old_style_end = '</style>'

new_css = '''
/* Smart Review */
.smart-review-header { background:linear-gradient(135deg,#7c3aed,#5b21b6); }
.stats-dashboard { display:grid; grid-template-columns:repeat(auto-fit, minmax(100px,1fr)); gap:8px; }
.stats-item { text-align:center; padding:10px 8px; background:#fff; border-radius:8px; box-shadow:0 1px 2px rgba(0,0,0,0.05); }
.stats-item .stats-num { font-size:22px; font-weight:700; }
.stats-item .stats-label { font-size:11px; color:#999; margin-top:2px; }
.weak-kp-tag { display:inline-block; margin:2px 4px; padding:3px 10px; background:#fff3e0; border-radius:12px; font-size:12px; color:#e65100; cursor:pointer; }
.weak-kp-tag:hover { background:#ffe0b2; }
'''

html = html.replace(old_style_end, new_css + '\n</style>')

# ============================================================
# Write output
# ============================================================
with open('quiz.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Enhanced quiz.html ({len(html)} chars)')
print('Features added:')
print('  - SM-2 spaced repetition algorithm')
print('  - Smart review mode (screen=smartreview)')
print('  - Learning stats dashboard on home screen')
print('  - Daily activity tracking & streak')
print('  - Post-answer SM-2 grading')
