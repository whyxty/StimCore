"""Главный Streamlit-файл приложения СКО."""
import streamlit as st

from modules.constants import reset_to_default
from modules.input_data import render_input_form, get_inputs, init_session_defaults, fill_example_inputs
from modules.theme import apply_theme, stimcore_header
from modules.tasks import (
    task_v1, task_v2, task_v3, task_v4, task_v5,
    task_v6, task_v7, task_v8, task_v9, task_v10, task_v11, task_v17,
)

st.set_page_config(page_title="StimCore — СКО", page_icon="◆", layout="wide")
apply_theme()

# Состояние констант — при первом запуске подгружаем нормативы Предкарпатья
if "constants" not in st.session_state:
    st.session_state["constants"] = reset_to_default()
init_session_defaults()

stimcore_header("StimCore", "Расчёт солянокислотной обработки")

st.sidebar.markdown("### ◆ STIMCORE")

SECTIONS = [
    "🛠 Настройки месторождения",
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
        sel["m_pr_default"] = c1.number_input("$m_{пр}$, % (граничная пористость коллектора) — В.1, В.2", value=float(sel["m_pr_default"]), help="Типично 7–11% для Предкарпатья")
        sel["h_pr_min"] = c1.number_input("$h_{пр}$, м (минимальная толщина поглощающего пласта) — В.1, В.3", value=float(sel["h_pr_min"]))
        sel["C_k_pr"] = c2.number_input("$C_{к.пр}$, % (минимальная карбонатность породы) — В.1, В.7", value=float(sel["C_k_pr"]))
        sel["C_gl_pr"] = c2.number_input("$C_{гл.пр}$, % (максимальная глинистость породы) — В.2", value=float(sel["C_gl_pr"]))
        sel["k_s_np"] = c3.number_input("$k_{s.пр}$ (минимальный прирост пористости после СКО) — В.1, В.4, В.5, В.6", value=float(sel["k_s_np"]), step=0.05)
        sel["q_pr"] = c3.number_input("$q_{пр}$, м³/сут (минимальная приёмистость скважины) — В.2", value=float(sel["q_pr"]))

    with st.expander("Градиенты давления и опрессовки", expanded=True):
        pg = cfg["pressure_gradients"]
        c1, c2 = st.columns(2)
        pg["grad_p_grp_oil"] = c1.number_input("grad $p_{грп}$ (градиент давления гидроразрыва, нефтяные) — В.3", value=float(pg["grad_p_grp_oil"]), step=0.01)
        pg["grad_p_grp_water"] = c2.number_input("grad $p_{грп}$ (градиент давления гидроразрыва, водонагнетательные) — В.3", value=float(pg["grad_p_grp_water"]), step=0.01)

    with st.expander("Кинетика реакции (α)", expanded=True):
        rk = cfg["reaction_kinetics"]
        rk["alpha_kgo"] = st.number_input(r"$\alpha$ в $k_{го}=e^{-\alpha r}$ (коэффициент кинетики реакции ГКР) — В.4", value=float(rk["alpha_kgo"]), step=0.01,
                                          help="Для Предкарпатья = 0.1")
        st.caption(rk.get("comment_alpha", ""))

    with st.expander("Свойства породы (диапазоны)", expanded=True):
        rp = cfg["rock_properties"]
        c1, c2, c3 = st.columns(3)
        rp["rho_sk_default"] = c1.number_input(r"$\rho_{ск}$, кг/м³ (плотность скелета породы) — В.5, В.7", value=float(rp["rho_sk_default"]))
        rp["rho_p_default"] = c2.number_input(r"$\rho_{п}$, кг/м³ (плотность пористой породы) — В.6, В.7", value=float(rp["rho_p_default"]))
        rp["k_ms_default"] = c3.number_input("$k_{ms}$ (коэффициент возрастания пористости после СКО) — В.1, В.5, В.7", value=float(rp["k_ms_default"]), step=0.05)
        rp["R_ms_default"] = c1.number_input("$R_{ms}$, кг/(мг·экв) (удельная масса растворённой породы на 1 мг·экв HCl) — В.5", value=float(rp["R_ms_default"]), step=1e-6, format="%.7f")

    with st.expander("Коэффициенты растворения (a, b)", expanded=True):
        d = cfg["dissolution_coefficients"]
        c1, c2 = st.columns(2)
        d["a_clay"] = c1.number_input("$a$ (доля растворимости глин в HCl) — В.6, В.7", value=float(d["a_clay"]), step=0.01)
        d["b_carbonate"] = c2.number_input("$b$ (доля растворимости карбонатов в HCl) — В.6, В.7", value=float(d["b_carbonate"]), step=0.01)
        st.caption(d.get("comment", ""))

    with st.expander("Регрессии k₀(m₀) — табл. B.11", expanded=True):
        for KL in range(1, 6):
            key = f"KL_{KL}"
            r = cfg["permeability_regressions"][key]
            c1, c2 = st.columns(2)
            r["A"] = c1.number_input(f"$KL_{KL}$ · $A$ (предэкспоненциальный коэффициент регрессии $k_0(m_0)$) — В.8", value=float(r["A"]), format="%.3e", key=f"reg_A_{KL}")
            r["B"] = c2.number_input(f"$KL_{KL}$ · $B$ (показатель степени регрессии $k_0(m_0)$) — В.8", value=float(r["B"]), step=0.01, key=f"reg_B_{KL}")

    with st.expander("k_s* = A·exp(B·C_к)", expanded=True):
        ps = cfg["permeability_change_after_sko"]
        c1, c2 = st.columns(2)
        ps["A"] = c1.number_input("$A$ (предэкспоненциальный коэффициент в $k_s^*=A\\,e^{B C_к}$) — В.8", value=float(ps["A"]), step=0.05)
        ps["B"] = c2.number_input("$B$ (коэффициент при $C_к$ в $k_s^*=A\\,e^{B C_к}$) — В.8", value=float(ps["B"]), step=0.01)

    with st.expander("Таблица B.2 — удельные дебиты (используется в В.2)", expanded=True):
        import pandas as pd
        df = pd.DataFrame(cfg["specific_debit_table"]["rows"])
        edited = st.data_editor(df, num_rows="dynamic", key="cfg_b2_editor")
        cfg["specific_debit_table"]["rows"] = edited.to_dict("records")

    st.markdown("---")
    render_input_form(inline=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    left, _, right = st.columns([2, 6, 2])
    if left.button("ПРИМЕР", use_container_width=True,
                   key="btn_example", type="secondary"):
        st.session_state["constants"] = reset_to_default()
        fill_example_inputs()
        st.rerun()
    if right.button("ДАЛЕЕ  →", use_container_width=True,
                    key="btn_next", type="primary"):
        st.session_state["_pending_section"] = "📋 Задачи СКО"
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
else:
    render_tasks()

