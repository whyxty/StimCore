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
        st.header("Исходные данные скважины")
        st.caption("Эти данные используются всеми задачами. Заполните один раз и переходите к расчётам.")
    else:
        st.markdown("### Данные скважины")
        st.caption("Эти данные используются всеми задачами расчёта СКО.")

    init_session_defaults()

    with st.expander("Идентификация и общие параметры", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.well_name = st.text_input("Название скважины (идентификатор объекта)", st.session_state.well_name)
            st.session_state.well_type = st.selectbox(
                "Тип скважины (нефтяная / водонагнетательная) (В.3)",
                ["нефтяная", "водонагнетательная"],
                index=0 if st.session_state.well_type == "нефтяная" else 1,
            )
            st.session_state.H = st.number_input("$H$, м (глубина залегания пласта) (В.2, В.3)", value=float(st.session_state.H), step=10.0)
            st.session_state.T_pl = st.number_input("$T_{пл}$, °C (пластовая температура) (В.4, В.11)", value=float(st.session_state.T_pl), step=1.0)
        with c2:
            st.session_state.p_pl = st.number_input("$p_{пл}$, МПа (пластовое давление) (В.2)", value=float(st.session_state.p_pl), step=0.5)
            st.session_state.p_opr = st.number_input("$p_{опр}$, МПа (давление опрессовки колонны) (В.3)", value=float(st.session_state.p_opr), step=0.5)
            st.session_state.r_c = st.number_input("$r_c$, м (радиус скважины по долоту) (В.5, В.9)", value=float(st.session_state.r_c), step=0.01, format="%.3f")
            st.session_state.r_k = st.number_input("$r_к$, м (радиус контура питания) (В.9)", value=float(st.session_state.r_k), step=10.0)
        with c3:
            st.session_state.h_ef = st.number_input("$h_{эф}$, м (эффективная перфорированная толщина пласта) (В.1, В.2, В.4, В.5)", value=float(st.session_state.h_ef), step=1.0)
            st.session_state.h_pta = st.number_input("$h_{пта}$, м (поглощающая толщина по термометрии/расходометрии) (В.1)", value=float(st.session_state.h_pta), step=1.0)
            st.session_state.m0 = st.number_input("$m_0$, % (начальная пористость пласта) (В.4, В.5, В.6, В.7, В.8)", value=float(st.session_state.m0), step=0.5)
            st.session_state.k0 = st.number_input("$k_0$, мкм² (начальная проницаемость пласта) (В.4, В.8, В.9)", value=float(st.session_state.k0), step=0.001, format="%.4f")

    with st.expander("Продуктивность и приёмистость", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.K_f = st.number_input("$K_ф$, т/(сут·МПа) (фактический коэффициент продуктивности) (В.1)", value=float(st.session_state.K_f))
            st.session_state.K_pot = st.number_input("$K_{пот}$, т/(сут·МПа) (потенциальный коэффициент продуктивности) (В.1)", value=float(st.session_state.K_pot))
        with c2:
            st.session_state.Q_f = st.number_input("$Q_ф$, м³/сут (фактический дебит жидкости) (В.2, В.9)", value=float(st.session_state.Q_f))
            st.session_state.q_inj = st.number_input("$q$, м³/сут (приёмистость скважины при закачке с ПАВ) (В.2)", value=float(st.session_state.q_inj))
        with c3:
            st.session_state.W_0 = st.number_input("$W_0$, % (обводнённость продукции) (В.9)", value=float(st.session_state.W_0))
            st.session_state.rho_n = st.number_input(r"$\rho_н$, т/м³ (плотность нефти в пластовых условиях) (В.9)", value=float(st.session_state.rho_n), step=0.01)

    with st.expander("Состав породы и фильтрационные коэффициенты", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.C_k = st.number_input("$C_к$, % (карбонатность породы) (В.1, В.6, В.8)", value=float(st.session_state.C_k))
            st.session_state.C_gl = st.number_input("$C_{гл}$, % (глинистость породы) (В.2, В.6)", value=float(st.session_state.C_gl))
            st.session_state.k_ms_lab = st.number_input("$k_{ms}$ (лабораторный коэффициент возрастания пористости после СКО) (В.1, В.5)", value=float(st.session_state.k_ms_lab), step=0.01)
        with c2:
            st.session_state.k_vo = st.number_input("$k_{во}$ (коэффициент охвата пласта обработкой по вертикали) (В.4, В.5)", value=float(st.session_state.k_vo), step=0.01)
            st.session_state.k_uf = st.number_input("$k_{уф}$ (коэффициент участия пор в фильтрации) (В.4, В.5)", value=float(st.session_state.k_uf), step=0.01)
            st.session_state.k_v = st.number_input("$k_в$ (коэффициент вытеснения нефти СКР) (В.4, В.5)", value=float(st.session_state.k_v), step=0.01)
        with c3:
            st.session_state.rho_sk = st.number_input(r"$\rho_{ск}$, кг/м³ (плотность скелета породы) (В.5, В.7)", value=float(st.session_state.rho_sk))
            st.session_state.rho_p = st.number_input(r"$\rho_п$, кг/м³ (плотность пористой породы) (В.6, В.7)", value=float(st.session_state.rho_p))
            st.session_state.R_ms = st.number_input("$R_{ms}$, кг/(мг·экв) (удельная масса растворённой породы на 1 мг·экв HCl) (В.5)", value=float(st.session_state.R_ms), step=1e-6, format="%.7f")
        st.session_state.K_collector_type = st.selectbox(
            "$KL$ (тип коллектора по табл. В.10) (В.8)",
            [1, 2, 3, 4, 5],
            index=int(st.session_state.K_collector_type) - 1,
        )

    with st.expander("Параметры кислотной обработки", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.C0_HCl = st.number_input("$C_0$, % (начальная концентрация HCl в кислотном растворе) (В.4, В.11, В.17)", value=float(st.session_state.C0_HCl), step=0.5)
            st.session_state.q_acid = st.number_input("$q_к$, м³/сут (расход кислотного раствора при закачке) (В.4, В.5)", value=float(st.session_state.q_acid))
        with c2:
            st.session_state.Fe3 = st.number_input("$Fe^{3+}$, % (содержание трёхвалентного железа в СКР) (В.11)", value=float(st.session_state.Fe3), step=0.01)
            st.session_state.N_as = st.number_input("$N_{ас}$, % (содержание асфальтенов в нефти) (В.11)", value=float(st.session_state.N_as))
        with c3:
            st.session_state.N_sm = st.number_input("$N_{см}$, % (содержание смол в нефти) (В.11)", value=float(st.session_state.N_sm))
            st.session_state.N_nf = st.number_input("$N_{нф}$, % (содержание нафтеновых кислот в нефти) (В.11)", value=float(st.session_state.N_nf))

    with st.expander("Конструкция скважины", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.H_no = st.number_input("$H_{н.о}$, м (глубина нижнего отверстия перфорации) (В.10)", value=float(st.session_state.H_no))
            st.session_state.H_vo = st.number_input("$H_{в.о}$, м (глубина верхнего отверстия перфорации) (В.10)", value=float(st.session_state.H_vo))
        with c2:
            st.session_state.D_k = st.number_input("$D_к$, м (внутренний диаметр эксплуатационной колонны) (В.10)", value=float(st.session_state.D_k), step=0.001, format="%.3f")
            st.session_state.d_vn = st.number_input("$d_{вн}$, м (внутренний диаметр НКТ) (В.10)", value=float(st.session_state.d_vn), step=0.001, format="%.3f")
            st.session_state.d_v = st.number_input("$d_в$, м (наружный диаметр НКТ) (В.10)", value=float(st.session_state.d_v), step=0.001, format="%.3f")
        with c3:
            st.session_state.rho_fluid = st.number_input(r"$\rho_{ж}$, кг/м³ (плотность продавочной жидкости) (В.10)", value=float(st.session_state.rho_fluid))

    with st.expander("Экономика", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.T_n = st.number_input("$T_н$, сут (длительность работы скважины после СКО) (В.9)", value=float(st.session_state.T_n))
        with c2:
            st.session_state.Tsena_n = st.number_input("$Ц_н$, руб/т (цена реализации нефти) (В.9)", value=float(st.session_state.Tsena_n))
        with c3:
            st.session_state.Sebest_n = st.number_input("$С_н$, руб/т (себестоимость добычи нефти) (В.9)", value=float(st.session_state.Sebest_n))

    with st.expander("Таблица продуктивных пластов", expanded=True):
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
            st.session_state["_pending_section"] = "Задачи СКО"
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
