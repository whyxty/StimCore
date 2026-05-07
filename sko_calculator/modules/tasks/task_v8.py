"""Задача В.8 — изменение проницаемости после СКО и ГКО.

Формулы по порядку:
    k_0   = A · m_0^B                       (табл. В.11) — начальная проницаемость
    k_s*  = 0.9 · exp(0.2 · C_к)            (В.44)       — прирост после СКО
    k_s   = k_s* · k_0                      (В.45)       — после СКО
    k_g*  = k_s* · (k_ms·k_mg)^n            (В.46/В.47)  — n=3 при k_0<0.001, иначе n=2
    k_g   = k_g* · k_0                      (В.48)       — после СКО+ГКО

Источники входных данных:
    - В.5 → k_ms (лаб.)            или
    - В.7 → k_ms (косв., fallback)
    - В.1 → k_mg (лаб.)
    - config.json: permeability_regressions (КЛ 1..5),
                   permeability_change_after_sko (A=0.9, B=0.2),
                   collector_types (имя КЛ, k_у.ф)
"""
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


_K0_THRESHOLD = 0.001   # мкм² — граница выбора (В.46) vs (В.47)


EXAMPLE = {
    "KL":              "KL_2",
    "m0":              14.0,
    "C_k":             3.1,
    "k_ms":            1.20,
    "k_mg":            1.15,
    "k0_use_override": False,
    "k0_user":         0.05,
}


def k0_from_regression(KL_key: str, m0: float, regs: dict) -> float:
    """k_0 = A · m_0^B (мкм²)."""
    p = regs[KL_key]
    return p["A"] * (m0 ** p["B"])


def k_s_star(C_k: float, A: float = 0.9, B: float = 0.2) -> float:
    """(В.44): k_s* = A · exp(B · C_к)."""
    return A * math.exp(B * C_k)


def k_g_star(k_s_star_v: float, k_ms: float, k_mg: float, k0: float) -> tuple[float, int]:
    """(В.46)/(В.47): возвращает (k_g*, n)."""
    n = 3 if k0 < _K0_THRESHOLD else 2
    return k_s_star_v * (k_ms * k_mg) ** n, n


def solve(*, KL_key: str, m0: float, C_k: float, k_ms: float, k_mg: float,
          k0_override: float | None, cfg: dict) -> dict:
    regs    = cfg.get("permeability_regressions", {})
    sko_par = cfg.get("permeability_change_after_sko", {"A": 0.9, "B": 0.2})

    k0_reg = k0_from_regression(KL_key, m0, regs)
    k0     = float(k0_override) if k0_override is not None else k0_reg

    ks_star = k_s_star(C_k, sko_par["A"], sko_par["B"])
    ks      = ks_star * k0
    kg_star, n = k_g_star(ks_star, k_ms, k_mg, k0)
    kg      = kg_star * k0

    return {
        "KL_key":  KL_key,
        "m0":      m0, "C_k": C_k,
        "k_ms":    k_ms, "k_mg": k_mg,
        "k0_reg":  k0_reg, "k0": k0,
        "ks_star": ks_star, "ks": ks,
        "kg_star": kg_star, "kg": kg,
        "n_exp":   n,
        "growth_sko":     ks / k0 if k0 else 0.0,
        "growth_sko_gko": kg / k0 if k0 else 0.0,
        "growth_gko":     kg / ks if ks else 0.0,
    }


