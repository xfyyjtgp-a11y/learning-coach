---
name: learning-coach
description: 基于元认知监控模型的学习教练，帮助用户系统化学习新知识/新技能。支持断点续学、切换学习目标、保存学习过程、认知循环和苏格拉底式追问。
version: 1.2.0
last_updated: 2026-04-03
author: Damon
---

# 学习教练 (Learning Coach)

## 安装

1. 将 `learning-coach/` 文件夹复制到 OpenClaw skills 目录（默认 `~/.openclaw/workspace/skills/`）
2. 确保 `scripts/coach.py` 有执行权限：`chmod +x scripts/coach.py`
3. 确保 `data/` 目录存在且可写（首次运行会自动初始化）
4. 如需 Obsidian 同步功能，确保已安装 `obsidian-vault` skill
5. 重启 OpenClaw 或刷新 skill 列表

无需额外 API Key 或环境变量配置。

> **核心理念**：不仅教你学什么，更是教你怎么学——通过元认知监控和系统化学习框架，成为你的第二大脑和学习伙伴。

## 核心功能

### ✅ 元认知监控循环

基于 Nelson & Narens (1990) 的元认知监控模型，简化为3个核心环节：

```
任务选择 → 掌握评估 → 策略调整 → 循环
```

### ✅ 断点续学

自动保存学习进度，随时可以继续上次的学习。

### ✅ 多目标管理

支持同时学习多个主题，可以随时切换学习目标。

### ✅ 认知循环记录

完整记录每次的元认知监控循环，形成学习日志。

### ✅ 思维导图生成

基于学习记录生成 Mermaid 格式的思维导图。

### ✅ 苏格拉底式追问（v1.2.0 新增）

嵌入式6维度追问框架，帮助零基础学习者深度思考：

```
澄清 → 假设 → 证据 → 视角 → 后果 → 反思
```

- **自动启用**：零基础用户建档时自动启用 SOCRATIC_PRIORITY 模式
- **最多3轮**：每个学习目标最多3轮追问，避免过度追问
- **随时退出**：输入"直接解释"可跳过追问，获得直接讲解
- **维度循环**：按顺序探索6个认知维度


## 可用命令

### 开始学习
```
学习 [主题] - 开始学习新主题
```

示例：
```
用户：学习 机器学习
教练：好的，让我先了解你的情况...
```

### 继续学习
```
继续 - 继续当前学习任务
继续 [主题] - 继续指定主题的学习
```

### 查看进度
```
查看进度 - 查看当前学习进度
查看进度 [主题] - 查看指定主题的进度
```

### 切换目标
```
切换目标 [主题] - 切换到另一个学习目标
学习目标列表 - 查看所有学习目标
```

### 评估掌握
```
评估 [概念] - 评估某个概念的掌握程度
socratic <任务> - 开始苏格拉底式评估
answer <回答> - 回答苏格拉底追问
explain - 请求直接解释（退出追问模式）
```

### 生成报告
```
学习报告 - 生成学习报告（包含思维导图）
导出记录 - 导出完整的学习记录
```

---

## 典型对话流程

### 场景1：开始学习新主题

```
用户：学习 机器学习

教练：🎯 检测到学习意图：机器学习

      快速确认一下你的情况：
      
      1. 你的基础是？
         a) 零基础
         b) 有编程基础
         c) 了解基本概念
         d) 有一定经验
      
      2. 你的学习目标是？
         a) 快速了解（1-2周）
         b) 系统学习（1-3个月）
         c) 求职准备（3-6个月）

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

### 场景2：元认知监控循环

```
教练：🧠 当前任务：理解监督学习

      让我评估一下你的掌握程度...

      【问题1】你能用自己的话解释什么是监督学习吗？
      a) 可以清晰解释
      b) 能说个大概
      c) 不太清楚
      d) 完全不知道

用户：b

