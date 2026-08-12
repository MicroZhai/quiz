# 刷题学习

一个简单、克制的热处理刷题学习网页。核心目标只有一个：**通过做题完成学习与巩固**。

## 使用

- 在线访问：GitHub Pages 仓库入口（启用 Pages 后使用 `index.html`）
- 本地使用：直接打开 `quiz.html`
- 无框架、无第三方运行时依赖，题库通过 `questions.js` 加载

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

## 数据文件

| 文件 | 作用 |
|---|---|
| `questions.json` | 权威题库数据源 |
| `questions.js` | 网页直接加载的数据文件，由构建脚本生成 |
| `knowledge_points.json` | 知识点资料，继续保留给题库维护使用 |
| `knowledge_system.json` | 既有知识体系数据，继续保留给资料维护使用 |
| `quiz.html` | 网页应用主文件 |
| `index.html` | GitHub Pages 轻量跳转入口，转到 `quiz.html` |
| `build_quiz.py` | 从 JSON 重新生成 `questions.js` |
| `validate_quiz.py` | 题库与入口文件校验 |
| `DESIGN.md` | 本项目长期界面与交互约束 |

## 题目数据约定

当前网页至少使用以下字段：

```json
{
  "id": 1,
  "type": "choice",
  "question": "题干",
  "options": ["选项 A", "选项 B"],
  "option_labels": ["A", "B"],
  "answer": "A",
  "explanation": "解析",
  "topic": "章节",
  "knowledge_point": "知识点"
}
```

支持的 `type`：`choice`、`truefalse`、`fill`、`shortanswer`、`calculation`。

## 更新题库

1. 修改 `questions.json`
2. 运行：

```bash
python validate_quiz.py --data-only
python build_quiz.py
python validate_quiz.py
```

3. 打开 `quiz.html` 检查实际显示

## 设计原则

项目不追求功能数量。长期保持：

- 一屏一个主要任务
- 页面结构先于卡片和装饰
- 统一对齐、间距、控件尺寸和状态几何
- 主强调色只用于当前操作与选择
- 正确 / 错误使用独立语义色
- 不模仿 macOS、Windows 或任何具体商业软件外壳
- 不用 Emoji 充当导航与核心功能图标
- 手机和桌面保持相同任务关系，只改变承载方式

详细规则见 `DESIGN.md`。
