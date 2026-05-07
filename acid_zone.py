# -*- coding: utf-8 -*-
"""
Расчёт параметров зоны растворения при солянокислотной обработке (СКР).
Методика по формулам (В.30)-(В.37).
"""

import math
import numpy as np
import matplotlib.pyplot as plt


def A(r, r_c):
    """Функция A(r) из (В.30)."""
    return (math.exp(-0.1 * r_c) * (0.1 * r_c + 1)
            - math.exp(-0.1 * r) * (0.1 * r + 1))


def V_ks(r, h_ef, k_vo, k_uf, k_v, m0, r_c):
    """Объём СКР, проникающего на радиус r (формула В.31, m0 в %)."""
    return 2 * math.pi * h_ef * k_vo * k_uf * k_v * m0 * A(r, r_c)


def build_radius_grid(r_c, r_max=10.0):
    """Сетка r согласно методике: шаг 0.1 до 1 м, 0.2 до 2 м, 1.0 до 10 м."""
    rs = [r_c]
    r = 0.2
    while r <= 1.0 + 1e-9:
        rs.append(round(r, 2)); r += 0.1
    r = 1.2
    while r <= 2.0 + 1e-9:
        rs.append(round(r, 2)); r += 0.2
    r = 3.0
    while r <= r_max + 1e-9:
        rs.append(round(r, 2)); r += 1.0
    return rs


def ask_float(prompt, default=None):
    s = input(prompt).strip().replace(",", ".")
    if not s and default is not None:
        return default
    return float(s)