教练：【问题2】监督学习和无监督学习的区别是什么？
      a) 完全清楚
      b) 大概知道
      c) 有点模糊
      d) 完全不清楚

用户：b

教练：【问题3】你能举一个监督学习的应用例子吗？
      a) 可以举多个例子
      b) 能举一个例子
      c) 想不起来
      d) 不知道

用户：b

教练：📊 掌握度评估结果：

      - 表层理解：✅ 70%
      - 语义理解：🟡 50%
      - 直觉理解：⚠️ 30%
      
      综合掌握度：50%（目标：80%）

      ⚠️ 检测到问题：你对监督学习的核心思想理解不够深入

      📝 推荐策略：
      1. 观看推荐视频：《吴恩达机器学习》第1-2周
      2. 阅读推荐文章：监督学习入门指南
      3. 动手实践：实现一个简单的线性回归

      你想：
      1. 继续深入当前任务
      2. 切换到前置知识（统计学基础）
      3. 先休息，稍后继续
```

### 场景3：断点续学

```
用户：继续

教练：🎯 检测到你上次的学习进度！

      【学习主题】机器学习
      【当前任务】理解监督学习
      【掌握度】50%
      【上次学习】2026-03-18 16:30

      你想：
      1. 继续学习监督学习
      2. 查看学习报告
      3. 切换到其他主题
```

### 场景4：切换学习目标

```
用户：学习目标列表

教练：📚 你当前的学习目标：

      1. 机器学习（进度：15%）
         - 当前任务：监督学习
         - 上次学习：2026-03-18 16:30
         
      2. 英语口语（进度：30%）
         - 当前任务：发音练习
         - 上次学习：2026-03-17 20:15

用户：切换目标 英语口语

教练：✅ 已切换到【英语口语】

      【当前任务】发音练习
      【掌握度】60%
      
      准备继续了吗？
```

### 场景5：苏格拉底式追问（v1.2.0 新增）

```
用户：学习 Python编程 --level 零基础

教练：🎯 检测到学习意图：Python编程
      ✅ 已自动启用苏格拉底优先模式（零基础）
      
      📋 学习档案已建立！
      【学习主题】Python编程
      【当前基础】零基础
      【苏格拉底模式】开启

用户：socratic 变量

教练：🤔 【苏格拉底式追问 · 第1/3轮】

      📍 维度：澄清
      
      ❓ 你具体指的是什么？
      
      💭 提示：能举个例子吗？
      
      ━━━━━━━━━━━━━━━━━━━━
      [直接解释] 跳过追问，直接讲解
      [继续追问] 继续深入探索
      ━━━━━━━━━━━━━━━━━━━━

用户：answer 我知道变量用来存数据，但不太清楚具体怎么用

教练：💡 回答中包含疑问
      
      🤔 【苏格拉底式追问 · 第2/3轮】
      
      📍 维度：假设
      
      ❓ 这个结论背后有哪些前提？
      
      💭 提示：你基于什么做出这个判断？
      
      ━━━━━━━━━━━━━━━━━━━━
      [直接解释] 跳过追问，直接讲解
      [继续追问] 继续深入探索
      ━━━━━━━━━━━━━━━━━━━━

用户：直接解释

