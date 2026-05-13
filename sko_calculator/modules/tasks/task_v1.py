"""Задача В.1 — обоснование выбора скважины (полная информация)."""
import streamlit as st
import pandas as pd

from ._shared import render_precarpathian_constants as _render_precarpathian_constants


_THRESHOLD_K_S = 1.1   # k_s.пр = 1.1 (формулы В.4, В.5)
_THRESHOLD_K_MSG = _THRESHOLD_K_S ** 2  # = 1.21 (формула В.6)


_EXAMPLE_LAYERS = [
    {"interval": "2733-2750", "h_ef": 17,  "porosity": 12.0},
    {"interval": "2750-2762", "h_ef": 12,  "porosity": 9.8},
    {"interval": "2762-2780", "h_ef": 18,  "porosity": 13.0},
    {"interval": "2780-2802", "h_ef": 22,  "porosity": 10.5},
    {"interval": "2802-2823", "h_ef": 21,  "porosity": 9.6},
]

EXAMPLE = {
    "K_f":      16.0,
    "K_pot":    51.0,
    "h_ef":     78.3,
    "h_pta":    17.0,
    "C_k":      3.1,
    "k_ms_lab": 1.2,
    "k_mg_lab": 1.15,
    # m_gr — заполняется из cfg
    "layers":   _EXAMPLE_LAYERS,
}


def solve(inp: dict, const: dict) -> dict:
    sel = const["well_selection"]

    K_f    = float(inp["K_f"])
    K_pot  = float(inp["K_pot"])
    m_gr   = float(inp["m_gr"])
    h_pta  = float(inp["h_pta"])
    h_pr   = float(sel["h_pr_min"])
    k_ms   = float(inp["k_ms_lab"])
    k_mg   = float(inp["k_mg_lab"])
    C_k    = float(inp["C_k"])
    C_k_pr = float(sel["C_k_pr"])
    h_ef   = float(inp["h_ef"])
    layers = inp.get("layers_table") or []

    # В.1 — ОП = Kф / Kпот < 1
    OP = K_f / K_pot if K_pot else float("inf")
    cond_OP = OP < 1.0

    # В.2 — пористость каждого пласта > mгр
    layer_results = []
    all_layers_ok = len(layers) > 0
    for L in layers:
        m0_i = float(L.get("porosity", 0))
        ok = m0_i > m_gr
        if not ok:
            all_layers_ok = False
        layer_results.append({
            "Интервал":          L.get("interval", "—"),
            "h_эф, м":           float(L.get("h_ef", 0)),
            "m₀, %":             m0_i,
            "m_гр, %":           m_gr,
            "m₀ > m_гр":        "✓" if ok else "✗",
        })

    # В.3 — hпгл > hпр
    cond_h = h_pta >= h_pr

    # В.4 — kms = ms/m₀ ≥ 1.1
    cond_kms = k_ms >= _THRESHOLD_K_S

    # В.5 — kmg = mg/ms ≥ 1.1
    cond_kmg = k_mg >= _THRESHOLD_K_S

    # В.6 — kmsg = kms * kmg ≥ 1.21
    k_msg = k_ms * k_mg
    cond_kmsg = k_msg >= _THRESHOLD_K_MSG

    # В.7 — Ck ≥ Ckпр → тип обработки
    cond_Ck = C_k >= C_k_pr
    treatment_type = "СКО + ГКО" if cond_Ck else "только ГКО"

    # В.8 — kв.о = hпгл / hэф
    k_vo_calc = h_pta / h_ef if h_ef else 0.0
    if k_vo_calc < 0.1:
        coverage_decision = "Вторичная перфорация или поинтервальная КО"
    elif k_vo_calc >= 0.5:
        coverage_decision = "Обработка всего разреза"
    else:
        coverage_decision = "1-я КО — весь разрез; 2–4-я КО — поинтервальные"

    # Итоговое решение: все обязательные критерии выполнены
    decision = all([cond_OP, all_layers_ok, cond_h, cond_kms, cond_kmg])

    return {
        "K_f": K_f, "K_pot": K_pot,
        "OP": OP, "cond_OP": cond_OP,
        "layer_results": layer_results, "all_layers_ok": all_layers_ok,
        "h_pta": h_pta, "h_pr": h_pr, "cond_h": cond_h,
        "k_ms": k_ms, "k_mg": k_mg, "k_msg": k_msg,
        "cond_kms": cond_kms, "cond_kmg": cond_kmg, "cond_kmsg": cond_kmsg,
        "C_k": C_k, "C_k_pr": C_k_pr, "cond_Ck": cond_Ck,
        "treatment_type": treatment_type,
        "k_vo_calc": k_vo_calc, "coverage_decision": coverage_decision,
        "decision": decision,
    }


