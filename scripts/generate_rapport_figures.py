#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère toutes les figures EDA pour le rapport LaTeX.
Output : Rapport/figures/eda_*.png
Usage  : python scripts/generate_rapport_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Chemins ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
SRC  = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

INSPECT_RAW_PATH  = ROOT / "reports" / "summaries" / "inspect_report.json"
CLASS_STATS_PATH  = ROOT / "reports" / "summaries" / "class_stats.json"
OUT_DIR           = ROOT / "Rapport" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Style global ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "font.size":       11,
    "axes.titlesize":  13,
    "axes.labelsize":  11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.dpi":      150,
    "savefig.dpi":     150,
    "savefig.bbox":    "tight",
    "savefig.pad_inches": 0.15,
})

SPLIT_COLORS = {
    "train":    "#2563EB",
    "eval":     "#16A34A",
    "test":     "#D97706",
    "external": "#DC2626",
}

# ── Chargement des données ────────────────────────────────────────────────────
with open(INSPECT_RAW_PATH, encoding="utf-8") as f:
    inspect_raw = json.load(f)

with open(CLASS_STATS_PATH, encoding="utf-8") as f:
    class_stats = json.load(f)

raw_splits   = {s["split"]: s for s in inspect_raw["splits"]}
ORIG_CLASSES = list(inspect_raw["class_names"].values())
NEW_CLASSES  = list(class_stats["class_names"].values())
SPLITS       = ["train", "eval", "test", "external"]


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Distribution des 14 classes brutes (dataset brut)
# ═══════════════════════════════════════════════════════════════════════════
def fig_raw_class_distribution():
    total_counts = {}
    for cls in ORIG_CLASSES:
        total = sum(
            raw_splits[s]["class_counts"].get(cls, 0)
            for s in ["train", "valid", "test", "external"]
        )
        total_counts[cls] = total

    sorted_items = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)
    classes, counts = zip(*sorted_items)
    total = sum(counts)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(
        range(len(classes)), counts,
        color=["#1D4ED8" if c > np.median(counts) else "#93C5FD" for c in counts],
        edgecolor="white", linewidth=0.5
    )
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Nombre d'annotations")
    ax.set_title("Distribution des 14 classes originales — Dataset brut", fontweight="bold", pad=12)

    for i, (bar, count) in enumerate(zip(bars, counts)):
        pct = count / total * 100
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
                f"{count:,}  ({pct:.1f}%)", va="center", fontsize=9)

    ax.set_xlim(0, max(counts) * 1.22)
    ax.axvline(np.median(counts), color="#EF4444", linestyle="--", linewidth=1.2,
               label=f"Médiane = {int(np.median(counts)):,}")
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = OUT_DIR / "eda_raw_class_distribution.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Distribution des 7 classes finales (dataset traité, global)
# ═══════════════════════════════════════════════════════════════════════════
def fig_processed_class_distribution():
    global_counts = class_stats["global"]["class_counts"]
    sorted_items  = sorted(global_counts.items(), key=lambda x: x[1], reverse=True)
    classes, counts = zip(*sorted_items)
    total = sum(counts)

    palette = ["#1D4ED8","#2563EB","#3B82F6","#60A5FA","#93C5FD","#BFDBFE","#DBEAFE"]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(range(len(classes)), counts,
                   color=palette, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Nombre d'annotations")
    ax.set_title("Distribution des 7 classes finales — Dataset traité (global)", fontweight="bold", pad=12)

    for bar, count in zip(bars, counts):
        pct = count / total * 100
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
                f"{count:,}  ({pct:.1f}%)", va="center", fontsize=9)

    ax.set_xlim(0, max(counts) * 1.22)
    fig.tight_layout()
    out = OUT_DIR / "eda_processed_class_distribution.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Distribution des 7 classes par split (barplot groupé)
# ═══════════════════════════════════════════════════════════════════════════
def fig_class_distribution_per_split():
    n_classes = len(NEW_CLASSES)
    x         = np.arange(n_classes)
    width     = 0.20
    offsets   = [-1.5, -0.5, 0.5, 1.5]

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, split in enumerate(SPLITS):
        counts = [class_stats["splits"][split]["class_counts"].get(c, 0) for c in NEW_CLASSES]
        bars   = ax.bar(x + offsets[i] * width, counts, width,
                        label=split.capitalize(), color=list(SPLIT_COLORS.values())[i],
                        edgecolor="white", linewidth=0.4)

    ax.set_xticks(x)
    ax.set_xticklabels(NEW_CLASSES, rotation=18, ha="right", fontsize=9)
    ax.set_ylabel("Nombre d'annotations")
    ax.set_title("Distribution des 7 classes par split", fontweight="bold", pad=12)
    ax.legend(title="Split", fontsize=9)
    fig.tight_layout()
    out = OUT_DIR / "eda_class_distribution_per_split.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Distribution des dimensions des images par split
