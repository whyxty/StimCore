"""Задача В.7 — изменение пористости песчаника после СКО (косвенный метод).

Применяется, когда нет прямых лабораторных данных по k_ms (как в В.5),
но известны состав породы (C_гл, C_к) и параметры из В.5/В.6.

Формулы по порядку:
    DG_s = a·C_гл + b·C_к              (В.38), % — берётся из В.6
    DV_s = ρ_п · DG_s / ρ_ск           (В.40), %
    m_s  = m_0 + DV_s                   (В.41), %
    k_ms = m_s / m_0                    (В.42)
    G_s  = ρ_ск · V_ks · (k_ms − 1)     (В.34), кг — на профиле V_ks(r) из В.5

Источники входных данных:
    - V.5: m_0, ρ_ск, V_ks(r), V_zad, k_ms (для сравнения)
    - V.6: C_гл, C_к, ρ_п, DG_s
    - config: a, b
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def solve(*, C_gl: float, C_k: float, rho_p: float, rho_sk: float,
          m0: float, V_zad: float | None, V_profile: pd.DataFrame | None,
          a: float, b: float, k_ms_v5: float | None) -> dict:
    """Считает В.7 по уже известным параметрам."""
    DG_s = a * C_gl + b * C_k                        # (В.38), %
    DV_s = rho_p * DG_s / rho_sk if rho_sk else 0.0  # (В.40), %
    m_s  = m0 + DV_s                                 # (В.41), %
    k_ms = m_s / m0 if m0 else 0.0                   # (В.42)

    G_s_point = None
    if V_zad is not None:
        G_s_point = rho_sk * V_zad * (k_ms - 1)      # (В.34), кг

    df_out = None
    if V_profile is not None:
        df_out = V_profile.copy()
        df_out["G_s_В.7, кг"] = rho_sk * df_out["V_ks, м³"] * (k_ms - 1)

    return {
        "DG_s":       DG_s,
        "DV_s":       DV_s,
        "m_0":        m0,
        "m_s":        m_s,
        "k_ms":       k_ms,
        "k_ms_v5":    k_ms_v5,
        "G_s_point":  G_s_point,
        "df":         df_out,
    }


def render(cfg: dict):
    st.subheader("Задача В.7 — Изменение пористости песчаника после СКО (косвенный метод)")

    with st.expander("📖 Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `C_гл` | содержание глин в породе (из В.6) | % (масс.) |
| `C_к` | содержание карбонатов (из В.6) | % (масс.) |
| `a, b` | коэффициенты растворимости (≈ 0,25 и 0,5) | – |
| `DG_s` | растворимость породы по массе (формула В.38) | % |
| `DV_s` | объёмная растворимость = прирост пористости | % |
| `ρ_п` | плотность пористой породы (из В.6) | кг/м³ |
| `ρ_ск` | плотность скелета (из В.5) | кг/м³ |
| `m_0` | начальная пористость (из В.5) | % |
| `m_s` | пористость после обработки СКР | % |
| `k_ms` | коэффициент возрастания пористости (косвенный) | – |
| `k_ms` (лаб.) | то же из В.5, для сравнения | – |
| `V_ks` | объём СКР на радиусе `r` (профиль из В.5) | м³ |
| `G_s` | масса растворённой породы (формула В.34) | кг |
""")

    st.latex(r"DG_s=a\,C_{\text{гл}}+b\,C_{\text{к}}\quad(B.38);\;\;"
             r"DV_s=\dfrac{\rho_{\text{п}}\,DG_s}{\rho_{\text{ск}}}\quad(B.40);\;\;"
             r"m_s=m_0+DV_s\;(B.41);\;\;k_{ms}=m_s/m_0\;(B.42);\;\;"
             r"G_s=\rho_{\text{ск}}V_{ks}(k_{ms}-1)\;(B.34)")

    # --- проверка зависимостей ---
    v5 = st.session_state.get("task_v5_result")
    v6_inp = {k.replace("v6_", ""): st.session_state[k]
              for k in st.session_state if k.startswith("v6_")}

    if not v5:
        st.warning("Сначала рассчитайте задачу **В.5** — оттуда берутся "
                   "m₀, ρ_ск, V_ks(r), V_зад, k_ms (для сравнения).")
        return None
    if not v6_inp or "C_gl" not in v6_inp:
        st.warning("Сначала откройте задачу **В.6** — оттуда берутся "
                   "C_гл, C_к, ρ_п (через её ввод).")
        return None

    # --- константы из конфига ---
    diss = cfg.get("dissolution_coefficients", {})
    a = diss.get("a_clay", 0.25)
    b = diss.get("b_carbonate", 0.5)

    with st.expander("📐 Константы (из config.json)", expanded=False):
        st.caption(f"Профиль: **{cfg.get('field_name', '?')}**.")
        c1, c2 = st.columns(2)
        c1.metric("a (доля алюмосиликатов)", f"{a:.2f}")
        c2.metric("b (доля карбонатов)",     f"{b:.2f}")

    # --- параметры из В.5 / В.6 ---
    m0       = v5["m_0"]
    rho_sk   = float(st.session_state.get("v5_rho_sk", 2700.0))
    V_zad    = v5["V_zad"]
    df_v5    = v5["df"]
    k_ms_v5  = v5["k_ms"]

    C_gl  = float(v6_inp["C_gl"])
    C_k   = float(v6_inp["C_k"])
    rho_p = float(v6_inp["rho_p"])

    st.info(f"Из **В.5**: m₀ = **{m0:.2f} %**, ρ_ск = **{rho_sk:.0f} кг/м³**, "
            f"V_зад = **{V_zad:.2f} м³**, k_ms (лаб.) = **{k_ms_v5:.3f}**.  \n"
            f"Из **В.6**: C_гл = **{C_gl:.2f} %**, C_к = **{C_k:.2f} %**, "
            f"ρ_п = **{rho_p:.0f} кг/м³**.")

    # --- расчёт ---
    res = solve(C_gl=C_gl, C_k=C_k, rho_p=rho_p, rho_sk=rho_sk,
                m0=m0, V_zad=V_zad, V_profile=df_v5,
                a=a, b=b, k_ms_v5=k_ms_v5)

    # --- сводные метрики ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DG_s, %", f"{res['DG_s']:.3f}")
    c2.metric("DV_s, %", f"{res['DV_s']:.3f}")
    c3.metric("m_0 → m_s, %", f"{res['m_s']:.2f}",
              delta=f"+{res['m_s']-res['m_0']:.2f} %")
    c4.metric("k_ms (косв.)", f"{res['k_ms']:.3f}",
              delta=f"Δ к В.5 = {res['k_ms']-res['k_ms_v5']:+.3f}")

    st.caption(
        f"DV_s = ρ_п·DG_s/ρ_ск = {rho_p:.0f}·{res['DG_s']:.3f}/{rho_sk:.0f} = "
        f"{res['DV_s']:.3f} %  →  m_s = {res['m_0']:.2f} + {res['DV_s']:.3f} = "
        f"{res['m_s']:.2f} %  →  k_ms = {res['m_s']:.2f}/{res['m_0']:.2f} = "
        f"{res['k_ms']:.3f}"
    )
    st.metric("G_s (для V_зад), кг", f"{res['G_s_point']:.1f}")

    # --- профиль G_s(r) ---
    if res["df"] is not None:
        with st.expander("📋 Профиль G_s(r) — сетка из В.5", expanded=False):
            st.dataframe(res["df"][["r, м", "V_ks, м³", "G_s_В.7, кг"]].style.format({
                "r, м": "{:.2f}", "V_ks, м³": "{:.4f}", "G_s_В.7, кг": "{:.2f}"
            }), use_container_width=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=res["df"]["r, м"], y=res["df"]["G_s_В.7, кг"]/1000.0,
            mode="lines+markers", name="G_s (В.7), т"))
        fig.update_layout(
            title="Масса растворённой породы G_s(r) — В.7 (косвенный k_ms)",
            xaxis_title="r, м", yaxis_title="G_s, т", height=420)
        st.plotly_chart(fig, use_container_width=True)

    # --- сохранение для В.8 ---
    st.session_state["task_v7_result"] = res
    st.session_state["v7_k_ms"] = res["k_ms"]
    st.session_state["v7_m_s"]  = res["m_s"]

    return res
