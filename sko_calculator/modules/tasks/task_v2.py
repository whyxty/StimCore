"""Задача В.2 — обоснование выбора скважины (ограниченная информация)."""
import streamlit as st

from ._shared import render_precarpathian_constants
import pandas as pd


_Q_PR   = 24.0   # мин. приёмистость, м³/сут (В.10)
_H_PR   = 5.0    # мин. толщина пласта, м (В.11)
_CGL_PR = 10.0   # макс. глинистость, % (В.12)
_E_PR   = 0.5    # мин. относительная гидропроводность (В.13)
_K_ENR  = 0.7    # мин. коэффициент энергопотенциала (В.14)
_RHO    = 1000.0 # плотность воды, кг/м³
_G      = 9.81   # ускорение свободного падения, м/с²

_DEFAULT_LAYERS = [
    {"interval": "гр. 7–9 %",   "h_ef": 13.2, "porosity": 8.0,  "k0": 0.005, "treat": True},
    {"interval": "гр. 9–11 %",  "h_ef": 27.2, "porosity": 10.0, "k0": 0.020, "treat": True},
    {"interval": "гр. 11–13 %", "h_ef": 14.1, "porosity": 12.0, "k0": 0.060, "treat": False},
    {"interval": "гр. 13–15 %", "h_ef": 27.4, "porosity": 14.0, "k0": 0.120, "treat": True},
]


EXAMPLE = {
    "Q_f":    86.6,
    "q_inj":  150.0,
    "p_pl":   25.0,
    "H":      2800.0,
    "C_gl":   6.6,
    "h_ef":   81.9,
    "layers": _DEFAULT_LAYERS,
}


def _q_ud(porosity: float, rows: list) -> float:
    """Удельный дебит по таблице В.2."""
    for r in rows:
        if r["porosity_min"] <= porosity < r["porosity_max"]:
            return float(r["specific_debit"])
    return 0.0


def solve(inp: dict, const: dict) -> dict:
    rows   = const["specific_debit_table"]["rows"]
    sel    = const["well_selection"]

    Q_f    = float(inp["Q_f"])
    q_inj  = float(inp["q_inj"])
    h_ef   = float(inp["h_ef"])
    C_gl   = float(inp["C_gl"])
    p_pl   = float(inp["p_pl"])
    H      = float(inp["H"])
    layers = inp.get("layers_table") or []

    # ── В.9 — ожидаемый дебит ────────────────────────────────────────────────
    layer_rows = []
    Q_oj = 0.0
    eps_obr = 0.0   # гидропроводность обрабатываемых пластов
    eps_skv = 0.0   # гидропроводность всех пластов

    for L in layers:
        m   = float(L.get("porosity", 0))
        h   = float(L.get("h_ef", 0))
        k0  = float(L.get("k0", 0))
        trt = bool(L.get("treat", True))

        q_sp = _q_ud(m, rows)
        Qi   = q_sp * h
        Q_oj += Qi

        eps_i = h * k0
        eps_skv += eps_i
        if trt:
            eps_obr += eps_i

        layer_rows.append({
            "Интервал":          L.get("interval", "—"),
            "h_эф, м":           h,
            "m₀, %":             m,
            "k₀, мкм²":          k0,
            "q_уд, м³/(сут·м)":  q_sp,
            "Q_i, м³/сут":       round(Qi, 2),
            "ε_i, мкм²·м":       round(eps_i, 4),
            "Обработка":         "✓" if trt else "—",
        })

    # ── В.8 — ОД ─────────────────────────────────────────────────────────────
    OD = Q_f / Q_oj if Q_oj else float("inf")
    cond_OD = OD < 1.0

    # ── В.10 — приёмистость ──────────────────────────────────────────────────
    cond_q = q_inj >= _Q_PR

    # ── В.11 — толщина ───────────────────────────────────────────────────────
    cond_h = h_ef >= _H_PR

    # ── В.12 — глинистость ───────────────────────────────────────────────────
    cond_Cgl = C_gl <= _CGL_PR

    # ── В.13 — относительная гидропроводность ────────────────────────────────
    e_ot = eps_obr / eps_skv if eps_skv else 0.0
    cond_e = e_ot > _E_PR

    # ── В.14 — энергетический потенциал ──────────────────────────────────────
    p_gst  = _RHO * _G * H * 1e-6
    k_enr  = p_pl / p_gst if p_gst else 0.0
    cond_enr = k_enr > _K_ENR

    decision = all([cond_OD, cond_q, cond_h, cond_Cgl, cond_e, cond_enr])

    return {
        "Q_f": Q_f, "Q_oj": Q_oj,
        "OD": OD, "cond_OD": cond_OD,
        "q_inj": q_inj, "cond_q": cond_q,
        "h_ef": h_ef, "cond_h": cond_h,
        "C_gl": C_gl, "cond_Cgl": cond_Cgl,
        "eps_obr": eps_obr, "eps_skv": eps_skv,
        "e_ot": e_ot, "cond_e": cond_e,
        "p_gst": p_gst, "k_enr": k_enr, "cond_enr": cond_enr,
        "layer_rows": layer_rows,
        "decision": decision,
    }