# ═══════════════════════════════════════════════════════════════════════════
def fig_image_dimensions():
    split_map = {
        "train":    raw_splits["train"],
        "eval":     raw_splits["valid"],
        "test":     raw_splits["test"],
        "external": raw_splits["external"],
    }

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    titles = ["Largeur (pixels)", "Hauteur (pixels)", "Ratio d'aspect (L/H)"]

    for split_name, split_data in split_map.items():
        widths, heights = [], []
        for size_str, count in split_data["image_sizes"].items():
            try:
                w, h = map(int, size_str.split("x"))
                widths.extend([w] * count)
                heights.extend([h] * count)
            except Exception:
                continue

        ratios = [w / h for w, h in zip(widths, heights)]
        color  = SPLIT_COLORS[split_name]
        label  = split_name.capitalize()

        for ax, data in zip(axes, [widths, heights, ratios]):
            ax.hist(data, bins=25, alpha=0.55, color=color, label=label, edgecolor="none")

    for ax, title in zip(axes, titles):
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel("Fréquence")
        ax.legend(fontsize=8)

    fig.suptitle("Distribution des dimensions des images par split", fontweight="bold", y=1.01)
    fig.tight_layout()
    out = OUT_DIR / "eda_image_dimensions.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 5 — Objets par image par split (densité)
# ═══════════════════════════════════════════════════════════════════════════
def fig_objects_per_image():
    split_labels = ["train", "eval", "test", "external"]
    split_keys   = ["train", "valid", "test", "external"]

    objs_per_img = []
    for key in split_keys:
        s = raw_splits[key]
        objs_per_img.append(s["num_objects"] / s["num_images"])

    colors = list(SPLIT_COLORS.values())
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(split_labels, objs_per_img, color=colors, edgecolor="white", linewidth=0.5)

    for bar, val in zip(bars, objs_per_img):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                f"{val:.2f}", ha="center", fontsize=10, fontweight="bold")

    ax.set_ylabel("Nombre moyen d'objets par image")
    ax.set_title("Densité d'annotations par split", fontweight="bold", pad=12)
    ax.set_ylim(0, max(objs_per_img) * 1.2)
    fig.tight_layout()
    out = OUT_DIR / "eda_objects_per_image.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 6 — Déséquilibre de classes : ratio min/max par split
# ═══════════════════════════════════════════════════════════════════════════
def fig_class_imbalance_ratio():
    fig, ax = plt.subplots(figsize=(9, 5))
    bar_width = 0.18
    x = np.arange(len(NEW_CLASSES))

    for i, split in enumerate(SPLITS):
        counts = np.array([class_stats["splits"][split]["class_counts"].get(c, 0) for c in NEW_CLASSES], dtype=float)
        total  = counts.sum()
        pcts   = counts / total * 100 if total > 0 else counts
        ax.bar(x + (i - 1.5) * bar_width, pcts, bar_width,
               label=split.capitalize(),
               color=list(SPLIT_COLORS.values())[i],
               edgecolor="white", linewidth=0.4)

    ax.set_xticks(x)
    ax.set_xticklabels(NEW_CLASSES, rotation=18, ha="right", fontsize=9)
    ax.set_ylabel("Part relative dans le split (%)")
    ax.set_title("Déséquilibre de classes — Part relative par split (%)", fontweight="bold", pad=12)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = OUT_DIR / "eda_class_imbalance_pct.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 7 — Comparaison Baseline vs Candidate (Chapitre 6)
