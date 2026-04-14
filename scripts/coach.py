#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习教练 (Learning Coach)
基于元认知监控模型的学习辅助系统

核心功能：
1. 元认知监控循环
2. 断点续学
3. 多目标管理
4. 认知循环记录
5. 思维导图生成
6. 苏格拉底式追问（嵌入式）
"""

import json
import os
import re
import shlex
import sys
import random
from datetime import datetime
from pathlib import Path
import uuid

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
PROFILES_FILE = DATA_DIR / "profiles.json"
RECORDS_FILE = DATA_DIR / "records.json"
MINDMAPS_DIR = Path(__file__).parent.parent / "mindmaps"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
MINDMAPS_DIR.mkdir(parents=True, exist_ok=True)


def safe_topic_dirname(topic):
    """将学习主题转换为适合 Windows 文件夹的名称。"""
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", (topic or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or "未命名主题"


def parse_start_arguments(tokens):
    """解析 start 命令参数，支持多词主题。"""
    topic_parts = []
    level = "未设置"
    goal = "未设置"
    time_budget = None
    i = 0

    while i < len(tokens):
        token = tokens[i]
        if token == "--level" and i + 1 < len(tokens):
            level = tokens[i + 1]
            i += 2
            continue
        if token == "--goal" and i + 1 < len(tokens):
            goal = tokens[i + 1]
            i += 2
            continue
        if token == "--time-budget" and i + 1 < len(tokens):
            time_budget = tokens[i + 1]
            i += 2
            continue

        topic_parts.append(token)
        i += 1

    topic = " ".join(topic_parts).strip()
    return topic, level, goal, time_budget


DOMAIN_BLUEPRINTS = {
    "bim_engineering": {
        "keywords": [
            "bim", "ifc", "revit", "工程", "建筑", "机电", "构件", "模型审核",
            "审图", "图结构", "数字孪生", "施工"
        ],
        "label": "BIM/工程数字化",
        "tasks": [
            {
                "name_template": "{topic}业务场景与审核目标梳理",
                "importance": 5,
                "desc_template": "明确{topic}的业务边界、目标指标、输入输出与典型问题。"
            },
            {
                "name_template": "{topic}数据源解析与模型结构理解",
                "importance": 5,
                "desc_template": "识别 IFC/Revit 等数据来源、构件关系与工程语义。"
            },
            {
                "name_template": "{topic}构件属性映射与图表示建模",
                "importance": 5,
                "desc_template": "把构件、属性、空间或连接关系映射成可计算的图或结构化表示。"
            },
            {
                "name_template": "{topic}规则逻辑与算法方案设计",
                "importance": 4,
                "desc_template": "设计审核规则、模型流程或规则与模型融合方案。"
            },
            {
                "name_template": "{topic}实战验证、报告输出与闭环优化",
                "importance": 4,
                "desc_template": "落地验证审核效果，输出报告，并根据误报漏报持续优化。"
            }
        ]
    },
    "ai_ml": {
        "keywords": [
            "机器学习", "深度学习", "神经网络", "gnn", "transformer", "llm",
            "大模型", "attention", "监督学习", "强化学习", "embedding", "图神经"
        ],
        "label": "AI/机器学习",
        "tasks": [
            {
                "name_template": "{topic}问题定义与任务形式化",
                "importance": 5,
                "desc_template": "明确{topic}要解决的任务类型、评价指标与训练目标。"
            },
            {
                "name_template": "{topic}核心概念、数学直觉与关键机制",
                "importance": 5,
                "desc_template": "理解{topic}的核心机制、关键公式和直觉解释。"
            },
            {
                "name_template": "{topic}数据表示、特征构造与输入输出设计",
                "importance": 5,
                "desc_template": "明确样本、标签、特征、结构信息与模型输入输出。"
            },
            {
                "name_template": "{topic}训练流程、调参与误差分析",
                "importance": 4,
                "desc_template": "掌握训练流程、超参数影响、常见失败模式与调试方法。"
            },
            {
                "name_template": "{topic}应用落地、泛化验证与复盘迁移",
                "importance": 4,
                "desc_template": "把{topic}迁移到真实场景，并分析泛化能力与适用边界。"
            }
        ]
    },
    "programming": {
        "keywords": [
            "python", "java", "javascript", "typescript", "react", "vue", "go",
            "rust", "c++", "框架", "前端", "后端", "api", "django", "flask", "spring"
        ],
        "label": "编程语言/框架",
        "tasks": [
            {
                "name_template": "{topic}核心语法与基本心智模型",
                "importance": 5,
                "desc_template": "建立{topic}的语法基础、执行模型与常用抽象。"
            },
            {
                "name_template": "{topic}关键组件与运行机制",
                "importance": 5,
                "desc_template": "理解框架组件、生命周期、依赖关系和底层机制。"
            },
            {
                "name_template": "{topic}典型项目结构与常见模式",
                "importance": 4,
                "desc_template": "熟悉工程目录、常见设计模式和最佳实践。"
            },
            {
                "name_template": "{topic}调试、测试与性能优化",
                "importance": 4,
                "desc_template": "掌握调试方法、测试策略以及性能与可维护性优化。"
            },
            {
                "name_template": "{topic}项目实战与知识迁移",
                "importance": 4,
                "desc_template": "通过项目把{topic}迁移到真实开发场景。"
            }
        ]
    },
    "data_systems": {
        "keywords": [
            "数据库", "sql", "etl", "数据仓库", "spark", "hadoop", "kafka",
            "airflow", "数据治理", "数据分析", "pipeline", "湖仓"
        ],
        "label": "数据工程/数据系统",
        "tasks": [
            {
                "name_template": "{topic}业务问题与数据链路梳理",
                "importance": 5,
                "desc_template": "明确{topic}中的业务目标、数据来源与链路边界。"
            },
            {
                "name_template": "{topic}数据模型、表结构与存储设计",
                "importance": 5,
                "desc_template": "理解表结构、索引、分区、建模方式与存储权衡。"
            },
            {
                "name_template": "{topic}处理流程、调度与质量控制",
                "importance": 5,
                "desc_template": "掌握采集、清洗、调度、重跑与质量校验流程。"
            },
            {
                "name_template": "{topic}性能、稳定性与异常排查",
                "importance": 4,
                "desc_template": "定位瓶颈、优化资源、处理延迟和失败重试。"
            },
            {
                "name_template": "{topic}场景应用、报表服务与复盘优化",
                "importance": 4,
                "desc_template": "把数据系统能力连接到分析、服务和持续优化闭环。"
            }
        ]
    }
}


# ==================== 苏格拉底追问配置 ====================

SOCRATIC_CONFIG = {
    "max_rounds": 3,  # 每个学习目标最多追问轮数
    "dimensions_order": ["clarify", "assumption", "evidence", "perspective", "consequence", "reflection"],
    "exit_options": {
        "explain": "直接解释",
        "continue": "继续追问"
    }
}

SOCRATIC_DIMENSIONS = {
    "clarify": {
        "name": "澄清",
        "question": "你具体指的是什么？",
        "prompts": [
            "能举个例子吗？",
            "哪个部分让你困惑？",
            "这个概念的核心是什么？",
            "用你自己的话说说看？"
        ]
    },
    "assumption": {
        "name": "假设",
        "question": "这个结论背后有哪些前提？",
        "prompts": [
            "你基于什么做出这个判断？",
            "有什么隐含的假设？",
            "这些前提成立吗？",
            "有没有前提被忽略了？"
        ]
    },
    "evidence": {
        "name": "证据",
        "question": "你依据的事实来自哪里？",
        "prompts": [
            "有数据支持吗？",
            "这个信息可靠吗？",
            "能找到反例吗？",
            "来源是什么？"
        ]
    },
    "perspective": {
        "name": "视角",
        "question": "还有谁可能持不同立场？",
        "prompts": [
            "从另一个角度看会怎样？",
            "反对意见是什么？",
            "为什么会有分歧？",
            "有没有其他解释？"
        ]
    },
    "consequence": {
        "name": "后果",
        "question": "如果这是真的会带来什么结果？",
        "prompts": [
            "接下来会发生什么？",
            "有什么影响？",
            "这会导致什么？",
            "短期和长期各有什么影响？"
        ]
    },
    "reflection": {
        "name": "反思",
        "question": "有什么被忽略或需要修正的地方？",
        "prompts": [
            "我们遗漏了什么？",
            "哪里可能有误解？",
            "需要重新思考什么？",
            "这个理解完整吗？"
        ]
    }
}


class SocraticQuestioner:
    """苏格拉底式追问引擎"""
    
    def __init__(self, config=None):
        self.config = config or SOCRATIC_CONFIG
        self.history = []  # 追问历史记录
        self.current_round = 0
        self.used_dimensions = set()
    
    def reset(self):
        """重置追问状态"""
        self.history = []
        self.current_round = 0
        self.used_dimensions = set()
    
    def get_next_dimension(self):
        """获取下一个追问维度"""
        available = [d for d in self.config["dimensions_order"] 
                     if d not in self.used_dimensions]
        if not available:
            # 所有维度都用过了，重置
            self.used_dimensions = set()
            available = self.config["dimensions_order"]
        return available[0] if available else None
    
    def generate_question(self, task_name, context=None):
        """
        生成苏格拉底式追问
        
        Args:
            task_name: 学习任务名称
            context: 上下文信息（上次回答等）
        
        Returns:
            dict: {
                "dimension": 维度名称,
                "main_question": 主问题,
                "prompt": 引导语,
                "round": 当前轮数,
                "options": 可选操作
            }
        """
        if self.current_round >= self.config["max_rounds"]:
            return None  # 达到上限
        
        dimension = self.get_next_dimension()
        if not dimension:
            return None
        
        dim_config = SOCRATIC_DIMENSIONS[dimension]
        prompt = random.choice(dim_config["prompts"])
        
        self.current_round += 1
        self.used_dimensions.add(dimension)
        
        question = {
            "dimension": dimension,
            "dimension_name": dim_config["name"],
            "main_question": dim_config["question"],
            "prompt": prompt,
            "round": self.current_round,
            "max_rounds": self.config["max_rounds"],
            "options": self.config["exit_options"],
            "task_name": task_name
        }
        
        self.history.append({
            "round": self.current_round,
            "dimension": dimension,
            "question": question
        })
        
        return question
    
    def process_answer(self, answer, auto_continue=True):
        """
        处理用户回答
        
        Args:
            answer: 用户回答（可以是文本或选项）
            auto_continue: 是否自动判断是否继续
        
        Returns:
            dict: {
                "action": "continue" | "explain" | "complete",
                "reason": 原因说明
            }
        """
        # 检查是否请求直接解释
        if isinstance(answer, str):
            if "直接解释" in answer or answer.lower() == "explain":
                return {"action": "explain", "reason": "用户选择直接解释"}
        
        # 记录回答
        if self.history:
            self.history[-1]["answer"] = answer
        
        # 检查是否达到上限
        if self.current_round >= self.config["max_rounds"]:
            return {"action": "explain", "reason": "已达到最大追问轮数"}
        
        # 判断回答质量（简单启发式）
        if isinstance(answer, str):
            # 短回答可能需要继续追问
            if len(answer) < 10:
                return {"action": "continue", "reason": "回答较短，继续深入"}
            # 包含疑问可能需要澄清
            if "?" in answer or "？" in answer:
                return {"action": "continue", "reason": "回答中包含疑问"}
        
        # 默认继续
        if auto_continue and self.current_round < self.config["max_rounds"]:
            return {"action": "continue", "reason": "继续深入探索"}
        
        return {"action": "complete", "reason": "评估完成"}
    
    def should_continue(self):
        """判断是否应该继续追问"""
        return self.current_round < self.config["max_rounds"]
    
    def get_summary(self):
        """获取追问总结"""
        return {
            "total_rounds": self.current_round,
            "dimensions_explored": list(self.used_dimensions),
            "history": self.history
        }

    def dump_state(self):
        """导出追问状态，便于跨命令恢复。"""
        return {
            "history": self.history,
            "current_round": self.current_round,
            "used_dimensions": list(self.used_dimensions)
        }

    def load_state(self, state):
        """恢复追问状态。"""
        state = state or {}
        self.history = state.get("history", [])
        self.current_round = state.get("current_round", 0)
        self.used_dimensions = set(state.get("used_dimensions", []))
    
    def format_question(self, question):
        """格式化问题用于显示"""
        if not question:
            return ""
        
        lines = [
            f"🤔 【苏格拉底式追问 · 第{question['round']}/{question['max_rounds']}轮】",
            f"",
            f"📍 维度：{question['dimension_name']}",
            f"",
            f"❓ {question['main_question']}",
            f"",
            f"💭 提示：{question['prompt']}",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"[直接解释] 跳过追问，直接讲解",
            f"[继续追问] 继续深入探索",
            f"━━━━━━━━━━━━━━━━━━━━"
        ]
        return "\n".join(lines)


class LearningCoach:
    """学习教练主类"""
    
    def __init__(self):
        self.profiles = self._load_profiles()
        self.records = self._load_records()
        self.current_profile = None
        self.socratic_questioner = SocraticQuestioner()  # 苏格拉底追问引擎
        self.socratic_mode = False  # 当前是否处于苏格拉底模式
        self._cleanup_duplicate_profiles()
    
    # ==================== 数据管理 ====================
    
    def _load_profiles(self):
        """加载学习档案"""
        if PROFILES_FILE.exists():
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"profiles": []}
    
    def _save_profiles(self):
        """保存学习档案"""
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)
    
    def _load_records(self):
        """加载认知循环日志"""
        if RECORDS_FILE.exists():
            with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"records": []}
    
    def _save_records(self):
        """保存认知循环日志"""
        with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def _parse_iso_datetime(self, value):
        """解析 ISO 时间字符串，失败时返回最小时间，便于排序。"""
        if not value:
            return datetime.min
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.min

    def _is_blank_profile(self, profile):
        """判断是否为空白学习档案。"""
        tasks = profile.get("tasks") or []
        current_task = profile.get("current_task")
        progress = profile.get("overall_progress", 0) or 0
        return not tasks and not current_task and progress <= 0

    def _ensure_profile_defaults(self, profile):
        """补齐学习档案缺失字段，兼容旧数据结构。"""
        changed = False
        defaults = {
            "time_budget": None,
            "tasks": [],
            "current_task": None,
            "overall_progress": 0.0,
            "socratic_mode": None,
            "socratic_round_count": 0,
            "socratic_session": None,
            "monitoring_history": [],
            "last_assessment": None,
            "last_strategy": [],
            "task_tree_metadata": None,
            "status": "active"
        }

        for key, value in defaults.items():
            if key not in profile:
                profile[key] = list(value) if isinstance(value, list) else value
                changed = True

        return changed

    def _cleanup_duplicate_profiles(self):
        """按主题清理重复档案，优先保留有学习进度的记录。"""
        profiles = self.profiles.get("profiles", [])
        grouped = {}
        changed = False

        for profile in profiles:
            if self._ensure_profile_defaults(profile):
                changed = True

        for profile in profiles:
            topic = (profile.get("topic") or "").strip()
            grouped.setdefault(topic, []).append(profile)

        cleaned_profiles = []
        for topic, topic_profiles in grouped.items():
            if len(topic_profiles) == 1:
                cleaned_profiles.extend(topic_profiles)
                continue

            non_blank_profiles = [p for p in topic_profiles if not self._is_blank_profile(p)]
            blank_profiles = [p for p in topic_profiles if self._is_blank_profile(p)]

            if non_blank_profiles:
                non_blank_profiles.sort(
                    key=lambda p: self._parse_iso_datetime(p.get("updated_at")),
                    reverse=True
                )
                cleaned_profiles.extend(non_blank_profiles)
                if blank_profiles:
                    changed = True
                continue

            # 同主题全部为空白时，仅保留最近一条。
            blank_profiles.sort(
                key=lambda p: self._parse_iso_datetime(p.get("updated_at")),
                reverse=True
            )
            cleaned_profiles.append(blank_profiles[0])
            if len(blank_profiles) > 1:
                changed = True

        if changed:
            self.profiles["profiles"] = cleaned_profiles
            self._save_profiles()

    def _monitoring_history(self, profile):
        """返回档案的监控历史列表。"""
        return profile.setdefault("monitoring_history", [])

    def _latest_monitoring(self, profile):
        """获取最近一次元认知监控记录。"""
        history = self._monitoring_history(profile)
        return history[-1] if history else None

    def _restore_socratic_session(self, profile):
        """从档案恢复苏格拉底会话状态。"""
        session = profile.get("socratic_session")
        if not session or not session.get("active"):
            return False

        self.current_profile = profile
        self.socratic_mode = True
        self.socratic_questioner.load_state(session.get("questioner_state"))
        profile["socratic_round_count"] = self.socratic_questioner.current_round
        return True

    def _persist_socratic_session(self, profile, task_name):
        """持久化苏格拉底会话，支持跨命令继续。"""
        profile["socratic_session"] = {
            "active": True,
            "task_name": task_name,
            "questioner_state": self.socratic_questioner.dump_state()
        }
        profile["socratic_round_count"] = self.socratic_questioner.current_round
        self._save_profiles()

    def _clear_socratic_session(self, profile):
        """清理已结束的苏格拉底会话。"""
        profile["socratic_session"] = None
        profile["socratic_round_count"] = 0
        self._save_profiles()

    def _default_learning_tasks(self, topic, goal=None):
        """为新主题生成通用学习路径。"""
        focus = goal or topic
        return [
            {
                "name": f"{topic}概念地图与关键术语",
                "importance": 5,
                "desc": f"建立{topic}的基本词汇表、问题空间与核心对象。"
            },
            {
                "name": f"{topic}核心机制与基本原理",
                "importance": 5,
                "desc": f"理解{topic}成立的关键机制、主流程与因果关系。"
            },
            {
                "name": f"{topic}典型示例拆解与理解",
                "importance": 4,
                "desc": f"通过代表性案例理解{topic}如何在真实问题中工作。"
            },
            {
                "name": f"{topic}动手练习与错误修正",
                "importance": 4,
                "desc": f"通过练习暴露误解并修正关于{topic}的薄弱点。"
            },
            {
                "name": f"{focus}应用实践与迁移复盘",
                "importance": 3,
                "desc": f"把{topic}迁移到目标场景，并复盘哪些能力已经稳定掌握。"
            }
        ]

    def _infer_domain_blueprint(self, topic, goal=None):
        """根据主题和目标推断最匹配的领域蓝图。"""
        haystack = f"{topic or ''} {goal or ''}".lower()
        best_key = None
        best_score = 0
        matched_keywords = []

        for domain_key, blueprint in DOMAIN_BLUEPRINTS.items():
            hits = [kw for kw in blueprint["keywords"] if kw.lower() in haystack]
            if len(hits) > best_score:
                best_key = domain_key
                best_score = len(hits)
                matched_keywords = hits

        if best_key:
            return {
                "domain": best_key,
                "label": DOMAIN_BLUEPRINTS[best_key]["label"],
                "matched_keywords": matched_keywords,
                "source": "domain_blueprint"
            }

        return {
            "domain": "generic",
            "label": "通用学习路径",
            "matched_keywords": [],
            "source": "generic_fallback"
        }

    def _build_tasks_from_blueprint(self, topic, goal=None):
        """按领域蓝图或通用模板生成任务树。"""
        metadata = self._infer_domain_blueprint(topic, goal)
        if metadata["domain"] == "generic":
            task_specs = self._default_learning_tasks(topic, goal)
        else:
            task_specs = []
            blueprint = DOMAIN_BLUEPRINTS[metadata["domain"]]
            focus = goal or topic
            for item in blueprint["tasks"]:
                task_specs.append({
                    "name": item["name_template"].format(topic=topic, goal=goal or topic, focus=focus),
                    "importance": item["importance"],
                    "desc": item["desc_template"].format(topic=topic, goal=goal or topic, focus=focus)
                })

        tasks = []
        for item in task_specs:
            tasks.append({
                "name": item["name"],
                "mastery": 0.0,
                "time_spent": "0h",
                "status": "not_started",
                "importance": item["importance"],
                "last_study": None,
                "desc": item.get("desc", "暂无详细说明")
            })

        return tasks, metadata

    def _ensure_task_tree_metadata(self, profile):
        """为旧档案补齐任务树元信息。"""
        if profile.get("task_tree_metadata"):
            return False
        profile["task_tree_metadata"] = self._infer_domain_blueprint(
            profile.get("topic"),
            profile.get("goal")
        )
        return True

    def _bootstrap_profile_tasks(self, profile):
        """在新档案为空时生成默认学习路径。"""
        if profile.get("tasks"):
            self._ensure_task_tree_metadata(profile)
            return

        tasks, metadata = self._build_tasks_from_blueprint(profile["topic"], profile.get("goal"))
        profile["tasks"] = tasks
        profile["task_tree_metadata"] = metadata
        next_task = self.select_task(profile)
        profile["current_task"] = next_task["name"] if next_task else None
        profile["updated_at"] = datetime.now().isoformat()

    def _record_monitoring_cycle(self, profile, task_name, mastery, strategy, source, notes=None, time_spent="0h"):
        """记录一次完整的监控-控制循环。"""
        assessment = {
            "mastery": mastery,
            "source": source
        }
        record = {
            "timestamp": datetime.now().isoformat(),
            "task_name": task_name,
            "assessment": assessment,
            "strategy": strategy,
            "notes": notes or ""
        }
        self._monitoring_history(profile).append(record)
        profile["last_assessment"] = assessment
        profile["last_strategy"] = strategy
        profile["updated_at"] = datetime.now().isoformat()
        self.create_record(profile["id"], {"name": task_name}, assessment, strategy, time_spent)
        self._save_profiles()
        return record
    
    # ==================== 学习档案管理 ====================
    
    def create_profile(self, topic, level, goal, time_budget=None):
        """创建学习档案"""
        topic = (topic or "").strip()

        # 同主题已有学习进度时，直接复用最新档案，避免生成重复空白记录。
        existing_profiles = [
            p for p in self.profiles["profiles"]
            if (p.get("topic") or "").strip() == topic
        ]
        progressed_profiles = [p for p in existing_profiles if not self._is_blank_profile(p)]
        if progressed_profiles:
            progressed_profiles.sort(
                key=lambda p: self._parse_iso_datetime(p.get("updated_at")),
                reverse=True
            )
            profile = progressed_profiles[0]
            self._ensure_profile_defaults(profile)
            if self._ensure_task_tree_metadata(profile):
                self._save_profiles()
            self.current_profile = profile
            self.socratic_mode = profile.get("socratic_mode") == "SOCRATIC_PRIORITY"
            return profile

        # 同主题已有空白档案时，复用并刷新元数据，而不是继续追加。
        blank_profiles = [p for p in existing_profiles if self._is_blank_profile(p)]
        if blank_profiles:
            blank_profiles.sort(
                key=lambda p: self._parse_iso_datetime(p.get("updated_at")),
                reverse=True
            )
            profile = blank_profiles[0]
            profile.update({
                "level": level,
                "goal": goal,
                "time_budget": time_budget,
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                "socratic_mode": "SOCRATIC_PRIORITY" if level == "零基础" else None
            })
            self._ensure_profile_defaults(profile)
            self._bootstrap_profile_tasks(profile)
            self._save_profiles()
            self.current_profile = profile
            if profile.get("socratic_mode") == "SOCRATIC_PRIORITY":
                self.socratic_questioner.reset()
                self.socratic_mode = True
            else:
                self.socratic_mode = False
            return profile

        # 判断是否启用苏格拉底优先模式
        socratic_mode = "SOCRATIC_PRIORITY" if level == "零基础" else None
        
        profile = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "level": level,
            "goal": goal,
            "time_budget": time_budget,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "tasks": [],
            "current_task": None,
            "overall_progress": 0.0,
            "socratic_mode": socratic_mode,  # 苏格拉底模式标志
            "socratic_round_count": 0,  # 当前追问轮数
            "monitoring_history": [],
            "last_assessment": None,
            "last_strategy": [],
            "task_tree_metadata": None
        }
        
        self._bootstrap_profile_tasks(profile)
        self.profiles["profiles"].append(profile)
        self._save_profiles()
        
        self.current_profile = profile
        
        # 如果启用苏格拉底优先模式，重置追问引擎
        if socratic_mode == "SOCRATIC_PRIORITY":
            self.socratic_questioner.reset()
            self.socratic_mode = True
        
        return profile
    
    def get_profile(self, topic=None):
        """获取学习档案"""
        if topic:
            for p in self.profiles["profiles"]:
                if p["topic"] == topic:
                    self._ensure_profile_defaults(p)
                    self._ensure_task_tree_metadata(p)
                    return p
            return None
        elif self.current_profile:
            self._ensure_profile_defaults(self.current_profile)
            self._ensure_task_tree_metadata(self.current_profile)
            return self.current_profile
        elif self.profiles["profiles"]:
            # 返回最近更新的档案
            profile = sorted(
                self.profiles["profiles"],
                key=lambda x: x["updated_at"],
                reverse=True
            )[0]
            self._ensure_profile_defaults(profile)
            self._ensure_task_tree_metadata(profile)
            return profile
        return None
    
    def list_profiles(self):
        """列出所有学习档案"""
        return self.profiles["profiles"]
    
    def switch_profile(self, topic):
        """切换学习目标"""
        profile = self.get_profile(topic)
        if profile:
            self.current_profile = profile
            profile["updated_at"] = datetime.now().isoformat()
            # 根据档案的苏格拉底模式设置状态
            if profile.get("socratic_mode") == "SOCRATIC_PRIORITY":
                self.socratic_mode = True
                self.socratic_questioner.reset()
            else:
                self.socratic_mode = False
            self._save_profiles()
            return profile
        return None
    
    def toggle_socratic_mode(self, enable=True):
        """切换苏格拉底模式"""
        self.socratic_mode = enable
        if enable:
            self.socratic_questioner.reset()
        if self.current_profile:
            self.current_profile["socratic_mode"] = "SOCRATIC_PRIORITY" if enable else None
            self._save_profiles()
        return self.socratic_mode
    
    def update_profile(self, profile_id, updates):
        """更新学习档案"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                p.update(updates)
                p["updated_at"] = datetime.now().isoformat()
                self._save_profiles()
                return p
        return None
    
    # ==================== 任务管理 ====================
    
    def add_task(self, profile_id, task_name, importance=3):
        """添加学习任务"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                for existing in p["tasks"]:
                    if existing["name"] == task_name:
                        return existing
                task = {
                    "name": task_name,
                    "mastery": 0.0,
                    "time_spent": "0h",
                    "status": "not_started",
                    "importance": importance,
                    "last_study": None
                }
                p["tasks"].append(task)
                if not p.get("current_task"):
                    p["current_task"] = task_name
                p["updated_at"] = datetime.now().isoformat()
                self._save_profiles()
                return task
        return None
    
    def update_task(self, profile_id, task_name, mastery, time_spent=None):
        """更新任务进度"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                normalized_mastery = max(0.0, min(1.0, mastery))
                for t in p["tasks"]:
                    if t["name"] == task_name:
                        t["mastery"] = normalized_mastery
                        if normalized_mastery <= 0:
                            t["status"] = "not_started"
                        elif normalized_mastery < 0.8:
                            t["status"] = "in_progress"
                        else:
                            t["status"] = "completed"
                        if time_spent:
                            t["time_spent"] = time_spent
                        t["last_study"] = datetime.now().isoformat()
                        
                        # 更新整体进度
                        if p["tasks"]:
                            p["overall_progress"] = sum(t["mastery"] for t in p["tasks"]) / len(p["tasks"])

                        next_task = self.select_task(p)
                        p["current_task"] = next_task["name"] if next_task else None

                        mastery_result = self.calculate_mastery({
                            "surface": normalized_mastery,
                            "semantic": normalized_mastery,
                            "intuitive": normalized_mastery
                        })
                        strategy = self.determine_control_actions(p, task_name, mastery_result)
                        self._record_monitoring_cycle(
                            p,
                            task_name,
                            mastery_result,
                            strategy,
                            "task_update",
                            notes="基于显式任务掌握度更新触发控制决策。",
                            time_spent=t.get("time_spent", "0h")
                        )

                        p["updated_at"] = datetime.now().isoformat()
                        return t
        return None
    
    def select_task(self, profile):
        """选择最重要的任务"""
        if not profile or not profile.get("tasks"):
            return None
        
        # 过滤未完成的任务
        incomplete = [t for t in profile["tasks"] if t["mastery"] < 0.8]
        
        if not incomplete:
            return None
        
        # 按重要性和掌握度排序
        incomplete.sort(key=lambda t: (
            -t.get("importance", 3),
            t["mastery"]
        ))
        
        return incomplete[0]
    
    # ==================== 认知循环 ====================
    
    def create_record(self, profile_id, task, assessment, decision, time_spent):
        """创建认知循环记录"""
        record = {
            "id": str(uuid.uuid4()),
            "profile_id": profile_id,
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "assessment": assessment,
            "decision": decision,
            "time_spent": time_spent
        }
        
        self.records["records"].append(record)
        self._save_records()
        
        return record
    
    def get_records(self, profile_id=None, task_name=None):
        """获取认知循环记录"""
        records = self.records["records"]
        
        if profile_id:
            records = [r for r in records if r["profile_id"] == profile_id]
        
        if task_name:
            records = [r for r in records if r["task"]["name"] == task_name]
        
        return records
    
    # ==================== 评估与策略 ====================
    
    def calculate_mastery(self, answers):
        """
        计算掌握度
        answers: {"surface": 0-1, "semantic": 0-1, "intuitive": 0-1}
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
    
    def recommend_strategy(self, mastery_level):
        """推荐学习策略"""
        if mastery_level < 0.3:
            return [
                "观看入门视频教程",
                "阅读基础概念文章",
                "寻找前置知识补充"
            ]
        elif mastery_level < 0.6:
            return [
                "阅读进阶文章",
                "完成练习题",
                "动手实践"
            ]
        else:
            return [
                "完成项目实践",
                "尝试教给他人",
                "应用到新场景"
            ]

    def determine_control_actions(self, profile, task_name, mastery_result):
        """根据监控结果生成控制决策。"""
        overall = mastery_result["overall"]
        strategy = []
        next_task = self.select_task(profile)

        if overall < 0.3:
            strategy.append(f"继续聚焦当前任务：{task_name}")
        elif overall < 0.8:
            strategy.append(f"在当前任务上补强薄弱点：{task_name}")
        else:
            if next_task and next_task["name"] != task_name:
                strategy.append(f"切换到下一关键任务：{next_task['name']}")
            else:
                strategy.append("进入综合复盘或项目实践迁移")

        strategy.extend(self.recommend_strategy(overall))
        return strategy
    
    # ==================== 苏格拉底式评估 ====================
    
    def start_socratic_assessment(self, task_name):
        """
        开始苏格拉底式评估
        
        Args:
            task_name: 要评估的学习任务名称
        
        Returns:
            dict: 第一个追问问题
        """
        if not self.current_profile:
            return None
        
        # 重置追问引擎
        self.socratic_questioner.reset()
        self.socratic_mode = True
        
        # 更新档案中的追问计数
        self.current_profile["socratic_round_count"] = 0
        
        # 生成第一个问题
        question = self.socratic_questioner.generate_question(task_name)
        self._persist_socratic_session(self.current_profile, task_name)

        return question
    
    def continue_socratic_assessment(self, answer):
        """
        继续苏格拉底式评估
        
        Args:
            answer: 用户回答
        
        Returns:
            dict: {
                "action": "continue" | "explain" | "complete",
                "question": 下一问题（如果继续）,
                "summary": 总结（如果结束）,
                "reason": 原因说明
            }
        """
        if not self.current_profile:
            return {"action": "error", "reason": "当前没有活动的学习档案"}

        session = self.current_profile.get("socratic_session") or {}
        task_name = session.get("task_name") or self.current_profile.get("current_task") or "当前任务"
        result = self.socratic_questioner.process_answer(answer)
        
        # 更新追问计数
        self.current_profile["socratic_round_count"] = self.socratic_questioner.current_round
        
        if result["action"] == "continue":
            # 生成下一个问题
            next_question = self.socratic_questioner.generate_question(task_name)
            if next_question:
                self._persist_socratic_session(self.current_profile, task_name)
                return {
                    "action": "continue",
                    "question": next_question,
                    "reason": result["reason"]
                }
            else:
                # 无法生成更多问题，转为解释
                result = {"action": "explain", "reason": "追问完成"}

        if result["action"] == "explain":
            # 用户请求直接解释或达到上限
            self.socratic_mode = False
            mastery = self.socratic_mastery_from_history()
            strategy = self.determine_control_actions(self.current_profile, task_name, mastery)
            self._record_monitoring_cycle(
                self.current_profile,
                task_name,
                mastery,
                strategy,
                "socratic_assessment",
                notes=result["reason"]
            )
            summary = self.socratic_questioner.get_summary()
            self._clear_socratic_session(self.current_profile)
            return {
                "action": "explain",
                "summary": summary,
                "mastery": mastery,
                "strategy": strategy,
                "reason": result["reason"]
            }

        mastery = self.socratic_mastery_from_history()
        strategy = self.determine_control_actions(self.current_profile, task_name, mastery)
        self._record_monitoring_cycle(
            self.current_profile,
            task_name,
            mastery,
            strategy,
            "socratic_assessment",
            notes=result["reason"]
        )
        summary = self.socratic_questioner.get_summary()
        self._clear_socratic_session(self.current_profile)
        self.socratic_mode = False
        return {
            "action": "complete",
            "summary": summary,
            "mastery": mastery,
            "strategy": strategy,
            "reason": result["reason"]
        }
    
    def socratic_mastery_from_history(self):
        """
        基于苏格拉底追问历史计算掌握度
        
        分析用户回答的深度和完整性，评估理解程度
        """
        summary = self.socratic_questioner.get_summary()
        history = summary.get("history", [])
        
        if not history:
            return {"overall": 0.0, "breakdown": {"surface": 0, "semantic": 0, "intuitive": 0}}
        
        # 基于回答数量和维度覆盖计算掌握度
        dimensions_explored = len(summary.get("dimensions_explored", []))
        rounds = summary.get("total_rounds", 0)
        
        # 简化评估逻辑（可后续扩展）
        # 维度覆盖越多，理解越全面
        coverage_score = min(dimensions_explored / 6, 1.0) * 0.4
        
        # 回答深度（基于回答字数和是否包含疑问）
        depth_score = 0.3  # 默认中等深度
        for h in history:
            answer = h.get("answer", "")
            if isinstance(answer, str):
                if len(answer) > 50:
                    depth_score += 0.1
                if "?" not in answer and "？" not in answer:
                    depth_score += 0.05
        depth_score = min(depth_score, 0.6)
        
        # 完整性（基于是否主动请求直接解释）
        completeness = 0.3 if rounds < 3 else 0.2  # 早退出表示有一定自信
        
        overall = coverage_score * 0.3 + depth_score * 0.5 + completeness * 0.2
        
        return {
            "overall": overall,
            "breakdown": {
                "surface": coverage_score,
                "semantic": depth_score,
                "intuitive": completeness
            }
        }
    
    # ==================== 思维导图生成 ====================
    
    def generate_mindmap(self, profile):
        """生成思维导图（Draw.io格式）"""
        if not profile:
            return None
        
        topic = profile.get("topic", "未命名主题")
        tasks = profile.get("tasks", [])
        
        # 如果是刚才讲的GNN内容且还没有任务，临时加上去以作展示
        if not tasks and topic == "GNN":
            tasks = [
                {"name": "图(Graph)", "mastery": 0.25, "desc": "由节点和边组成，用于表示实体和关系的数据结构"},
                {"name": "节点(Node)", "mastery": 0.25, "desc": "表示BIM模型中的独立构件(如柱子、梁、板等)"},
                {"name": "边(Edge)", "mastery": 0.25, "desc": "表示构件之间的空间、物理连接或包含关系"},
                {"name": "消息传递", "mastery": 0.25, "desc": "GNN核心机制：收集邻居特征、聚合特征，并更新自身特征的过程"},
                {"name": "长距离依赖", "mastery": 0.25, "desc": "传统GNN难以捕捉的跨越多个网络层(节点)的联系"},
                {"name": "Transformer", "mastery": 0.25, "desc": "利用自注意力机制(Self-Attention)实现全局视野的架构"},
                {"name": "Graph Transformer", "mastery": 0.25, "desc": "结合GNN局部结构提取与Transformer全局信息交互的融合模型"}
            ]
            
        if not tasks:
            return None

        # Draw.io XML 构建
        xml_lines = [
            '<mxfile host="Trae" modified="{}" agent="LearningCoach" version="21.1.2" type="device">'.format(datetime.now().isoformat()),
            '  <diagram id="mindmap" name="学习导图">',
            '    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800" math="0" shadow="0" defaultFontFamily="sans-serif">',
            '      <root>',
            '        <mxCell id="0" />',
            '        <mxCell id="1" parent="0" />'
        ]
        
        # 中心节点
        root_id = "node_root"
        xml_lines.append(
            f'        <mxCell id="{root_id}" value="{topic} 学习地图" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=18;" vertex="1" parent="1">'
            f'          <mxGeometry x="500" y="50" width="200" height="80" as="geometry" />'
            f'        </mxCell>'
        )
        
        # 遍历任务生成子节点
        start_y = 200
        cols = 3
        x_spacing = 300
        y_spacing = 150
        
        for i, task in enumerate(tasks):
            task_id = f"node_task_{i}"
            name = task["name"]
            mastery = task.get("mastery", 0)
            desc = task.get("desc", "暂无详细说明")
            
            mastery_pct = int(mastery * 100)
            status = "✅" if mastery >= 0.8 else "⏳" if mastery > 0 else "⭕"
            
            import html
            # 构建内部 HTML 并使用 html.escape 进行转义
            inner_html = f"<div style='text-align:center;'><b>{name}</b><br/>{status} {mastery_pct}%<hr/><span style='font-size:12px;color:#666;'>{desc}</span></div>"
            escaped_label = html.escape(inner_html)
            
            row = i // cols
            col = i % cols
            
            x = 200 + col * x_spacing
            y = start_y + row * y_spacing
            
            xml_lines.append(
                f'        <mxCell id="{task_id}" value="{escaped_label}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;align=center;verticalAlign=middle;" vertex="1" parent="1">'
                f'          <mxGeometry x="{x}" y="{y}" width="260" height="100" as="geometry" />'
                f'        </mxCell>'
            )
            
            # 连线
            edge_id = f"edge_{i}"
            xml_lines.append(
                f'        <mxCell id="{edge_id}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="{root_id}" target="{task_id}">'
                f'          <mxGeometry relative="1" as="geometry" />'
                f'        </mxCell>'
            )
            
        xml_lines.extend([
            '      </root>',
            '    </mxGraphModel>',
            '  </diagram>',
            '</mxfile>'
        ])
        
        drawio_xml = "\n".join(xml_lines)
        
        # 保存到按主题分类的目录
        topic_dir = MINDMAPS_DIR / safe_topic_dirname(topic)
        topic_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{topic}_mindmap_{datetime.now().strftime('%Y%m%d')}.drawio"
        filepath = topic_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(drawio_xml)
        
        return {"mindmap": "已生成 Draw.io 格式思维导图", "file": str(filepath)}
    
    # ==================== 学习报告 ====================
    
    def generate_report(self, profile):
        """生成学习报告"""
        if not profile:
            return None
        
        records = self.get_records(profile["id"])
        latest_monitoring = self._latest_monitoring(profile)
        next_task = self.select_task(profile)
        
        report = {
            "topic": profile["topic"],
            "level": profile["level"],
            "goal": profile["goal"],
            "task_tree_metadata": profile.get("task_tree_metadata"),
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
            "overall_progress": profile["overall_progress"],
            "tasks": profile["tasks"],
            "current_task": profile["current_task"],
            "next_task": next_task["name"] if next_task else None,
            "last_assessment": profile.get("last_assessment"),
            "last_strategy": profile.get("last_strategy", []),
            "latest_monitoring": latest_monitoring,
            "monitoring_history_count": len(profile.get("monitoring_history", [])),
            "total_records": len(records),
            "total_time": self._calculate_total_time(records)
        }
        
        return report
    
    def _calculate_total_time(self, records):
        """计算总学习时间"""
        total_minutes = 0
        for r in records:
            time_str = r.get("time_spent", "0h")
            # 简单解析（支持 "30min", "1h", "1h30min" 等格式）
            if "h" in time_str:
                parts = time_str.split("h")
                total_minutes += int(parts[0]) * 60
                if len(parts) > 1 and "min" in parts[1]:
                    total_minutes += int(parts[1].replace("min", ""))
            elif "min" in time_str:
                total_minutes += int(time_str.replace("min", ""))
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return f"{hours}h{minutes}min" if minutes > 0 else f"{hours}h"
    
    # ==================== 导出功能 ====================
    
    def export_data(self):
        """导出所有数据"""
        return {
            "profiles": self.profiles,
            "records": self.records,
            "exported_at": datetime.now().isoformat()
        }


# ==================== 命令行接口 ====================

def print_help():
    """打印帮助信息"""
    help_text = """
