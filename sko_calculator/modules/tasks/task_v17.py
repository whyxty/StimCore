"""Задача В.17 — расчёт количества реагентов для приготовления кислотного раствора.

Принятые решения:
1. Только СКО — HF и табл. В.27 не используются.
2. V_втс — два параллельных столбца расчёта: «без запаса» (В.56) и «с запасом» (В.57).
3. ГКР не считаем.
4. Концентрации ингибитора/стабилизатора/ПАВ из В.11 — по товарной массе.
5. То же для ПАВ.
6. Товарная HCl: два параллельных варианта 27 % и 31 % (по табл. В.29).
7. Уксусная кислота — как добавка по формуле (В.93).
8. Полный итог сохраняется в session_state["task_v17_result"].

Формулы:
    V_т.к = 10·C_з·ρ_з / C_т.п                    (В.92, жидкая кислота)
    V_т.п = 1000·C_з.п·ρ_з / (C_т.п·ρ_т.п)        (В.93, добавка)
    V_т.ж = 1000 − Σ V_r                          (В.94, растворитель)
    G_r   = V_r·R_r·V_k / 1000                    (В.95, масса в т)
"""
import numpy as np
import pandas as pd
import streamlit as st

from ._shared import render_precarpathian_constants


EXAMPLE = {
    "C_inh":   0.3,
    "C_stab":  0.5,
    "C_surf":  0.3,
    "C_buf":   0.3,
    "buf_pav": "ОП-10",
}


# ───── табл. В.26 — соляная кислота при 20 °C (заданные концентрации в КР) ─────
TABLE_B26_HCl = {
    # C_HCl, % : (ρ, г/см³;  активная часть HCl, г/см³)
    8:  {"rho": 1.038, "active": 0.083},
    10: {"rho": 1.047, "active": 0.105},
    12: {"rho": 1.057, "active": 0.127},
    15: {"rho": 1.073, "active": 0.163},
    20: {"rho": 1.098, "active": 0.220},
    25: {"rho": 1.125, "active": 0.282},
    30: {"rho": 1.149, "active": 0.345},
}

# ───── табл. В.29 — товарная HCl (опечатка в исходнике 1.55 для 31 % исправлена на 1.155) ─────
TOVAR_HCl = {
    27: {"rho_t": 1.14,  "active_g_cm3": 0.31},
    31: {"rho_t": 1.155, "active_g_cm3": 0.35},
}

# ───── табл. В.29 — реагенты (товарная конц. %, товарная плотность кг/л=т/м³) ─────
REAGENT_TOVAR = {
    "Катапин КИ-1":               {"C_t": 95.0,  "rho_t": 1.05},
    "Катапин + уротропин (1:1)":  {"C_t": 95.0,  "rho_t": 1.05},  # для смеси берём по основному
    "И-2-А":                      {"C_t": 100.0, "rho_t": 1.04},
    "Б2":                         {"C_t": 100.0, "rho_t": 1.03},
    "Уксусная кислота":           {"C_t": 60.0,  "rho_t": 1.07},
    "Лимонная кислота":           {"C_t": 100.0, "rho_t": 1.54},
    "Сульфат натрия":             {"C_t": 100.0, "rho_t": 2.63},
    "Уксусная + лимонная кислота":{"C_t": 60.0,  "rho_t": 1.07},  # доминирует уксусная
    "КРАСТ":                      {"C_t": 100.0, "rho_t": 1.25},
    "ОП-10":                      {"C_t": 100.0, "rho_t": 1.05},
    "Превоцел W-OF-7":            {"C_t": 99.0,  "rho_t": 1.10},
    "превоцел W-OF-7":            {"C_t": 99.0,  "rho_t": 1.10},
    "ОП-7":                       {"C_t": 100.0, "rho_t": 1.05},
    "ОЖК":                        {"C_t": 100.0, "rho_t": 1.00},
    "Сапал":                      {"C_t": 100.0, "rho_t": 1.05},
    "Сульфанол":                  {"C_t": 38.0,  "rho_t": 1.17},
    "АНП-2":                      {"C_t": 100.0, "rho_t": 1.05},
    "Карпатол":                   {"C_t": 100.0, "rho_t": 0.99},
    "МЛ-80":                      {"C_t": 100.0, "rho_t": 1.05},
    "Прогалит":                   {"C_t": 100.0, "rho_t": 1.10},
    "Неонол":                     {"C_t": 99.0,  "rho_t": 1.04},
    "неонол":                     {"C_t": 99.0,  "rho_t": 1.04},
    "ТЕАС-М":                     {"C_t": 100.0, "rho_t": 1.10},
    "Дисольван":                  {"C_t": 100.0, "rho_t": 1.09},
    "диссольван":                 {"C_t": 100.0, "rho_t": 1.09},
    "проксанол":                  {"C_t": 100.0, "rho_t": 1.05},
    "проксамин":                  {"C_t": 100.0, "rho_t": 1.05},
    "КАУФЭ-14":                   {"C_t": 100.0, "rho_t": 1.05},
}