# ═══════════════════════════════════════════════════════════════════════════
def fig_model_comparison():
    splits    = ["eval", "test", "external"]
    metrics   = ["mAP50", "mAP50-95", "Précision", "Rappel"]

    baseline = {
        "eval":     [0.3246, 0.1358, 0.6951, 0.3935],
        "test":     [0.4222, 0.2113, 0.8596, 0.4674],
        "external": [0.3248, 0.1464, 0.6822, 0.3829],
    }
    candidate = {
        "eval":     [0.3129, 0.1378, 0.6894, 0.3679],
        "test":     [0.4072, 0.1992, 0.8939, 0.4412],
        "external": [0.3317, 0.1596, 0.7571, 0.3829],
    }

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
    x      = np.arange(len(metrics))
    width  = 0.32
    colors = {"Baseline (Champion)": "#1D4ED8", "Candidate": "#DC2626"}

    for ax, split in zip(axes, splits):
        b_vals = baseline[split]
        c_vals = candidate[split]

        bars_b = ax.bar(x - width / 2, b_vals, width,
                        label="Baseline (Champion)",
                        color="#1D4ED8", edgecolor="white", linewidth=0.5)
        bars_c = ax.bar(x + width / 2, c_vals, width,
                        label="Candidate",
                        color="#DC2626", edgecolor="white", linewidth=0.5, alpha=0.85)

        # Annotations valeurs
        for bar in bars_b:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.008,
                    f"{bar.get_height():.3f}",
                    ha="center", va="bottom", fontsize=7.5, color="#1D4ED8",
                    fontweight="bold")
        for bar in bars_c:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.008,
                    f"{bar.get_height():.3f}",
                    ha="center", va="bottom", fontsize=7.5, color="#DC2626",
                    fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=9)
        ax.set_title(f"Split : {split.upper()}", fontweight="bold", pad=10)
        ax.set_ylabel("Score" if split == "eval" else "")
        ax.set_ylim(0, 1.05)
        ax.yaxis.grid(True, linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)

    # Légende commune
    handles = [
        mpatches.Patch(color="#1D4ED8", label="Baseline (Champion)"),
        mpatches.Patch(color="#DC2626", label="Candidate", alpha=0.85),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2,
               fontsize=10, bbox_to_anchor=(0.5, 1.02))

    fig.suptitle(
        "Comparaison Baseline vs Candidate — mAP50, mAP50-95, Précision, Rappel",
        fontweight="bold", fontsize=13, y=1.07
    )
    fig.tight_layout()
    out = OUT_DIR / "eval_model_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 8 — Radar chart Baseline vs Candidate (vue synthétique)
# ═══════════════════════════════════════════════════════════════════════════
def fig_model_radar():
    from matplotlib.patches import FancyArrowPatch
    import matplotlib.patheffects as pe

    labels   = ["mAP50\neval", "mAP50\ntest", "mAP50\nexternal",
                "mAP50-95\neval", "mAP50-95\ntest", "mAP50-95\nexternal",
                "Précision\neval", "Rappel\ntest"]
    baseline  = [0.3246, 0.4222, 0.3248, 0.1358, 0.2113, 0.1464, 0.6951, 0.4674]
    candidate = [0.3129, 0.4072, 0.3317, 0.1378, 0.1992, 0.1596, 0.6894, 0.4412]

    N      = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    b_vals = baseline  + baseline[:1]
    c_vals = candidate + candidate[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    ax.plot(angles, b_vals, "o-", linewidth=2.2, color="#1D4ED8",
            label="Baseline (Champion)")
    ax.fill(angles, b_vals, alpha=0.15, color="#1D4ED8")

    ax.plot(angles, c_vals, "s--", linewidth=2.2, color="#DC2626",
            label="Candidate")
    ax.fill(angles, c_vals, alpha=0.10, color="#DC2626")

    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9)
    ax.set_ylim(0, 0.95)
    ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_yticklabels(["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7"],
                       fontsize=7, color="grey")
    ax.grid(color="grey", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_title("Vue radar — Comparaison globale des deux variantes",
                 fontweight="bold", pad=20, fontsize=12)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=10)

    fig.tight_layout()
    out = OUT_DIR / "eval_model_radar.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 9 — Architecture de déploiement cloud