学习教练 (Learning Coach) - 基于元认知监控模型的学习辅助系统

可用命令：
  start <主题>           开始学习新主题
  continue [主题]        继续学习（可指定主题）
  list                   列出所有学习目标
  switch <主题>          切换学习目标
  status [主题]          查看学习进度
  report [主题]          生成学习报告
  mindmap [主题]         生成思维导图
  socratic <任务>        开始苏格拉底式评估
  answer <回答>          回答苏格拉底追问
  explain                请求直接解释（退出追问模式）
  export                 导出所有数据
  help                   显示帮助信息

苏格拉底模式说明：
  - 零基础用户自动启用苏格拉底优先模式
  - 使用6维度追问框架引导深度思考
  - 最多3轮追问，可随时输入"直接解释"退出
  - 维度：澄清→假设→证据→视角→后果→反思

示例：
  python coach.py start 机器学习 --level 零基础
  python coach.py socratic 监督学习
  python coach.py continue
  python coach.py status
"""
    print(help_text)


def interactive_mode():
    """交互模式"""
    coach = LearningCoach()
    
    print("=" * 60)
    print("🧠 学习教练 (Learning Coach)")
    print("=" * 60)
    print()
    
    while True:
        try:
            cmd = input("教练> ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            args = parts[1] if len(parts) > 1 else None
            
            if action in ["exit", "quit", "q"]:
                print("再见！继续加油学习！")
                break
            
            elif action == "help":
                print_help()
            
            elif action == "start":
                if not args:
                    print("请指定学习主题，例如：start 机器学习")
                    continue
                topic, level, goal, time_budget = parse_start_arguments(shlex.split(args))
                if not topic:
                    print("请指定学习主题，例如：start 机器学习")
                    continue
                profile = coach.create_profile(topic, level, goal, time_budget)
                print(f"✅ 已创建学习档案：{topic}")
                print(f"档案ID：{profile['id']}")
                if profile.get("task_tree_metadata"):
                    print(f"任务树：{profile['task_tree_metadata'].get('label', '通用学习路径')}")
                print(f"当前任务：{profile.get('current_task') or '尚未生成'}")
                if profile.get('socratic_mode') == "SOCRATIC_PRIORITY":
                    print("🎯 已自动启用苏格拉底优先模式（零基础）")
            
            elif action == "continue":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案，请先用 start 命令创建")
                    continue
                coach.current_profile = profile
                print(f"继续学习：{profile['topic']}")
                print(f"当前进度：{profile['overall_progress']*100:.1f}%")
                print(f"当前任务：{profile.get('current_task') or '暂无'}")
                if profile.get("last_strategy"):
                    print("建议策略：")
                    for item in profile["last_strategy"]:
                        print(f"  - {item}")

            elif action == "switch":
                if not args:
                    print("请指定要切换的学习主题，例如：switch 机器学习")
                    continue
                profile = coach.switch_profile(args)
                if not profile:
                    print("未找到对应学习档案")
                    continue
                print(f"✅ 已切换到：{profile['topic']}")
                print(f"当前任务：{profile.get('current_task') or '暂无'}")
            
            elif action == "list":
                profiles = coach.list_profiles()
                if not profiles:
                    print("暂无学习档案")
                    continue
                print("📚 学习目标列表：")
                for i, p in enumerate(profiles, 1):
                    progress = p['overall_progress'] * 100
                    print(f"{i}. {p['topic']} - 进度：{progress:.1f}%")
            
            elif action == "status":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案")
                    continue
                coach.current_profile = profile
                report = coach.generate_report(profile)
                print(f"📊 学习进度报告：{report['topic']}")
                if report.get("task_tree_metadata"):
                    print(f"任务树：{report['task_tree_metadata'].get('label', '通用学习路径')}")
                print(f"整体进度：{report['overall_progress']*100:.1f}%")
                print(f"总学习时间：{report['total_time']}")
                print(f"当前任务：{report['current_task'] or '暂无'}")
                print(f"下一步：{report['next_task'] or '进入复盘或项目实践'}")
                if report.get("last_strategy"):
                    print("最近控制策略：")
                    for item in report["last_strategy"]:
                        print(f"  - {item}")
                if report['tasks']:
                    print("任务列表：")
                    for t in report['tasks']:
                        status = "✅" if t['mastery'] >= 0.8 else "⏳" if t['mastery'] > 0 else "⭕"
                        print(f"  {status} {t['name']} - {t['mastery']*100:.0f}%")
            
            elif action == "report":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案")
                    continue
                report = coach.generate_report(profile)
                print(json.dumps(report, ensure_ascii=False, indent=2))
            
            elif action == "mindmap":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案")
                    continue
                result = coach.generate_mindmap(profile)
                if result:
                    print(f"✅ 思维导图已生成")
                    print(f"文件：{result['file']}")
                    print()
                    print(result['mindmap'])
            
            elif action == "export":
                data = coach.export_data()
                print(json.dumps(data, ensure_ascii=False, indent=2))
            
            elif action == "socratic":
                if not args:
                    print("请指定要评估的任务，例如：socratic 监督学习")
                    continue
                if not coach.current_profile:
                    print("请先选择一个学习档案，使用 start 或 switch 命令")
                    continue
                question = coach.start_socratic_assessment(args)
                if question:
                    print(coach.socratic_questioner.format_question(question))
                else:
                    print("无法生成苏格拉底追问")
            
            elif action == "answer":
                if not args:
                    print("请提供你的回答")
                    continue
                profile = coach.get_profile()
                if not profile or not coach._restore_socratic_session(profile):
                    print("当前不在苏格拉底模式，请先使用 socratic 命令开始评估")
                    continue
                result = coach.continue_socratic_assessment(args)
                if result["action"] == "continue":
                    print(f"\n💡 {result['reason']}")
                    print(coach.socratic_questioner.format_question(result["question"]))
                elif result["action"] == "explain":
                    print(f"\n📚 {result['reason']}")
                    summary = result.get("summary", {})
                    print(f"已探索维度：{', '.join(summary.get('dimensions_explored', []))}")
                    print(f"追问轮数：{summary.get('total_rounds', 0)}")
                    print("\n正在生成直接解释...")
                    mastery = result.get("mastery", {})
                    print(f"\n📊 估计掌握度：{mastery['overall']*100:.0f}%")
                    for item in result.get("strategy", []):
                        print(f"  - {item}")
                else:
                    print(f"\n✅ {result['reason']}")
                    summary = result.get("summary", {})
                    print(f"评估完成！共探索 {summary.get('total_rounds', 0)} 轮。")
                    print(f"📊 估计掌握度：{result['mastery']['overall']*100:.0f}%")
                    for item in result.get("strategy", []):
                        print(f"  - {item}")
            
            elif action == "explain":
                profile = coach.get_profile()
                if not profile or not coach._restore_socratic_session(profile):
                    print("当前不在苏格拉底模式")
                    continue
                # 用户请求直接解释
                result = coach.continue_socratic_assessment("直接解释")
                print(f"\n📚 {result['reason']}")
                summary = result.get("summary", {})
                print(f"已探索维度：{', '.join(summary.get('dimensions_explored', []))}")
                mastery = result.get("mastery", {})
                print(f"\n📊 估计掌握度：{mastery['overall']*100:.0f}%")
                for item in result.get("strategy", []):
                    print(f"  - {item}")
                print("\n正在生成直接解释...")
            
            else:
                print(f"未知命令：{action}")
                print("输入 'help' 查看可用命令")
        
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误：{e}")


def main():
    """主函数"""
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    coach = LearningCoach()
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "help"
    # 合并所有后续参数（支持多参数）
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    if action == "help":
        print_help()
    
    elif action == "start":
        if not args:
            print("用法：python coach.py start <主题>")
            print("可选参数：--level <基础等级> --goal <学习目标>")
            return
        topic, level, goal, time_budget = parse_start_arguments(shlex.split(args))
        if not topic:
            print("用法：python coach.py start <主题>")
            return
        profile = coach.create_profile(topic, level, goal, time_budget)
        print(f"✅ 已创建学习档案：{topic}")
        if profile.get('socratic_mode') == "SOCRATIC_PRIORITY":
            print("🎯 已自动启用苏格拉底优先模式（零基础）")
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    
    elif action == "list":
        profiles = coach.list_profiles()
        print(json.dumps(profiles, ensure_ascii=False, indent=2))
    
    elif action == "status":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        report = coach.generate_report(profile)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif action == "continue":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        coach.current_profile = profile
        print(json.dumps({
            "topic": profile["topic"],
            "overall_progress": profile["overall_progress"],
            "current_task": profile.get("current_task"),
            "last_strategy": profile.get("last_strategy", [])
        }, ensure_ascii=False, indent=2))
    
    elif action == "switch":
        if not args:
            print("用法：python coach.py switch <主题>")
            return
        profile = coach.switch_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        
    elif action == "add-task":
        if not args:
            print("用法：python coach.py add-task <任务名称> [重要性(1-5)]")
            return
        
        parts = args.rsplit(' ', 1)
        importance = 3
        task_name = args
        
        if len(parts) == 2 and parts[1].isdigit():
            task_name = parts[0].strip()
            importance = int(parts[1])
            
        profile = coach.get_profile()
        if not profile:
            print("未找到学习档案")
            return
            
        task = coach.add_task(profile["id"], task_name, importance)
        if task:
            print(f"✅ 已添加任务：{task_name} (重要性: {importance})")
            print(json.dumps(task, ensure_ascii=False, indent=2))
        else:
            print("添加任务失败")
            
    elif action == "update-task":
        if not args:
            print("用法：python coach.py update-task <任务名称> <掌握度>")
            return
        
        parts = args.rsplit(' ', 1)
        if len(parts) != 2:
            print("用法：python coach.py update-task <任务名称> <掌握度>")
            return
            
        task_name = parts[0].strip()
        try:
            mastery = float(parts[1])
        except ValueError:
            print("掌握度必须是一个数字")
            return
            
        profile = coach.get_profile()
        if not profile:
            print("未找到学习档案")
            return
            
        task = coach.update_task(profile["id"], task_name, mastery)
        if task:
            print(json.dumps(task, ensure_ascii=False, indent=2))
        else:
            print(f"未找到任务：{task_name}")
    
    elif action == "report":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        report = coach.generate_report(profile)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif action == "mindmap":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        result = coach.generate_mindmap(profile)
        if result:
            print(f"✅ 思维导图已生成：{result['file']}")
            print()
            print(result['mindmap'])
    
    elif action == "export":
        data = coach.export_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    
    elif action == "socratic":
        if not args:
            print("用法：python coach.py socratic <任务名称>")
            return
        profile = coach.get_profile()
        if not profile:
            print("请先创建学习档案")
            return
        coach.current_profile = profile
        question = coach.start_socratic_assessment(args)
        if question:
            print(coach.socratic_questioner.format_question(question))
        else:
            print("无法生成苏格拉底追问")
    
    elif action == "answer":
        if not args:
            print("用法：python coach.py answer <你的回答>")
            return
        
        # 恢复状态
        profile = coach.get_profile()
        if not profile or not coach._restore_socratic_session(profile):
            print("当前没有进行中的苏格拉底会话，请先使用 socratic 命令")
            return
        result = coach.continue_socratic_assessment(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "explain":
        profile = coach.get_profile()
        if not profile or not coach._restore_socratic_session(profile):
            print("当前没有进行中的苏格拉底会话")
            return
        result = coach.continue_socratic_assessment("直接解释")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "toggle-socratic":
        enable = args.lower() == "on" if args else True
        mode = coach.toggle_socratic_mode(enable)
        print(f"苏格拉底模式：{'开启' if mode else '关闭'}")
    
    else:
        print(f"未知命令：{action}")
        print_help()


if __name__ == "__main__":
    if sys.platform == "win32":
        import sys
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    main()
