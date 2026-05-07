"""Главный Streamlit-файл приложения СКО."""
import streamlit as st

from modules.constants import reset_to_default, empty_config
from modules.input_data import render_input_form, get_inputs, init_session_defaults
from modules.theme import apply_theme, stimcore_header
from modules.tasks import (
    task_v1, task_v2, task_v3, task_v4, task_v5,
    task_v6, task_v7, task_v8, task_v9, task_v10, task_v11, task_v17,
)

st.set_page_config(page_title="StimCore — СКО", page_icon="◆", layout="wide")
apply_theme()

# Состояние констант — при первом запуске пусто
if "constants" not in st.session_state:
    st.session_state["constants"] = empty_config()
init_session_defaults()

stimcore_header("StimCore", "Расчёт солянокислотной обработки")

st.sidebar.markdown("### ◆ STIMCORE")

SECTIONS = [
    "🛠 Настройки месторождения",
    "📥 Ввод данных скважины",
    "📋 Задачи СКО",
]
if "section" not in st.session_state:
    st.session_state["section"] = SECTIONS[0]

# Отложенный переход (выставляется кнопкой, применяется до создания radio)
_pending = st.session_state.pop("_pending_section", None)
if _pending:
    st.session_state["section"] = _pending

section = st.sidebar.radio("Раздел", SECTIONS, key="section")


def render_constants_ui():
    st.header("🛠 Настройки месторождения (константы)")
    cfg = st.session_state["constants"]

    with st.expander("Критерии отбора скважины", expanded=True):
        sel = cfg["well_selection"]
        c1, c2, c3 = st.columns(3)
        sel["m_pr_default"] = c1.number_input("m_пр, % (мин. пористость)", value=float(sel["m_pr_default"]), help="Типично 7–11% для Предкарпатья")
        sel["h_pr_min"] = c1.number_input("h_пр, м (мин. толщина)", value=float(sel["h_pr_min"]))
        sel["C_k_pr"] = c2.number_input("C_к.пр, % (мин. карбонатность)", value=float(sel["C_k_pr"]))
        sel["C_gl_pr"] = c2.number_input("C_гл.пр, % (макс. глины)", value=float(sel["C_gl_pr"]))
        sel["k_s_np"] = c3.number_input("k_s.np (мин. возрастание пористости)", value=float(sel["k_s_np"]), step=0.05)
        sel["q_pr"] = c3.number_input("q_пр, м³/сут (мин. приёмистость)", value=float(sel["q_pr"]))

    with st.expander("Градиенты давления и опрессовки"):
        pg = cfg["pressure_gradients"]
        c1, c2 = st.columns(2)
        pg["grad_p_grp_oil"] = c1.number_input("grad p_грп нефт.", value=float(pg["grad_p_grp_oil"]), step=0.01)
        pg["grad_p_grp_water"] = c2.number_input("grad p_грп водонагн.", value=float(pg["grad_p_grp_water"]), step=0.01)

    with st.expander("Кинетика реакции (α)"):
        rk = cfg["reaction_kinetics"]
        rk["alpha_kgo"] = st.number_input("α в k_го = exp(-α·r)", value=float(rk["alpha_kgo"]), step=0.01,
                                          help="Для Предкарпатья = 0.1")
        st.caption(rk.get("comment_alpha", ""))

    with st.expander("Свойства породы (диапазоны)"):
        rp = cfg["rock_properties"]
        c1, c2, c3 = st.columns(3)
        rp["rho_sk_default"] = c1.number_input("ρ_ск default, кг/м³", value=float(rp["rho_sk_default"]))
        rp["rho_p_default"] = c2.number_input("ρ_п default, кг/м³", value=float(rp["rho_p_default"]))
        rp["k_ms_default"] = c3.number_input("k_ms default", value=float(rp["k_ms_default"]), step=0.05)
        rp["R_ms_default"] = c1.number_input("R_ms default", value=float(rp["R_ms_default"]), step=1e-6, format="%.7f")

    with st.expander("Коэффициенты растворения (a, b)"):
        d = cfg["dissolution_coefficients"]
        c1, c2 = st.columns(2)
        d["a_clay"] = c1.number_input("a (глины)", value=float(d["a_clay"]), step=0.01)
        d["b_carbonate"] = c2.number_input("b (карбонаты)", value=float(d["b_carbonate"]), step=0.01)
        st.caption(d.get("comment", ""))

    with st.expander("Регрессии k₀(m₀) — табл. B.11"):
        for KL in range(1, 6):
            key = f"KL_{KL}"
            r = cfg["permeability_regressions"][key]
            c1, c2 = st.columns(2)
            r["A"] = c1.number_input(f"{key} A", value=float(r["A"]), format="%.3e", key=f"reg_A_{KL}")
            r["B"] = c2.number_input(f"{key} B", value=float(r["B"]), step=0.01, key=f"reg_B_{KL}")

    with st.expander("k_s* = A·exp(B·C_к)"):
        ps = cfg["permeability_change_after_sko"]
        c1, c2 = st.columns(2)
        ps["A"] = c1.number_input("A (k_s*)", value=float(ps["A"]), step=0.05)
        ps["B"] = c2.number_input("B (k_s*)", value=float(ps["B"]), step=0.01)

    with st.expander("Таблица B.2 — удельные дебиты"):
        import pandas as pd
        df = pd.DataFrame(cfg["specific_debit_table"]["rows"])
        edited = st.data_editor(df, num_rows="dynamic", key="cfg_b2_editor")
        cfg["specific_debit_table"]["rows"] = edited.to_dict("records")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    left, _, right = st.columns([2, 6, 2])
    if left.button("ПРИМЕР", use_container_width=True,
                   key="btn_example", type="secondary"):
        st.session_state["constants"] = reset_to_default()
        st.rerun()
    if right.button("ДАЛЕЕ  →", use_container_width=True,
                    key="btn_next", type="primary"):
        st.session_state["_pending_section"] = "📥 Ввод данных скважины"
        st.rerun()


TASKS = [
    ("В.1 Выбор скважины (полная информация)", task_v1.render),
    ("В.2 Выбор скважины (огранич. информация)", task_v2.render),
    ("В.3 Расход и давление при нагнетании", task_v3.render),
    ("В.4 Длительность реакции СКР", task_v4.render),
    ("В.5 Зона растворения (Рис. B.3)", task_v5.render),
    ("В.6 Растворённая порода (по составу)", task_v6.render),
    ("В.7 Изменение пористости", task_v7.render),
    ("В.8 Проницаемость до/после (Рис. B.4)", task_v8.render),
    ("В.9 Эффективность СКО", task_v9.render),
    ("В.10 Объёмы вспомогательных жидкостей", task_v10.render),
    ("В.11 Состав КР (СКО)", task_v11.render),
    ("В.17 Количество реагентов", task_v17.render),
]


def render_tasks():
    st.header("📋 Задачи СКО")
    cfg = st.session_state["constants"]
    titles = [t[0] for t in TASKS]
    sel = st.selectbox("Выберите задачу", titles)
    idx = titles.index(sel)
    TASKS[idx][1](cfg)


if section.startswith("🛠"):
    render_constants_ui()
elif section.startswith("📥"):
    render_input_form()
else:
    render_tasks()

st.sidebar.markdown("---")
st.sidebar.caption("Литература: Приложение В — методика проектирования КО (только ветка СКО).")
