import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.linewidth": 1.2,
})

# ── ИСХОДНЫЕ ДАННЫЕ ──────────────────────────────────────────────────────────
h_eff     = 8.0
k_vo      = 0.6
k_uf      = 0.7
k_v       = 0.9
m0        = 18.0       # %
r_c       = 0.1        # м
rho_ck    = 2500.0
k_ms      = 1.10
V_target  = 6.0        # м³
C_ms      = 4.46e6     # мг-экв/м³
R_ms      = 20e-6
acid_loss = 0.9

# ── ФУНКЦИИ ──────────────────────────────────────────────────────────────────
def A_of_r(r):
    return (
        np.exp(-0.1 * r_c) * (0.1 * r_c + 1)
        - np.exp(-0.1 * r)  * (0.1 * r  + 1)
    )

def Vks(r):
    return 2 * np.pi * h_eff * k_vo * k_uf * k_v * m0 * A_of_r(r)

def Gs_kg(r):
    return rho_ck * Vks(r) * (k_ms - 1)

Gms   = acid_loss * V_target * C_ms * R_ms   # кг
Gms_t = Gms / 1000.0

# ── СЕТКА ────────────────────────────────────────────────────────────────────
r_dense   = np.linspace(r_c, 10.0, 8000)
Vks_arr   = Vks(r_dense)
Gs_arr_kg = Gs_kg(r_dense)
Gs_arr_t  = Gs_arr_kg / 1000.0

r_zr  = float(np.interp(Gms,     Gs_arr_kg, r_dense))
r_prr = float(np.interp(V_target, Vks_arr,   r_dense))
V_zr  = float(np.interp(r_zr,    r_dense,    Vks_arr))

vol_marks = [3.0, 6.0, 9.0]
r_marks   = [float(np.interp(v, Vks_arr, r_dense)) for v in vol_marks]

x_max  = max(r_prr * 1.3, 2.5)
mask   = r_dense <= x_max
r_plt  = r_dense[mask]
Vks_p  = Vks_arr[mask]
Gs_p   = Gs_arr_t[mask]

gs_top   = max(Gs_p) * 1.05
vks_top  = max(Vks_p) * 1.15

# ── РИСУНОК ──────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(12, 8))
ax2 = ax1.twinx()

# Выровнять нули осей
ax1.set_ylim(0, gs_top)
ax2.set_ylim(0, vks_top)
ax1.set_xlim(0, x_max)

# ── G_s ──────────────────────────────────────────────────────────────────────
line_gs, = ax1.plot(r_plt, Gs_p, color="black", lw=2.2, label=r"$G_s$")
ax1.text(r_plt[-1] - 0.04, Gs_p[-1] * 0.97, r"$G_s$",
         fontsize=13, ha="right", va="top", fontweight="bold")

ax1.axhline(Gms_t, color="black", lw=1.2, linestyle="--")
ax1.text(0.12, Gms_t + gs_top * 0.015,
         f"$G_{{ms}}={int(Gms)}$ кг", fontsize=10)

# ── V_ks ─────────────────────────────────────────────────────────────────────
line_vks, = ax2.plot(r_plt, Vks_p, color="#555", lw=2.2,
                     linestyle="-.", label=r"$V_{ks}$")
ax2.text(r_plt[-1] - 0.04, Vks_p[-1] * 0.90, r"$V_{ks}$",
         fontsize=13, ha="right", va="top", color="#555", fontweight="bold")

for v, rv in zip(vol_marks, r_marks):
    if rv <= x_max:
        ax2.plot(rv, v, "o", ms=8, color="black", zorder=6)
        ax2.text(rv + 0.04, v + vks_top * 0.02, f"{int(v)} м³", fontsize=9)

ax2.axhline(V_target, color="#888", lw=1.0, linestyle="--", alpha=0.6)

# V_з.р
ax2.plot(r_zr, V_zr, "o", ms=8, color="black", zorder=6)
ax2.text(r_zr + 0.08, V_zr - vks_top * 0.07,
         f"$V_{{з.р}}={V_zr:.2f}$ м³", fontsize=9, color="#555")

# ── C/C0 штриховка (внутри поля, вверху) ────────────────────────────────────
C0_hi  = gs_top * 0.97
C0_lo  = gs_top * 0.78
C01_lo = gs_top * 0.71

