"""Задача В.3 — обоснование расхода и давления при нагнетании кислотного раствора."""
import streamlit as st

from ._shared import render_precarpathian_constants
import pandas as pd
import plotly.graph_objects as go


_G         = 9.8      # м/с²
_RHO       = 1000.0   # кг/м³ (вода)
_Q_MIN     = 24.0     # м³/сут — минимум из В.10 (коррозия НКТ)
_Q_REC_LO  = 150.0    # м³/сут — нижний рекомендуемый
_Q_REC_HI  = 500.0    # м³/сут — верхний рекомендуемый

_DEFAULT_INJECT = [
    {"t, мин": 5,  "q, м³/сут": 225, "p_у, МПа": 15.0},
    {"t, мин": 10, "q, м³/сут": 225, "p_у, МПа": 13.5},
    {"t, мин": 20, "q, м³/сут": 225, "p_у, МПа": 12.5},
    {"t, мин": 30, "q, м³/сут": 225, "p_у, МПа": 12.0},
    {"t, мин": 40, "q, м³/сут": 225, "p_у, МПа": 12.0},
]


EXAMPLE = {
    "H":         2800.0,
    "p_opr":     20.0,
    "rho":       1070.0,
    "well_type": "нефтяная",
    "q_k":       250.0,
    "p_k":       12.0,
    "use_v20":   False,
    "inject":    _DEFAULT_INJECT,
}


# ─────────────────────────────────────────────────────────────────────────────
def solve(inp: dict, const: dict) -> dict:
    pg   = const["pressure_gradients"]
    sel  = const["well_selection"]

    H         = float(inp["H"])
    p_opr     = float(inp["p_opr"])
    rho       = float(inp["rho_fluid"])
    well_type = inp["well_type"]
    q_k       = float(inp["q_k"])
    p_k       = float(inp["p_k"])
    use_v20   = bool(inp.get("use_v20", False))

    # В.19 — гидростатическое давление
    p_gst = rho * _G * H * 1e-6

    # В.17 / В.20 — градиент ГРП
    if use_v20:
        grad_p_grp = 100.0 * (p_gst + 0.008 * H) / H
    else:
        if well_type == "нефтяная":
            grad_p_grp = pg["grad_p_grp_oil"]
        else:
            grad_p_grp = pg["grad_p_grp_water"]

    # Давление ГРП на забое (В.17 обратно)
    p_grp_zab = grad_p_grp * 0.01 * H

    # В.18 — градиент давления при КО (нормативный)
    if well_type == "нефтяная":
        grad_p_k_norm = pg["grad_p_k_oil"]
    else:
        grad_p_k_norm = pg["grad_p_k_water"]

    # Нормативное давление на устье при КО
    p_k_norm = grad_p_k_norm * 0.01 * H - p_gst

    # Фактический градиент при введённом p_k
    grad_p_k_fact = (p_gst + p_k) / (0.01 * H)

    # В.15 — p_k ≤ p_опр
    cond_p_opr = p_k <= p_opr

    # В.16 — grad p_k < grad p_грп
    cond_grp = grad_p_k_fact < grad_p_grp

    # В.10 — q_k ≥ 24 м³/сут
    cond_q_min = q_k >= _Q_MIN

    # Рекомендованный диапазон расхода
    in_rec_range = _Q_REC_LO <= q_k <= _Q_REC_HI

    decision = all([cond_p_opr, cond_grp, cond_q_min])

    return {
        "H": H, "p_opr": p_opr, "rho": rho,
        "p_gst": p_gst,
        "grad_p_grp": grad_p_grp, "p_grp_zab": p_grp_zab,
        "grad_p_k_norm": grad_p_k_norm, "p_k_norm": p_k_norm,
        "grad_p_k_fact": grad_p_k_fact,
        "q_k": q_k, "p_k": p_k,
        "cond_p_opr": cond_p_opr,
        "cond_grp": cond_grp,
        "cond_q_min": cond_q_min,
        "in_rec_range": in_rec_range,
        "decision": decision,
        "use_v20": use_v20,
    }


