import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "axes.linewidth": 1.2,
})

fig, ax = plt.subplots(figsize=(9, 7))
ax2 = ax.twinx()

# ── ПРЕДЕЛЫ ОСЕЙ ─────────────────────────────────────────────────────────────
ax.set_xlim(0, 2.6)
ax.set_ylim(0, 2.0)
ax2.set_ylim(0, 10)

ax.set_xticks([0.5, 1.0, 1.5, 2.0])
ax.set_xticklabels(["0,5", "1,0", "1,5", "2,0"])
ax.set_yticks([0, 1, 2])
ax2.set_yticks([0, 5, 10])

ax.set_xlabel("$r$, м", fontsize=12, labelpad=4)
ax.set_ylabel("")
ax2.set_ylabel("")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax2.spines["top"].set_visible(False)

# Рамка вручную
for (x0, y0, x1, y1) in [
    (0, 0, 2.6, 0),
    (0, 0, 0, 2.0),
    (0, 2.0, 2.6, 2.0),
    (2.6, 0, 2.6, 2.0),
]:
    ax.plot([x0, x1], [y0, y1], "k-", lw=1.2, clip_on=False,
            transform=ax.transData, zorder=10)

# ── ПОДПИСИ ОСЕЙ НАВЕРХУ ─────────────────────────────────────────────────────
ax.text(-0.04, 2.03, "$G_{s,\\,т}$", fontsize=12, ha="right", va="bottom",
        clip_on=False, transform=ax.transData)
ax.text(2.64, 2.03, "$V_{ks}$, м³", fontsize=12, ha="left", va="bottom",
        clip_on=False, transform=ax.transData)

# ── ВНУТРЕННЯЯ ГОРИЗОНТАЛЬНАЯ ЛИНИЯ СО СТРЕЛКОЙ ─────────────────────────────
ax.annotate("", xy=(2.52, 1.25), xytext=(0.05, 1.25),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1),
            annotation_clip=False)
ax.text(2.54, 1.28, "$r$, м", va="bottom", ha="left", fontsize=11,
        clip_on=False)

# ── ПУНКТИРНАЯ ЛИНИЯ r_c ─────────────────────────────────────────────────────
ax.plot([0.15, 0.15], [0.00, 1.95], "k--", lw=1.1)
ax.text(0.10, -0.12, "$r_c$", ha="center", fontsize=11, clip_on=False)

# ── ЗАШТРИХОВАННЫЙ ПРЯМОУГОЛЬНИК C = C0 ──────────────────────────────────────
C0_x = [0.15, 0.78, 0.78, 0.15, 0.15]
C0_y = [1.25, 1.25, 1.72, 1.72, 1.25]
ax.fill(C0_x, C0_y, hatch="////", facecolor="white", edgecolor="black", lw=0.8, zorder=3)
ax.plot(C0_x, C0_y, "k-", lw=1.0, zorder=4)
ax.text(0.46, 1.74, "$C=C_0$", ha="center", va="bottom", fontsize=11, zorder=5)
ax.text(0.15, 1.74, "$C/C_0$", ha="left", va="bottom", fontsize=11)

# ── ВЕРТИКАЛЬНЫЙ СКАЧОК КОНЦЕНТРАЦИИ ─────────────────────────────────────────
ax.plot([0.78, 0.78], [1.72, 1.25], "k-", lw=1.1, zorder=4)

# ── ПОЛОСКА C = 0.1 C0 ───────────────────────────────────────────────────────
C01_x = [0.78, 2.00, 2.00, 0.78, 0.78]
C01_y = [1.25, 1.25, 1.33, 1.33, 1.25]
ax.fill(C01_x, C01_y, hatch="////", facecolor="white", edgecolor="black", lw=0.8, zorder=3)
ax.plot(C01_x, C01_y, "k-", lw=1.0, zorder=4)
ax.text(0.80, 1.35, "$C=0{,}1C_0$", ha="left", va="bottom", fontsize=10)
ax.text(1.50, 1.36, "18 м³", ha="center", fontsize=10)

