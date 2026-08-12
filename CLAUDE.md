# 刷题学习 — 项目维护记录

## 项目定位

本项目是一个简单的热处理刷题学习网页。核心不是堆功能，而是让用户通过连续做题、即时解析和错题重练完成学习。

长期设计合同见 `DESIGN.md`。后续 AI 或人工修改界面前，应先遵守该文件，避免重新引入复杂导航、卡片堆叠和系统界面模仿。

## 当前结构

```text
quiz/
├── quiz.html               # 主网页应用
├── index.html              # GitHub Pages 轻量入口，跳转到 quiz.html
├── questions.json          # 权威题库数据源
├── questions.js            # 网页加载数据，build_quiz.py 生成
├── knowledge_points.json   # 知识点资料
├── knowledge_system.json   # 既有知识体系资料
├── build_quiz.py           # 构建 questions.js
├── validate_quiz.py        # 题库 / 入口一致性校验
├── README.md               # 使用说明
└── DESIGN.md               # UI / UX 长期约束
```

## 当前网页

一级导航固定：

- 首页
- 练习
- 错题
- 我的

### 首页

- 继续上次练习
- 今日进度
- 顺序 / 随机 / 错题快速练习
- 章节入口

### 练习

- 顺序练习
- 随机练习
- 未做题
- 按章节开始

### 做题

支持：

- choice：单选直接判题，多选提交后判题
- truefalse：直接判题
- fill：标准化文本后判定
- shortanswer / calculation：显示参考答案后自评

作答后显示：

- 正确 / 错误状态
- 正确答案（答错时）
- 解析
- 知识点

### 错题

- 答错自动收录
- 记录累计答错次数
- 按知识点汇总薄弱项
- 支持专项重练
- 连续答对两次自动移出待复习并记为已巩固

### 我的

- 已做题数
- 总正确率
- 今日完成
- 自动 / 浅色 / 深色
- 重置本机学习记录

## 本地数据

使用原有 key：

`heat_treatment_quiz`

当前 state version：`2`。

旧版本数据会迁移：保留总作答 / 正确数与旧错题；旧的复杂页面状态不再继续使用。

## 维护流程

修改题库：

```bash
python validate_quiz.py --data-only
python build_quiz.py
python validate_quiz.py
```

修改网页：

1. 编辑 `quiz.html`
2. 运行 `python build_quiz.py`，确保题库脚本为最新
3. 运行 `python validate_quiz.py`
4. 浏览器检查桌面与手机宽度

## 题库现状

当前仓库题库记录为 715 题。题库数据本身与这次界面重构分离，重构不修改题目、答案和解析。

## 不再恢复的旧方向

除非产品目标发生明确变化，否则不要重新加入以下一级页面：

- 复习资料
- 阅读模式
- 知识体系
- 学习建议
- 模拟考试大面板

相关知识内容应优先进入“题目解析 / 知识点”上下文，而不是再次扩大一级信息架构。
