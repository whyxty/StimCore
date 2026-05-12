"""Задача В.5 — параметры зоны растворения СКР.

Расчёт по формулам (В.30)–(В.37):
- V_ks(r)  — объём СКР, проникшего на радиус r            (В.31)
- t_u      — длительность закачивания                      (В.32)
- k_ms     — коэф. возрастания пористости (лаб. или Δm_s)  (В.33)
- G_s      — масса растворённой породы                     (В.34)
- G_ms     — макс. растворимость в объёме СКР              (В.37) = (В.36) в (В.35)
- r_пр.р   — радиус продуктов реакции (по заданному V_ks)
- r_з.р    — радиус зоны растворения (пересечение G_s(r) = G_ms)
- m_c      — пористость после обработки

Согласовано:
- m_0 задаётся в % (в (В.30) "/100" и "·100" взаимно сокращаются).
- k_г.о в (В.30) не входит — в тексте методики это упоминание без участия в формуле.
- Коэффициенты: k_в.о (охват по вертикали), k_у.ф (участие пор), k_в (вытеснение).
"""
import math
import numpy as np
import pandas as pd
import streamlit as st

from ._shared import render_precarpathian_constants
import plotly.graph_objects as go

from modules.reference_tables import get_C_ms

EXAMPLE = {
    "r_c":       0.1,
    "h_ef":      78.3,
    "m0":        14.0,
    "k_vo":      0.35,
    "k_uf":      0.28,
    "k_v":       0.50,
    "rho_sk":    2700.0,
    "k_ms_mode": "напрямую",
    "k_ms_lab":  1.20,
    "dm_s":      2.8,
    "R_ms":      2.0e-5,
    "C0_HCl":    15.0,
    "q_acid":    260.0,
    "V_zad":     12.0,
}

_DEFAULTS = {
    "r_c":       0.0,
    "h_ef":      0.0,
    "m0":        0.0,
    "k_vo":      0.0,
    "k_uf":      0.0,
    "k_v":       0.0,
    "rho_sk":    0.0,
    "k_ms_mode": "напрямую",
    "k_ms_lab":  1.0,
    "dm_s":      0.0,
    "R_ms":      0.0,
    "C0_HCl":    0.0,
    "q_acid":    0.0,
    "V_zad":     0.0,
}


# ---------- математика ----------

def A_of_r(r: float, r_c: float, alpha: float = 0.1) -> float:
    """Скобочная функция A(r) из (В.30)."""
    return (math.exp(-alpha * r_c) * (alpha * r_c + 1)
            - math.exp(-alpha * r)  * (alpha * r  + 1))


def V_ks_of_r(r, r_c, h_ef, k_vo, k_uf, k_v, m0_pct, alpha=0.1):
    """Объём СКР на радиус r (В.31). m0_pct — пористость в %."""
    return 2 * math.pi * h_ef * k_vo * k_uf * k_v * m0_pct * A_of_r(r, r_c, alpha)


def _build_grid(r_c: float, r_max: float = 10.0):
    """Сетка r согласно методике: шаг 0.1 до 1; 0.2 до 2; 1.0 до 10."""
    rs = [r_c]
    r = max(0.2, math.ceil(r_c * 10) / 10)
    while r <= 1.0 + 1e-9:
        rs.append(round(r, 2)); r += 0.1
    r = 1.2
    while r <= 2.0 + 1e-9:
        rs.append(round(r, 2)); r += 0.2
    r = 2.5
    while r <= r_max + 1e-9:
        rs.append(round(r, 2))
        r += 0.5 if r < 3.0 else 1.0
    # уникализация и сортировка
    return sorted(set(round(x, 3) for x in rs))


# ---------- основной расчёт ----------