def get_HCl_props(C_HCl_pct: float) -> dict:
    """Линейная интерполяция табл. В.26."""
    keys = sorted(TABLE_B26_HCl.keys())
    rho_vals = [TABLE_B26_HCl[k]["rho"] for k in keys]
    return {"rho": float(np.interp(C_HCl_pct, keys, rho_vals))}


def get_reagent_tovar(name: str) -> dict:
    """Достаёт товарные данные реагента (с защитой от пробелов/регистра)."""
    if name in REAGENT_TOVAR:
        return REAGENT_TOVAR[name]
    # пробуем без учёта регистра
    for k, v in REAGENT_TOVAR.items():
        if k.lower() == name.lower():
            return v
    # неизвестный реагент — фолбэк
    return {"C_t": 100.0, "rho_t": 1.05, "_unknown": True}


# ───── формулы ─────
def V_tk(C_z_pct: float, rho_z_gcm3: float, C_tp_active_gcm3: float) -> float:
    """(В.92) — удельный объём жидкой кислоты, л/м³."""
    return 10.0 * C_z_pct * rho_z_gcm3 / C_tp_active_gcm3


def V_tp(C_zp_pct: float, rho_z_gcm3: float, C_tp_pct: float, rho_tp_kgl: float) -> float:
    """(В.93) — удельный объём добавки, л/м³."""
    return 1000.0 * C_zp_pct * rho_z_gcm3 / (C_tp_pct * rho_tp_kgl)


def mass_t(V_ud_lm3: float, rho_tp_kgl: float, V_k_m3: float) -> float:
    """(В.95) — масса реагента, т."""
    return V_ud_lm3 * rho_tp_kgl * V_k_m3 / 1000.0


# ───── основной расчёт ─────
def build_fluid(*, name: str, V_k_m3: float, rho_base_gcm3: float,
                base_name: str, base_rho_t: float,
                components: list) -> pd.DataFrame:
    """
    components — список dict:
        {"role": "acid|additive", "name": str, "C_z": %, ...}
        для acid: C_tp_active (г/см³), rho_tp (кг/л)
        для additive: C_tp (%), rho_tp (кг/л)
    """
    rows = []
    sum_ud = 0.0
    for c in components:
        if c["role"] == "acid":
            V_ud = V_tk(c["C_z"], rho_base_gcm3, c["C_tp_active"])
        else:
            V_ud = V_tp(c["C_z"], rho_base_gcm3, c["C_tp"], c["rho_tp"])
        sum_ud += V_ud
        rows.append({
            "Реагент":        c["name"],
            "C_зад, %":       c["C_z"],
            "Уд. объём, л/м³": V_ud,
            "Товарный объём, л": V_ud * V_k_m3,
            "Масса, т":       mass_t(V_ud, c["rho_tp"], V_k_m3),
        })
    # растворитель (вода/нефть-основа)
    V_solvent = 1000.0 - sum_ud
    rows.append({
        "Реагент":         base_name,
        "C_зад, %":        100.0,
        "Уд. объём, л/м³": V_solvent,
        "Товарный объём, л": V_solvent * V_k_m3,
        "Масса, т":        mass_t(V_solvent, base_rho_t, V_k_m3),
    })
    df = pd.DataFrame(rows)
    df.attrs["name"] = name
    df.attrs["V_k_m3"] = V_k_m3
    df.attrs["sum_ud"] = sum_ud + V_solvent
    df.attrs["valid"] = sum_ud <= 1000.0
    return df


