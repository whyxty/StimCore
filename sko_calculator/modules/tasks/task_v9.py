"""Задача В.9 — технологическая и экономическая эффективность СКО.

Принятые решения (по согласованию с пользователем):
1. r_к — пользовательский ввод.
2. k_пр.р = k_0 (без коэффициента α) → применяется только формула (В.50).
3. ε_от — подтягивается из задачи В.2.
4. ρ_н в кг/м³.
5. Z_к.о — простой ввод суммой.
6. Только СКО (k_g из В.8 не используем).
7. Q_s = A_s · Q_ф (в первоисточнике опечатка `Q_s = A_s·Q_s` — в (В.51)
   правая часть должна быть Q_ф; см. В.49/В.50, где A_s = Q_s/Q_0, и В.52,
   где фигурирует (Q_s − Q_ф)).

Источники входных данных через session_state:
    - В.5 → r_c, r_з.р, r_пр.р
    - В.8 → k_0, k_s
    - В.2 → Q_ф, ε_от
"""
import math
import numpy as np
import pandas as pd
import streamlit as st

from ._shared import render_precarpathian_constants
import plotly.graph_objects as go


EXAMPLE = {
    "r_k":     250.0,
    "T_n":     100.0,
    "rho_n":   840.0,
    "W_0":     20.0,
    "C_n":     30000.0,
    "S_n":     18000.0,
    "Z_ko":    150000.0,
    "use_eps": True,
}


def A_s_simple(r_c: float, r_k: float, r_zr: float, r_pr: float,
               k0: float, k_s: float) -> float:
    """Формула (В.50) — схема «а», k_пр.р = k_0."""
    return math.log(r_k / r_c) / (
        (k0 / k_s) * math.log(r_zr / r_c) + math.log(r_k / r_pr)
    )


def solve(*, r_c: float, r_zr: float, r_pr: float, r_k: float,
          k0: float, k_s: float,
          Q_f: float, eps_ot: float | None,
          T_n: float, rho_n_kgm3: float, W_0: float,
          C_n: float, S_n: float, Z_ko: float,
          use_eps_ot: bool) -> dict:

    A_s = A_s_simple(r_c, r_k, r_zr, r_pr, k0, k_s)

    rho_n_tm3 = rho_n_kgm3 / 1000.0          # кг/м³ → т/м³

    if use_eps_ot and eps_ot is not None:
        # формула (В.53)
        Q_s = A_s * eps_ot * Q_f + (1.0 - eps_ot) * Q_f
        # формула (В.54)
        DQ_n = (A_s - 1.0) * eps_ot * Q_f * T_n * rho_n_tm3 * (100.0 - W_0) / 100.0
        method = "с учётом ε_от (В.53/В.54)"
    else:
        # формула (В.51): Q_s = A_s · Q_ф (см. п.7 в шапке)
        Q_s = A_s * Q_f
        # формула (В.52)
        DQ_n = (Q_s - Q_f) * T_n * rho_n_tm3 * (100.0 - W_0) / 100.0
        method = "без ε_от (В.51/В.52)"

    # формула (В.55)
    E_n = (C_n - S_n) * DQ_n - Z_ko

    # окупаемость (сут): когда выручка от прироста = Z_ко
    daily_profit = (C_n - S_n) * (Q_s - Q_f) * rho_n_tm3 * (100.0 - W_0) / 100.0
    payback_days = (Z_ko / daily_profit) if daily_profit > 0 else None

    return {
        "A_s": A_s,
        "Q_f": Q_f, "Q_s": Q_s, "dQ": Q_s - Q_f,
        "DQ_n": DQ_n,
        "E_n": E_n,
        "method": method,
        "use_eps_ot": use_eps_ot,
        "eps_ot": eps_ot,
        "payback_days": payback_days,
        "inputs": {
            "r_c": r_c, "r_zr": r_zr, "r_pr": r_pr, "r_k": r_k,
            "k0": k0, "k_s": k_s,
            "T_n": T_n, "rho_n_kgm3": rho_n_kgm3, "W_0": W_0,
            "C_n": C_n, "S_n": S_n, "Z_ko": Z_ko,
        },
    }