def solve(inp: dict, const: dict) -> dict:
    alpha  = const.get("reaction_kinetics", {}).get("alpha_kgo", 0.1)
    r_c    = inp["r_c"]
    h_ef   = inp["h_ef"]
    m0     = inp["m0"]                         # %
    k_vo   = inp["k_vo"]
    k_uf   = inp["k_uf"]
    k_v    = inp["k_v"]
    rho_sk = inp["rho_sk"]
    R_ms   = inp["R_ms"]
    C0     = inp["C0_HCl"]                     # %
    q_k    = inp["q_acid"]                     # м³/сут
    V_zad  = inp["V_zad"]                      # м³

    # --- k_ms ---
    if inp.get("k_ms_mode") == "по Δm_s":
        dms = inp["dm_s"]
        k_ms = (m0 + dms) / m0                 # (В.33)
    else:
        k_ms = inp["k_ms_lab"]

    # --- C_ms из табл. В.4 (кг/л → кг/м³) ---
    C_ms = get_C_ms(C0) * 1000.0
    DC_s = 0.9 * C_ms                          # (В.36), кг/м³

    # --- профиль по r ---
    rs = _build_grid(r_c, 10.0)
    rows = []
    for r in rs:
        Ar = A_of_r(r, r_c, alpha)
        V  = V_ks_of_r(r, r_c, h_ef, k_vo, k_uf, k_v, m0, alpha)
        Gs = rho_sk * V * (k_ms - 1)           # (В.34), кг
        rows.append({"r, м": r, "A(r)": Ar, "V_ks, м³": V, "G_s, кг": Gs})
    df = pd.DataFrame(rows)

    # --- по заданному V_zad: r_пр.р, t_u, G_ms, r_з.р ---
    Vmax = df["V_ks, м³"].max()
    if V_zad <= Vmax:
        r_pr = float(np.interp(V_zad, df["V_ks, м³"], df["r, м"]))
    else:
        r_pr = float(df["r, м"].iloc[-1])

    t_u  = 1440.0 * V_zad / q_k if q_k > 0 else 0.0    # (В.32), мин
    G_ms = 0.9 * V_zad * C_ms * R_ms                   # (В.37), кг
    G_s_zad = rho_sk * V_zad * (k_ms - 1)              # масса растворённой породы при V=V_zad

    # r_з.р: точка, где G_s(r) = G_ms
    if G_ms <= df["G_s, кг"].max():
        r_zr = float(np.interp(G_ms, df["G_s, кг"], df["r, м"]))
    else:
        r_zr = float(df["r, м"].iloc[-1])

    m_c = k_ms * m0                                    # пористость после обработки, %

    return {
        "k_ms":    k_ms,
        "C_ms":    C_ms,
        "DC_s":    DC_s,
        "df":      df,
        "V_zad":   V_zad,
        "r_pr_p":  r_pr,
        "t_u":     t_u,
        "G_ms":    G_ms,
        "G_s_zad": G_s_zad,
        "r_zr":    r_zr,
        "m_0":     m0,
        "m_c":     m_c,
    }


# ---------- UI ----------

def _render_constants_block(cfg: dict):
    """Блок констант профиля месторождения — справочно (read-only)."""
    rk   = cfg.get("reaction_kinetics", {})
    rock = cfg.get("rock_properties", {})
    alpha     = rk.get("alpha_kgo", 0.1)
    rho_min   = rock.get("rho_sk_min", 2000)
    rho_max   = rock.get("rho_sk_max", 2700)
    rho_def   = rock.get("rho_sk_default", 2700)
    kms_min   = rock.get("k_ms_min", 1.1)
    kms_max   = rock.get("k_ms_max", 1.3)
    kms_def   = rock.get("k_ms_default", 1.2)
    Rms_min   = rock.get("R_ms_min", 1.7e-5)
    Rms_max   = rock.get("R_ms_max", 2.5e-5)
    Rms_def   = rock.get("R_ms_default", 2.0e-5)

    with st.expander("📐 Константы профиля месторождения (из config.json)", expanded=False):
        st.caption(f"Профиль: **{cfg.get('field_name', '?')}**. "
                   "Изменение — в разделе «🛠 Настройки месторождения».")
        c1, c2, c3 = st.columns(3)
        c1.metric("α (kг.о = e^(−α·r))", f"{alpha:.3f}")
        c1.caption(rk.get("comment_alpha", ""))
        c2.metric("ρ_ск, кг/м³", f"{rho_min:.0f} … {rho_max:.0f}",
                  delta=f"def={rho_def:.0f}", delta_color="off")
        c3.metric("k_ms", f"{kms_min:.2f} … {kms_max:.2f}",
                  delta=f"def={kms_def:.2f}", delta_color="off")
        c1.metric("R_ms, кг/(м³·экв)",
                  f"{Rms_min:.2e} … {Rms_max:.2e}",
                  delta=f"def={Rms_def:.2e}", delta_color="off")
        c2.caption("Применять для слабокарбонатных песчаников Предкарпатья.")

    return {
        "alpha":   alpha,
        "rho_def": rho_def, "rho_min": rho_min, "rho_max": rho_max,
        "kms_def": kms_def, "kms_min": kms_min, "kms_max": kms_max,
        "Rms_def": Rms_def, "Rms_min": Rms_min, "Rms_max": Rms_max,
    }