教练：📚 用户选择直接解释
      已探索维度：澄清, 假设
      追问轮数：2
      
      📊 估计掌握度：25%
      
      正在生成直接解释...
      
      [概念讲解内容]
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
          "status": "in_progress",
          "last_study": "2026-03-18T16:30:00"
        },
        {
          "name": "无监督学习",
          "mastery": 0,
          "time_spent": "0h",
          "status": "not_started"
        }
      ],
      "current_task": "监督学习",
      "overall_progress": 0.15
    }
  ]
}
```

### 认知循环日志 (data/records.json)

```json
{
  "records": [
    {
      "id": "record-001",
      "profile_id": "uuid-123",
      "timestamp": "2026-03-18T16:30:00",
      "task": {
        "name": "监督学习",
        "importance": 5,
        "difficulty": 3
      },
      "assessment": {
        "questions": [
          {"question": "...", "answer": "b"},
          {"question": "...", "answer": "b"}
        ],
        "mastery_level": 0.5,
        "mastery_breakdown": {
          "surface": 0.7,
          "semantic": 0.5,
          "intuitive": 0.3
        }
      },
      "decision": {
        "action": "continue",
        "strategy": ["观看视频", "阅读文章", "动手实践"],
        "reason": "掌握度不足，建议继续深入"
      },
      "time_spent": "30min"
    }
  ]
}
```

---

## 核心算法

### 1. 掌握度评估算法

```python
def calculate_mastery(answers):
    """
    计算掌握度
    - 表层理解：能识别、能回忆
    - 语义理解：能解释、能说明
    - 直觉理解：能应用、能举例
    
    权重：表层 0.2, 语义 0.3, 直觉 0.5
    """
    mastery = {
        "surface": answers.get("surface", 0),
        "semantic": answers.get("semantic", 0),
        "intuitive": answers.get("intuitive", 0)
    }
    
    overall = (
        mastery["surface"] * 0.2 +
        mastery["semantic"] * 0.3 +
        mastery["intuitive"] * 0.5
    )
    
    return {"overall": overall, "breakdown": mastery}
```

### 2. 任务选择算法

```python
def select_task(tasks):
    """
    选择最重要的任务
    优先级：未开始 > 进行中 > 已完成
    重要性：核心概念 > 重要概念 > 基础概念
    """
    # 过滤未完成的任务
    incomplete = [t for t in tasks if t["mastery"] < 0.8]
    
    if not incomplete:
        return None  # 所有任务已完成
    
    # 按重要性和掌握度排序
    incomplete.sort(key=lambda t: (
        -t.get("importance", 3),  # 重要性高的优先
        t["mastery"]               # 掌握度低的优先
    ))
    
    return incomplete[0]
```

### 3. 策略推荐算法

```python
def recommend_strategy(task, mastery):
    """
    根据任务和掌握度推荐学习策略
    """
    strategies = []
    
    if mastery["overall"] < 0.3:
        # 低掌握度：从基础开始
        strategies = [
            "观看入门视频",
            "阅读基础教程",
            "寻找前置知识"
        ]
    elif mastery["overall"] < 0.6:
        # 中等掌握度：深入理解
        strategies = [
            "阅读进阶文章",
            "完成练习题",
            "动手实践"
        ]
    else:
        # 较高掌握度：巩固应用
        strategies = [
            "完成项目",
            "教给他人",
            "应用到新场景"
        ]
    
    return strategies
```

---

## 文件结构

```
learning-coach/
├── SKILL.md                 # 本文档
├── scripts/
│   ├── coach.py             # 主程序
│   └── obsidian_sync.py     # Obsidian 同步（→ skills/obsidian-vault/scripts/obsidian_sync.py）
├── data/
│   ├── profiles.json        # 学习档案
│   └── records.json         # 认知循环日志
└── mindmaps/
    └── *.md                 # 生成的思维导图
