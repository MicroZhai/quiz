# 2000题导入自动验收诊断

## 清理旧正式题库完全重复项

退出码：0

```text
{
  "before": 715,
  "duplicate_groups": 17,
  "removed": 17,
  "after": 698,
  "details": [
    {
      "keep_id": 3,
      "removed_ids": [
        654
      ],
      "question": "珠光体组织的相组成为：（ ）。",
      "merged_changes": []
    },
    {
      "keep_id": 29,
      "removed_ids": [
        647
      ],
      "question": "黄铜的主要热处理方式是 （ ）。",
      "merged_changes": [
        "采用更完整解析"
      ]
    },
    {
      "keep_id": 32,
      "removed_ids": [
        641
      ],
      "question": "尺寸相近，形状相同，不同材料，硬度值不同的几项产品由于不规范管理，导致这几项产品在热处理后混合在一起无法分开，请选出能将这几项产品区分出来的方法。（ ）",
      "merged_changes": []
    },
    {
      "keep_id": 107,
      "removed_ids": [
        681
      ],
      "question": "在共析温度以下存在的奥氏体称为过冷奥氏体。",
      "merged_changes": [
        "采用更完整解析"
      ]
    },
    {
      "keep_id": 129,
      "removed_ids": [
        679
      ],
      "question": "合金钢中含有锰、铬、镍、硅、铝、铜、磷等元素时，会降低第二类回火脆性倾向。",
      "merged_changes": []
    },
    {
      "keep_id": 171,
      "removed_ids": [
        669
      ],
      "question": "金属结晶时，过冷度越大，结晶后晶粒也越粗大。",
      "merged_changes": []
    },
    {
      "keep_id": 197,
      "removed_ids": [
        465
      ],
      "question": "再结晶过程没有恒定的转变温度。",
      "merged_changes": []
    },
    {
      "keep_id": 277,
      "removed_ids": [
        704
      ],
      "question": "已知某碳钢在退火状态的金相组织中，珠光体含量为45%，其它为铁素体，试计算该钢的含碳量，并指出大概的钢号。",
      "merged_changes": [
        "采用更完整解析"
      ]
    },
    {
      "keep_id": 457,
      "removed_ids": [
        483
      ],
      "question": "当介质的冷却速度大于钢的临界冷速时工件整个截面上都能发生 马氏体转变。",
      "merged_changes": []
    },
    {
      "keep_id": 495,
      "removed_ids": [
        675
      ],
      "question": "锻件在热处理过程中需要加装负载热电偶时，负载热电偶加装的具体位置必须在产品装炉位置图上进行标识。",
      "merged_changes": []
    },
    {
      "keep_id": 633,
      "removed_ids": [
        662
      ],
      "question": "钢淬火后，进行低温回火，得到的组织为（ ）。",
      "merged_changes": []
    },
    {
      "keep_id": 642,
      "removed_ids": [
        660
      ],
      "question": "合金元素总含量为（ ）的合金钢，属于中合金钢。",
      "merged_changes": [
        "采用更完整解析"
      ]
    },
    {
      "keep_id": 656,
      "removed_ids": [
        661
      ],
      "question": "金属的塑性变形是通过（ ）实现的。",
      "merged_changes": []
    },
    {
      "keep_id": 663,
      "removed_ids": [
        684
      ],
      "question": "厚薄不均匀的工件浸入淬火介质冷却时，薄的部分先浸入淬火介质，带凹槽的工件， 凹槽面朝下浸入淬火介质。",
      "merged_changes": []
    },
    {
      "keep_id": 666,
      "removed_ids": [
        683
      ],
      "question": "马氏体不锈钢锻件在正火保温过程中，电炉故障（炉丝断），可将锻件炉冷至600℃以 下出炉空冷，设备修复后按工艺重新进行正火。",
      "merged_changes": [
        "采用更完整解析"
      ]
    },
    {
      "keep_id": 667,
      "removed_ids": [
        682
      ],
      "question": "导热性差的金属工件或坯料，加热或冷却时会产生内外温差，导致内外不同的膨胀或 收缩，产生应力、变形或破坏。",
      "merged_changes": []
    },
    {
      "keep_id": 668,
      "removed_ids": [
        685
      ],
      "question": "产品在存放、周转和运输时，应采取保护措施，防止混批、锈蚀、磕碰、压伤及变形 等，应使用相应的搬运设备，以不破坏原标识为前提。",
      "merged_changes": [
        "采用更完整解析"
      ]
    }
  ]
}
```

## 合并审校题库

退出码：0

```text
{
  "base": 698,
  "source": 2000,
  "imported": 2000,
  "merged": 2698,
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
[INFO] 题目总数: 2698
[INFO] 题型: calculation=16, choice=1785, fill=139, shortanswer=76, truefalse=682
[OK] 校验通过，0 个警告
```

## 生成 questions.js

退出码：0

```text
[OK] Generated questions.js (1,825,370 chars, 2698 questions, 27 KPs, 5 parts)
[DONE] Build complete. Open quiz.html to verify.
```

## 2000题专项验收

退出码：0

```text
[INFO] total: 2698
[INFO] imported: 2000
[INFO] imported types: {'truefalse': 418, 'choice': 1521, 'shortanswer': 61}
[INFO] imported levels: {'初级工': 296, '中级工': 301, '高级工': 253, '技师/高级技师': 187, '强化练习': 963}
[INFO] review status: {'reviewed': 1035, 'fixed': 3, 'composite_verified': 962}
[OK] reviewed 2000-bank integration validation passed
```

## 网页结构验收

退出码：0

```text
[INFO] 题目总数: 2698
[INFO] 题型: calculation=16, choice=1785, fill=139, shortanswer=76, truefalse=682
[OK] 校验通过，0 个警告
```


## PWA缓存

已更新到题数 2698。