def _render_inputs(cfg: dict):
    # дефолты из profile (для кнопки «ПРИМЕР»)
    rock = cfg.get("rock_properties", {})
    EXAMPLE["rho_sk"]   = rock.get("rho_sk_default", EXAMPLE["rho_sk"])
    EXAMPLE["k_ms_lab"] = rock.get("k_ms_default",   EXAMPLE["k_ms_lab"])
    EXAMPLE["R_ms"]     = rock.get("R_ms_default",   EXAMPLE["R_ms"])
    for k, v in _DEFAULTS.items():
        st.session_state.setdefault(f"v5_{k}", v)

    with st.expander("📥 Исходные данные — В.5", expanded=True):
        c1, c2, c3 = st.columns(3)
        st.session_state["v5_r_c"]  = c1.number_input("r_c, м — радиус скважины",
            value=float(st.session_state["v5_r_c"]), step=0.01, format="%.3f")
        st.session_state["v5_h_ef"] = c2.number_input("h_эф, м — эффективная толщина",
            value=float(st.session_state["v5_h_ef"]), step=1.0)
        st.session_state["v5_m0"]   = c3.number_input("m₀, % — начальная пористость",
            value=float(st.session_state["v5_m0"]), step=0.5)

        st.session_state["v5_k_vo"] = c1.number_input("k_в.о — охват по вертикали",
            value=float(st.session_state["v5_k_vo"]), step=0.01)
        st.session_state["v5_k_uf"] = c2.number_input("k_у.ф — участие пор в фильтрации",
            value=float(st.session_state["v5_k_uf"]), step=0.01)
        st.session_state["v5_k_v"]  = c3.number_input("k_в — коэф. вытеснения",
            value=float(st.session_state["v5_k_v"]), step=0.01)

        st.session_state["v5_rho_sk"] = c1.number_input("ρ_ск, кг/м³ — плотность скелета",
            value=float(st.session_state["v5_rho_sk"]), step=10.0)

        st.session_state["v5_k_ms_mode"] = c2.selectbox(
            "Способ задания k_ms",
            options=["напрямую", "по Δm_s"],
            index=0 if st.session_state["v5_k_ms_mode"] == "напрямую" else 1,
        )
        if st.session_state["v5_k_ms_mode"] == "напрямую":
            st.session_state["v5_k_ms_lab"] = c3.number_input(
                "k_ms (1.1…1.3)",
                value=float(st.session_state["v5_k_ms_lab"]), step=0.01)
        else:
            st.session_state["v5_dm_s"] = c3.number_input(
                "Δm_s, % — приращение пористости (лаб.)",
                value=float(st.session_state["v5_dm_s"]), step=0.1)

        st.session_state["v5_R_ms"]   = c1.number_input(
            "R_ms, кг/(м³·экв)  [(17…25)·10⁻⁶]",
            value=float(st.session_state["v5_R_ms"]), step=1e-6, format="%.2e")
        st.session_state["v5_C0_HCl"] = c2.number_input("C₀ HCl, % — концентрация",
            value=float(st.session_state["v5_C0_HCl"]), step=0.5)
        st.session_state["v5_q_acid"] = c3.number_input("q_к, м³/сут — расход СКР",
            value=float(st.session_state["v5_q_acid"]), step=10.0)
        st.session_state["v5_V_zad"]  = c1.number_input("V_ks, м³ — заданный объём закачки",
            value=float(st.session_state["v5_V_zad"]), step=1.0)

    return {k: st.session_state[f"v5_{k}"] for k in _DEFAULTS}