def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.9 — Технологическая и экономическая эффективность СКО")
    if btn_col.button("ПРИМЕР", key="btn_example_v9", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v9_{k}"] = v
        st.rerun()


    render_precarpathian_constants(cfg)
    with st.expander("Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `r_c` | радиус скважины (из В.5) | м |
| `r_з.р` | радиус зоны растворения (из В.5) | м |
| `r_пр.р` | радиус продуктов реакции (из В.5) | м |
| `r_к` | радиус контура питания | м |
| `k_0` | проницаемость до обработки (из В.8) | мкм² |
| `k_s` | проницаемость в зоне растворения (из В.8) | мкм² |
| `k_пр.р` | проницаемость в зоне продуктов реакции (= k_0, схема «а») | мкм² |
| `A_s` | коэффициент возрастания дебита (отношение Q_s/Q_0) | – |
| `Q_ф` | фактический дебит до обработки (= Q_0; из В.2) | м³/сут |
| `Q_s` | дебит после обработки | м³/сут |
| `ε_от` | относительная гидропроводность обрабатываемых пластов (из В.2) | – |
| `T_н` | длительность повышенного дебита | сут |
| `ρ_н` | плотность нефти | кг/м³ |
| `W_0` | обводнённость продукции | % |
| `ΔQ_н` | дополнительная добыча нефти | т |
| `Ц_н` | цена 1 т нефти | руб/т |
| `С_н` | себестоимость 1 т нефти | руб/т |
| `Z_к.о` | стоимость СКО | руб |
| `Э_н` | экономический эффект СКО | руб |
""")

    st.latex(r"A_s=\dfrac{\ln(r_к/r_c)}{(k_0/k_s)\ln(r_{\text{з.р}}/r_c)+\ln(r_к/r_{\text{пр.р}})}\quad(B.50)")
    st.latex(r"Q_s=A_s\,Q_ф\;(B.51)^{*};\;\;"
             r"\Delta Q_н=(Q_s-Q_ф)\,T_н\,\rho_н\,(100-W_0)/100\;(B.52)")
    st.latex(r"Q_s=A_s\,\varepsilon_{\text{от}}\,Q_ф+(1-\varepsilon_{\text{от}})\,Q_ф\;(B.53);\;\;"
             r"\Delta Q_н=(A_s-1)\,\varepsilon_{\text{от}}\,Q_ф\,T_н\,\rho_н\,(100-W_0)/100\;(B.54)")
    st.latex(r"Э_н=(Ц_н-С_н)\,\Delta Q_н-Z_{\text{к.о}}\quad(B.55)")
    st.caption("* В первоисточнике опечатка: формула (В.51) записана как `Q_s = A_s·Q_s`. "
               "По смыслу (Q_ф = Q_0 и определение A_s = Q_s/Q_0) корректная запись — "
               "`Q_s = A_s · Q_ф`.")

    # ---- проверка зависимостей ----
    v5 = st.session_state.get("task_v5_result")
    v8 = st.session_state.get("task_v8_result")
    v2 = st.session_state.get("task_v2_result")

    missing = []
    if not v5: missing.append("**В.5** (нужны r_c, r_з.р, r_пр.р)")
    if not v8: missing.append("**В.8** (нужны k_0, k_s)")
    if not v2: missing.append("**В.2** (нужны Q_ф и ε_от)")
    if missing:
        st.warning("Сначала рассчитайте: " + ", ".join(missing))
        return None

    r_c   = float(v5["df"]["r, м"].iloc[0])
    r_zr  = float(v5["r_zr"])
    r_pr  = float(v5["r_pr_p"])
    k0    = float(v8["k0"])
    k_s   = float(v8["ks"])
    Q_f   = float(v2["Q_f"])
    eps_ot= float(v2["e_ot"])

    st.info(
        f"Из **В.5**: r_c = **{r_c:.3f} м**, r_з.р = **{r_zr:.3f} м**, "
        f"r_пр.р = **{r_pr:.3f} м**.  \n"
        f"Из **В.8**: k_0 = **{k0:.6f} мкм²**, k_s = **{k_s:.6f} мкм²**.  \n"
        f"Из **В.2**: Q_ф = **{Q_f:.2f} м³/сут**, ε_от = **{eps_ot:.3f}**."
    )

    # ---- ввод параметров В.9 ----
    _DEF = {
        "r_k":       0.0,
        "T_n":       0.0,
        "rho_n":     0.0,
        "W_0":       0.0,
        "C_n":       0.0,
        "S_n":       0.0,
        "Z_ko":      0.0,
        "use_eps":   False,
    }
    for k, v in _DEF.items():
        st.session_state.setdefault(f"v9_{k}", v)

    with st.expander("Исходные данные — В.9", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v9_r_k"] = c1.number_input(
            "r_к, м — радиус контура питания",
            value=float(st.session_state["v9_r_k"]), step=10.0,
            help="Типично 200–500 м, задаётся пользователем")
        st.session_state["v9_T_n"] = c2.number_input(
            "T_н, сут — длительность повышенного дебита",
            value=float(st.session_state["v9_T_n"]), step=10.0)
        st.session_state["v9_rho_n"] = c3.number_input(
            "ρ_н, кг/м³ — плотность нефти",
            value=float(st.session_state["v9_rho_n"]), step=10.0)

        c1, c2, c3 = st.columns(3)
        st.session_state["v9_W_0"] = c1.number_input(
            "W₀, % — обводнённость",
            value=float(st.session_state["v9_W_0"]), step=1.0,
            min_value=0.0, max_value=100.0)
        st.session_state["v9_C_n"] = c2.number_input(
            "Ц_н, руб/т — цена нефти",
            value=float(st.session_state["v9_C_n"]), step=1000.0)
        st.session_state["v9_S_n"] = c3.number_input(
            "С_н, руб/т — себестоимость",
            value=float(st.session_state["v9_S_n"]), step=1000.0)

        c1, c2 = st.columns(2)
        st.session_state["v9_Z_ko"] = c1.number_input(
            "Z_к.о, руб — стоимость СКО",
            value=float(st.session_state["v9_Z_ko"]), step=10000.0)
        st.session_state["v9_use_eps"] = c2.checkbox(
            "Учитывать ε_от (формулы В.53/В.54)",
            value=bool(st.session_state["v9_use_eps"]),
            help="Если включено — учитывается, что прирост даёт только обрабатываемая часть пластов.")

    # ---- расчёт ----
    res = solve(
        r_c=r_c, r_zr=r_zr, r_pr=r_pr, r_k=st.session_state["v9_r_k"],
        k0=k0, k_s=k_s,
        Q_f=Q_f, eps_ot=eps_ot,
        T_n=st.session_state["v9_T_n"],
        rho_n_kgm3=st.session_state["v9_rho_n"],
        W_0=st.session_state["v9_W_0"],
        C_n=st.session_state["v9_C_n"],
        S_n=st.session_state["v9_S_n"],
        Z_ko=st.session_state["v9_Z_ko"],
        use_eps_ot=st.session_state["v9_use_eps"],
    )

    # ---- сводные метрики ----
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("A_s", f"{res['A_s']:.3f}")
    c2.metric("Q_ф → Q_s, м³/сут", f"{res['Q_s']:.2f}",
              delta=f"+{res['dQ']:.2f}")
    c3.metric("ΔQ_н, т", f"{res['DQ_n']:.1f}")
    c4.metric("Э_н, руб", f"{res['E_n']:,.0f}".replace(",", " "),
              delta="прибыль" if res["E_n"] > 0 else "убыток",
              delta_color="normal" if res["E_n"] > 0 else "inverse")

    if res["payback_days"] is not None:
        st.caption(f"Срок окупаемости СКО: **{res['payback_days']:.1f} сут** "
                   f"({res['payback_days']/30:.1f} мес.). Метод: {res['method']}.")
    else:
        st.caption(f"Эффект отсутствует (Q_s ≤ Q_ф). Метод: {res['method']}.")

    # ---- расшифровка ----
    st.markdown("**Подстановка в формулу A_s (В.50):**")
    st.latex(
        rf"A_s=\dfrac{{\ln({res['inputs']['r_k']:.0f}/{r_c:.3f})}}"
        rf"{{({k0:.4g}/{k_s:.4g})\,\ln({r_zr:.3f}/{r_c:.3f})"
        rf"+\ln({res['inputs']['r_k']:.0f}/{r_pr:.3f})}}"
        rf"={res['A_s']:.3f}"
    )

    # ---- чувствительность A_s к r_к ----
    rk_grid = np.linspace(max(r_pr * 1.1, 50), 1000, 80)
    A_curve = [A_s_simple(r_c, rk, r_zr, r_pr, k0, k_s) for rk in rk_grid]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rk_grid, y=A_curve, mode="lines",
                             name="A_s(r_к)", line=dict(width=2)))
    fig.add_trace(go.Scatter(x=[res['inputs']['r_k']], y=[res['A_s']],
                             mode="markers", name="Текущее значение",
                             marker=dict(size=11, color="#d62728", symbol="diamond")))
    fig.update_layout(
        title="Чувствительность A_s к радиусу контура питания r_к",
        xaxis_title="r_к, м", yaxis_title="A_s",
        height=380)
    st.plotly_chart(fig, use_container_width=True)

    # ---- зависимость ΔQ_н и Э_н от T_н ----
    T_grid = np.linspace(0, max(st.session_state["v9_T_n"] * 2, 200), 50)
    rho_n_tm3 = st.session_state["v9_rho_n"] / 1000.0
    if res["use_eps_ot"]:
        DQ_curve = (res['A_s'] - 1.0) * eps_ot * Q_f * T_grid * rho_n_tm3 \
                   * (100 - st.session_state["v9_W_0"]) / 100.0
    else:
        DQ_curve = (res['Q_s'] - Q_f) * T_grid * rho_n_tm3 \
                   * (100 - st.session_state["v9_W_0"]) / 100.0
    E_curve = (st.session_state["v9_C_n"] - st.session_state["v9_S_n"]) * DQ_curve \
              - st.session_state["v9_Z_ko"]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=T_grid, y=DQ_curve, mode="lines",
                              name="ΔQ_н, т", yaxis="y1"))
    fig2.add_trace(go.Scatter(x=T_grid, y=E_curve, mode="lines",
                              name="Э_н, руб", yaxis="y2",
                              line=dict(dash="dash")))
    fig2.add_hline(y=0, line_color="gray", line_width=1)
    if res["payback_days"] is not None and res["payback_days"] <= T_grid.max():
        fig2.add_vline(x=res["payback_days"], line_dash="dot", line_color="green",
                       annotation_text=f"окуп. {res['payback_days']:.0f} сут")
    fig2.update_layout(
        title="ΔQ_н и Э_н в зависимости от T_н",
        xaxis_title="T_н, сут",
        yaxis=dict(title="ΔQ_н, т"),
        yaxis2=dict(title="Э_н, руб", overlaying="y", side="right"),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.session_state["task_v9_result"] = res
    return res
