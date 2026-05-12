"""Управление вводом исходных данных скважины."""
import streamlit as st
import pandas as pd


EXAMPLE_INPUTS = {
    "well_name": "Скважина №1",
    "K_f": 16.0, "K_pot": 51.0, "Q_f": 86.6, "q_inj": 150.0,
    "p_pl": 25.0, "H": 2800.0, "h_ef": 78.3, "h_pta": 17.0,
    "C_k": 3.1, "C_gl": 6.6, "k_ms_lab": 1.2, "m0": 14.0, "k0": 0.044,
    "T_pl": 85.0, "k_vo": 0.35, "k_uf": 0.28, "k_v": 0.5,
    "q_acid": 260.0, "C0_HCl": 15.0, "rho_sk": 2700.0, "rho_p": 2300.0,
    "R_ms": 2.0e-5, "Fe3": 0.1, "N_as": 1.0, "N_sm": 5.0, "N_nf": 0.1,
    "rho_fluid": 1000.0, "p_opr": 25.0, "well_type": "нефтяная",
    "r_c": 0.1, "r_k": 200.0, "T_n": 100.0, "rho_n": 0.84,
    "Q_f_oil": 86.6, "W_0": 81.9, "Tsena_n": 15.0, "Sebest_n": 8.0,
    "H_no": 2823.0, "H_vo": 2733.0, "D_k": 0.124, "d_vn": 0.073,
    "d_v": 0.062, "K_collector_type": 2,
    "layers_table": [
        {"interval": "2733-2750", "h_ef": 17, "porosity": 12.0},
        {"interval": "2750-2762", "h_ef": 12, "porosity": 9.8},
        {"interval": "2762-2780", "h_ef": 18, "porosity": 13.0},
        {"interval": "2780-2802", "h_ef": 22, "porosity": 10.5},
        {"interval": "2802-2823", "h_ef": 21, "porosity": 9.6},
    ],
}

EMPTY_INPUTS = {k: ("" if isinstance(v, str) else
                    [] if isinstance(v, list) else
                    0 if isinstance(v, int) else 0.0)
                for k, v in EXAMPLE_INPUTS.items()}
EMPTY_INPUTS["well_type"] = "нефтяная"
EMPTY_INPUTS["K_collector_type"] = 1


def init_session_defaults():
    for k, v in EMPTY_INPUTS.items():
        st.session_state.setdefault(k, v)


def fill_example_inputs():
    for k, v in EXAMPLE_INPUTS.items():
        st.session_state[k] = v