def _render_inputs(cfg: dict) -> dict:
    sel = cfg["well_selection"]

    # defaults — пустые при первом открытии; реальные значения по кнопке «ПРИМЕР»
    st.session_state.setdefault("v1_K_f",      0.0)
    st.session_state.setdefault("v1_K_pot",    0.0)
    st.session_state.setdefault("v1_h_ef",     0.0)
    st.session_state.setdefault("v1_h_pta",    0.0)
    st.session_state.setdefault("v1_C_k",      0.0)
    st.session_state.setdefault("v1_k_ms_lab", 1.0)
    st.session_state.setdefault("v1_k_mg_lab", 1.0)
    st.session_state.setdefault("v1_m_gr",     0.0)
    st.session_state.setdefault("v1_layers",   [
        {"interval": "", "h_ef": 0.0, "porosity": 0.0},
    ])

    with st.expander("Исходные данные — В.1", expanded=True):
        st.markdown("**Коэффициенты продуктивности (из КВД/КВУ)**")
        c1, c2 = st.columns(2)
        st.session_state["v1_K_f"] = c1.number_input(
            "K_ф, т/(сут·МПа) — фактический",
            value=float(st.session_state["v1_K_f"]),
            help="Вся зона дренажа, включая ПЗП",
        )
        st.session_state["v1_K_pot"] = c2.number_input(
            "K_пот, т/(сут·МПа) — потенциальный",
            value=float(st.session_state["v1_K_pot"]),
            help="Удалённая зона, поздний участок КВД (метод Хорнера)",
        )

        st.markdown("**Толщины пластов (из расходометрии / термометрии)**")
        c1, c2 = st.columns(2)
        st.session_state["v1_h_pta"] = c1.number_input(
            "h_пгл, м — толщина поглощающего пласта",
            value=float(st.session_state["v1_h_pta"]),
            help="Определяется расходометрией при нагнетании или термометрией",
        )
        st.session_state["v1_h_ef"] = c2.number_input(
            "h_эф, м — перфорированная толщина продуктивных пластов",
            value=float(st.session_state["v1_h_ef"]),
        )

        st.markdown("**Состав породы (из кернового анализа)**")
        c1, c2, c3 = st.columns(3)
        st.session_state["v1_C_k"] = c1.number_input(
            "C_к, % — карбонатность",
            value=float(st.session_state["v1_C_k"]),
            help="Рентгено-фазовый или кислотный анализ керна",
        )
        st.session_state["v1_k_ms_lab"] = c2.number_input(
            "k_ms = m_s / m₀ — прирост пористости после СКО",
            value=float(st.session_state["v1_k_ms_lab"]),
            min_value=1.0, step=0.01, format="%.2f",
            help="Лабораторный эксперимент с СКР до полного удаления карбонатов",
        )
        st.session_state["v1_k_mg_lab"] = c3.number_input(
            "k_mg = m_g / m_s — прирост пористости после ГКО",
            value=float(st.session_state["v1_k_mg_lab"]),
            min_value=1.0, step=0.01, format="%.2f",
            help="Лабораторный эксперимент с ГКР (тот же объём, что СКР)",
        )

        st.markdown("**Граничная пористость**")
        st.session_state["v1_m_gr"] = st.number_input(
            f"m_гр, % — нижний предел пористости коллектора "
            f"(для Предкарпатья {sel['m_pr_min']}–{sel['m_pr_max']}%)",
            value=float(st.session_state["v1_m_gr"]),
            min_value=0.0, max_value=30.0, step=0.5,
        )

        st.markdown("**Таблица продуктивных пластов** (ГИС + керн)")
        import pandas as pd
        df = pd.DataFrame(st.session_state["v1_layers"])
        edited = st.data_editor(
            df, num_rows="dynamic", use_container_width=True, key="v1_layers_editor"
        )
        st.session_state["v1_layers"] = edited.to_dict("records")

    return {
        "K_f":          st.session_state["v1_K_f"],
        "K_pot":        st.session_state["v1_K_pot"],
        "h_ef":         st.session_state["v1_h_ef"],
        "h_pta":        st.session_state["v1_h_pta"],
        "C_k":          st.session_state["v1_C_k"],
        "k_ms_lab":     st.session_state["v1_k_ms_lab"],
        "k_mg_lab":     st.session_state["v1_k_mg_lab"],
        "m_gr":         st.session_state["v1_m_gr"],
        "layers_table": st.session_state["v1_layers"],
    }