# ── ВЕРТИКАЛЬНЫЕ ЛИНИИ ────────────────────────────────────────────────────────
ax.plot([0.78, 0.78], [0.00, 1.25], "k-", lw=1.1)
ax.plot([2.00, 2.00], [0.00, 1.25], "k-", lw=1.1)

# ── СТРЕЛКИ ──────────────────────────────────────────────────────────────────
ax.annotate("", xy=(0.78, 0.95), xytext=(0.15, 0.95),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0))
ax.text(0.45, 0.87, "$r_{з.р}$", ha="center", fontsize=11)

ax.annotate("", xy=(2.00, 1.17), xytext=(0.15, 1.17),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0))
ax.text(1.55, 1.10, "$r_{пр.р}$", ha="center", fontsize=11)

# Gms — стрелка от оси (r=0) до зоны растворения
ax.annotate("", xy=(0.78, 0.55), xytext=(0.00, 0.55),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0))
ax.text(0.05, 0.61, "$G_{ms}=480$ кг", ha="left", fontsize=10)

ax.annotate("", xy=(0.78, 0.00), xytext=(0.78, 0.18),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0))

# ── КРИВАЯ G_s (выпрямлена — почти линейный рост) ────────────────────────────
Gs_x = np.array([0.35, 0.78, 1.20, 1.58])
Gs_y = np.array([0.20, 0.55, 1.15, 1.86])
spl_gs = make_interp_spline(Gs_x, Gs_y, k=2)
x_gs = np.linspace(Gs_x[0], Gs_x[-1], 400)
ax.plot(x_gs, spl_gs(x_gs), "k-", lw=1.5, zorder=5)
ax.text(1.60, 1.70, "$G_s$", ha="left", fontsize=12, fontweight="bold")

# ── КРИВАЯ V_ks (выпрямлена — почти линейный рост) ───────────────────────────
Vks_x = np.array([0.30, 0.78, 1.40, 2.00, 2.45])
Vks_y = np.array([0.10, 0.27, 0.66, 1.20, 1.75])
spl_vks = make_interp_spline(Vks_x, Vks_y, k=2)
x_vks = np.linspace(Vks_x[0], Vks_x[-1], 400)
ax.plot(x_vks, spl_vks(x_vks), "k-", lw=1.5, zorder=5)
ax.text(1.70, 0.70, "$V_{ks}$", ha="left", fontsize=12, fontweight="bold")

# ── ТОЧКИ-КРУЖКИ ─────────────────────────────────────────────────────────────
points_x = [0.78, 0.78, 1.40, 2.00, 2.45]
points_y = [0.55, 0.27, 0.66, 1.20, 1.75]
ax.scatter(points_x, points_y,
           s=55, facecolors="white", edgecolors="black", lw=1.4, zorder=8)

# ── ПОДПИСИ ОБЪЁМОВ ──────────────────────────────────────────────────────────
ax.text(0.86, 0.57, "6 м³", ha="left", fontsize=10)
ax.text(0.82, 0.32, "$V_{з.р}$", ha="left", fontsize=10)
ax.text(1.45, 0.68, "3 м³", ha="left", fontsize=10)
ax.text(2.05, 1.13, "6 м³", ha="left", fontsize=10)
ax.text(2.35, 1.80, "9 м³", ha="left", fontsize=10)

# ── ФИНАЛЬНЫЕ НАСТРОЙКИ ──────────────────────────────────────────────────────
ax.tick_params(direction="in", length=5, width=1.0, top=False, right=False)
ax2.tick_params(direction="in", length=5, width=1.0, top=False, left=False)

ax.set_title(
    "Рис. В.3. Развитие зоны растворения пласта\n"
    "и профиль нейтрализации кислоты (типичная картина)",
    fontsize=11, pad=10,
)

plt.tight_layout()
plt.savefig("plot_b4_schema.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.show()