# ═══════════════════════════════════════════════════════════════════════════
def fig_deployment_architecture():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # ── Couleurs ──────────────────────────────────────────────────────────
    C_USER    = "#EFF6FF"
    C_VERCEL  = "#F0FDF4"
    C_RAILWAY = "#FEF3C7"
    C_DOCKER  = "#FEE2E2"
    C_MODEL   = "#F3E8FF"
    C_BORDER  = "#334155"

    def box(x, y, w, h, color, label, sublabel="", icon=""):
        rect = plt.Rectangle((x, y), w, h, fc=color, ec=C_BORDER,
                              linewidth=1.5, zorder=3)
        ax.add_patch(rect)
        cx, cy = x + w / 2, y + h / 2
        if icon:
            ax.text(cx, cy + 0.28, icon, ha="center", va="center",
                    fontsize=18, zorder=4)
            ax.text(cx, cy - 0.22, label, ha="center", va="center",
                    fontsize=10, fontweight="bold", color="#1e293b", zorder=4)
        else:
            ax.text(cx, cy + 0.15, label, ha="center", va="center",
                    fontsize=10, fontweight="bold", color="#1e293b", zorder=4)
        if sublabel:
            ax.text(cx, cy - 0.28, sublabel, ha="center", va="center",
                    fontsize=8, color="#475569", zorder=4, style="italic")

    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="#1e293b",
                                   lw=1.8, mutation_scale=16), zorder=5)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 0.18
            ax.text(mx, my, label, ha="center", va="bottom",
                    fontsize=8, color="#1e293b",
                    bbox=dict(fc="white", ec="none", pad=1))

    def cloud_badge(x, y, text, color):
        ax.text(x, y, text, ha="center", va="center", fontsize=7.5,
                color="white", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", fc=color,
                          ec="none", zorder=6))

    # ── Blocs principaux ──────────────────────────────────────────────────
    # Utilisateur
    box(0.3, 2.8, 1.8, 1.4, C_USER,    "Utilisateur",  "Navigateur web", "👤")
    # Vercel
    box(3.0, 2.8, 2.2, 1.4, C_VERCEL,  "Vercel",       "Frontend React", "🟢")
    # Railway
    box(6.2, 2.8, 2.2, 1.4, C_RAILWAY, "Railway",      "Backend FastAPI", "🚂")
    # Docker
    box(9.4, 2.8, 2.2, 1.4, C_DOCKER,  "Docker",       "Image CPU 1.19 GB", "🐳")
    # Modèle
    box(12.0, 2.8, 1.7, 1.4, C_MODEL,  "YOLOv8s",      "Champion (21MB)", "🧠")

    # ── Flèches horizontales ──────────────────────────────────────────────
    arrow(2.1, 3.5, 3.0, 3.5, "HTTPS")
    arrow(5.2, 3.5, 6.2, 3.5, "POST /predict")
    arrow(8.4, 3.5, 9.4, 3.5, "Run container")
    arrow(11.6, 3.5, 12.0, 3.5, "Inference")

    # ── Flèche retour ─────────────────────────────────────────────────────
    ax.annotate("", xy=(2.1, 3.2), xytext=(3.0, 3.2),
                arrowprops=dict(arrowstyle="-|>", color="#64748b",
                                lw=1.2, mutation_scale=14,
                                linestyle="dashed"), zorder=5)
    ax.text(2.55, 3.02, "JSON détections", ha="center", fontsize=7.5,
            color="#64748b", style="italic")

    # ── GitHub en haut ────────────────────────────────────────────────────
    box(4.5, 5.2, 5.0, 1.1, "#F8FAFC", "GitHub", "JadFalaq/detection_dentaire_mlops", "🐙")

    # Flèches CI/CD vers Vercel et Railway
    ax.annotate("", xy=(4.1, 4.2), xytext=(5.5, 5.2),
                arrowprops=dict(arrowstyle="-|>", color="#3b82f6",
                                lw=1.4, mutation_scale=13), zorder=5)
    ax.annotate("", xy=(7.3, 4.2), xytext=(7.3, 5.2),
                arrowprops=dict(arrowstyle="-|>", color="#3b82f6",
                                lw=1.4, mutation_scale=13), zorder=5)

    cloud_badge(4.6, 4.72, "Auto-deploy", "#3b82f6")
    cloud_badge(7.85, 4.72, "Auto-deploy", "#3b82f6")

    # ── CI/CD badge ───────────────────────────────────────────────────────
    box(5.2, 0.4, 3.6, 1.0, "#F0FDF4", "GitHub Actions CI/CD",
        "Tests → Build → Deploy", "✅")

    ax.annotate("", xy=(7.0, 5.2), xytext=(7.0, 1.4),
                arrowprops=dict(arrowstyle="-|>", color="#16a34a",
                                lw=1.2, mutation_scale=12,
                                linestyle="dotted"), zorder=2)

    # ── URLs en bas ───────────────────────────────────────────────────────
    ax.text(4.1, 0.15, "detection-dentaire-mlops.vercel.app",
            ha="center", fontsize=7.5, color="#1d4ed8", style="italic")
    ax.text(7.3, 0.15, "detectiondentairemlops-production.up.railway.app",
            ha="center", fontsize=7.5, color="#d97706", style="italic")

    # ── Titre ─────────────────────────────────────────────────────────────
    ax.set_title("Architecture de déploiement — Système entièrement cloud",
                 fontsize=13, fontweight="bold", pad=14)

    fig.tight_layout()
    out = OUT_DIR / "deployment_architecture.png"
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[OK] {out.name}")


# ═══════════════════════════════════════════════════════════════════════════
# Lancement
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Génération des figures EDA pour le rapport...\n")
    fig_raw_class_distribution()
    fig_processed_class_distribution()
    fig_class_distribution_per_split()
    fig_image_dimensions()
    fig_objects_per_image()
    fig_class_imbalance_ratio()
    print("\nGénération des figures d'évaluation...\n")
    fig_model_comparison()
    fig_model_radar()
    print("\nGénération des figures de déploiement...\n")
    fig_deployment_architecture()
    print(f"\nToutes les figures sont dans : {OUT_DIR}")
