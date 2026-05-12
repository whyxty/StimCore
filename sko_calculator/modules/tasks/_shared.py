"""Общие UI-блоки, переиспользуемые задачами В.1–В.17."""
import streamlit as st


def render_precarpathian_constants(cfg: dict) -> None:
    """Красный информационный блок с нормативными константами Предкарпатья.

    Используется в шапке каждой задачи СКО, чтобы пользователь видел
    пороговые значения (В.2–В.7) прямо рядом с расчётом.
    """
    sel = cfg.get("well_selection", {}) or {}
    m_min = sel.get("m_pr_min", 0)
    m_max = sel.get("m_pr_max", 0)
    h_pr = sel.get("h_pr_min", 0)
    k_s = sel.get("k_s_np", 0)
    C_k = sel.get("C_k_pr", 0)
    try:
        k_msg = float(k_s) ** 2
    except Exception:
        k_msg = 0.0

    st.markdown(
        f"""
<div style="border:1px solid #e74c3c; border-radius:6px; padding:10px 16px; margin-bottom:12px;">
<b style="color:#e74c3c;">Константы Предкарпатья (нормативные пороговые значения)</b><br><br>
<span style="color:#e74c3c;">
&bull; <b>m<sub>гр</sub> = {m_min}–{m_max} %</b> &nbsp;—&nbsp; граничная пористость коллектора (В.2)<br>
&bull; <b>h<sub>пр</sub> = {h_pr} м</b> &nbsp;—&nbsp; минимальная толщина поглощающего пласта (В.3)<br>
&bull; <b>k<sub>ms.пр</sub> = {k_s} </b> &nbsp;—&nbsp; минимальный прирост пористости после СКО (В.4)<br>
&bull; <b>k<sub>mg.пр</sub> = {k_s} </b> &nbsp;—&nbsp; минимальный прирост пористости после ГКО (В.5)<br>
&bull; <b>k<sub>msg.пр</sub> = {k_msg:.2f}</b> &nbsp;—&nbsp; суммарный прирост пористости (В.6)<br>
&bull; <b>C<sub>к.пр</sub> = {C_k} %</b> &nbsp;—&nbsp; минимальная карбонатность для применения СКО (В.7)
</span>
</div>
""",
        unsafe_allow_html=True,
    )