# ─────────────────────────────────────────────────────────────────────────────
def _render_precarpathian_constants(cfg: dict, well_type: str):
    pg = cfg["pressure_gradients"]
    sel = cfg["well_selection"]
    if well_type == "нефтяная":
        grp = pg["grad_p_grp_oil"]
        gk  = pg["grad_p_k_oil"]
        opr_lo, opr_hi = pg["p_opr_production_min"], pg["p_opr_production_max"]
    else:
        grp = pg["grad_p_grp_water"]
        gk  = pg["grad_p_k_water"]
        opr_lo, opr_hi = pg["p_opr_production_min"], pg["p_opr_production_max"]

    st.markdown(
        f"""
<div style="border:1px solid #e74c3c; border-radius:6px; padding:10px 16px; margin-bottom:12px;">
<b style="color:#e74c3c;">Константы Предкарпатья — {well_type} скважина</b><br><br>
<span style="color:#e74c3c;">
&bull; <b>grad p<sub>грп</sub> = {grp} МПа/100 м</b> &nbsp;—&nbsp; градиент давления ГРП (В.17)<br>
&bull; <b>grad p<sub>к</sub> = {gk} МПа/100 м</b> &nbsp;—&nbsp; нормативный градиент при КО (В.18)<br>
&bull; <b>p<sub>опр</sub> = {opr_lo}–{opr_hi} МПа</b> &nbsp;—&nbsp; типовой диапазон давлений опрессовки (В.15)<br>
&bull; <b>q<sub>min</sub> = {_Q_MIN:.0f} м³/сут</b> &nbsp;—&nbsp; минимальный расход кислоты (В.10)<br>
&bull; <b>q<sub>k</sub> = {_Q_REC_LO:.0f}–{_Q_REC_HI:.0f} м³/сут</b> &nbsp;—&nbsp; рекомендуемый рабочий диапазон расхода
</span>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_inputs(cfg: dict) -> dict:
    pg = cfg["pressure_gradients"]

    st.session_state.setdefault("v3_H",         0.0)
    st.session_state.setdefault("v3_p_opr",     0.0)
    st.session_state.setdefault("v3_rho",       0.0)
    st.session_state.setdefault("v3_well_type", "нефтяная")
    st.session_state.setdefault("v3_q_k",       0.0)
    st.session_state.setdefault("v3_p_k",       0.0)
    st.session_state.setdefault("v3_use_v20",   False)
    st.session_state.setdefault("v3_inject",    [
        {"t, мин": 0, "q, м³/сут": 0, "p_у, МПа": 0.0},
    ])

    with st.expander("Исходные данные — В.3", expanded=True):
        st.markdown("**Параметры скважины и колонны**")
        c1, c2, c3, c4 = st.columns(4)
        st.session_state["v3_H"] = c1.number_input(
            "H, м — глубина залегания пласта",
            value=float(st.session_state["v3_H"]), step=10.0,
        )
        st.session_state["v3_p_opr"] = c2.number_input(
            "p_опр, МПа — давление опрессовки колонны",
            value=float(st.session_state["v3_p_opr"]), step=0.5,
            help=f"Эксплуатационные: {pg['p_opr_production_min']}–{pg['p_opr_production_max']} МПа; "
                 f"Разведочные: {pg['p_opr_exploration_min']}–{pg['p_opr_exploration_max']} МПа",
        )
        st.session_state["v3_rho"] = c3.number_input(
            "ρ жидкости, кг/м³",
            value=float(st.session_state["v3_rho"]),
            help="Вода: 1000; 15% HCl: ~1070; 10% HF+HCl: ~1060",
        )
        st.session_state["v3_well_type"] = c4.selectbox(
            "Тип скважины",
            ["нефтяная", "водонагнетательная"],
            index=0 if st.session_state["v3_well_type"] == "нефтяная" else 1,
        )

        st.markdown("**Параметры закачки кислоты**")
        c1, c2, c3 = st.columns(3)
        st.session_state["v3_q_k"] = c1.number_input(
            "q_к, м³/сут — расход кислоты",
            value=float(st.session_state["v3_q_k"]),
            min_value=0.0, step=10.0,
            help=f"Рекомендуемый диапазон: {_Q_REC_LO:.0f}–{_Q_REC_HI:.0f} м³/сут",
        )
        st.session_state["v3_p_k"] = c2.number_input(
            "p_к, МПа — давление на устье при КО",
            value=float(st.session_state["v3_p_k"]), step=0.5,
            help="Берётся из кривой p_у = f(t) после стабилизации",
        )
        st.session_state["v3_use_v20"] = c3.checkbox(
            "Использовать В.20 для grad p_грп",
            value=bool(st.session_state["v3_use_v20"]),
            help="Включить, если данные по ГРП на месторождении отсутствуют",
        )

        st.markdown("**Кривая p_у = f(t) — результаты пробного нагнетания**")
        df = pd.DataFrame(st.session_state["v3_inject"])
        edited = st.data_editor(
            df, num_rows="dynamic", use_container_width=True, key="v3_inject_editor"
        )
        st.session_state["v3_inject"] = edited.to_dict("records")

    return {
        "H":         st.session_state["v3_H"],
        "p_opr":     st.session_state["v3_p_opr"],
        "rho_fluid": st.session_state["v3_rho"],
        "well_type": st.session_state["v3_well_type"],
        "q_k":       st.session_state["v3_q_k"],
        "p_k":       st.session_state["v3_p_k"],
        "use_v20":   st.session_state["v3_use_v20"],
        "inject_pts": st.session_state["v3_inject"],
    }


def _icon(ok: bool) -> str:
    return "[+]" if ok else "[-]"


# ─────────────────────────────────────────────────────────────────────────────
def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.3 — Расход и давление при нагнетании кислотного раствора")
    if btn_col.button("ПРИМЕР", key="btn_example_v3", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v3_{k}"] = v
        st.rerun()


    render_precarpathian_constants(cfg, task="В.3")
    with st.expander("Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `H` | глубина залегания пласта | м |
| `ρ` | плотность жидкости (вода / СКР / ГКР) | кг/м³ |
| `g` | ускорение свободного падения (= 9,8) | м/с² |
| `p_гст = ρ·g·H·10⁻⁶` | гидростатическое давление столба жидкости | МПа |
| `p_пл` | пластовое давление | МПа |
| `p_опр` | давление опрессовки эксплуатационной колонны | МПа |
| `p_к` | давление на устье при закачке кислоты | МПа |
| `p_к норм.` | нормативное `p_к` из табличного `grad p_к` | МПа |
| `p_грп` | давление гидроразрыва пласта | МПа |
| `grad p_к` | градиент давления при КО | МПа/100 м |
| `grad p_к.норм.` | нормативный градиент при КО (Предкарпатье) | МПа/100 м |
| `grad p_грп` | градиент давления гидроразрыва (табл./формула В.20) | МПа/100 м |
| `q_к` | расход (темп закачки) кислоты | м³/сут |
| `q_min` | минимально допустимый расход (= 24 м³/сут) | м³/сут |
| `q_рек` | рекомендуемый рабочий диапазон (150…500 м³/сут) | м³/сут |
| `t` | время от начала нагнетания | мин |
| `p_у = f(t)` | кривая давления на устье при пробном нагнетании | МПа |
""")

    # Тип скважины нужен для блока констант — читаем из session state
    wt = st.session_state.get("v3_well_type", "нефтяная")
    _render_precarpathian_constants(cfg, wt)

    with st.expander("Формулы методики", expanded=False):
        st.latex(r"\text{В.15} \quad p_k \leq p_{\text{опр}}")
        st.latex(r"\text{В.16} \quad \operatorname{grad}\,p_k < \operatorname{grad}\,p_{\text{грп}}")
        st.latex(r"\text{В.17} \quad \operatorname{grad}\,p_{\text{грп}} = \frac{p_{\text{грп}}}{0{,}01 \cdot H}")
        st.latex(r"\text{В.18} \quad \operatorname{grad}\,p_k = \frac{p_{\text{гст}} + p_k}{0{,}01 \cdot H}")
        st.latex(r"\text{В.19} \quad p_{\text{гст}} = \rho \cdot g \cdot H \cdot 10^{-6}")
        st.latex(r"\text{В.20} \quad \operatorname{grad}\,p_{\text{грп}} = \frac{100 \cdot (p_{\text{гст}} + 0{,}008H)}{H}")
        st.caption("В.20 применяется только при отсутствии данных о фактическом ГРП")

    inp = _render_inputs(cfg)
    res = solve(inp, cfg)

    # ── График p_у = f(t) ────────────────────────────────────────────────────
    pts = inp["inject_pts"]
    if pts:
        df_pts = pd.DataFrame(pts)
        cols = df_pts.columns.tolist()
        t_col   = cols[0]
        py_col  = cols[2] if len(cols) >= 3 else cols[-1]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_pts[t_col], y=df_pts[py_col],
            mode="lines+markers", name="p_у, МПа",
            line=dict(color="#2196F3", width=2),
            marker=dict(size=7),
        ))
        fig.add_hline(
            y=res["p_opr"], line_dash="dash", line_color="#e74c3c",
            annotation_text=f"p_опр = {res['p_opr']} МПа",
            annotation_position="bottom right",
        )
        fig.add_hline(
            y=res["p_k"], line_dash="dot", line_color="#ff9800",
            annotation_text=f"p_к = {res['p_k']} МПа (введено)",
            annotation_position="top right",
        )
        fig.update_layout(
            title="Кривая p_у = f(t) при пробном нагнетании",
            xaxis_title="t, мин",
            yaxis_title="p_у, МПа",
            height=350,
            margin=dict(t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Метрики верхнего уровня ──────────────────────────────────────────────
    st.markdown("### Результаты")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("p_гст, МПа",             f"{res['p_gst']:.3f}")
    c2.metric("grad p_грп, МПа/100 м",  f"{res['grad_p_grp']:.3f}",
              help="В.20" if res["use_v20"] else "Табличное значение (В.17)")
    c3.metric("grad p_к факт., МПа/100 м", f"{res['grad_p_k_fact']:.3f}")
    c4.metric("p_к норм. на устье, МПа",   f"{res['p_k_norm']:.2f}",
              help="Из нормативного grad p_к для данного типа скважины")

    # ── Критерии по шагам ───────────────────────────────────────────────────
    st.markdown("### Пошаговая проверка критериев")

    # Расход
    with st.expander(f"{_icon(res['cond_q_min'])} Расход кислоты q_к"):
        c1, c2, c3 = st.columns(3)
        c1.metric("q_к введённый, м³/сут",  f"{res['q_k']:.1f}")
        c2.metric("q_min (В.10), м³/сут",   f"{_Q_MIN:.0f}")
        c3.metric(f"Рек. диапазон {_Q_REC_LO:.0f}–{_Q_REC_HI:.0f} м³/сут",
                  "✓ в диапазоне" if res["in_rec_range"] else "вне диапазона")
        st.markdown(f"""
| Предел | Значение | Обоснование |
|---|---|---|
| Минимум | {_Q_MIN:.0f} м³/сут | 6 м³ кислоты за 6 ч (коррозия НКТ), В.10 |
| Рекомендуемый | {_Q_REC_LO:.0f}–{_Q_REC_HI:.0f} м³/сут | Промысловый опыт КО |
| Максимум | не ограничен | Определяется только давлением |
""")
        if not res["cond_q_min"]:
            st.error(f"q_к < q_min! Кислота не успеет прокачаться за допустимое время.")

    # В.19
    with st.expander("🔢 В.19 — Гидростатическое давление"):
        c1, c2, c3 = st.columns(3)
        c1.metric("ρ, кг/м³", f"{res['rho']:.0f}")
        c2.metric("H, м",     f"{res['H']:.0f}")
        c3.metric("p_гст, МПа", f"{res['p_gst']:.3f}")
        st.latex(
            rf"p_{{гст}} = {res['rho']:.0f} \times 9{{,}}8 \times {res['H']:.0f} "
            rf"\times 10^{{-6}} = {res['p_gst']:.3f} \text{{ МПа}}"
        )

    # В.17 / В.20
    grp_label = "В.20 (расчётный, данных по ГРП нет)" if res["use_v20"] else "В.17 (табличный, Предкарпатье)"
    with st.expander(f"🔢 {grp_label} — Градиент давления ГРП"):
        c1, c2 = st.columns(2)
        c1.metric("grad p_грп, МПа/100 м", f"{res['grad_p_grp']:.3f}")
        c2.metric("p_грп на забое, МПа",   f"{res['p_grp_zab']:.2f}")
        if res["use_v20"]:
            st.latex(
                rf"\operatorname{{grad}}\,p_{{грп}} = "
                rf"\frac{{100 \cdot ({res['p_gst']:.3f} + 0{{,}}008 \times {res['H']:.0f})}}"
                rf"{{{res['H']:.0f}}} = {res['grad_p_grp']:.3f} \text{{ МПа/100 м}}"
            )
        else:
            st.caption(f"Табличное значение для {'нефтяной' if inp['well_type'] == 'нефтяная' else 'водонагнетательной'} скважины Предкарпатья")

    # В.18
    with st.expander("🔢 В.18 — Нормативное давление на устье при КО"):
        c1, c2 = st.columns(2)
        c1.metric("grad p_к норм., МПа/100 м", f"{res['grad_p_k_norm']:.2f}")
        c2.metric("p_к норм. на устье, МПа",   f"{res['p_k_norm']:.2f}")
        st.latex(
            rf"p_{{к}} = \operatorname{{grad}}\,p_{{к}} \times 0{{,}}01 \times H - p_{{гст}} = "
            rf"{res['grad_p_k_norm']:.2f} \times 0{{,}}01 \times {res['H']:.0f} - "
            rf"{res['p_gst']:.3f} = {res['p_k_norm']:.2f} \text{{ МПа}}"
        )

    # В.15
    with st.expander(f"{_icon(res['cond_p_opr'])} В.15 — p_к ≤ p_опр"):
        c1, c2, c3 = st.columns(3)
        c1.metric("p_к введённое, МПа", f"{res['p_k']:.2f}")
        c2.metric("p_опр, МПа",         f"{res['p_opr']:.2f}")
        c3.metric("Условие p_к ≤ p_опр",
                  "выполнено" if res["cond_p_opr"] else "НЕ выполнено")
        if res["cond_p_opr"]:
            st.success("Закачку можно проводить **без пакера** — упрощает и удешевляет процесс.")
        else:
            st.error("Требуется пакер или снижение расхода q_к.")

    # В.16
    with st.expander(f"{_icon(res['cond_grp'])} В.16 — grad p_к < grad p_грп"):
        c1, c2, c3 = st.columns(3)
        c1.metric("grad p_к факт., МПа/100 м",  f"{res['grad_p_k_fact']:.3f}")
        c2.metric("grad p_грп, МПа/100 м",       f"{res['grad_p_grp']:.3f}")
        c3.metric("Условие grad p_к < grad p_грп",
                  "выполнено" if res["cond_grp"] else "НЕ выполнено")
        st.latex(
            rf"\operatorname{{grad}}\,p_{{к}} = "
            rf"\frac{{{res['p_gst']:.3f} + {res['p_k']:.2f}}}{{0{{,}}01 \times {res['H']:.0f}}} = "
            rf"{res['grad_p_k_fact']:.3f} \text{{ МПа/100 м}}"
        )
        if not res["cond_grp"]:
            st.error("Возможен гидроразрыв пласта! Снизить p_к или q_к.")

    # ── Итоговый вывод ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Итоговое заключение")

    criteria = [
        ("В.10  q_к ≥ 24 м³/сут",              res["cond_q_min"]),
        ("В.15  p_к ≤ p_опр",                   res["cond_p_opr"]),
        ("В.16  grad p_к < grad p_грп",          res["cond_grp"]),
    ]
    for label, ok in criteria:
        st.write(f"{'' if ok else ''} {label}")

    if res["decision"]:
        st.success(
            f"**Параметры закачки обоснованы.** "
            f"q_к = {res['q_k']:.0f} м³/сут, p_к = {res['p_k']:.2f} МПа."
        )
    else:
        failed = [label for label, ok in criteria if not ok]
        st.error(f"**Параметры не удовлетворяют условиям.** Не выполнены: {', '.join(failed)}.")

    st.session_state["task_v3_result"] = res
    return res
