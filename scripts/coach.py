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
"""

import json
import os
import sys
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


class LearningCoach:
    """学习教练主类"""
    
    def __init__(self):
        self.profiles = self._load_profiles()
        self.records = self._load_records()
        self.current_profile = None
    
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
    
    # ==================== 学习档案管理 ====================
    
    def create_profile(self, topic, level, goal, time_budget=None):
        """创建学习档案"""
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
            "overall_progress": 0.0
        }
        
        self.profiles["profiles"].append(profile)
        self._save_profiles()
        
        self.current_profile = profile
        return profile
    
    def get_profile(self, topic=None):
        """获取学习档案"""
        if topic:
            for p in self.profiles["profiles"]:
                if p["topic"] == topic:
                    return p
            return None
        elif self.current_profile:
            return self.current_profile
        elif self.profiles["profiles"]:
            # 返回最近更新的档案
            return sorted(
                self.profiles["profiles"],
                key=lambda x: x["updated_at"],
                reverse=True
            )[0]
        return None
    
    def list_profiles(self):
        """列出所有学习档案"""
        return self.profiles["profiles"]
    
    def switch_profile(self, topic):
        """切换学习目标"""
        profile = self.get_profile(topic)
        if profile:
            self.current_profile = profile
            return profile
        return None
    
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
                task = {
                    "name": task_name,
                    "mastery": 0.0,
                    "time_spent": "0h",
                    "status": "not_started",
                    "importance": importance,
                    "last_study": None
                }
                p["tasks"].append(task)
                p["updated_at"] = datetime.now().isoformat()
                self._save_profiles()
                return task
        return None
    
    def update_task(self, profile_id, task_name, mastery, time_spent=None):
        """更新任务进度"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                for t in p["tasks"]:
                    if t["name"] == task_name:
                        t["mastery"] = mastery
                        t["status"] = "in_progress" if mastery < 0.8 else "completed"
                        if time_spent:
                            t["time_spent"] = time_spent
                        t["last_study"] = datetime.now().isoformat()
                        
                        # 更新整体进度
                        if p["tasks"]:
                            p["overall_progress"] = sum(t["mastery"] for t in p["tasks"]) / len(p["tasks"])
                        
                        p["updated_at"] = datetime.now().isoformat()
                        self._save_profiles()
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
    
    # ==================== 思维导图生成 ====================
    
    def generate_mindmap(self, profile):
        """生成思维导图（Mermaid格式）"""
        if not profile or not profile.get("tasks"):
            return None
        
        topic = profile["topic"]
        tasks = profile["tasks"]
        
        # 生成 Mermaid 代码
        lines = [f"mindmap", f"  root(({topic}))"]
        
        for task in tasks:
            mastery = task["mastery"]
            mastery_pct = int(mastery * 100)
            status = "✅" if mastery >= 0.8 else "⏳" if mastery > 0 else "⭕"
            lines.append(f"    {task['name']} {status} {mastery_pct}%")
        
        mindmap = "\n".join(lines)
        
        # 保存到文件
        filename = f"{topic}_mindmap_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = MINDMAPS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {topic} 学习思维导图\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("```mermaid\n")
            f.write(mindmap)
            f.write("\n```\n")
        
        return {"mindmap": mindmap, "file": str(filepath)}
    
    # ==================== 学习报告 ====================
    
    def generate_report(self, profile):
        """生成学习报告"""
        if not profile:
            return None
        
        records = self.get_records(profile["id"])
        
        report = {
            "topic": profile["topic"],
            "level": profile["level"],
            "goal": profile["goal"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
            "overall_progress": profile["overall_progress"],
            "tasks": profile["tasks"],
            "current_task": profile["current_task"],
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
  export                 导出所有数据
  help                   显示帮助信息

示例：
  python coach.py start 机器学习
  python coach.py continue
  python coach.py status
  python coach.py report 机器学习
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
                # 简化版：直接创建档案
                topic = args
                profile = coach.create_profile(topic, "未设置", "未设置")
                print(f"✅ 已创建学习档案：{topic}")
                print(f"档案ID：{profile['id']}")
            
            elif action == "continue":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案，请先用 start 命令创建")
                    continue
                print(f"继续学习：{profile['topic']}")
                print(f"当前进度：{profile['overall_progress']*100:.1f}%")
            
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
                report = coach.generate_report(profile)
                print(f"📊 学习进度报告：{report['topic']}")
                print(f"整体进度：{report['overall_progress']*100:.1f}%")
                print(f"总学习时间：{report['total_time']}")
                if report['tasks']:
                    print("任务列表：")
                    for t in report['tasks']:
                        status = "✅" if t['mastery'] >= 0.8 else "⏳"
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
    args = sys.argv[2] if len(sys.argv) > 2 else None
    
    if action == "help":
        print_help()
    
    elif action == "start":
        if not args:
            print("用法：python coach.py start <主题>")
            return
        profile = coach.create_profile(args, "未设置", "未设置")
        print(f"✅ 已创建学习档案：{args}")
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
    
    else:
        print(f"未知命令：{action}")
        print_help()


if __name__ == "__main__":
    main()