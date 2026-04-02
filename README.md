# Learning Coach 🧠

> **不仅教你学什么，更是教你怎么学** —— 基于元认知监控模型的学习教练，成为你的第二大脑和学习伙伴。

## 核心思想

### 元认知监控循环

基于 Nelson & Narens (1990) 的元认知监控模型，Learning Coach 将学习过程简化为 3 个核心环节：

```
任务选择 → 掌握评估 → 策略调整 → 循环
```

**为什么有效？**

传统学习往往缺乏"自我监控"——你不知道自己是否真正掌握了某个概念。元认知监控通过不断评估和调整，让学习变成一个**可迭代、可量化**的过程。

### 三层掌握度模型

Learning Coach 将"掌握"分为三个层次：

| 层次 | 定义 | 权重 |
|------|------|------|
| **表层理解** | 能识别、能回忆 | 20% |
| **语义理解** | 能解释、能说明 | 30% |
| **直觉理解** | 能应用、能举例 | 50% |

只有当**直觉理解**达到一定水平，才算真正掌握。这也是为什么我们强调"动手实践"和"教给他人"。

### 个性化学习策略

系统根据当前掌握度自动推荐策略：

| 掌握度范围 | 推荐策略 |
|------------|----------|
| 0% - 30% | 入门视频 → 基础文章 → 前置知识补充 |
| 30% - 60% | 进阶文章 → 练习题 → 动手实践 |
| 60% - 80% | 项目实践 → 教给他人 → 新场景应用 |

---

## 功能特性

- ✅ **元认知监控循环** - 持续评估掌握度，动态调整策略
- ✅ **断点续学** - 自动保存进度，随时继续
- ✅ **多目标管理** - 同时追踪多个学习主题
- ✅ **认知循环记录** - 完整记录每次学习过程
- ✅ **思维导图生成** - Mermaid 格式，可视化学习路径

---

## 安装与使用

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/mosqlee/learning-coach.git
cd learning-coach

# 直接运行（无需安装依赖，纯 Python 标准库）
python scripts/coach.py
```

### 命令行模式

```bash
# 开始新主题
python scripts/coach.py start 机器学习

# 查看进度
python scripts/coach.py status

# 列出所有学习目标
python scripts/coach.py list

# 生成思维导图
python scripts/coach.py mindmap

# 导出数据
python scripts/coach.py export
```

### 交互模式

```bash
python scripts/coach.py

# 进入交互界面
教练> start 机器学习
教练> continue
教练> status
教练> report
教练> mindmap
```

---

## 作为 OpenClaw Skill 使用

Learning Coach 原本是为 [OpenClaw](https://github.com/openclaw/openclaw) 设计的 Skill，可以与 AI 助手无缝集成：

### 触发方式

在 OpenClaw 中直接说：
- `学习 机器学习` → 开始学习新主题
- `继续` → 继续上次的学习
- `查看进度` → 查看当前进度
- `评估 监督学习` → 评估概念掌握度

### 典型对话

```
用户：学习 机器学习

教练：🎯 检测到学习意图：机器学习

      快速确认一下你的情况：
      1. 你的基础是？
         a) 零基础  b) 有编程基础  c) 了解基本概念  d) 有一定经验
      2. 你的学习目标是？
         a) 快速了解（1-2周）  b) 系统学习（1-3个月）  c) 求职准备（3-6个月）

用户：1-b 2-c

教练：📋 学习档案已建立！
      
      【学习主题】机器学习
      【当前基础】有编程基础
      【学习目标】求职准备
      【预计时间】3-6个月
      
      正在为你生成学习路径...
      
      🗺️ 认知地图：
      - 监督学习（核心）
        - 分类
        - 回归
      - 无监督学习
      - 特征工程
      - 模型评估
      
      📌 第一个学习任务：理解监督学习
      准备好了吗？我们开始吧！
```

---

## 数据结构

### 学习档案 (data/profiles.json)

```json
{
  "profiles": [
    {
      "id": "uuid-123",
      "topic": "机器学习",
      "level": "有编程基础",
      "goal": "求职准备",
      "time_budget": "3-6个月",
      "created_at": "2026-03-18T16:00:00",
      "updated_at": "2026-03-18T16:30:00",
      "status": "active",
      "tasks": [
        {
          "name": "监督学习",
          "mastery": 0.5,
          "time_spent": "2h",
          "status": "in_progress"
        }
      ],
      "current_task": "监督学习",
      "overall_progress": 0.15
    }
  ]
}
```

### 认知循环日志 (data/records.json)

每次学习评估都会记录完整的认知循环：

```json
{
  "records": [
    {
      "id": "record-001",
      "profile_id": "uuid-123",
      "timestamp": "2026-03-18T16:30:00",
      "task": {"name": "监督学习", "importance": 5, "difficulty": 3},
      "assessment": {
        "mastery_level": 0.5,
        "mastery_breakdown": {"surface": 0.7, "semantic": 0.5, "intuitive": 0.3}
      },
      "decision": {
        "action": "continue",
        "strategy": ["观看视频", "阅读文章", "动手实践"],
        "reason": "掌握度不足，建议继续深入"
      }
    }
  ]
}
```

---

## 文件结构

```
learning-coach/
├── README.md           # 本文档
├── SKILL.md            # OpenClaw Skill 配置（可选）
├── scripts/
│   └── coach.py        # 主程序
├── data/
│   ├── profiles.json   # 学习档案（自动生成）
│   └── records.json    # 认知循环日志（自动生成）
└── mindmaps/
    └── *.md            # 生成的思维导图（自动生成）
```

---

## 核心算法

### 掌握度计算

```python
def calculate_mastery(answers):
    """
    表层理解 × 0.2 + 语义理解 × 0.3 + 直觉理解 × 0.5 = 综合掌握度
    """
    return (
        answers["surface"] * 0.2 +
        answers["semantic"] * 0.3 +
        answers["intuitive"] * 0.5
    )
```

### 任务优先级

```python
def select_task(tasks):
    """
    优先级排序：
    1. 未开始的任务优先
    2. 重要性高的任务优先
    3. 掌握度低的任务优先（薄弱点优先攻克）
    """
    incomplete = [t for t in tasks if t["mastery"] < 0.8]
    incomplete.sort(key=lambda t: (-t["importance"], t["mastery"]))
    return incomplete[0]
```

---

## 参考文献

1. Nelson, T. O., & Narens, L. (1990). *Metamemory: A theoretical framework and new findings*. The Psychology of Learning and Motivation.

2. Ausubel, D. P. (1968). *Educational Psychology: A Cognitive View*. Holt, Rinehart & Winston.

---

## License

MIT License - 自由使用、修改、分发

---

## 贡献

欢迎提交 Issue 和 PR！

---

**让学习变成一个可迭代、可量化、可持续的过程。** 🚀