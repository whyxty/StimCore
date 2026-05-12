"""Задача В.11 — выбор состава кислотного раствора, продавочной и вытесняющей жидкостей.

Принятые решения:
1. Табл. В.16: жёсткое дерево по k_0 (порог 0,1) → затем по (N_ас, N_см).
2. Ингибитор — один рекомендованный по T_пл из табл. В.17.
3. Стабилизатор: если Fe³⁺ = 0 → не добавляем; иначе подбираем по табл. В.18.
4. ПАВ из табл. В.19: буквальное следование таблице, при множественных
   совпадениях выводим список возможных вариантов.
5. Продавочная и вытесняющая жидкости — тот же ПАВ, что в КР; если в КР
   ПАВ не выбран — стандартный ОП-10 0,3 %.
6. HCl и HF — ползунки (10–15 % / 1–3 %).
7. C_к, k_0 — тянутся из В.6/В.8; остальные 7 параметров — ввод здесь.
8. Рецептура сохраняется в session_state["task_v11_result"].
"""
import streamlit as st

from ._shared import render_precarpathian_constants


EXAMPLE = {
    "C_k":   3.1,
    "k0":    0.05,
    "N_ko":  0,
    "T_pl":  70.0,
    "Fe3":   0.0,
    "W_vn":  2,
    "N_as":  1.0,
    "N_sm":  4.0,
    "N_nf":  0.2,
    "HCl":   12.0,
    "HF":    3.0,
    "ratio": "1:1",
}


# ───────── Таблица В.15 — выбор y (% HF) ─────────
def select_y_HF(C_k: float, N_ko: int) -> int:
    n = min(N_ko, 5)
    if C_k <= 3:
        return [1, 2, 2, 3, 3, 3][n]
    if C_k <= 5:
        return [0, 0, 1, 2, 3, 3][n]
    return [0, 0, 0, 1, 2, 3][n]


# ───────── Таблица В.16 — тип КР ─────────
def select_solution_type(N_as: float, N_sm: float, k0: float) -> dict:
    """Возвращает dict со списком требуемых добавок."""
    high_oil = (N_as >= 2) or (N_sm >= 6)
    low_perm = k0 < 0.1
    if not high_oil and not low_perm:
        # N_ас<2 и N_см<6; k_0≥0,1
        name = "Ингибированный КР"
        need = {"inhibitor": True, "stabilizer": False, "surfactant": False}
    elif not high_oil and low_perm:
        # N_ас<2 или N_см<6; k_0<0,1
        name = "Ингибированный и стабилизированный КР"
        need = {"inhibitor": True, "stabilizer": True, "surfactant": False}
    elif high_oil and low_perm:
        # N_ас≥2 или N_см≥6; k_0<0,1
        name = "Ингибированный и стабилизированный КР улучшенной фильтруемости (с ПАВ)"
        need = {"inhibitor": True, "stabilizer": True, "surfactant": True}
    else:
        # N_ас≥2 или N_см≥6; k_0≥0,1
        name = "Ингибированный КР улучшенной фильтруемости (с ПАВ)"
        need = {"inhibitor": True, "stabilizer": False, "surfactant": True}
    return {"name": name, **need}


# ───────── Таблица В.17 — ингибитор по T_пл ─────────
_INHIBITOR_TABLE = [
    # (T_min, T_max, name, conc_text)
    (0,    60,  "Катапин КИ-1",                "0,2 %"),
    (60,   90,  "Катапин КИ-1",                "0,3 %"),
    (90,  110,  "Катапин КИ-1",                "0,4 %"),
    (110, 130,  "Катапин КИ-1",                "0,5 %"),
]

def select_inhibitor(T_pl: float) -> dict:
    for tmin, tmax, name, conc in _INHIBITOR_TABLE:
        if tmin <= T_pl < tmax:
            return {"name": name, "conc": conc, "T_range": f"{tmin}–{tmax} °C"}
    if T_pl >= 130:
        return {"name": "Катапин + уротропин (1:1)", "conc": "0,5+0,5 %",
                "T_range": "≥ 130 °C — на пределе применимости"}
    return {"name": "Катапин КИ-1", "conc": "0,2 %", "T_range": "по умолч."}


