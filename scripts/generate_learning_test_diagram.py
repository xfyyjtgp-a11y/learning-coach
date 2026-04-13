from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "profiles.json"
MINDMAPS_DIR = ROOT / "mindmaps"


def load_best_profile() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    profiles = data.get("profiles", [])
    if not profiles:
        raise RuntimeError("No learning profiles found.")

    return max(
        profiles,
        key=lambda p: (
            len(p.get("tasks", [])),
            p.get("overall_progress", 0),
            p.get("updated_at", ""),
        ),
    )


def safe_topic_dirname(topic: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", (topic or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or "未命名主题"


def build_output_paths(topic: str) -> tuple[Path, Path]:
    topic_dir = MINDMAPS_DIR / safe_topic_dirname(topic)
    topic_dir.mkdir(parents=True, exist_ok=True)
    svg_file = topic_dir / "learning_path_test.svg"
    png_file = topic_dir / "learning_path_test.png"
    return svg_file, png_file


def pick_next_step(profile: dict) -> str:
    current_task = profile.get("current_task")
    tasks = profile.get("tasks", [])

    for idx, task in enumerate(tasks):
        if task.get("name") == current_task and idx + 1 < len(tasks):
            return tasks[idx + 1].get("name", "继续深化实战案例")

    if tasks:
        return "进入更完整的落地实现主题"

    return "先拆分学习任务并建立阶段路径"


def mastery_text(task: dict) -> str:
    mastery = int(round(float(task.get("mastery", 0)) * 100))
    status = task.get("status", "pending")
    return f"{status} | 掌握度 {mastery}%"


def add_task_box(ax, x: float, y: float, w: float, h: float, title: str, subtitle: str, face: str, edge: str) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=2,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", fontsize=12, fontweight="bold", color="#111827")
    ax.text(x + w / 2, y + h * 0.28, subtitle, ha="center", va="center", fontsize=9.5, color="#374151")


def add_arrow(ax, x1: float, y1: float, x2: float, y2: float, label: str) -> None:
    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=2,
        color="#2563eb",
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arrow)
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 + 0.18
    ax.text(
        mx,
        my,
        label,
        ha="center",
        va="center",
        fontsize=9,
        color="#1d4ed8",
        bbox={"boxstyle": "round,pad=0.2", "fc": "#ffffff", "ec": "#bfdbfe", "alpha": 0.98},
    )


def main() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False

    profile = load_best_profile()
    tasks = profile.get("tasks", [])
    topic = profile.get("topic", "未命名主题")
    svg_file, png_file = build_output_paths(topic)
    level = profile.get("level", "未知基础")
    goal = profile.get("goal", "未设置目标")
    current_task = profile.get("current_task") or "尚未开始"
    progress = float(profile.get("overall_progress", 0))
    next_step = pick_next_step(profile)

    fig, ax = plt.subplots(figsize=(16, 9), dpi=160)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    ax.text(0.6, 8.4, "Learning Coach 测试图", fontsize=22, fontweight="bold", color="#0f172a")
    ax.text(
        0.6,
        7.95,
        f"主题: {topic}    基础: {level}    目标: {goal}",
        fontsize=12.5,
        color="#334155",
    )
    ax.text(
        0.6,
        7.55,
        "图类型: 学习路径复盘图（阶段流程 + 进度摘要）",
        fontsize=11.5,
        color="#475569",
    )

    # Progress bar
    ax.text(0.6, 6.95, "总体进度", fontsize=11, color="#334155", fontweight="bold")
    ax.add_patch(FancyBboxPatch((2.0, 6.78), 5.8, 0.32, boxstyle="round,pad=0.02,rounding_size=0.06", facecolor="#e2e8f0", edgecolor="#cbd5e1"))
    ax.add_patch(FancyBboxPatch((2.0, 6.78), 5.8 * progress, 0.32, boxstyle="round,pad=0.02,rounding_size=0.06", facecolor="#2563eb", edgecolor="#2563eb"))
    ax.text(7.95, 6.94, f"{int(round(progress * 100))}%", fontsize=11, color="#1d4ed8", fontweight="bold")

    # Legend
    legend_y = 6.15
    ax.add_patch(Rectangle((0.6, legend_y - 0.08), 0.28, 0.18, facecolor="#dcfce7", edgecolor="#16a34a"))
    ax.text(0.95, legend_y, "已完成", fontsize=10, va="center", color="#166534")
    ax.add_patch(Rectangle((2.1, legend_y - 0.08), 0.28, 0.18, facecolor="#dbeafe", edgecolor="#2563eb"))
    ax.text(2.45, legend_y, "当前重点", fontsize=10, va="center", color="#1d4ed8")
    ax.add_patch(Rectangle((4.05, legend_y - 0.08), 0.28, 0.18, facecolor="#f8fafc", edgecolor="#94a3b8"))
    ax.text(4.4, legend_y, "后续建议", fontsize=10, va="center", color="#475569")

    left = 0.8
    y = 4.65
    width = 2.5
    height = 1.15
    gap = 0.45

    for idx, task in enumerate(tasks):
        x = left + idx * (width + gap)
        is_current = task.get("name") == current_task
        face = "#dbeafe" if is_current else "#dcfce7"
        edge = "#2563eb" if is_current else "#16a34a"
        add_task_box(ax, x, y, width, height, task.get("name", "未命名任务"), mastery_text(task), face, edge)
        if idx < len(tasks) - 1:
            add_arrow(ax, x + width, y + height / 2, x + width + gap, y + height / 2, "主学习路径")

    summary = FancyBboxPatch(
        (0.8, 1.0),
        14.4,
        2.55,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.5,
        edgecolor="#cbd5e1",
        facecolor="#ffffff",
    )
    ax.add_patch(summary)

    ax.text(1.15, 3.15, "学习观察", fontsize=14, fontweight="bold", color="#0f172a")
    observations = [
        f"当前学习位置: {current_task}",
        f"已完成任务: {len([t for t in tasks if t.get('status') == 'completed'])} / {len(tasks)}",
        "知识结构: 图表示 -> GNN机制 -> Transformer机制 -> 融合架构 -> BIM实战",
        f"下一步建议: {next_step}",
    ]
    for i, line in enumerate(observations):
        ax.text(1.2, 2.7 - i * 0.42, f"- {line}", fontsize=11.2, color="#334155")

    footer = FancyBboxPatch(
        (10.7, 1.35),
        3.9,
        1.6,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.4,
        edgecolor="#bfdbfe",
        facecolor="#eff6ff",
    )
    ax.add_patch(footer)
    ax.text(10.95, 2.55, "选型说明", fontsize=12.5, fontweight="bold", color="#1e3a8a")
    ax.text(10.95, 2.16, "这组数据是顺序学习任务，", fontsize=10.5, color="#1e40af")
    ax.text(10.95, 1.82, "最适合用流程型学习路径图呈现。", fontsize=10.5, color="#1e40af")
    ax.text(10.95, 1.48, "它比思维导图更容易看出进度和下一步。", fontsize=10.5, color="#1e40af")

    plt.tight_layout()
    fig.savefig(svg_file, format="svg", bbox_inches="tight")
    fig.savefig(png_file, format="png", bbox_inches="tight")
    plt.close(fig)

    print(f"SVG: {svg_file}")
    print(f"PNG: {png_file}")


if __name__ == "__main__":
    main()