def solve(*, V_ks: float, V_prd: float, V_vts_56: float, V_vts_57: float,
          C_HCl_skr: float, tovar_HCl_pct: int,
          inhibitor: dict | None,
          stabilizer: dict | None,
          surfactant: dict | None,
          buffer_pav_name: str,
          C_inhibitor_pct: float,
          C_stabilizer_pct: float,
          C_surfactant_pct: float,
          C_buffer_pav_pct: float) -> dict:

    # плотность СКР заданной концентрации (табл. В.26)
    rho_skr = get_HCl_props(C_HCl_skr)["rho"]
    tov_HCl = TOVAR_HCl[tovar_HCl_pct]
    rho_HCl_t = tov_HCl["rho_t"]

    # компоненты СКР
    skr_comp = [{
        "role": "acid", "name": f"HCl ({tovar_HCl_pct} % товарная)",
        "C_z": C_HCl_skr,
        "C_tp_active": tov_HCl["active_g_cm3"],
        "rho_tp": rho_HCl_t,
    }]
    if inhibitor:
        ti = get_reagent_tovar(inhibitor["name"])
        skr_comp.append({"role": "additive", "name": f"Ингибитор: {inhibitor['name']}",
                         "C_z": C_inhibitor_pct, "C_tp": ti["C_t"], "rho_tp": ti["rho_t"]})
    if stabilizer:
        ts = get_reagent_tovar(stabilizer["name"])
        skr_comp.append({"role": "additive", "name": f"Стабилизатор: {stabilizer['name']}",
                         "C_z": C_stabilizer_pct, "C_tp": ts["C_t"], "rho_tp": ts["rho_t"]})
    if surfactant:
        tp = get_reagent_tovar(surfactant["name"])
        skr_comp.append({"role": "additive", "name": f"ПАВ: {surfactant['name']}",
                         "C_z": C_surfactant_pct, "C_tp": tp["C_t"], "rho_tp": tp["rho_t"]})

    df_skr = build_fluid(name="СКР", V_k_m3=V_ks,
                         rho_base_gcm3=rho_skr,
                         base_name="Вода техническая", base_rho_t=1.00,
                         components=skr_comp)

    # буферные жидкости — вода + ПАВ
    tb = get_reagent_tovar(buffer_pav_name)
    buffer_comp = [{"role": "additive", "name": f"ПАВ: {buffer_pav_name}",
                    "C_z": C_buffer_pav_pct, "C_tp": tb["C_t"], "rho_tp": tb["rho_t"]}]

    df_prd = build_fluid(name="Продавочная", V_k_m3=V_prd,
                         rho_base_gcm3=1.00,
                         base_name="Вода техническая", base_rho_t=1.00,
                         components=buffer_comp)
    df_vts_56 = build_fluid(name="Вытесняющая (без запаса)", V_k_m3=V_vts_56,
                            rho_base_gcm3=1.00,
                            base_name="Вода техническая", base_rho_t=1.00,
                            components=buffer_comp)
    df_vts_57 = build_fluid(name="Вытесняющая (с запасом)", V_k_m3=V_vts_57,
                            rho_base_gcm3=1.00,
                            base_name="Вода техническая", base_rho_t=1.00,
                            components=buffer_comp)

    return {
        "rho_skr":   rho_skr,
        "tovar_HCl": tovar_HCl_pct,
        "skr":       df_skr,
        "prd":       df_prd,
        "vts_56":    df_vts_56,
        "vts_57":    df_vts_57,
    }


def _shopping_list(*dfs: pd.DataFrame) -> pd.DataFrame:
    """Сводный список покупок: суммирует массы и объёмы по реагентам через все жидкости."""
    rows = []
    for df in dfs:
        for _, r in df.iterrows():
            rows.append({
                "Реагент": r["Реагент"],
                "Объём, л": r["Товарный объём, л"],
                "Масса, т": r["Масса, т"],
            })
    out = pd.DataFrame(rows).groupby("Реагент", as_index=False).sum()
    return out.sort_values("Масса, т", ascending=False)