# ───────── Таблица В.18 — стабилизатор по (T_пл, Fe³⁺) ─────────
_STABILIZER_TABLE = [
    # (T_max, Fe_max, name, conc)
    (60,  0.1, "Уксусная кислота",             "1,0 %"),
    (60,  0.2, "Уксусная кислота",             "1,5 %"),
    (60,  0.5, "Уксусная кислота",             "3,0 %"),
    (90,  0.3, "Лимонная кислота",             "0,5 %"),
    (90,  0.5, "Лимонная кислота",             "1,0 %"),
    (110, 0.3, "Сульфат натрия",               "0,08 %"),
    (120, 0.2, "Уксусная + лимонная кислота",  "2,0+0,4 %"),
    (140, 0.3, "КРАСТ",                        "0,07 %"),
]

def select_stabilizer(T_pl: float, Fe3: float) -> dict | None:
    if Fe3 <= 0:
        return None
    for T_max, Fe_max, name, conc in _STABILIZER_TABLE:
        if T_pl < T_max and Fe3 < Fe_max:
            return {"name": name, "conc": conc,
                    "rule": f"T_пл < {T_max} °C, Fe³⁺ < {Fe_max} %"}
    return {"name": "—", "conc": "—",
            "rule": "Условия выходят за табличные диапазоны"}


# ───────── Таблица В.19 — ПАВ (буквально) ─────────
# Каждая строка: условия (W_вн, N_ас, N_нф, T_пл) и список ПАВ.
_SURFACTANT_TABLE = [
    {
        "rule":  "W_вн = 1 и N_ас ≤ 1 и T_пл > 80 °C",
        "match": lambda W, Na, Nn, T: W == 1 and Na <= 1 and T > 80,
        "PAV":   ["—  не применяются"],
    },
    {
        "rule":  "W_вн > 2; N_нф > 0,3 или N_ас > 1; T_пл > 80 °C",
        "match": lambda W, Na, Nn, T: W > 2 and (Nn > 0.3 or Na > 1) and T > 80,
        "PAV":   ["ОП-10", "превоцел W-OF-7", "ОП-7", "ОЖК", "Сапал",
                  "диссольван", "проксанол", "проксамин", "КАУФЭ-14"],
    },
    {
        "rule":  "W_вн > 2; N_ас > 1 %; T_пл ≤ 80 °C",
        "match": lambda W, Na, Nn, T: W > 2 and Na > 1 and T <= 80,
        "PAV":   ["ОП-10", "превоцел W-OF-7", "неонол", "ОП-7", "ОЖК",
                  "Сапал", "диссольван", "проксамин", "КАУФЭ-14"],
    },
    {
        "rule":  "W_вн = 2; T_пл > 80 °C",
        "match": lambda W, Na, Nn, T: W == 2 and T > 80,
        "PAV":   ["ОП-10", "превоцел W-OF-7", "ОП-7"],
    },
    {
        "rule":  "W_вн = 2; T_пл ≤ 80 °C",
        "match": lambda W, Na, Nn, T: W == 2 and T <= 80,
        "PAV":   ["ОП-10", "неонол", "превоцел W-OF-7"],
    },
]

def select_surfactant(W_vn: int, N_as: float, N_nf: float, T_pl: float) -> dict:
    matches = []
    for row in _SURFACTANT_TABLE:
        if row["match"](W_vn, N_as, N_nf, T_pl):
            matches.append(row)
    if not matches:
        return {"PAV_list": ["ОП-10 (по умолчанию)"], "rules": ["условия вне табл. В.19"]}
    pav_set = []
    for row in matches:
        for p in row["PAV"]:
            if p not in pav_set:
                pav_set.append(p)
    return {"PAV_list": pav_set, "rules": [m["rule"] for m in matches]}