def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.8 — Изменение проницаемости после СКО и ГКО")
    if btn_col.button("ПРИМЕР", key="btn_example_v8", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v8_{k}"] = v
        st.rerun()

    with st.expander("📖 Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| КЛ | тип коллектора (табл. В.10) | – |
| `m_0` | начальная пористость | % |
| `C_к` | карбонатность породы | % |
| `k_у.ф` | коэффициент участия пор в фильтрации (табл. В.10) | – |
| `k_0` | начальная проницаемость (по регрессии Будзеня, табл. В.11) | мкм² |
| `A, B` | коэффициенты регрессии `k_0 = A·m_0^B` для выбранного КЛ | – |
| `k_s*` | коэффициент возрастания проницаемости после СКО (= 0,9·exp(0,2·C_к)) | – |
| `k_s` | проницаемость после СКО (= k_s* · k_0) | мкм² |
| `k_ms` | прирост пористости после СКО (из В.5/В.7) | – |
| `k_mg` | прирост пористости после ГКО (из В.1) | – |
| `k_g*` | коэффициент возрастания проницаемости после СКО+ГКО | – |
| `n` | показатель степени: 3 при `k_0 < 0,001 мкм²`, иначе 2 | – |
| `k_g` | проницаемость после СКО+ГКО (= k_g* · k_0) | мкм² |
""")

    st.latex(r"k_0=A\,m_0^{B}\;\text{(табл. В.11)};\;\;"
             r"k_s^{*}=0{,}9\exp(0{,}2\,C_{\text{к}})\;(B.44);\;\;"
             r"k_s=k_s^{*}k_0\;(B.45)")
    st.latex(r"k_g^{*}=k_s^{*}(k_{ms}k_{mg})^{n},\;\;"
             r"n=\begin{cases}3,&k_0<0{,}001\;\text{мкм}^2\\2,&k_0\ge 0{,}001\;\text{мкм}^2\end{cases}"
             r"\;(B.46/B.47);\;\;k_g=k_g^{*}k_0\;(B.48)")

    # --- константы ---
    regs    = cfg.get("permeability_regressions", {})
    sko_par = cfg.get("permeability_change_after_sko", {"A": 0.9, "B": 0.2})
    coll    = cfg.get("collector_types", {})

    with st.expander("📐 Константы (из config.json)", expanded=False):
        st.caption(f"Профиль: **{cfg.get('field_name', '?')}**.")
        rows = []
        for k in ["KL_1", "KL_2", "KL_3", "KL_4", "KL_5"]:
            if k in regs:
                ct = coll.get(k, {})
                rows.append({
                    "КЛ":              k.replace("KL_", ""),
                    "Тип":             ct.get("name", "—"),
                    "Цемент":          ct.get("cement", "—"),
                    "Глинистость, %":  ct.get("clay", "—"),
                    "k_у.ф":           ct.get("k_uf", "—"),
                    "A":               regs[k]["A"],
                    "B":               regs[k]["B"],
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"Параметры (В.44): k_s* = {sko_par['A']}·exp({sko_par['B']}·C_к)")

    # --- подтягивание k_ms, k_mg из других задач ---
    v5  = st.session_state.get("task_v5_result")
    v7  = st.session_state.get("task_v7_result")
    v1  = st.session_state.get("task_v1_result")

    k_ms_default = None
    k_ms_src     = None
    if v5 and "k_ms" in v5:
        k_ms_default = float(v5["k_ms"]); k_ms_src = "В.5 (лаб.)"
    elif v7 and "k_ms" in v7:
        k_ms_default = float(v7["k_ms"]); k_ms_src = "В.7 (косв.)"
    else:
        k_ms_default = 1.20

    k_mg_default = None
    k_mg_src     = None
    if v1 and "k_mg" in v1:
        k_mg_default = float(v1["k_mg"]); k_mg_src = "В.1"
    else:
        k_mg_default = 1.15

    info_parts = []
    if k_ms_src: info_parts.append(f"k_ms подтянут из **{k_ms_src}** = {k_ms_default:.3f}")
    if k_mg_src: info_parts.append(f"k_mg подтянут из **{k_mg_src}** = {k_mg_default:.3f}")
    if info_parts:
        st.info("  •  ".join(info_parts))
    else:
        st.warning("k_ms / k_mg из других задач не найдены — используются значения по умолчанию.")

    # --- ввод ---
    _DEF = {
        "KL":              "KL_1",
        "m0":              0.0,
        "C_k":             0.0,
        "k_ms":            1.0,
        "k_mg":            1.0,
        "k0_use_override": False,
        "k0_user":         0.0,
    }
    for k, v in _DEF.items():
        st.session_state.setdefault(f"v8_{k}", v)

    KL_options = [k for k in ["KL_1", "KL_2", "KL_3", "KL_4", "KL_5"] if k in regs]
    KL_labels  = [f"{k.replace('KL_', 'КЛ ')} — {coll.get(k, {}).get('name', '')}"
                  for k in KL_options]

    with st.expander("📥 Исходные данные — В.8", expanded=True):
        c1, c2, c3 = st.columns(3)
        idx = KL_options.index(st.session_state["v8_KL"]) \
              if st.session_state["v8_KL"] in KL_options else 1
        sel_label = c1.selectbox("Тип коллектора (КЛ)", KL_labels, index=idx)
        st.session_state["v8_KL"] = KL_options[KL_labels.index(sel_label)]

        st.session_state["v8_m0"]   = c2.number_input(
            "m₀, % — начальная пористость",
            value=float(st.session_state["v8_m0"]), step=0.5)
        st.session_state["v8_C_k"]  = c3.number_input(
            "C_к, % — карбонатность",
            value=float(st.session_state["v8_C_k"]), step=0.1)

        c1, c2 = st.columns(2)
        st.session_state["v8_k_ms"] = c1.number_input(
            f"k_ms — прирост пористости после СКО ({k_ms_src or 'по умолч.'})",
            value=float(st.session_state["v8_k_ms"]), min_value=1.0, step=0.01)
        st.session_state["v8_k_mg"] = c2.number_input(
            f"k_mg — прирост пористости после ГКО ({k_mg_src or 'по умолч.'})",
            value=float(st.session_state["v8_k_mg"]), min_value=1.0, step=0.01)

        c1, c2 = st.columns([1, 2])
        st.session_state["v8_k0_use_override"] = c1.checkbox(
            "Задать k_0 вручную",
            value=bool(st.session_state["v8_k0_use_override"]),
            help="Если k_0 известно из ГИС/керна, можно ввести вручную "
                 "вместо расчёта по регрессии Будзеня (табл. В.11).")
        if st.session_state["v8_k0_use_override"]:
            st.session_state["v8_k0_user"] = c2.number_input(
                "k_0, мкм² — пользовательское значение",
                value=float(st.session_state["v8_k0_user"]),
                min_value=0.0, step=0.001, format="%.6f")

    # --- расчёт ---
    KL_key = st.session_state["v8_KL"]
    k0_override = st.session_state["v8_k0_user"] if st.session_state["v8_k0_use_override"] else None
    res = solve(KL_key=KL_key, m0=st.session_state["v8_m0"], C_k=st.session_state["v8_C_k"],
                k_ms=st.session_state["v8_k_ms"], k_mg=st.session_state["v8_k_mg"],
                k0_override=k0_override, cfg=cfg)

    # --- сводные метрики ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("k₀ (по регрессии), мкм²", f"{res['k0_reg']:.6f}")
    c2.metric("k₀ (используется), мкм²", f"{res['k0']:.6f}",
              delta="вручную" if k0_override is not None else "по регрессии",
              delta_color="off")
    c3.metric("k_s* (раз)", f"{res['ks_star']:.3f}")
    c4.metric("k_g* (раз)", f"{res['kg_star']:.3f}",
              delta=f"n = {res['n_exp']}", delta_color="off")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("k_s, мкм² (после СКО)",      f"{res['ks']:.6f}",
              delta=f"×{res['growth_sko']:.2f}")
    c2.metric("k_g, мкм² (после СКО+ГКО)",  f"{res['kg']:.6f}",
              delta=f"×{res['growth_sko_gko']:.2f}")
    c3.metric("Доп. эффект ГКО (k_g/k_s)",  f"×{res['growth_gko']:.2f}")
    c4.metric("Применённая формула",
              "В.46 (k₀<0,001)" if res['n_exp'] == 3 else "В.47 (k₀≥0,001)")

    st.caption(
        f"k_s* = 0,9·exp(0,2·{res['C_k']:.2f}) = {res['ks_star']:.3f};  "
        f"k_g* = k_s*·(k_ms·k_mg)^{res['n_exp']} = "
        f"{res['ks_star']:.3f}·({res['k_ms']:.3f}·{res['k_mg']:.3f})^{res['n_exp']} = "
        f"{res['kg_star']:.3f}"
    )

    # --- таблица «до/после» ---
    st.markdown("**Сводка изменения проницаемости:**")
    df_cmp = pd.DataFrame([{
        "Этап":             "Исходно",
        "k, мкм²":          res["k0"],
        "Прирост к k₀":     "1.00",
    }, {
        "Этап":             "После СКО",
        "k, мкм²":          res["ks"],
        "Прирост к k₀":     f"×{res['growth_sko']:.2f}",
    }, {
        "Этап":             "После СКО+ГКО",
        "k, мкм²":          res["kg"],
        "Прирост к k₀":     f"×{res['growth_sko_gko']:.2f}",
    }])
    st.dataframe(df_cmp.style.format({"k, мкм²": "{:.6f}"}),
                 use_container_width=True, hide_index=True)

    # --- график рис. В.4 ---
    Ck_grid = np.linspace(0.0, 10.0, 101)
    ks_curve = 0.9 * np.exp(0.2 * Ck_grid)

    # верхние/нижние границы для k_g* (как на рис. В.4)
    pair_lo = 1.10
    pair_hi = 1.25
    n_kg = res['n_exp']

    kg_curve_user = ks_curve * (res['k_ms'] * res['k_mg']) ** n_kg
    kg_lo = ks_curve * (pair_lo * pair_lo) ** n_kg
    kg_hi = ks_curve * (pair_hi * pair_hi) ** n_kg

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Ck_grid, y=ks_curve, mode="lines",
                             name="1) k_s* (СКО, B.44)",
                             line=dict(color="#1f77b4", width=2.5)))
    fig.add_trace(go.Scatter(x=Ck_grid, y=kg_lo, mode="lines",
                             name=f"k_g* нижняя (k_ms=k_mg=1,1; n={n_kg})",
                             line=dict(color="#d62728", width=1, dash="dot")))
    fig.add_trace(go.Scatter(x=Ck_grid, y=kg_hi, mode="lines",
                             name=f"k_g* верхняя (k_ms=k_mg=1,25; n={n_kg})",
                             line=dict(color="#d62728", width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(214,39,40,0.10)"))
    fig.add_trace(go.Scatter(x=Ck_grid, y=kg_curve_user, mode="lines",
                             name=f"k_g* (введ. k_ms={res['k_ms']:.2f}, "
                                  f"k_mg={res['k_mg']:.2f}; n={n_kg})",
                             line=dict(color="#d62728", width=2.5)))
    # точка пользователя
    fig.add_trace(go.Scatter(x=[res['C_k']], y=[res['ks_star']], mode="markers",
                             name="Точка: k_s*",
                             marker=dict(color="#1f77b4", size=11, symbol="circle")))
    fig.add_trace(go.Scatter(x=[res['C_k']], y=[res['kg_star']], mode="markers",
                             name="Точка: k_g*",
                             marker=dict(color="#d62728", size=11, symbol="diamond")))
    fig.update_layout(
        title="Рис. В.4 — изменение проницаемости после СКО и ГКО",
        xaxis_title="C_к, %",
        yaxis_title="Коэффициент возрастания проницаемости (раз)",
        yaxis_type="log",
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=-0.35),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- сохранение для В.9 ---
    st.session_state["task_v8_result"] = res
    st.session_state["v8_k0"] = res["k0"]
    st.session_state["v8_ks"] = res["ks"]
    st.session_state["v8_kg"] = res["kg"]

    return res
