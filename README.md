# 刷题学习


<!-- reviewed-bank-status:start -->
## 当前题库状态

- 正式题库共 **2698 题**，均为去重后的可刷题记录。
- 本次“金属热处理工考工晋级大题库”审校后正式加入 **2000 题**。
- 正式题型：选择题 1785 / 判断题 682 / 填空题 139 / 简答题 76 / 计算题 16。
- 新增题库所有题目均包含学习解析；简答/案例题包含“参考答案要点 + 解析”；强化辨析题包含逐项对错解释。
- 审校、修题、去重和最终验收记录位于 `audit/`，正式来源标识为 `metal_heat_treatment_2000_reviewed_2026`。

<!-- reviewed-bank-status:end -->

一个简单、克制的热处理刷题学习网页，核心目标只有一个：**通过做题完成学习与巩固**。

## 在线与 PWA

- 在线地址：`https://microzhai.github.io/quiz/`
- GitHub Pages 根入口 `index.html` 同时作为 PWA 外壳。
- 支持安装到桌面 / 手机主屏幕；安装后以 `standalone` 模式运行。
- Service Worker 会缓存应用外壳、当前题库数据和图标，完成一次在线加载后可离线打开核心刷题功能。
- 本地直接双击 `quiz.html` 仍可使用普通网页模式；Service Worker / PWA 安装需要 HTTPS（GitHub Pages 已满足）。

## 页面

- **首页**：继续上次练习、今日进度、快速练习、章节入口
- **练习**：顺序练习、随机练习、未做题，按章节开始
- **错题**：自动收录答错题；连续答对两次后自动移出；支持按薄弱知识点重练
- **我的**：学习统计、外观设置、重置本机学习记录

## 做题支持

- 单选题：点击选项直接判题
- 多选题：选完后提交
- 判断题：直接判题
- 填空题：标准化后判定
- 简答题 / 计算题：先看参考答案，再自评
- 每题答完显示答案解析和知识点

## 主要文件

- `index.html`：GitHub Pages / PWA 入口
- `quiz.html`：刷题应用主体
- `questions.json`：当前网页使用的权威题库数据源
- `questions.js`：网页加载的数据文件，由构建脚本生成
- `knowledge_points.json`：知识点解析数据
- `build_quiz.py`：从 JSON 生成 `questions.js`
- `validate_quiz.py`：题库与入口一致性校验
- `manifest.webmanifest`：PWA 元数据
- `service-worker.js`：离线缓存与更新策略
- `icons/`：PWA 安装图标
- `DESIGN.md`：界面与交互长期设计合同
- `热处理题库/`：新增的大题库原始资料目录；其中资料不会自动替换当前网页题库，导入前需先结构化和校验

## 题库维护

当前网页题库仍以 `questions.json` 为准。更换或扩充题库后：

```bash
python validate_quiz.py --data-only
python build_quiz.py
python validate_quiz.py
```

通过校验后再部署。不要直接手改 `questions.js`。

## 设计原则

项目保持：**少功能、重体验、重规范、重学习效率**。

一级入口固定为：首页 / 练习 / 错题 / 我的。新增功能必须直接服务“开始练习 → 作答 → 反馈 → 解析 → 错题重练 → 掌握”的学习闭环。详细规则见 `DESIGN.md`。