# C = C_0 : r_c … r_зр
ax1.fill_betweenx([C0_lo, C0_hi], r_c, r_zr,
                  hatch="////", facecolor="white", edgecolor="black", lw=0.5, zorder=3)
ax1.plot([r_c, r_zr, r_zr, r_c, r_c],
         [C0_lo, C0_lo, C0_hi, C0_hi, C0_lo], "k-", lw=0.9, zorder=4)

# C = 0.1C_0 : r_зр … r_прр
ax1.fill_betweenx([C01_lo, C0_lo], r_zr, r_prr,
                  hatch="///", facecolor="white", edgecolor="black", lw=0.5, zorder=3)
ax1.plot([r_zr, r_prr, r_prr, r_zr, r_zr],
         [C01_lo, C01_lo, C0_lo, C0_lo, C01_lo], "k-", lw=0.9, zorder=4)

# Подписи внутри зон
ax1.text((r_c + r_zr) / 2, (C0_hi + C0_lo) / 2,
         "$C = C_0$", ha="center", va="center", fontsize=9)
ax1.text((r_zr + r_prr) / 2, (C0_lo + C01_lo) / 2,
         "$C = 0.1C_0$", ha="center", va="center", fontsize=9)
ax1.text(r_c + 0.01, C0_hi + gs_top * 0.005,
         "$C/C_0$", fontsize=10, va="bottom")

# ── Вертикальные линии ───────────────────────────────────────────────────────
ax1.axvline(r_zr,  color="black", lw=1.0, linestyle=":", zorder=2)
ax1.axvline(r_prr, color="black", lw=1.0, linestyle=":", zorder=2)

# Горизонтальные стрелки + подписи радиусов (внутри поля, внизу)
y_arr1 = gs_top * 0.06
y_arr2 = gs_top * 0.02

ax1.annotate("", xy=(r_zr, y_arr1), xytext=(r_c, y_arr1),
             arrowprops=dict(arrowstyle="<->", lw=1.0, color="black"))
ax1.text((r_c + r_zr) / 2, y_arr1 + gs_top * 0.02,
         r"$r_{з.р}$", ha="center", fontsize=10)

ax1.annotate("", xy=(r_prr, y_arr2), xytext=(r_c, y_arr2),
             arrowprops=dict(arrowstyle="<->", lw=1.0, color="black"))
ax1.text((r_c + r_prr) / 2, y_arr2 - gs_top * 0.04,
         r"$r_{пр.р}$", ha="center", fontsize=10)

# Вертикальные стрелки-указатели на G_ms и V_target
ax1.annotate("", xy=(r_zr, Gms_t), xytext=(r_zr, 0),
             arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#888"))
ax2.annotate("", xy=(r_prr, V_target), xytext=(r_prr, 0),
             arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#888"))

# ── Оформление осей ──────────────────────────────────────────────────────────
ax1.set_xlabel("r, м", fontsize=13)
ax1.set_ylabel("$G_{s,т}$", fontsize=13)
ax2.set_ylabel("$V_{ks}$, м³", fontsize=13)
ax1.xaxis.set_minor_locator(MultipleLocator(0.25))
ax1.grid(True, which="major", linestyle="--", alpha=0.35)

ax1.set_title(
    "Рис. В.3  Развитие зоны растворения пласта и профиль нейтрализации кислоты",
    fontsize=11, pad=14,
)

p1 = mpatches.Patch(facecolor="white", edgecolor="black", hatch="////", label="$C = C_0$")
p2 = mpatches.Patch(facecolor="white", edgecolor="black", hatch="///",  label="$C = 0.1C_0$")
ax1.legend(handles=[line_gs, line_vks, p1, p2],
           loc="upper left", fontsize=10, framealpha=0.95)

plt.tight_layout()
plt.savefig("plot_b4.png", dpi=150, bbox_inches="tight")
print("Saved: plot_b4.png")
print(f"Gms   = {Gms:.1f} kg  ({Gms_t:.3f} t)")
print(f"r_zr  = {r_zr:.3f} m")
print(f"r_prr = {r_prr:.3f} m")
print(f"V_zr  = {V_zr:.3f} m3")
