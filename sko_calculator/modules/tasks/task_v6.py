"""Задача В.6 — количество растворённой породы по составу.

Применяется, когда нет k_ms из В.5, либо для сравнения с ним.
Формулы:
    DG_s = a·C_гл + b·C_к              (В.38), %
    G_s  = ρ_п · V_ks · DG_s / m_0      (В.39), кг

Параметры m_0 и V_ks(r) тянутся из результата задачи В.5 (через session_state).
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from ._shared import render_precarpathian_constants


EXAMPLE = {
    "C_gl":  6.6,    # содержание глин, %
    "C_k":   3.1,    # содержание карбонатов, %
    "rho_p": 2250.0, # плотность пористой породы, кг/м³ (среднее 2200–2300)
}

_DEFAULTS = {
    "C_gl":  0.0,
    "C_k":   0.0,
    "rho_p": 0.0,
}


def solve(inp: dict, cfg: dict, m0: float, V_profile: pd.DataFrame | None,
          V_zad: float | None, k_ms_ref: float | None, rho_sk_ref: float | None) -> dict:
    """
    inp        — C_gl, C_k, rho_p
    m0         — пористость, %
    V_profile  — DataFrame с колонками 'r, м' и 'V_ks, м³' (из В.5)
    V_zad      — заданный объём для одиночного результата, м³
    k_ms_ref   — k_ms из В.5 (для сравнения), либо None
    rho_sk_ref — ρ_ск из В.5 (для сравнения), либо None
    """
    diss = cfg.get("dissolution_coefficients", {})
    a = diss.get("a_clay", 0.25)
    b = diss.get("b_carbonate", 0.5)

    C_gl, C_k, rho_p = inp["C_gl"], inp["C_k"], inp["rho_p"]
    DG_s = a * C_gl + b * C_k                       # (В.38), %

    # точечный результат для V_zad
    G_s_point = None
    G_s_v5    = None
    if V_zad is not None and m0 > 0:
        G_s_point = rho_p * V_zad * DG_s / m0       # (В.39), кг
        if k_ms_ref is not None and rho_sk_ref is not None:
            G_s_v5 = rho_sk_ref * V_zad * (k_ms_ref - 1)   # (В.34) из В.5

    # профиль G_s(r) на сетке В.5
    df_out = None
    if V_profile is not None and m0 > 0:
        df_out = V_profile.copy()
        df_out["G_s_В.6, кг"] = rho_p * df_out["V_ks, м³"] * DG_s / m0
        if k_ms_ref is not None and rho_sk_ref is not None:
            df_out["G_s_В.5, кг"] = rho_sk_ref * df_out["V_ks, м³"] * (k_ms_ref - 1)

    return {
        "a": a, "b": b,
        "DG_s": DG_s,
        "G_s_point": G_s_point,
        "G_s_v5":    G_s_v5,
        "df":        df_out,
    }


def _render_inputs(cfg: dict):
    diss = cfg.get("dissolution_coefficients", {})
    a = diss.get("a_clay", 0.25); b = diss.get("b_carbonate", 0.5)

    with st.expander("Константы (из config.json)", expanded=False):
        st.caption(f"Профиль: **{cfg.get('field_name', '?')}**. "
                   "Ред. — раздел «Настройки месторождения».")
        c1, c2 = st.columns(2)
        c1.metric("a (доля алюмосиликатов)", f"{a:.2f}")
        c2.metric("b (доля карбонатов)",     f"{b:.2f}")
        st.caption(diss.get("comment", ""))

    for k, v in _DEFAULTS.items():
        st.session_state.setdefault(f"v6_{k}", v)

    with st.expander("Исходные данные — В.6", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v6_C_gl"]  = c1.number_input(
            "C_гл, % — содержание глин",
            value=float(st.session_state["v6_C_gl"]), step=0.1)
        st.session_state["v6_C_k"]   = c2.number_input(
            "C_к, % — содержание карбонатов",
            value=float(st.session_state["v6_C_k"]), step=0.1)
        st.session_state["v6_rho_p"] = c3.number_input(
            "ρ_п, кг/м³ — плотность пористой породы (2200…2300)",
            value=float(st.session_state["v6_rho_p"]), step=10.0)

    return {k: st.session_state[f"v6_{k}"] for k in _DEFAULTS}


def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.6 — Количество растворённой породы (по составу)")
    if btn_col.button("ПРИМЕР", key="btn_example_v6", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v6_{k}"] = v
        st.rerun()

    render_precarpathian_constants(cfg)

    with st.expander("Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `C_гл` | содержание глин в породе | % (масс.) |
| `C_к` | содержание карбонатов CaCO₃ + MgCO₃ | % (масс.) |
| `a` | доля алюмосиликатов, растворимая в избытке HCl (≈ 0,25) | – |
| `b` | доля карбонатов, растворимая в избытке HCl (≈ 0,5) | – |
| `DG_s` | растворимость породы по массе | % |
| `ρ_п` | средняя плотность пористой породы (2200…2300) | кг/м³ |
| `m_0` | начальная пористость (из В.5) | % |
| `V_ks` | объём СКР (из В.5) | м³ |
| `G_s` | масса растворённой породы по составу (В.6) | кг |
| `ρ_ск` | плотность скелета (из В.5) — для сравнения с В.5 | кг/м³ |
| `k_ms` | коэффициент возрастания пористости (из В.5) — для сравнения | – |
""")

    st.latex(r"DG_s = a\cdot C_{\text{гл}} + b\cdot C_{\text{к}}\quad(B.38);\;\;"
             r"G_s = \rho_{\text{п}}\,V_{ks}\,DG_s/m_0\quad(B.39)")

    # подтягиваем результат В.5
    v5 = st.session_state.get("task_v5_result")
    if not v5:
        st.warning("Сначала откройте и рассчитайте задачу В.5 — оттуда берутся "
                   "m₀, V_ks(r), а также k_ms и ρ_ск для сравнения.")
        return None

    m0         = v5["m_0"]
    V_zad      = v5["V_zad"]
    df_v5      = v5["df"]
    k_ms_ref   = v5["k_ms"]
    rho_sk_ref = None
    # ρ_ск из ввода В.5 (через session_state)
    if "v5_rho_sk" in st.session_state:
        rho_sk_ref = float(st.session_state["v5_rho_sk"])

    st.info(f"Из В.5 подтянуто: m₀ = **{m0:.2f} %**, "
            f"V_ks (заданный) = **{V_zad:.2f} м³**, "
            f"k_ms = **{k_ms_ref:.3f}**, ρ_ск = **{rho_sk_ref:.0f} кг/м³**.")

    inp = _render_inputs(cfg)
    res = solve(inp, cfg, m0=m0, V_profile=df_v5, V_zad=V_zad,
                k_ms_ref=k_ms_ref, rho_sk_ref=rho_sk_ref)

    # сводка
    c1, c2, c3 = st.columns(3)
    c1.metric("DG_s, %",           f"{res['DG_s']:.3f}")
    c2.metric("G_s (В.6), кг",     f"{res['G_s_point']:.1f}")
    if res["G_s_v5"] is not None:
        delta = res["G_s_point"] - res["G_s_v5"]
        c3.metric("G_s (В.5) для сравн., кг",
                  f"{res['G_s_v5']:.1f}",
                  delta=f"Δ = {delta:+.1f} кг")

    st.caption(f"DG_s = {res['a']:.2f}·C_гл + {res['b']:.2f}·C_к "
               f"= {res['a']:.2f}·{inp['C_gl']:.2f} + {res['b']:.2f}·{inp['C_k']:.2f} "
               f"= {res['DG_s']:.3f} %")

    # таблица и график профиля
    if res["df"] is not None:
        with st.expander("Профиль G_s(r) — сетка из В.5", expanded=False):
            fmt = {"r, м": "{:.2f}", "V_ks, м³": "{:.4f}", "G_s_В.6, кг": "{:.2f}"}
            if "G_s_В.5, кг" in res["df"].columns:
                fmt["G_s_В.5, кг"] = "{:.2f}"
            cols = ["r, м", "V_ks, м³", "G_s_В.6, кг"]
            if "G_s_В.5, кг" in res["df"].columns:
                cols.append("G_s_В.5, кг")
            st.dataframe(res["df"][cols].style.format(fmt), use_container_width=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=res["df"]["r, м"], y=res["df"]["G_s_В.6, кг"]/1000.0,
                                 mode="lines+markers", name="G_s (В.6, по составу), т"))
        if "G_s_В.5, кг" in res["df"].columns:
            fig.add_trace(go.Scatter(x=res["df"]["r, м"], y=res["df"]["G_s_В.5, кг"]/1000.0,
                                     mode="lines+markers",
                                     name="G_s (В.5, по k_ms), т",
                                     line=dict(dash="dash")))
        fig.update_layout(
            title="Сравнение G_s(r): В.6 (по составу) vs В.5 (по k_ms)",
            xaxis_title="r, м", yaxis_title="G_s, т", height=440)
        st.plotly_chart(fig, use_container_width=True)

    st.session_state["task_v6_result"] = res
    return res
