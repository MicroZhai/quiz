# 2000题导入自动验收诊断

## 合并审校题库

退出码：0

```text
{
  "base": 715,
  "source": 2000,
  "imported": 2000,
  "merged": 2715,
  "duplicates": 0,
  "held": 0,
  "fixed": 3,
  "by_type": {
    "truefalse": 418,
    "choice": 1521,
    "shortanswer": 61
  },
  "by_level": {
    "初级工": 296,
    "中级工": 301,
    "高级工": 253,
    "技师/高级技师": 187,
    "强化练习": 963
  }
}
```

## 应用修题与简答格式

退出码：0

```text
[OK] applied reviewed fixes: 3; formatted short-answer references
```

## 题库数据校验

退出码：0

```text
[INFO] 题目总数: 2715
[INFO] 题型: calculation=17, choice=1791, fill=139, shortanswer=76, truefalse=692
[OK] 校验通过，0 个警告
```

## 生成 questions.js

退出码：0

```text
[OK] Generated questions.js (1,831,390 chars, 2715 questions, 27 KPs, 5 parts)
[DONE] Build complete. Open quiz.html to verify.
```

## 2000题专项验收

退出码：1

```text
[INFO] total: 2715
[INFO] imported: 2000
[INFO] imported types: {'truefalse': 418, 'choice': 1521, 'shortanswer': 61}
[INFO] imported levels: {'初级工': 296, '中级工': 301, '高级工': 253, '技师/高级技师': 187, '强化练习': 963}
[INFO] review status: {'reviewed': 1035, 'fixed': 3, 'composite_verified': 962}
[ERROR] 全题库存在完整重复题: [465, 483, 641, 647, 654, 660, 661, 662, 669, 675, 679, 681, 682, 683, 684, 685, 704]
[FAIL] 1 errors
```