def main():
    print("=== Расчёт параметров зоны растворения СКР ===\n")
    print("Введите исходные данные (десятичный разделитель — точка или запятая):\n")

    h_ef = ask_float("h_эф, эффективная толщина пласта, м: ")
    r_c  = ask_float("r_c, радиус скважины, м [0.1]: ", 0.1)
    m0   = ask_float("m_0, начальная пористость, % : ")
    k_vo = ask_float("k_в.о, коэф. охвата по вертикали, дол.ед.: ")
    k_uf = ask_float("k_у.ф, коэф. участия пор в фильтрации, дол.ед.: ")
    k_v  = ask_float("k_в, коэф. вытеснения, дол.ед.: ")
    q_k  = ask_float("q_k, расход СКР, м³/сут: ")
    V_zad= ask_float("V_ks (заданный объём закачки), м³: ")
    C_ms = ask_float("C_ms, начальная концентрация СКР, кг/м³ (из задачи В.4): ")
    rho  = ask_float("ρ_ск, плотность скелета, кг/м³ (2000…2700): ")

    print("\nКоэффициент возрастания пористости:")
    print("  1 — задать k_ms напрямую (1.1…1.3)")
    print("  2 — рассчитать по Δm_s (лабораторное приращение пористости, %)")
    mode = input("Выбор [1/2], по умолчанию 1: ").strip() or "1"
    if mode == "2":
        dms = ask_float("Δm_s, %: ")
        k_ms = (m0 + dms) / m0
        print(f"  → k_ms = {k_ms:.4f}")
    else:
        k_ms = ask_float("k_ms: ")

    R_ms = ask_float("R_ms, кг/(м³·экв)  [например 20e-6]: ")

    # ---- 1. Таблица V_ks(r) и A(r) ----
    rs = build_radius_grid(r_c, 10.0)
    Ar = [A(r, r_c) for r in rs]
    Vr = [V_ks(r, h_ef, k_vo, k_uf, k_v, m0, r_c) for r in rs]
    Gs = [rho * V * (k_ms - 1) for V in Vr]   # (В.34) масса растворённой породы, кг

    print("\nТаблица В.7 расчётная:")
    print(f"{'r, м':>6} | {'A(r)':>12} | {'V_ks, м³':>12} | {'G_s, кг':>12}")
    print("-" * 52)
    for r, a, v, g in zip(rs, Ar, Vr, Gs):
        print(f"{r:>6.2f} | {a:>12.6f} | {v:>12.4f} | {g:>12.2f}")

    # ---- 2. Радиус, отвечающий заданному V_ks ----
    r_pr_p = float(np.interp(V_zad, Vr, rs))   # rпр.р
    print(f"\nРадиус продуктов реакции r_пр.р (по V_ks={V_zad} м³): {r_pr_p:.3f} м")

    # ---- 3. Длительность закачивания (В.32) ----
    t_u = 1440 * V_zad / q_k
    print(f"Длительность закачивания t_u = {t_u:.1f} мин = {t_u/60:.2f} ч")

    # ---- 4. Максимальная растворимость G_ms (В.37) и радиус зоны растворения ----
    DC_s = 0.9 * C_ms
    G_ms = 0.9 * V_zad * C_ms * R_ms          # кг, при V_ks = V_zad
    print(f"\nDC_s = 0.9·C_ms = {DC_s:.3f} кг/м³")
    print(f"G_ms (макс. растворимость для V_ks={V_zad} м³) = {G_ms:.4f} кг")

    # Чтобы найти r_з.р, строим G_ms(V) и пересекаем с G_s(r):
    # для каждого r находим V_ks(r) и соответствующее G_ms(r) = 0.9*V_ks(r)*C_ms*R_ms,
    # затем r_з.р — точка, где G_s(r) = G_ms_заданное (от полного V_zad).
    # Стандартный способ по методике: на оси G_s откладываем G_ms и читаем r по кривой G_s(r).
    if G_ms <= max(Gs):
        r_zr = float(np.interp(G_ms, Gs, rs))
        print(f"Радиус зоны растворения r_з.р = {r_zr:.3f} м")
    else:
        r_zr = None
        print("G_ms превышает максимум G_s(r) на интервале — увеличьте r_max.")

    # ---- 5. Изменение пористости ----
    m_c = k_ms * m0
    print(f"\nПористость после обработки: m_c = k_ms·m_0 = {m_c:.2f} %")
    print(f"Прирост пористости Δm = {m_c - m0:.2f} %")

    # ---- 6. Графики ----
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    axes[0].plot(rs, Vr, 'b-o', ms=3)
    axes[0].axhline(V_zad, color='r', ls='--', label=f'V_ks={V_zad}')
    if r_pr_p:
        axes[0].axvline(r_pr_p, color='r', ls=':')
    axes[0].set_xlabel('r, м'); axes[0].set_ylabel('V_ks, м³')
    axes[0].set_title('V_ks = f(r)'); axes[0].grid(True); axes[0].legend()

    axes[1].plot(rs, Gs, 'g-o', ms=3)
    axes[1].axhline(G_ms, color='r', ls='--', label=f'G_ms={G_ms:.2f}')
    if r_zr:
        axes[1].axvline(r_zr, color='r', ls=':', label=f'r_з.р={r_zr:.2f} м')
    axes[1].set_xlabel('r, м'); axes[1].set_ylabel('G_s, кг')
    axes[1].set_title('G_s = f(r)'); axes[1].grid(True); axes[1].legend()

    # Профиль нейтрализации (прямоугольный): C/C0 = 1 при r<=r_з.р, 0 при r>r_з.р
    if r_zr:
        r_prof = np.linspace(r_c, max(rs), 500)
        c_rel = np.where(r_prof <= r_zr, 1.0, 0.0)
        axes[2].plot(r_prof, c_rel, 'm-', lw=2)
        axes[2].axvline(r_zr, color='r', ls=':', label=f'r_з.р={r_zr:.2f} м')
    axes[2].set_xlabel('r, м'); axes[2].set_ylabel('C/C₀')
    axes[2].set_title('Профиль нейтрализации'); axes[2].grid(True); axes[2].legend()
    axes[2].set_ylim(-0.05, 1.1)

    plt.tight_layout()
    plt.savefig('acid_zone_results.png', dpi=120)
    print("\nГрафики сохранены: acid_zone_results.png")
    plt.show()


if __name__ == "__main__":
    main()