# ───────── основной решатель ─────────
def solve(*, C_k: float, k0: float, N_ko: int, T_pl: float,
          Fe3: float, W_vn: int, N_as: float, N_sm: float, N_nf: float,
          C_HCl_pct: float, C_HF_pct: float, ratio_SKR_GKR: str) -> dict:

    y = select_y_HF(C_k, N_ko)                          # табл. В.15
    sol_type = select_solution_type(N_as, N_sm, k0)     # табл. В.16

    inhibitor  = select_inhibitor(T_pl)                  # табл. В.17
    stabilizer = (select_stabilizer(T_pl, Fe3)
                  if sol_type["stabilizer"] else None)   # табл. В.18

    if sol_type["surfactant"]:
        surf = select_surfactant(W_vn, N_as, N_nf, T_pl) # табл. В.19
    else:
        surf = None

    # тип обработки
    if y == 0:
        treatment = f"СКО — солянокислотный раствор {C_HCl_pct:.0f} % HCl"
        gkr = None
    else:
        gkr_HF = max(C_HF_pct, float(y))
        treatment = (f"ГКО — последовательно: СКР ({C_HCl_pct:.0f} % HCl) → "
                     f"ГКР ({C_HCl_pct:.0f} % HCl + {gkr_HF:.0f} % HF), "
                     f"соотношение СКР:ГКР = {ratio_SKR_GKR}")
        gkr = {"HCl": C_HCl_pct, "HF": gkr_HF, "ratio": ratio_SKR_GKR}

    # Продавочная и вытесняющая (тот же ПАВ что в КР, иначе ОП-10)
    if surf and surf["PAV_list"]:
        pav_for_buffers = surf["PAV_list"][0]
        # фильтр случая «не применяются»
        if pav_for_buffers.startswith("—"):
            pav_for_buffers = "ОП-10"
    else:
        pav_for_buffers = "ОП-10"
    buffer_fluid = f"вода + {pav_for_buffers} 0,3 %"

    return {
        "y_HF":      y,
        "type":      sol_type["name"],
        "needs":     {k: v for k, v in sol_type.items() if k != "name"},
        "treatment": treatment,
        "skr":       {"HCl_pct": C_HCl_pct},
        "gkr":       gkr,
        "inhibitor": inhibitor,
        "stabilizer": stabilizer,
        "surfactant": surf,
        "buffer_fluid": buffer_fluid,
    }


