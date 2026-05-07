"""Задача В.10 — объёмы продавочной и вытесняющей жидкости.

Принятые решения:
1. Опечатка в (В.58) исправлена: во втором слагаемом — d_нар² (наружный
   диаметр НКТ), а не d_вн²; иначе кольцевое пространство было бы посчитано
   неверно.
2. V_з.р = V_ks(r = r_з.р) — берётся интерполяцией профиля из В.5.
3. Оба варианта V_втс выводятся параллельно: «без запаса» (В.56) и
   «с запасом» (В.57).
4. Диаметры НКТ и эксплуатационной колонны — выбор из списка типоразмеров.
5. H_н.о, H_в.о — ввод вручную (заново).
6. Результат сохраняется в session_state для возможной передачи в В.11.

Источники входных данных:
    - В.5 → V_ks (заданный), r_з.р, профиль V_ks(r), q_к
"""
import math
import numpy as np
import pandas as pd
import streamlit as st


# Стандартные типоразмеры НКТ (ГОСТ 633-80): внешний / внутренний, м
TUBING_OPTIONS = {
    "НКТ 60 мм":   {"d_out": 0.0603, "d_in": 0.0503},
    "НКТ 73 мм":   {"d_out": 0.0730, "d_in": 0.0620},
    "НКТ 89 мм":   {"d_out": 0.0889, "d_in": 0.0760},
    "НКТ 102 мм":  {"d_out": 0.1016, "d_in": 0.0886},
    "НКТ 114 мм":  {"d_out": 0.1143, "d_in": 0.1003},
}

# Стандартные эксплуатационные колонны: внутренний диаметр, м
CASING_OPTIONS = {
    "Колонна 140 мм": {"D_in": 0.1280},
    "Колонна 146 мм": {"D_in": 0.1320},
    "Колонна 168 мм": {"D_in": 0.1500},
    "Колонна 178 мм": {"D_in": 0.1610},
    "Колонна 219 мм": {"D_in": 0.1990},
}


def V_vts_no_reserve(V_zr: float) -> float:
    """(В.56) — без запаса: V_втс = 1.2·V_з.р."""
    return 1.2 * V_zr


def V_vts_with_reserve(V_ks: float) -> float:
    """(В.57) — с запасом: V_втс = 0.3·V_ks."""
    return 0.3 * V_ks


def V_prd(d_in: float, d_out: float, D_in: float,
          H_no: float, H_vo: float) -> float:
    """(В.58, испр.): V_прд = 0.785·[d_вн²·H_но + (D_к² − d_нар²)·(H_но − H_во)]."""
    inside_NKT  = d_in ** 2 * H_no
    annular     = (D_in ** 2 - d_out ** 2) * (H_no - H_vo)
    return 0.785 * (inside_NKT + annular)


def V_ks_at_r(df: pd.DataFrame, r: float) -> float:
    """V_ks(r) — интерполяция по профилю из В.5."""
    return float(np.interp(r, df["r, м"], df["V_ks, м³"]))


def solve(*, V_ks: float, V_zr: float,
          d_in: float, d_out: float, D_in: float,
          H_no: float, H_vo: float, q_k: float | None) -> dict:

    V_vts_56 = V_vts_no_reserve(V_zr)
    V_vts_57 = V_vts_with_reserve(V_ks)
    V_pr     = V_prd(d_in, d_out, D_in, H_no, H_vo)

    # Общий объём закачки для каждого варианта V_втс
    V_total_56 = V_ks + V_vts_56 + V_pr
    V_total_57 = V_ks + V_vts_57 + V_pr

    # Длительность закачки (мин)
    t_56 = 1440.0 * V_total_56 / q_k if q_k else None
    t_57 = 1440.0 * V_total_57 / q_k if q_k else None

    return {
        "V_ks":      V_ks,
        "V_zr":      V_zr,
        "V_vts_56":  V_vts_56,
        "V_vts_57":  V_vts_57,
        "V_prd":     V_pr,
        "V_inside_NKT": 0.785 * d_in ** 2 * H_no,
        "V_annular":    0.785 * (D_in ** 2 - d_out ** 2) * (H_no - H_vo),
        "V_total_56": V_total_56,
        "V_total_57": V_total_57,
        "t_56":      t_56,
        "t_57":      t_57,
    }