def render_input_form(inline: bool = False):
    """Форма ввода данных скважины.

    inline=True → встраиваемый режим: без шапки страницы и без кнопок
    навигации (используется внутри страницы «Настройки месторождения»).
    """
    if not inline:
        st.header("📥 Исходные данные скважины")
        st.caption("Эти данные используются всеми задачами. Заполните один раз и переходите к расчётам.")
    else:
        st.markdown("### 📥 Данные скважины")
        st.caption("Эти данные используются всеми задачами расчёта СКО.")

    init_session_defaults()

    with st.expander("🪪 Идентификация и общие параметры", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.well_name = st.text_input("Название скважины", st.session_state.well_name)
            st.session_state.well_type = st.selectbox(
                "Тип скважины (В.3)",
                ["нефтяная", "водонагнетательная"],
                index=0 if st.session_state.well_type == "нефтяная" else 1,
            )
            st.session_state.H = st.number_input("Глубина пласта H, м (В.2, В.3)", value=float(st.session_state.H), step=10.0)
            st.session_state.T_pl = st.number_input("Пластовая температура T_пл, °C (В.4, В.11)", value=float(st.session_state.T_pl), step=1.0)
        with c2:
            st.session_state.p_pl = st.number_input("Пластовое давление p_пл, МПа (В.2)", value=float(st.session_state.p_pl), step=0.5)
            st.session_state.p_opr = st.number_input("Давление опрессовки p_опр, МПа (В.3)", value=float(st.session_state.p_opr), step=0.5)
            st.session_state.r_c = st.number_input("Радиус скважины r_c, м (В.5, В.9)", value=float(st.session_state.r_c), step=0.01, format="%.3f")
            st.session_state.r_k = st.number_input("Радиус контура питания r_к, м (В.9)", value=float(st.session_state.r_k), step=10.0)
        with c3:
            st.session_state.h_ef = st.number_input("Эффективная толщина h_эф, м (В.1, В.2, В.4, В.5)", value=float(st.session_state.h_ef), step=1.0)
            st.session_state.h_pta = st.number_input("Толщина поглощающая h_пта, м — термометрия (В.1)", value=float(st.session_state.h_pta), step=1.0)
            st.session_state.m0 = st.number_input("Пористость m_0, % (В.4, В.5, В.6, В.7, В.8)", value=float(st.session_state.m0), step=0.5)
            st.session_state.k0 = st.number_input("Проницаемость k_0, мкм² (В.4, В.8, В.9)", value=float(st.session_state.k0), step=0.001, format="%.4f")

    with st.expander("📊 Продуктивность и приёмистость", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.K_f = st.number_input("K_ф, т/(сут·МПа) (В.1)", value=float(st.session_state.K_f))
            st.session_state.K_pot = st.number_input("K_пот, т/(сут·МПа) (В.1)", value=float(st.session_state.K_pot))
        with c2:
            st.session_state.Q_f = st.number_input("Q_ф фактический дебит, м³/сут (В.2, В.9)", value=float(st.session_state.Q_f))
            st.session_state.q_inj = st.number_input("q приёмистость с ПАВ, м³/сут (В.2)", value=float(st.session_state.q_inj))
        with c3:
            st.session_state.W_0 = st.number_input("Обводнённость W_0, % (В.9)", value=float(st.session_state.W_0))
            st.session_state.rho_n = st.number_input("Плотность нефти ρ_н, т/м³ (В.9)", value=float(st.session_state.rho_n), step=0.01)

    with st.expander("🪨 Состав породы и фильтрационные коэффициенты", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.C_k = st.number_input("Карбонатность C_к, % (В.1, В.6, В.8)", value=float(st.session_state.C_k))
            st.session_state.C_gl = st.number_input("Глинистость C_гл, % (В.2, В.6)", value=float(st.session_state.C_gl))
            st.session_state.k_ms_lab = st.number_input("k_ms лаб., возрастание пористости (В.1, В.5)", value=float(st.session_state.k_ms_lab), step=0.01)
        with c2:
            st.session_state.k_vo = st.number_input("k_во охват по вертикали (В.4, В.5)", value=float(st.session_state.k_vo), step=0.01)
            st.session_state.k_uf = st.number_input("k_уф участие пор (В.4, В.5)", value=float(st.session_state.k_uf), step=0.01)
            st.session_state.k_v = st.number_input("k_в вытеснение (В.4, В.5)", value=float(st.session_state.k_v), step=0.01)
        with c3:
            st.session_state.rho_sk = st.number_input("ρ_ск, кг/м³ (В.5, В.7)", value=float(st.session_state.rho_sk))
            st.session_state.rho_p = st.number_input("ρ_п, кг/м³ (В.6, В.7)", value=float(st.session_state.rho_p))
            st.session_state.R_ms = st.number_input("R_ms, кг/(мг·экв) (В.5)", value=float(st.session_state.R_ms), step=1e-6, format="%.7f")
        st.session_state.K_collector_type = st.selectbox(
            "Тип коллектора KL по табл. B.10 (В.8)",
            [1, 2, 3, 4, 5],
            index=int(st.session_state.K_collector_type) - 1,
        )

    with st.expander("⚗ Параметры кислотной обработки", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.C0_HCl = st.number_input("Начальная концентрация HCl C_0, % (В.4, В.11, В.17)", value=float(st.session_state.C0_HCl), step=0.5)
            st.session_state.q_acid = st.number_input("Расход СКР q_к, м³/сут (В.4, В.5)", value=float(st.session_state.q_acid))
        with c2:
            st.session_state.Fe3 = st.number_input("Содержание Fe³⁺, % (В.11)", value=float(st.session_state.Fe3), step=0.01)
            st.session_state.N_as = st.number_input("Асфальтены N_ас, % (В.11)", value=float(st.session_state.N_as))
        with c3:
            st.session_state.N_sm = st.number_input("Смолы N_см, % (В.11)", value=float(st.session_state.N_sm))
            st.session_state.N_nf = st.number_input("Нафтеновые кислоты N_нф, % (В.11)", value=float(st.session_state.N_nf))

    with st.expander("🧱 Конструкция скважины", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.H_no = st.number_input("H_н.о — нижнее отв. перфорации, м (В.10)", value=float(st.session_state.H_no))
            st.session_state.H_vo = st.number_input("H_в.о — верхнее отв. перфорации, м (В.10)", value=float(st.session_state.H_vo))
        with c2:
            st.session_state.D_k = st.number_input("D_к внутр. ЭК, м (В.10)", value=float(st.session_state.D_k), step=0.001, format="%.3f")
            st.session_state.d_vn = st.number_input("d_вн внутр. НКТ, м (В.10)", value=float(st.session_state.d_vn), step=0.001, format="%.3f")
            st.session_state.d_v = st.number_input("d_в наруж. НКТ, м (В.10)", value=float(st.session_state.d_v), step=0.001, format="%.3f")
        with c3:
            st.session_state.rho_fluid = st.number_input("ρ продавочной жидкости, кг/м³ (В.10)", value=float(st.session_state.rho_fluid))

    with st.expander("💰 Экономика", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.T_n = st.number_input("Длительность работы T_н, сут (В.9)", value=float(st.session_state.T_n))
        with c2:
            st.session_state.Tsena_n = st.number_input("Цена нефти Ц_н, руб/т (В.9)", value=float(st.session_state.Tsena_n))
        with c3:
            st.session_state.Sebest_n = st.number_input("Себестоимость С_н, руб/т (В.9)", value=float(st.session_state.Sebest_n))

    with st.expander("📑 Таблица продуктивных пластов", expanded=False):
        df = pd.DataFrame(st.session_state.layers_table)
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="layers_editor")
        st.session_state.layers_table = edited.to_dict("records")

    if not inline:
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        left, _, right = st.columns([2, 6, 2])
        if left.button("ПРИМЕР", use_container_width=True,
                       key="btn_example_inputs", type="secondary"):
            fill_example_inputs()
            st.rerun()
        if right.button("ДАЛЕЕ  →", use_container_width=True,
                        key="btn_next_inputs", type="primary"):
            st.session_state["_pending_section"] = "📋 Задачи СКО"
            st.rerun()


def get_inputs() -> dict:
    """Снимок всех данных скважины."""
    keys = [
        "well_name", "well_type", "K_f", "K_pot", "Q_f", "q_inj", "p_pl", "H",
        "h_ef", "h_pta", "C_k", "C_gl", "k_ms_lab", "m0", "k0", "T_pl",
        "k_vo", "k_uf", "k_v", "q_acid", "C0_HCl", "rho_sk", "rho_p", "R_ms",
        "Fe3", "N_as", "N_sm", "N_nf", "rho_fluid", "p_opr", "r_c", "r_k",
        "T_n", "rho_n", "W_0", "Tsena_n", "Sebest_n", "H_no", "H_vo",
        "D_k", "d_vn", "d_v", "K_collector_type", "layers_table",
    ]
    return {k: st.session_state.get(k) for k in keys}
