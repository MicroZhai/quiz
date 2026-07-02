# 热处理考试复习资料 — 项目记录

## 项目概述

为用户构建热处理考试复习系统：一个可阅读的 Markdown 复习文档 + 一个交互式刷题网页。已推送到 https://github.com/MicroZhai/quiz ，通过 GitHub Pages 可在手机上使用。

## 文件结构

```
热处理复习资料/
├── 复习题整合.md       ← 📖 唯一复习文档，含全部715题及答案
├── quiz.html           ← 🧪 交互式刷题网页（单文件，零依赖）
├── index.html          ← 同 quiz.html，GitHub Pages 默认入口
├── questions.js        ← 题库数据+知识点数据，build_quiz.py 生成
├── questions.json      ← 📚 题库数据源（JSON，715题）
├── knowledge_points.json ← 📚 知识点数据源（26个知识点解析）
├── build_quiz.py       ← 🔧 核心构建：JSON→questions.js+同步index.html
├── json_to_md.py       ← 🔧 JSON→复习题整合.md
├── README.md           ← 项目说明
└── CLAUDE.md           ← 本文档：项目记录与维护指南
```

## 题库数据

- **总题数**：715 题
- **题型分布**：选择题 270 / 判断题 274 / 填空题 139 / 简答题 15 / 计算题 17
- **知识模块**：热处理基础知识 / 热处理设备与工艺 / 质量管理 / 仪表知识 / 综合复习
- **知识点**：26 个核心知识点，覆盖率 ~95%

## 关键决策记录

### 1. 文档整合（2026-07-01）
- 5 个原始 .md → 1 个 `复习题整合.md`，原始文件已删除

### 2. 选择题答案恢复
- `（ ）` → `（ D ）`，括号内填入正确答案字母，从 questions.json 匹配

### 3. 判断题拆分
- 一行多题按 `(标记)数字、` 断点拆分，少量无法完全自动拆分

### 4. 删除作图题
- 用户明确不需要，全文件清除

### 5. JSON 为单一数据源
- questions.json 为权威数据源，build_quiz.py 幂等生成 questions.js
- 知识点数据来自 knowledge_points.json

### 6. GitHub Pages 部署
- Repo：https://github.com/MicroZhai/quiz
- 访问地址：https://microzhai.github.io/quiz/
- 推送命令：`git push origin master:main`

### 7. 题库数据大清理（2026-07-01）
- 拆分合并题、补全答案、清理杂散字符，679→714 题

### 8. 题库二次修复（2026-07-02）
- 修复三处未正确录入区域，714→715 题

### 9. 答题反馈动画（2026-07-02）
- 7 组 CSS 动画：正确弹跳、错误抖动、字母弹跳、反馈滑入、卡片光晕、分数弹入

### 10. 阅读模式升级（2026-07-02）
- 6 项改进：知识点标注、答案显隐切换、阅读进度记忆、题内搜索、字号调节、阅读统计

## 维护指南

### 修改题目内容
1. 编辑 `questions.json`（数据源）
2. 运行 `python json_to_md.py` 重新生成 `复习题整合.md`
3. 运行 `python build_quiz.py` 重新生成 questions.js + 同步 index.html
4. 在浏览器打开 quiz.html 验证

### 修改知识点解析
1. 编辑 `knowledge_points.json`
2. 运行 `python build_quiz.py`（知识点嵌入 questions.js 和 quiz.html）

### 推送到 GitHub
```bash
git add -A
git commit -m "描述修改内容"
git push origin master:main
```

## quiz.html 技术要点

- 纯静态 HTML/CSS/JS，零依赖，file:// 协议可直接打开
- 题库通过 `<script src="questions.js">` 加载（`window.ALL_QUESTIONS`）
- 知识点数据内嵌在 HTML 中（`KNOWLEDGE_POINTS` / `KP_MAP`）
- **四个 Tab**：🧪 刷题 / 📖 复习资料 / 📜 阅读模式 / 📋 学习建议
- **阅读模式**：章节导航 + 知识点标注 + 题内搜索 + 字号调节 + 答案显隐 + 进度记忆
- **复习模式**：按知识点分组展示，左侧知识点导航，解析可展开
- **学习建议页**：推荐学习路径、知识点题量分布、薄弱环节分析、高分技巧
- **刷题反馈**：答完题显示对应知识点解析，7 组 CSS 动画反馈
- **考试模式**：按比例从题库抽题，一页卷面，自动判分
- **SM-2 间隔重复**：智能复习基于遗忘曲线，localStorage 持久化
- **填空题判分**：模糊匹配，关键词覆盖 ≥60% 算对
- **错题本**：localStorage 持久化存储
- **配色**：≥90 绿色 / ≥75 蓝色 / ≥60 橙色 / <60 红色

## 已知局限

1. 约 5 道填空题因源数据破损严重，答案靠领域知识推断
2. 少量填空题 OCR 乱码未完全修复
3. 综合复习章节与前面章节有重复（汇总性质，刻意保留）
4. ~30 道题（~4%）未匹配到知识点标签，归入"综合/未分类"
