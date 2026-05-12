"""Общие UI-блоки, переиспользуемые задачами В.1–В.17."""
import streamlit as st


# Какие нормативные пороги относятся к какой задаче.
# Ключи строки в блоке: m, h, k_ms, k_mg, k_msg, C_k.
# В.1 — обоснование выбора скважины: проверяет все пороги сразу.
_TASK_KEYS: dict[str, list[str]] = {
    "В.1": ["m", "h", "k_ms", "k_mg", "k_msg", "C_k"],
    "В.2": ["m"],
    "В.3": ["h"],
    "В.4": ["k_ms"],
    "В.5": ["k_mg"],
    "В.6": ["k_msg"],
    "В.7": ["C_k"],
}


def render_precarpathian_constants(cfg: dict, task: str | None = None) -> None:
    """Красный информационный блок с нормативными константами Предкарпатья.

    Параметр ``task`` (например ``"В.2"``) ограничивает блок только теми
    порогами, которые реально проверяются в этой задаче. Если задача
    не использует пороговые константы, блок не выводится вовсе.
    """
    keys = _TASK_KEYS.get(task or "В.1", [])
    if not keys:
        return

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

    rows = {
        "m":    f"&bull; <b>m<sub>гр</sub> = {m_min}–{m_max} %</b> &nbsp;—&nbsp; граничная пористость коллектора (В.2)",
        "h":    f"&bull; <b>h<sub>пр</sub> = {h_pr} м</b> &nbsp;—&nbsp; минимальная толщина поглощающего пласта (В.3)",
        "k_ms": f"&bull; <b>k<sub>ms.пр</sub> = {k_s}</b> &nbsp;—&nbsp; минимальный прирост пористости после СКО (В.4)",
        "k_mg": f"&bull; <b>k<sub>mg.пр</sub> = {k_s}</b> &nbsp;—&nbsp; минимальный прирост пористости после ГКО (В.5)",
        "k_msg":f"&bull; <b>k<sub>msg.пр</sub> = {k_msg:.2f}</b> &nbsp;—&nbsp; суммарный прирост пористости (В.6)",
        "C_k":  f"&bull; <b>C<sub>к.пр</sub> = {C_k} %</b> &nbsp;—&nbsp; минимальная карбонатность для применения СКО (В.7)",
    }
    body = "<br>".join(rows[k] for k in keys)

    st.markdown(
        f"""
<div style="border:1px solid #e74c3c; border-radius:6px; padding:10px 16px; margin-bottom:12px;">
<b style="color:#e74c3c;">Константы Предкарпатья (нормативные пороговые значения)</b><br><br>
<span style="color:#e74c3c;">
{body}
</span>
</div>
""",
        unsafe_allow_html=True,
    )