# ───── UI ─────
def render(cfg: dict):
    title_col, btn_col = st.columns([5, 1])
    title_col.subheader("Задача В.17 — Расчёт количества реагентов")
    if btn_col.button("ПРИМЕР", key="btn_example_v17", type="secondary", use_container_width=True):
        for k, v in EXAMPLE.items():
            st.session_state[f"v17_{k}"] = v
        st.rerun()


    render_precarpathian_constants(cfg, task="В.17")
    with st.expander("Обозначения", expanded=False):
        st.markdown("""
| Символ | Значение | Ед. |
|---|---|---|
| `V_т.к` | удельный объём товарной жидкой кислоты | л/м³ |
| `V_т.п` | удельный объём товарной добавки (ингибитор/стаб./ПАВ) | л/м³ |
| `V_т.ж` | удельный объём растворителя (вода) | л/м³ |
| `G_r` | масса реагента на полный объём раствора | т |
| `C_з` | заданная концентрация кислоты в КР | % |
| `C_з.п` | заданная концентрация добавки (по товарной массе) | % |
| `ρ_з` | плотность КР заданной концентрации (табл. В.26) | г/см³ |
| `C_т.п` | для жидкой кислоты — активная часть, г/см³; для добавки — % | – |
| `ρ_т.п` | товарная плотность реагента (табл. В.29) | кг/л |
| `V_k` | объём готового раствора (СКР, продавочной, вытесняющей) | м³ |
""")

    st.latex(r"V_{\text{т.к}} = \dfrac{10\,C_з\,\rho_з}{C_{\text{т.п}}}\quad(B.92)")
    st.latex(r"V_{\text{т.п}} = \dfrac{1000\,C_{з.п}\,\rho_з}{C_{\text{т.п}}\,\rho_{\text{т.п}}}\quad(B.93)")
    st.latex(r"V_{\text{т.ж}} = 1000-\sum V_r\quad(B.94);\;\;G_r=V_r\,R_r\,V_k/1000\quad(B.95)")

    # ───── зависимости ─────
    v10 = st.session_state.get("task_v10_result")
    v11 = st.session_state.get("task_v11_result")

    missing = []
    if not v10: missing.append("**В.10** (нужны V_ks, V_прд, V_втс)")
    if not v11: missing.append("**В.11** (нужны состав КР и ПАВ для буферов)")
    if missing:
        st.warning("Сначала рассчитайте: " + ", ".join(missing))
        return None

    if v11.get("y_HF", 0) > 0:
        st.warning("В В.11 выбрана ГКО (y > 0). Этот модуль считает **только СКО** — "
                   "ГКР игнорируется, расчёт ведётся для СКР.")

    V_ks      = float(v10["V_ks"])
    V_prd     = float(v10["V_prd"])
    V_vts_56  = float(v10["V_vts_56"])
    V_vts_57  = float(v10["V_vts_57"])
    C_HCl_skr = float(v11["skr"]["HCl_pct"])

    # имена и концентрации добавок (трактуем как товарную массу)
    inhibitor  = v11.get("inhibitor")
    stabilizer = v11.get("stabilizer")
    surf       = v11.get("surfactant")
    surf_obj   = None
    surf_name  = None
    if surf and surf.get("PAV_list"):
        surf_name = surf["PAV_list"][0]
        surf_obj  = {"name": surf_name}

    st.info(
        f"**Из В.10:** V_ks = {V_ks:.3f} м³, V_прд = {V_prd:.3f} м³, "
        f"V_втс (без зап.) = {V_vts_56:.3f} м³, V_втс (с зап.) = {V_vts_57:.3f} м³.  \n"
        f"**Из В.11:** {v11['type']}; СКР {C_HCl_skr:.0f} % HCl; "
        f"ингибитор: {inhibitor['name'] if inhibitor else '—'}; "
        f"стабилизатор: {stabilizer['name'] if stabilizer else '—'}; "
        f"ПАВ в КР: {surf_name or '—'}."
    )

    # ───── ввод концентраций (по товарной массе) и товарной HCl ─────
    _DEF = {
        "C_inh":   0.0,
        "C_stab":  0.0,
        "C_surf":  0.0,
        "C_buf":   0.0,
        "buf_pav": surf_name or "ОП-10",
    }
    for k, v in _DEF.items():
        st.session_state.setdefault(f"v17_{k}", v)

    with st.expander("Концентрации добавок (по товарной массе)", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        st.session_state["v17_C_inh"] = c1.number_input(
            "Ингибитор, %",
            value=float(st.session_state["v17_C_inh"]), step=0.05, format="%.2f")
        st.session_state["v17_C_stab"] = c2.number_input(
            "Стабилизатор, %",
            value=float(st.session_state["v17_C_stab"]), step=0.05, format="%.2f")
        st.session_state["v17_C_surf"] = c3.number_input(
            "ПАВ в КР, %",
            value=float(st.session_state["v17_C_surf"]), step=0.05, format="%.2f")
        st.session_state["v17_C_buf"] = c4.number_input(
            "ПАВ в буферах, %",
            value=float(st.session_state["v17_C_buf"]), step=0.05, format="%.2f")

        all_pavs = [surf_name or "ОП-10"] + [
            n for n in REAGENT_TOVAR
            if n not in (surf_name or "") and any(p in n for p in
                ("ОП-10", "ОП-7", "Превоцел", "превоцел", "Неонол", "неонол",
                 "Сульфанол", "Дисольван", "диссольван"))
        ]
        all_pavs = list(dict.fromkeys(all_pavs))    # uniq, сохраняя порядок
        idx = all_pavs.index(st.session_state["v17_buf_pav"]) \
              if st.session_state["v17_buf_pav"] in all_pavs else 0
        st.session_state["v17_buf_pav"] = st.selectbox(
            "ПАВ для продавочной и вытесняющей жидкостей",
            all_pavs, index=idx,
            help="По умолчанию — тот же, что в КР (или ОП-10, если в КР ПАВ не выбран)")

    # ───── расчёт по двум товарным HCl (27 и 31 %) ─────
    results = {}
    for tov in (27, 31):
        results[tov] = solve(
            V_ks=V_ks, V_prd=V_prd, V_vts_56=V_vts_56, V_vts_57=V_vts_57,
            C_HCl_skr=C_HCl_skr, tovar_HCl_pct=tov,
            inhibitor=inhibitor, stabilizer=stabilizer, surfactant=surf_obj,
            buffer_pav_name=st.session_state["v17_buf_pav"],
            C_inhibitor_pct=st.session_state["v17_C_inh"],
            C_stabilizer_pct=st.session_state["v17_C_stab"],
            C_surfactant_pct=st.session_state["v17_C_surf"],
            C_buffer_pav_pct=st.session_state["v17_C_buf"],
        )

    rho_skr = results[27]["rho_skr"]
    st.markdown(f"**Плотность СКР {C_HCl_skr:.0f} % HCl** (по табл. В.26): "
                f"ρ_з = **{rho_skr:.3f} г/см³**")

    # ───── вывод по двум вариантам товарной HCl ─────
    fmt = {"C_зад, %": "{:.3f}",
           "Уд. объём, л/м³": "{:.3f}",
           "Товарный объём, л": "{:.2f}",
           "Масса, т": "{:.4f}"}

    for tov, res in results.items():
        st.markdown(f"## Вариант: товарная HCl **{tov} %**")

        # СКР
        with st.expander(f"🟦 СКР — V_k = {V_ks:.3f} м³", expanded=True):
            st.dataframe(res["skr"].style.format(fmt),
                         use_container_width=True, hide_index=True)
            st.caption(f"Σ удельных объёмов = {res['skr'].attrs['sum_ud']:.1f} л/м³ "
                       + ("✓" if res['skr'].attrs['valid'] else "> 1000!"))

        # Продавочная
        with st.expander(f"🟨 Продавочная жидкость — V_k = {V_prd:.3f} м³", expanded=False):
            st.dataframe(res["prd"].style.format(fmt),
                         use_container_width=True, hide_index=True)

        # Вытесняющая (оба варианта)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"🟧 **Вытесняющая (без запаса)** — V_k = {V_vts_56:.3f} м³")
            st.dataframe(res["vts_56"].style.format(fmt),
                         use_container_width=True, hide_index=True)
        with c2:
            st.markdown(f"🟥 **Вытесняющая (с запасом)** — V_k = {V_vts_57:.3f} м³")
            st.dataframe(res["vts_57"].style.format(fmt),
                         use_container_width=True, hide_index=True)

        # сводный список покупок (по сценарию «с запасом»)
        st.markdown(f"#### 🛒 Сводный список реагентов (вариант «с запасом»)")
        shop = _shopping_list(res["skr"], res["prd"], res["vts_57"])
        st.dataframe(shop.style.format({"Объём, л": "{:.2f}", "Масса, т": "{:.4f}"}),
                     use_container_width=True, hide_index=True)

    # ───── сохранение ─────
    st.session_state["task_v17_result"] = {
        "C_HCl_skr": C_HCl_skr,
        "tovar_HCl_options": list(results.keys()),
        "by_tovar_HCl": {
            tov: {
                "skr":      res["skr"].to_dict("records"),
                "prd":      res["prd"].to_dict("records"),
                "vts_56":   res["vts_56"].to_dict("records"),
                "vts_57":   res["vts_57"].to_dict("records"),
            }
            for tov, res in results.items()
        }
    }
    return results