def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.5 — Параметры зоны растворения СКР")
    if btn_col.button("ПРИМЕР", key="btn_example_v5", type="secondary", use_container_width=True):
        rock = cfg.get("rock_properties", {})
        EXAMPLE["rho_sk"]   = rock.get("rho_sk_default", EXAMPLE["rho_sk"])
        EXAMPLE["k_ms_lab"] = rock.get("k_ms_default",   EXAMPLE["k_ms_lab"])
        EXAMPLE["R_ms"]     = rock.get("R_ms_default",   EXAMPLE["R_ms"])
        for k, v in EXAMPLE.items():
            st.session_state[f"v5_{k}"] = v
        st.rerun()


    render_precarpathian_constants(cfg)
    with st.expander("📖 Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `r_c` | радиус скважины | м |
| `r` | текущий радиус от оси скважины | м |
| `r_пр.р` | радиус продуктов реакции (глубина проникновения СКР) | м |
| `r_з.р` | радиус зоны растворения породы | м |
| `h_эф` | эффективная толщина пласта | м |
| `m_0` | начальная пористость | % |
| `m_c` | пористость после обработки СКР | % |
| `k_в.о` | коэффициент охвата пласта СКР по вертикали | дол.ед. |
| `k_у.ф` | коэффициент участия пор в фильтрации СКР (лаб.) | дол.ед. |
| `k_в` | коэффициент вытеснения пластовой жидкости КР (лаб.) | дол.ед. |
| `k_ms` | коэффициент возрастания пористости после СКО | – |
| `Δm_s` | приращение пористости в лаб. эксперименте | % |
| `A(r)` | вспомогательная функция в формуле (В.30) | – |
| `V_ks` | объём СКР, проникший на радиус `r` | м³ |
| `q_к` | расход (темп закачки) СКР | м³/сут |
| `t_u` | длительность закачивания СКР | мин |
| `ρ_ск` | плотность скелета породы | кг/м³ |
| `G_s` | масса растворённой породы | кг |
| `G_ms` | максимальная масса породы, растворимая в данном объёме СКР | кг |
| `C_ms` | массовая концентрация HCl в СКР (по табл. В.4) | кг/м³ |
| `DC_s` | потеря кислотности (90 % от `C_ms`) | кг/м³ |
| `R_ms` | средняя растворимость породы на единицу потери кислотности | кг/(м³·экв) |
| `C/C₀` | отношение текущей концентрации к начальной | – |
""")

    st.latex(r"V_{ks}=2\pi\,h_{\text{эф}}\,k_{\text{в.о}}\,k_{\text{у.ф}}\,k_{\text{в}}\,"
             r"m_0\bigl[e^{-0{,}1r_c}(0{,}1r_c+1)-e^{-0{,}1r}(0{,}1r+1)\bigr]\quad(B.31)")
    st.latex(r"G_s=\rho_{\text{ск}}V_{ks}(k_{ms}-1)\quad(B.34);\;\;"
             r"G_{ms}=0{,}9\,V_{ks}\,C_{ms}\,R_{ms}\quad(B.37)")

    _render_constants_block(cfg)
    inp = _render_inputs(cfg)
    res = solve(inp, cfg)
    df = res["df"]

    # --- сводные результаты ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("k_ms",          f"{res['k_ms']:.3f}")
    c2.metric("C_ms, кг/м³",   f"{res['C_ms']:.2f}")
    c3.metric("t_u, мин",      f"{res['t_u']:.1f}")
    c4.metric("Δm = m_c−m₀, %",f"{res['m_c']-res['m_0']:.2f}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("r_пр.р, м",     f"{res['r_pr_p']:.3f}")
    c2.metric("r_з.р, м",      f"{res['r_zr']:.3f}")
    c3.metric("G_ms, кг",      f"{res['G_ms']:.2f}")
    c4.metric("G_s(V_зад), кг",f"{res['G_s_zad']:.1f}")

    st.markdown(f"**Пористость после обработки:** m_c = k_ms·m₀ = "
                f"{res['k_ms']:.3f}·{res['m_0']:.2f} = **{res['m_c']:.2f} %** "
                f"(прирост Δm = {res['m_c']-res['m_0']:.2f} %).")

    # --- таблица В.7 ---
    with st.expander("📋 Таблица B.7 — A(r), V_ks(r), G_s(r)", expanded=False):
        st.dataframe(df.style.format({
            "r, м": "{:.2f}",
            "A(r)": "{:.6f}",
            "V_ks, м³": "{:.4f}",
            "G_s, кг": "{:.2f}",
        }), use_container_width=True)

    # --- график 1: V_ks(r) и G_s(r) ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["r, м"], y=df["V_ks, м³"],
                             name="V_ks(r), м³", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=df["r, м"], y=df["G_s, кг"]/1000.0,
                             name="G_s(r), т", mode="lines+markers", yaxis="y2"))
    fig.add_hline(y=res["V_zad"], line_dash="dash", line_color="red",
                  annotation_text=f"V_зад={res['V_zad']} м³")
    fig.add_vline(x=res["r_pr_p"], line_dash="dot", line_color="red",
                  annotation_text=f"r_пр.р={res['r_pr_p']:.2f} м")
    fig.add_vline(x=res["r_zr"],   line_dash="dot", line_color="green",
                  annotation_text=f"r_з.р={res['r_zr']:.2f} м")
    fig.update_layout(
        title="Развитие зоны растворения (рис. B.3)",
        xaxis_title="r, м",
        yaxis=dict(title="V_ks, м³"),
        yaxis2=dict(title="G_s, т", overlaying="y", side="right"),
        height=460,
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- график 2: профиль нейтрализации (прямоугольный) ---
    r_prof = np.linspace(res["df"]["r, м"].min(), res["df"]["r, м"].max(), 400)
    c_rel = np.where(r_prof <= res["r_zr"], 1.0, 0.0)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=r_prof, y=c_rel, mode="lines", name="C/C₀"))
    fig2.add_vline(x=res["r_zr"], line_dash="dot", line_color="green",
                   annotation_text=f"r_з.р={res['r_zr']:.2f} м")
    fig2.update_layout(
        title="Профиль нейтрализации СКР (прямоугольный)",
        xaxis_title="r, м", yaxis_title="C/C₀",
        yaxis=dict(range=[-0.05, 1.1]),
        height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.session_state["task_v5_result"] = res
    return res