def _render_precarpathian_constants():
    st.markdown(
        f"""
<div style="border:1px solid #e74c3c; border-radius:6px; padding:10px 16px; margin-bottom:12px;">
<b style="color:#e74c3c;">Константи Предкарпатья (нормативні порогові значення)</b><br><br>
<span style="color:#e74c3c;">
&bull; <b>q<sub>пр</sub> = {_Q_PR:.0f} м³/сут</b> &nbsp;—&nbsp; мінімальна приймистість (В.10): 6 м³ кислоти за 6 год<br>
&bull; <b>h<sub>пр</sub> = {_H_PR:.0f} м</b> &nbsp;—&nbsp; мінімальна ефективна товщина (В.11): h̄ − 2σ = 13 − 2·4<br>
&bull; <b>C<sub>г.пр</sub> = {_CGL_PR:.0f} %</b> &nbsp;—&nbsp; максимальна глинистість колекторів (В.12)<br>
&bull; <b>ε<sub>от.пр</sub> = {_E_PR}</b> &nbsp;—&nbsp; мінімальна відносна гідропровідність (В.13)<br>
&bull; <b>k<sub>енр.пр</sub> = {_K_ENR}</b> &nbsp;—&nbsp; мінімальний енергопотенціал пласта (В.14)
</span>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_inputs(cfg: dict) -> dict:
    # defaults — пустые при первом открытии; реальные значения по кнопке «ПРИМЕР»
    st.session_state.setdefault("v2_Q_f",    0.0)
    st.session_state.setdefault("v2_q_inj",  0.0)
    st.session_state.setdefault("v2_p_pl",   0.0)
    st.session_state.setdefault("v2_H",      0.0)
    st.session_state.setdefault("v2_C_gl",   0.0)
    st.session_state.setdefault("v2_h_ef",   0.0)
    st.session_state.setdefault("v2_layers", [
        {"interval": "", "h_ef": 0.0, "porosity": 0.0, "k0": 0.0, "treat": False},
    ])

    with st.expander("📥 Исходные данные — В.2", expanded=True):
        st.markdown("**Дебит и приёмистость**")
        c1, c2 = st.columns(2)
        st.session_state["v2_Q_f"] = c1.number_input(
            "Q_ф, м³/сут — фактический дебит жидкости",
            value=float(st.session_state["v2_Q_f"]),
            help="Замер на устье скважины",
        )
        st.session_state["v2_q_inj"] = c2.number_input(
            "q, м³/сут — приёмистость при нагнетании (p < p_опр)",
            value=float(st.session_state["v2_q_inj"]),
            help="Замер при нагнетании с давлением ниже давления опрессовки колонны",
        )

        st.markdown("**Параметры пласта**")
        c1, c2, c3 = st.columns(3)
        st.session_state["v2_p_pl"] = c1.number_input(
            "p_пл, МПа — пластовое давление",
            value=float(st.session_state["v2_p_pl"]), step=0.5,
            help="КВД или статический уровень, приведённое к глубине H",
        )
        st.session_state["v2_H"] = c2.number_input(
            "H, м — глубина залегания пласта",
            value=float(st.session_state["v2_H"]), step=10.0,
        )
        st.session_state["v2_h_ef"] = c3.number_input(
            "h_эф, м — суммарная перфорированная толщина",
            value=float(st.session_state["v2_h_ef"]), step=1.0,
            help="По данным ГИС + перфорационный план",
        )

        st.markdown("**Состав породы**")
        st.session_state["v2_C_gl"] = st.number_input(
            "C_гл, % — содержание глин в коллекторах",
            value=float(st.session_state["v2_C_gl"]),
            help="Гамма-каротаж (ГК) или химический анализ керна",
        )

        st.markdown(
            "**Таблица продуктивных пластов** "
            "(ГИС: интервал, h_эф, пористость, k₀; "
            "колонка «treat» — подвергается обработке)"
        )
        df = pd.DataFrame(st.session_state["v2_layers"])
        edited = st.data_editor(
            df, num_rows="dynamic", use_container_width=True, key="v2_layers_editor"
        )
        st.session_state["v2_layers"] = edited.to_dict("records")

    return {
        "Q_f":        st.session_state["v2_Q_f"],
        "q_inj":      st.session_state["v2_q_inj"],
        "p_pl":       st.session_state["v2_p_pl"],
        "H":          st.session_state["v2_H"],
        "C_gl":       st.session_state["v2_C_gl"],
        "h_ef":       st.session_state["v2_h_ef"],
        "layers_table": st.session_state["v2_layers"],
    }


def _icon(ok: bool) -> str:
    return "✅" if ok else "❌"


def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.2 — Обоснование выбора скважины (ограниченная информация)")
    if btn_col.button("ПРИМЕР", key="btn_example_v2", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v2_{k}"] = v
        st.rerun()

    render_precarpathian_constants(cfg)

    with st.expander("📖 Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `Q_ф` | фактический дебит жидкости (замер на устье) | м³/сут |
| `Q_ож` | ожидаемый дебит по таблице удельных дебитов | м³/сут |
| `q_уд,i` | удельный дебит i-го пласта (табл. В.2) | м³/(сут·м) |
| `ОД = Q_ф/Q_ож` | отношение дебитов | – |
| `q` | приёмистость скважины при нагнетании | м³/сут |
| `q_пр` | минимальная приёмистость (= 24 м³/сут) | м³/сут |
| `h_эф` | суммарная перфорированная толщина | м |
| `h_пр` | минимально допустимая толщина (= 5 м) | м |
| `m_0` | пористость пласта (ГИС) | % |
| `k_0` | начальная проницаемость | мкм² |
| `C_гл` | глинистость коллектора | % |
| `C_г.пр` | максимально допустимая глинистость (= 10 %) | % |
| `ε_i = k_0·h` | гидропроводность i-го пласта | мкм²·м |
| `ε_обр` | гидропроводность обрабатываемых пластов | мкм²·м |
| `ε_скв` | суммарная гидропроводность всех пластов | мкм²·м |
| `ε_от = ε_обр/ε_скв` | относительная гидропроводность | – |
| `ε_от.пр` | минимальное значение `ε_от` (= 0,5) | – |
| `p_пл` | пластовое давление | МПа |
| `H` | глубина залегания пласта | м |
| `ρ` | плотность воды (= 1000 кг/м³) | кг/м³ |
| `g` | ускорение свободного падения (= 9,81) | м/с² |
| `p_гст = ρ·g·H·10⁻⁶` | гидростатическое давление | МПа |
| `k_энр = p_пл/p_гст` | коэффициент энергопотенциала | – |
| `k_энр.пр` | минимальный энергопотенциал (= 0,7) | – |
""")

    _render_precarpathian_constants()

    with st.expander("📐 Формулы методики", expanded=False):
        st.latex(r"\text{В.8} \quad ОД = \frac{Q_\phi}{Q_{ож}} < 1")
        st.latex(r"\text{В.9} \quad Q_{ож} = \sum_{i=1}^{n} q_{уд,i} \cdot h_{эф,i}")
        st.latex(r"\text{В.10} \quad q \geq q_{пр} = 24 \ \text{м}^3/\text{сут}")
        st.latex(r"\text{В.11} \quad h_{эф} \geq h_{пр} = 5 \ \text{м}")
        st.latex(r"\text{В.12} \quad C_{гл} \leq C_{г.пр} = 10\%")
        st.latex(r"\text{В.13} \quad \varepsilon_{от} = \frac{\varepsilon_{обр}}{\varepsilon_{скв}} > 0{,}5")
        st.latex(r"\text{В.14} \quad k_{энр} = \frac{p_{пл}}{p_{гст}} > 0{,}7, \quad p_{гст} = \rho g H \cdot 10^{-6}")

    with st.expander("📋 Таблица В.2 — удельные дебиты эоценовых пластов Предкарпатья", expanded=False):
        rows = cfg["specific_debit_table"]["rows"]
        df_ref = pd.DataFrame([
            {"Пористость, %": f"{r['porosity_min']}–{r['porosity_max'] if r['porosity_max'] < 999 else '≥' + str(r['porosity_min'])}",
             "q_уд, м³/(сут·м)": r["specific_debit"]}
            for r in rows
        ])
        st.dataframe(df_ref, use_container_width=True, hide_index=True)

    inp = _render_inputs(cfg)
    res = solve(inp, cfg)

    # ── Метрики верхнего уровня ──────────────────────────────────────────────
    st.markdown("### Результаты")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Q_ф, м³/сут",  f"{res['Q_f']:.1f}")
    c2.metric("Q_ож, м³/сут", f"{res['Q_oj']:.2f}")
    c3.metric("ОД = Qф / Qож", f"{res['OD']:.3f}",
              delta="< 1 ✓" if res["cond_OD"] else "≥ 1 ✗",
              delta_color="normal" if res["cond_OD"] else "inverse")
    c4.metric("k_энр",         f"{res['k_enr']:.3f}",
              delta="> 0.7 ✓" if res["cond_enr"] else "≤ 0.7 ✗",
              delta_color="normal" if res["cond_enr"] else "inverse")

    # ── Критерии по шагам ───────────────────────────────────────────────────
    st.markdown("### Пошаговая проверка критериев")

    # В.8–В.9
    with st.expander(f"{_icon(res['cond_OD'])} В.8–В.9 — Отношение дебитов ОД"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Q_ф, м³/сут",  f"{res['Q_f']:.1f}")
        c2.metric("Q_ож, м³/сут", f"{res['Q_oj']:.2f}")
        c3.metric("ОД",           f"{res['OD']:.4f}",
                  delta="< 1 ✓" if res["cond_OD"] else "≥ 1 ✗",
                  delta_color="normal" if res["cond_OD"] else "inverse")
        st.markdown("**Расчёт Q_ож по пластам (Таблица В.2):**")
        st.dataframe(pd.DataFrame(res["layer_rows"]), use_container_width=True, hide_index=True)

    # В.10
    with st.expander(f"{_icon(res['cond_q'])} В.10 — Приёмистость скважины"):
        c1, c2, c3 = st.columns(3)
        c1.metric("q факт., м³/сут", f"{res['q_inj']:.1f}")
        c2.metric("q_пр, м³/сут",    f"{_Q_PR:.0f}")
        c3.metric("Условие q ≥ q_пр",
                  "выполнено" if res["cond_q"] else "НЕ выполнено")
        st.caption("Обоснование: 6 м³ кислоты / 6 ч допустимого контакта с НКТ = 24 м³/сут")

    # В.11
    with st.expander(f"{_icon(res['cond_h'])} В.11 — Суммарная толщина пластов"):
        c1, c2, c3 = st.columns(3)
        c1.metric("h_эф факт., м", f"{res['h_ef']:.1f}")
        c2.metric("h_пр, м",       f"{_H_PR:.0f}")
        c3.metric("Условие h_эф ≥ h_пр",
                  "выполнено" if res["cond_h"] else "НЕ выполнено")
        st.caption("Обоснование: h_пр = h̄ − 2σ = 13 − 2·4 = 5 м (термометрия по скважинам)")

    # В.12
    with st.expander(f"{_icon(res['cond_Cgl'])} В.12 — Глинистость коллекторов"):
        c1, c2, c3 = st.columns(3)
        c1.metric("C_гл факт., %",  f"{res['C_gl']:.1f}")
        c2.metric("C_г.пр, %",      f"{_CGL_PR:.0f}")
        c3.metric("Условие C_гл ≤ C_г.пр",
                  "выполнено" if res["cond_Cgl"] else "НЕ выполнено")
        if not res["cond_Cgl"]:
            st.warning("Высокая глинистость — порода может быть непроницаемой. Рассмотреть ГКО.")

    # В.13
    with st.expander(f"{_icon(res['cond_e'])} В.13 — Относительная гидропроводность"):
        c1, c2, c3 = st.columns(3)
        c1.metric("ε_обр, мкм²·м", f"{res['eps_obr']:.4f}")
        c2.metric("ε_скв, мкм²·м", f"{res['eps_skv']:.4f}")
        c3.metric("ε_от = ε_обр / ε_скв", f"{res['e_ot']:.3f}",
                  delta="> 0.5 ✓" if res["cond_e"] else "≤ 0.5 ✗",
                  delta_color="normal" if res["cond_e"] else "inverse")
        st.caption(
            "Физический смысл: доля продуктивности обрабатываемых пластов "
            "в суммарной продуктивности скважины. "
            "При ε_от ≤ 0,5 КО не даст заметного прироста дебита."
        )

    # В.14
    with st.expander(f"{_icon(res['cond_enr'])} В.14 — Энергетический потенциал пласта"):
        c1, c2, c3 = st.columns(3)
        c1.metric("p_пл, МПа",   f"{res['k_enr'] * res['p_gst']:.2f}")
        c2.metric("p_гст, МПа",  f"{res['p_gst']:.3f}")
        c3.metric("k_энр",       f"{res['k_enr']:.3f}",
                  delta="> 0.7 ✓" if res["cond_enr"] else "≤ 0.7 ✗",
                  delta_color="normal" if res["cond_enr"] else "inverse")
        st.caption(f"p_гст = ρ·g·H·10⁻⁶ = 1000 · 9,81 · {inp['H']:.0f} · 10⁻⁶ = {res['p_gst']:.3f} МПа")

    # ── Итоговый вывод ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Итоговое заключение")

    criteria = [
        ("В.8   ОД < 1",                    res["cond_OD"]),
        ("В.10  q ≥ 24 м³/сут",             res["cond_q"]),
        ("В.11  h_эф ≥ 5 м",                res["cond_h"]),
        ("В.12  C_гл ≤ 10 %",               res["cond_Cgl"]),
        ("В.13  ε_от > 0,5",                res["cond_e"]),
        ("В.14  k_энр > 0,7",               res["cond_enr"]),
    ]
    for label, ok in criteria:
        st.write(f"{'✅' if ok else '❌'} {label}")

    if res["decision"]:
        st.success("**КО целесообразна.** Все критерии выполнены.")
    else:
        failed = [label for label, ok in criteria if not ok]
        st.error(f"**КО не рекомендуется.** Не выполнены: {', '.join(failed)}.")

    st.session_state["task_v2_result"] = res
    return res