# ───────── UI ─────────
def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.11 — Выбор состава кислотного раствора и буферных жидкостей")
    if btn_col.button("ПРИМЕР", key="btn_example_v11", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v11_{k}"] = v
        st.rerun()


    render_precarpathian_constants(cfg)
    with st.expander("📖 Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `C_к` | карбонатность породы (из В.6/общий ввод) | % |
| `k_0` | начальная проницаемость (из В.8) | мкм² |
| `N_ко` | число ранее проведённых КО | – |
| `T_пл` | пластовая температура | °C |
| `Fe³⁺` | ожидаемое содержание железа после нагнетания СКР | % |
| `W_вн` | тип пластовой воды (1 — гидрокарб., 2 — хлоркальц., >2 — др.) | – |
| `N_ас` | содержание асфальтенов в нефти | % |
| `N_см` | содержание смол в нефти | % |
| `N_нф` | содержание нафтеновых кислот | % |
| `y` | концентрация HF в ГКР (по табл. В.15) | % |
| СКР | солянокислотный раствор | – |
| ГКР | глинокислотный раствор (HCl + HF) | – |
| ПАВ | поверхностно-активное вещество | – |
""")

    # --- источник входных данных ---
    v6_C_k = float(st.session_state.get("v6_C_k", 0.0))
    v8 = st.session_state.get("task_v8_result")
    k0_default = float(v8["k0"]) if v8 else 0.05

    if v6_C_k:
        st.info(f"Из **В.6**: C_к = **{v6_C_k:.2f} %**.  "
                + (f"Из **В.8**: k_0 = **{k0_default:.6f} мкм²**." if v8 else ""))
    else:
        st.warning("Откройте В.6 и В.8 для автоматической подстановки C_к и k_0.")

    _DEF = {
        "C_k":   0.0,
        "k0":    0.0,
        "N_ko":  0,
        "T_pl":  0.0,
        "Fe3":   0.0,
        "W_vn":  1,
        "N_as":  0.0,
        "N_sm":  0.0,
        "N_nf":  0.0,
        "HCl":   10.0,
        "HF":    1.0,
        "ratio": "1:1",
    }
    for k, v in _DEF.items():
        st.session_state.setdefault(f"v11_{k}", v)

    with st.expander("📥 Исходные данные — В.11", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v11_C_k"] = c1.number_input(
            "C_к, % — карбонатность",
            value=float(st.session_state["v11_C_k"]), step=0.1)
        st.session_state["v11_k0"]  = c2.number_input(
            "k_0, мкм² — проницаемость",
            value=float(st.session_state["v11_k0"]), step=0.001, format="%.6f")
        st.session_state["v11_N_ko"] = c3.number_input(
            "N_ко — число проведённых КО",
            value=int(st.session_state["v11_N_ko"]), step=1, min_value=0)

        c1, c2, c3 = st.columns(3)
        st.session_state["v11_T_pl"] = c1.number_input(
            "T_пл, °C — пластовая температура",
            value=float(st.session_state["v11_T_pl"]), step=5.0)
        st.session_state["v11_Fe3"]  = c2.number_input(
            "Fe³⁺, % — ожид. содержание железа",
            value=float(st.session_state["v11_Fe3"]), step=0.05, format="%.2f")
        st.session_state["v11_W_vn"] = c3.selectbox(
            "W_вн — тип пластовой воды",
            options=[1, 2, 3],
            index=[1, 2, 3].index(int(st.session_state["v11_W_vn"])),
            format_func=lambda x: {1: "1 — гидрокарбонатнатриевые",
                                   2: "2 — хлоркальциевые",
                                   3: ">2 — другие"}[x])

        c1, c2, c3 = st.columns(3)
        st.session_state["v11_N_as"] = c1.number_input(
            "N_ас, % — асфальтены",
            value=float(st.session_state["v11_N_as"]), step=0.1)
        st.session_state["v11_N_sm"] = c2.number_input(
            "N_см, % — смолы",
            value=float(st.session_state["v11_N_sm"]), step=0.1)
        st.session_state["v11_N_nf"] = c3.number_input(
            "N_нф, % — нафтеновые кислоты",
            value=float(st.session_state["v11_N_nf"]), step=0.05, format="%.2f")

        c1, c2, c3 = st.columns(3)
        st.session_state["v11_HCl"] = c1.slider(
            "Концентрация HCl, %", 10.0, 15.0,
            float(st.session_state["v11_HCl"]), step=0.5)
        st.session_state["v11_HF"]  = c2.slider(
            "Концентрация HF, % (если ГКО)", 1.0, 3.0,
            float(st.session_state["v11_HF"]), step=0.5)
        st.session_state["v11_ratio"] = c3.selectbox(
            "Соотношение СКР:ГКР (если y > 0)",
            ["3:1", "2:1", "1:1", "1:2", "1:3"],
            index=["3:1", "2:1", "1:1", "1:2", "1:3"].index(
                st.session_state["v11_ratio"]))

    # --- расчёт ---
    res = solve(
        C_k=st.session_state["v11_C_k"],
        k0=st.session_state["v11_k0"],
        N_ko=int(st.session_state["v11_N_ko"]),
        T_pl=st.session_state["v11_T_pl"],
        Fe3=st.session_state["v11_Fe3"],
        W_vn=int(st.session_state["v11_W_vn"]),
        N_as=st.session_state["v11_N_as"],
        N_sm=st.session_state["v11_N_sm"],
        N_nf=st.session_state["v11_N_nf"],
        C_HCl_pct=st.session_state["v11_HCl"],
        C_HF_pct=st.session_state["v11_HF"],
        ratio_SKR_GKR=st.session_state["v11_ratio"],
    )

    # --- пошаговое отображение ---
    st.markdown("### Пошаговое решение")

    with st.expander(f"Шаг 1. Табл. В.15 → y = {res['y_HF']} % HF", expanded=True):
        st.markdown(
            f"При **C_к = {st.session_state['v11_C_k']:.2f} %** и "
            f"**N_ко = {st.session_state['v11_N_ko']}** → **y = {res['y_HF']} %**."
        )
        if res['y_HF'] == 0:
            st.success("y = 0 → выполняется только **СКО**.")
        else:
            st.info(f"y > 0 → выполняется **ГКО** (СКР затем ГКР с {res['y_HF']} % HF).")

    with st.expander(f"Шаг 2. Табл. В.16 → {res['type']}", expanded=True):
        st.markdown(
            f"- N_ас = {st.session_state['v11_N_as']:.1f} %, "
            f"N_см = {st.session_state['v11_N_sm']:.1f} %, "
            f"k_0 = {st.session_state['v11_k0']:.4f} мкм²\n"
            f"- Требуются добавки: "
            f"{'ингибитор ✓ ' if res['needs']['inhibitor'] else ''}"
            f"{'стабилизатор ✓ ' if res['needs']['stabilizer'] else ''}"
            f"{'ПАВ ✓' if res['needs']['surfactant'] else ''}"
        )

    with st.expander(f"Шаг 3. Табл. В.17 → ингибитор: "
                     f"{res['inhibitor']['name']} {res['inhibitor']['conc']}",
                     expanded=True):
        st.markdown(f"Диапазон применения: **{res['inhibitor']['T_range']}**.")

    if res["stabilizer"] is not None:
        with st.expander(f"Шаг 4. Табл. В.18 → стабилизатор: "
                         f"{res['stabilizer']['name']} {res['stabilizer']['conc']}",
                         expanded=True):
            st.markdown(f"Условие срабатывания: **{res['stabilizer']['rule']}**.")
    else:
        with st.expander("Шаг 4. Табл. В.18 → стабилизатор НЕ требуется",
                         expanded=False):
            if st.session_state["v11_Fe3"] <= 0:
                st.markdown("Fe³⁺ = 0 — стабилизатор не нужен.")
            else:
                st.markdown("По типу КР (табл. В.16) стабилизатор не требуется.")

    if res["surfactant"] is not None:
        with st.expander(f"Шаг 5. Табл. В.19 → ПАВ", expanded=True):
            st.markdown("**Рекомендуемые ПАВ (0,3–0,5 %):** "
                        + ", ".join(res["surfactant"]["PAV_list"]))
            st.markdown("**Условия:** " + "; ".join(res["surfactant"]["rules"]))
    else:
        with st.expander("Шаг 5. Табл. В.19 → ПАВ НЕ требуется", expanded=False):
            st.markdown("По типу КР (табл. В.16) ПАВ в кислотный раствор не добавляется.")

    # --- финальный рецепт ---
    st.markdown("### 🧪 Итоговая рецептура")
    lines = [
        f"**Тип обработки:** {res['treatment']}",
        f"**Тип кислотного раствора:** {res['type']}",
        f"**Ингибитор:** {res['inhibitor']['name']} — {res['inhibitor']['conc']}",
    ]
    if res["stabilizer"] is not None:
        lines.append(f"**Стабилизатор:** {res['stabilizer']['name']} — {res['stabilizer']['conc']}")
    if res["surfactant"] is not None:
        lines.append(f"**ПАВ в КР:** {res['surfactant']['PAV_list'][0]} — 0,3–0,5 % "
                     f"(альтернативы: {', '.join(res['surfactant']['PAV_list'][1:]) or '—'})")
    lines.append(f"**Продавочная жидкость:** {res['buffer_fluid']}")
    lines.append(f"**Вытесняющая жидкость:** {res['buffer_fluid']}")
    st.markdown("\n\n".join(f"- {l}" for l in lines))

    # текстовый вариант для копирования
    txt = "\n".join(l.replace("**", "") for l in lines)
    with st.expander("📋 Текст для копирования"):
        st.code(txt, language="text")

    st.session_state["task_v11_result"] = res
    return res