def _icon(ok: bool) -> str:
    return "[+]" if ok else "[-]"




def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.1 — Обоснование выбора скважины (полная информация)")
    if btn_col.button("ПРИМЕР", key="btn_example_v1", type="secondary", use_container_width=True):
        sel = cfg["well_selection"]
        for k, v in EXAMPLE.items():
            st.session_state[f"v1_{k}"] = v
        st.session_state["v1_m_gr"] = float(sel["m_pr_default"])
        st.rerun()

    _render_precarpathian_constants(cfg, task="В.1")

    with st.expander("Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `K_ф` | фактический коэффициент продуктивности скважины | т/(сут·МПа) |
| `K_пот` | потенциальный коэффициент продуктивности (удалённая зона) | т/(сут·МПа) |
| `m_0` | начальная пористость пласта (керн/ГИС) | % |
| `m_гр` | граничная пористость коллектора (норматив) | % |
| `h_эф` | перфорированная толщина продуктивных пластов | м |
| `h_пгл` | толщина поглощающего пласта (расходометрия/термометрия) | м |
| `h_пр` | минимально допустимая толщина пласта | м |
| `m_s` | пористость после СКО | % |
| `m_g` | пористость после ГКО | % |
| `C_к` | карбонатность породы | % |
| `C_к.пр` | минимальная карбонатность для СКО | % |
""")

    with st.expander("Производные величины (формулы определения)", expanded=False):
        st.latex(r"ОП = \frac{K_\phi}{K_{пот}} \quad \text{— отношение продуктивности}")
        st.latex(r"k_{ms} = \frac{m_s}{m_0} \quad \text{— прирост пористости после СКО (лаб.)}")
        st.latex(r"k_{mg} = \frac{m_g}{m_s} \quad \text{— прирост пористости после ГКО (лаб.)}")
        st.latex(r"k_{msg} = k_{ms} \cdot k_{mg} \quad \text{— суммарный прирост пористости}")
        st.latex(r"k_{в.о} = \frac{h_{пгл}}{h_{эф}} \quad \text{— коэффициент охвата разреза по вертикали}")

    with st.expander("Формулы методики", expanded=False):
        st.latex(r"\text{В.1} \quad ОП = \frac{K_\phi}{K_{пот}} < 1")
        st.latex(r"\text{В.2} \quad m_0 > m_{гр}")
        st.latex(r"\text{В.3} \quad h_{пгл} > h_{пр}")
        st.latex(r"\text{В.4} \quad k_{ms} = \frac{m_s}{m_0} \geq 1{,}1")
        st.latex(r"\text{В.5} \quad k_{mg} = \frac{m_g}{m_s} \geq 1{,}1")
        st.latex(r"\text{В.6} \quad k_{msg} = k_{ms} \cdot k_{mg} \geq 1{,}21")
        st.latex(r"\text{В.7} \quad C_k \geq C_{k,пр} = 3\%")
        st.latex(r"\text{В.8} \quad k_{в.о} = \frac{h_{пгл}}{h_{эф}}")

    inp = _render_inputs(cfg)
    res = solve(inp, cfg)

    # ── Метрики верхнего уровня ──────────────────────────────────────────────
    st.markdown("### Результаты")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("K_ф, т/(сут·МПа)",   f"{res['K_f']:.2f}")
    c2.metric("K_пот, т/(сут·МПа)", f"{res['K_pot']:.2f}")
    c3.metric("ОП = Kф / Kпот",     f"{res['OP']:.3f}",
              delta="< 1 ✓" if res["cond_OP"] else "≥ 1 ✗",
              delta_color="normal" if res["cond_OP"] else "inverse")
    c4.metric("k_в.о = hпгл / hэф", f"{res['k_vo_calc']:.3f}")

    # ── Критерии по шагам ───────────────────────────────────────────────────
    st.markdown("### Пошаговая проверка критериев")

    # В.1
    with st.expander(f"{_icon(res['cond_OP'])} В.1 — Отношение продуктивности ОП"):
        col1, col2 = st.columns(2)
        col1.markdown(f"**ОП = {res['OP']:.4f}**")
        col2.markdown(f"Условие ОП < 1: **{'выполнено' if res['cond_OP'] else 'НЕ выполнено'}**")

    # В.2
    with st.expander(f"{_icon(res['all_layers_ok'])} В.2 — Пористость пластов m₀ > m_гр"):
        df = pd.DataFrame(res["layer_results"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not res["all_layers_ok"]:
            st.warning("Один или несколько пластов не являются коллекторами — исключить из обработки.")

    # В.3
    with st.expander(f"{_icon(res['cond_h'])} В.3 — Толщина поглощающего пласта"):
        col1, col2, col3 = st.columns(3)
        col1.metric("h_пгл (расходометрия/термометрия), м", f"{res['h_pta']:.1f}")
        col2.metric("h_пр (предельная), м",                  f"{res['h_pr']:.1f}")
        col3.metric("Условие h_пгл ≥ h_пр",
                    "выполнено" if res["cond_h"] else "НЕ выполнено")

    # В.4–В.6
    with st.expander(f"{_icon(res['cond_kms'] and res['cond_kmg'])} В.4–В.6 — Прирост пористости (керновый анализ)"):
        col1, col2, col3 = st.columns(3)
        col1.metric("k_ms = m_s / m₀",    f"{res['k_ms']:.3f}",
                    delta="≥ 1.1 ✓" if res["cond_kms"] else "< 1.1 ✗",
                    delta_color="normal" if res["cond_kms"] else "inverse")
        col2.metric("k_mg = m_g / m_s",   f"{res['k_mg']:.3f}",
                    delta="≥ 1.1 ✓" if res["cond_kmg"] else "< 1.1 ✗",
                    delta_color="normal" if res["cond_kmg"] else "inverse")
        col3.metric("k_msg = k_ms × k_mg", f"{res['k_msg']:.3f}",
                    delta="≥ 1.21 ✓" if res["cond_kmsg"] else "< 1.21 ✗",
                    delta_color="normal" if res["cond_kmsg"] else "inverse")
        st.caption(f"Нормативы: k_ms.пр = k_mg.пр = {_THRESHOLD_K_S:.1f},  "
                   f"k_msg.пр = {_THRESHOLD_K_MSG:.2f}")

    # В.7
    with st.expander(f"{_icon(res['cond_Ck'])} В.7 — Карбонатность и выбор вида КО"):
        col1, col2, col3 = st.columns(3)
        col1.metric("C_к факт., %",   f"{res['C_k']:.2f}")
        col2.metric("C_к.пр, %",      f"{res['C_k_pr']:.1f}")
        col3.metric("Вид обработки",  res["treatment_type"])
        if res["cond_Ck"]:
            st.success("C_к ≥ C_к.пр → сначала СКО, затем ГКО")
        else:
            st.info("C_к < C_к.пр → только ГКО (карбонатность недостаточна для СКО)")

    # В.8
    with st.expander("В.8 — Коэффициент охвата разреза поглощением"):
        col1, col2 = st.columns(2)
        col1.metric("k_в.о = h_пгл / h_эф", f"{res['k_vo_calc']:.3f}")
        col2.info(res["coverage_decision"])
        st.markdown("""
| k_в.о | Технология |
|---|---|
| < 0,1 | Вторичная перфорация **или** поинтервальная КО |
| 0,1 – 0,5 | 1-я КО — весь разрез; 2–4-я — поинтервальные |
| ≥ 0,5 | Обработка всего разреза |
""")

    # ── Итоговый вывод ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Итоговое заключение")

    criteria = [
        ("В.1  ОП < 1",               res["cond_OP"]),
        ("В.2  m₀ > m_гр (все пласты)", res["all_layers_ok"]),
        ("В.3  h_пгл ≥ h_пр",          res["cond_h"]),
        ("В.4  k_ms ≥ 1,1",            res["cond_kms"]),
        ("В.5  k_mg ≥ 1,1",            res["cond_kmg"]),
    ]
    for label, ok in criteria:
        st.write(f"{_icon(ok)} {label}")

    if res["decision"]:
        st.success(
            f"**КО целесообразна.** Вид обработки: {res['treatment_type']}. "
            f"Технология по разрезу: {res['coverage_decision']}."
        )
    else:
        failed = [label for label, ok in criteria if not ok]
        st.error(f"**КО не рекомендуется.** Не выполнены критерии: {', '.join(failed)}.")

    # Передаём результат следующим задачам
    st.session_state["task_v1_result"] = res
    return res