def render(cfg: dict):
    st.subheader("Задача В.10 — Объёмы продавочной и вытесняющей жидкости")

    with st.expander("📖 Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `V_ks` | заданный объём закачиваемого СКР (из В.5) | м³ |
| `V_з.р` | объём СКР, отвечающий радиусу зоны растворения (из В.5) | м³ |
| `r_з.р` | радиус зоны растворения (из В.5) | м |
| `V_втс` | объём вытесняющей жидкости | м³ |
| `V_прд` | объём продавочной жидкости | м³ |
| `d_вн` | внутренний диаметр НКТ | м |
| `d_нар` | наружный диаметр НКТ | м |
| `D_к` | внутренний диаметр эксплуатационной колонны | м |
| `H_н.о` | глубина нижнего отверстия перфорации (или нижней границы интервала) | м |
| `H_в.о` | глубина верхнего отверстия перфорации (или верхней границы интервала) | м |
| `q_к` | расход СКР при закачке (из В.5) | м³/сут |
| `V_общ` | суммарный объём закачки = V_ks + V_втс + V_прд | м³ |
""")

    st.latex(r"V_{\text{втс}}=1{,}2\,V_{\text{з.р}}\quad(B.56)\;\;\text{(без запаса)}")
    st.latex(r"V_{\text{втс}}=0{,}3\,V_{ks}\quad(B.57)\;\;\text{(с запасом)}")
    st.latex(r"V_{\text{прд}}=0{,}785\,\bigl[d_{\text{вн}}^{2}H_{\text{н.о}}"
             r"+(D_{\text{к}}^{2}-d_{\text{нар}}^{2})(H_{\text{н.о}}-H_{\text{в.о}})\bigr]\quad(B.58)")
    st.caption("В первоисточнике (В.58) во втором слагаемом стоит `d_вн²`, "
               "что физически некорректно — кольцевое пространство ограничено "
               "**наружным** диаметром НКТ. В коде используется `d_нар²`.")

    # ---- зависимости ----
    v5 = st.session_state.get("task_v5_result")
    if not v5:
        st.warning("Сначала рассчитайте задачу **В.5** — оттуда берутся V_ks, r_з.р, q_к.")
        return None

    V_ks_zad = float(v5["V_zad"])
    r_zr     = float(v5["r_zr"])
    df_v5    = v5["df"]
    V_zr     = V_ks_at_r(df_v5, r_zr)

    q_k = float(st.session_state.get("v5_q_acid", 0.0)) or None

    st.info(f"Из **В.5**: V_ks (заданный) = **{V_ks_zad:.3f} м³**, "
            f"r_з.р = **{r_zr:.3f} м**, "
            f"V_з.р = V_ks(r_з.р) = **{V_zr:.4f} м³**"
            + (f", q_к = **{q_k:.0f} м³/сут**." if q_k else "."))

    # ---- ввод параметров В.10 ----
    _DEF = {
        "tubing":  "НКТ 73 мм",
        "casing":  "Колонна 168 мм",
        "H_no":    2820.0,
        "H_vo":    2733.0,
    }
    for k, v in _DEF.items():
        st.session_state.setdefault(f"v10_{k}", v)

    with st.expander("📥 Исходные данные — В.10", expanded=True):
        c1, c2 = st.columns(2)
        st.session_state["v10_tubing"] = c1.selectbox(
            "НКТ — типоразмер",
            list(TUBING_OPTIONS.keys()),
            index=list(TUBING_OPTIONS.keys()).index(st.session_state["v10_tubing"]))
        t_par = TUBING_OPTIONS[st.session_state["v10_tubing"]]
        c1.caption(f"d_вн = {t_par['d_in']*1000:.1f} мм, "
                   f"d_нар = {t_par['d_out']*1000:.1f} мм")

        st.session_state["v10_casing"] = c2.selectbox(
            "Эксплуатационная колонна",
            list(CASING_OPTIONS.keys()),
            index=list(CASING_OPTIONS.keys()).index(st.session_state["v10_casing"]))
        c_par = CASING_OPTIONS[st.session_state["v10_casing"]]
        c2.caption(f"D_к (вн.) = {c_par['D_in']*1000:.1f} мм")

        c1, c2 = st.columns(2)
        st.session_state["v10_H_no"] = c1.number_input(
            "H_н.о, м — глубина нижнего отверстия перфорации",
            value=float(st.session_state["v10_H_no"]), step=1.0)
        st.session_state["v10_H_vo"] = c2.number_input(
            "H_в.о, м — глубина верхнего отверстия перфорации",
            value=float(st.session_state["v10_H_vo"]), step=1.0)

        if st.session_state["v10_H_no"] <= st.session_state["v10_H_vo"]:
            st.error("H_н.о должно быть больше H_в.о (нижнее отверстие глубже верхнего).")
            return None

    # ---- расчёт ----
    res = solve(
        V_ks=V_ks_zad, V_zr=V_zr,
        d_in=t_par["d_in"], d_out=t_par["d_out"], D_in=c_par["D_in"],
        H_no=st.session_state["v10_H_no"], H_vo=st.session_state["v10_H_vo"],
        q_k=q_k,
    )

    # ---- сводка ----
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("V_з.р, м³",       f"{res['V_zr']:.4f}")
    c2.metric("V_втс (без зап.), м³", f"{res['V_vts_56']:.4f}")
    c3.metric("V_втс (с зап.), м³",   f"{res['V_vts_57']:.4f}")
    c4.metric("V_прд, м³",       f"{res['V_prd']:.4f}")

    c1, c2 = st.columns(2)
    c1.metric("V_общ (без зап.), м³", f"{res['V_total_56']:.3f}",
              delta=(f"t = {res['t_56']:.0f} мин" if res['t_56'] else None),
              delta_color="off")
    c2.metric("V_общ (с зап.), м³", f"{res['V_total_57']:.3f}",
              delta=(f"t = {res['t_57']:.0f} мин" if res['t_57'] else None),
              delta_color="off")

    # ---- расшифровка V_прд ----
    st.markdown("**Расшифровка V_прд (В.58):**")
    st.markdown(
        f"- Объём в НКТ (от устья до H_н.о): "
        f"0,785·{t_par['d_in']:.4f}²·{st.session_state['v10_H_no']:.1f} = "
        f"**{res['V_inside_NKT']:.4f} м³**\n"
        f"- Объём кольцевого пространства (между НКТ и колонной "
        f"в интервале H_н.о − H_в.о = "
        f"{st.session_state['v10_H_no']-st.session_state['v10_H_vo']:.1f} м): "
        f"0,785·({c_par['D_in']:.4f}² − {t_par['d_out']:.4f}²)·"
        f"{st.session_state['v10_H_no']-st.session_state['v10_H_vo']:.1f} = "
        f"**{res['V_annular']:.4f} м³**\n"
        f"- Итого V_прд = **{res['V_prd']:.4f} м³**"
    )

    # ---- сводная таблица ----
    st.markdown("**Сводный план закачки:**")
    df = pd.DataFrame([
        {"Этап": "СКР (V_ks)",                      "Объём, м³": res["V_ks"]},
        {"Этап": "Вытесняющая (В.56, без запаса)",  "Объём, м³": res["V_vts_56"]},
        {"Этап": "Вытесняющая (В.57, с запасом)",   "Объём, м³": res["V_vts_57"]},
        {"Этап": "Продавочная (В.58)",              "Объём, м³": res["V_prd"]},
        {"Этап": "ИТОГО (вариант без запаса)",      "Объём, м³": res["V_total_56"]},
        {"Этап": "ИТОГО (вариант с запасом)",       "Объём, м³": res["V_total_57"]},
    ])
    st.dataframe(df.style.format({"Объём, м³": "{:.4f}"}),
                 use_container_width=True, hide_index=True)

    # ---- сохранение ----
    st.session_state["task_v10_result"] = res
    return res