```

---

## 使用注意事项

### ⚠️ 数据持久化

- 所有学习进度自动保存到 `data/profiles.json`
- 每次认知循环记录保存到 `data/records.json`
- 可以随时导出或备份这些文件

### ⚠️ 断点续学

- 每次使用"继续"命令时，会自动加载上次的学习进度
- 支持跨会话续学（关闭后再打开）

### ⚠️ 多目标管理

- 可以同时追踪多个学习主题
- 每个主题独立记录进度和认知循环
- 可以随时切换，不会丢失进度

---

## 后续优化方向

### Phase 2（可选）
- [ ] 学习资源推荐（集成搜索）
- [ ] 前置知识检测
- [ ] 学习计划制定
- [ ] 可视化进度图表

### Phase 3（可选）
- [ ] 个性化适配
- [ ] 游戏化元素
- [ ] 知识图谱可视化

---

## 参考文献

1. Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *The Psychology of Learning and Motivation*.

2. Ausubel, D. P. (1968). *Educational Psychology: A Cognitive View*. Holt, Rinehart & Winston.

3. 老奇好好奇. (2026). 一名年更UP主的三年：我们是如何快速学习陌生领域的？[视频]. Bilibili.

---

## 更新日志

### v1.2.0 (2026-04-03)
- ✨ 苏格拉底式追问集成（Phase 1）
- ✅ 6维度追问框架：澄清→假设→证据→视角→后果→反思
- ✅ SOCRATIC_PRIORITY 模式：零基础自动启用
- ✅ 最大追问次数限制：每个学习目标最多3轮
- ✅ 退出机制："直接解释"选项随时可用
- ✅ 基于追问历史的掌握度评估
- ✅ 向后兼容：原有功能不受影响

### v1.1.0 (2026-03-28)
- ✅ Obsidian 知识库集成（学习记录持久化）
- ✅ 学习档案同步到 Obsidian `_profiles/`
- ✅ 认知循环记录同步到 `_sessions/`
- ✅ 掌握度≥80%自动创建原子笔记到 `_insights/`
- ✅ 思维导图同步到 `_maps/`
- ✅ 启动时从 Obsidian 读取学习上下文

### v1.0.0 (2026-03-18)
- ✨ 初始版本
- ✅ 元认知监控循环（简化版）
- ✅ 断点续学
- ✅ 多目标管理
- ✅ 认知循环记录
- ✅ 思维导图生成

---

## Obsidian 知识库集成

> 学习数据（JSON）是机器可读的中间态，Obsidian（Markdown）是人类可读的终态。

### 同步命令

使用 `obsidian-vault` skill 提供的同步工具：

```bash
# 同步学习档案
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-profile \
  --profile-json '{"topic":"机器学习","level":"有基础","goal":"求职","overall_progress":0.5}'

# 同步认知循环
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-session \
  --topic "机器学习" \
  --record-json '{"task":{"name":"监督学习"},"assessment":{"mastery_level":0.5}}'

# 同步学习洞察（掌握度≥80%时触发）
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-insight \
  --concept "监督学习" --topic "机器学习" --content "核心要义"

# 同步思维导图
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-mindmap \
  --topic "机器学习" --mermaid "mindmap\n  root((ML))\n    监督学习"

# 读取学习上下文（启动时）
python3 skills/obsidian-vault/scripts/obsidian_sync.py learning-context --topic "机器学习"
```

### Obsidian 目录结构

```
00_Learning/
├── README.md                    ← 学习总览（自动生成）
├── _profiles/{topic}.md         ← 学习档案
├── _sessions/{date}-{task}-认知循环.md  ← 认知循环记录
├── _insights/{concept}.md       ← 学习洞察（原子笔记）
└── _maps/{topic}-认知地图.md    ← 思维导图
```

### 同步时机

| 事件 | 操作 | 条件 |
|------|------|------|
| 创建/更新学习档案 | → `_profiles/{topic}.md` | 每次建档或进度更新 |
| 完成认知循环 | → `_sessions/{date}-{task}-认知循环.md` | 每次评估完成 |
| 掌握度达标 | → `_insights/{concept}.md` | 掌握度 ≥ 80% |
| 生成认知地图 | → `_maps/{topic}-认知地图.md` | 首次生成路径 |
| 启动会话 | ← 读取 Obsidian 上下文 | 用户说"继续学" |

### AI 操作指南

1. **认知循环完成后**：调用 `learning-session` 同步记录，然后调用 `learning-profile` 更新档案
2. **掌握度 ≥ 80%**：额外调用 `learning-insight` 创建原子笔记
3. **用户说"继续学"**：先调用 `learning-context` 读取上次进度
4. **生成认知地图**：调用 `learning-mindmap` 同步