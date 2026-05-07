"""Связующий слой между API и существующими solve()-функциями старого Streamlit-проекта.

Задача: вызвать математику задач В.1–В.11, В.17 из sko_calculator/modules/tasks/*.py
и вернуть JSON-сериализуемые dict'ы. Streamlit-зависимости (st.*) не используются —
вызываются ТОЛЬКО pure-функции solve().
"""
import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Подключаем путь до старого проекта, чтобы импортировать solve() из tasks/
_ROOT = Path(__file__).resolve().parents[2]
_LEGACY = _ROOT / "sko_calculator"
if str(_LEGACY) not in sys.path:
    sys.path.insert(0, str(_LEGACY))


def _to_serializable(obj):
    """Рекурсивно превращает pandas/numpy/typing-объекты в JSON-сериализуемые."""
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict("records")
    if isinstance(obj, pd.Series):
        return obj.to_list()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if (math.isnan(v) or math.isinf(v)) else v
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serializable(v) for v in obj]
    return obj


# ───────── В.1: выбор скважины (полная информация) ─────────
def calc_v1(inp: dict, cfg: dict) -> dict:
    from modules.tasks.task_v1 import solve as solve_v1
    payload = {
        "K_f":        inp["K_f"],
        "K_pot":      inp["K_pot"],
        "h_ef":       inp["h_ef"],
        "h_pta":      inp["h_pta"],
        "C_k":        inp["C_k"],
        "k_ms_lab":   inp["k_ms_lab"],
        "k_mg_lab":   inp["k_mg_lab"],
        "m_gr":       cfg.get("well_selection", {}).get("m_pr_default", 8),
        "layers_table": inp.get("layers", []),
    }
    return _to_serializable(solve_v1(payload, cfg))


# ───────── В.2: выбор скважины (ограниченная информация) ─────────
def calc_v2(inp: dict, cfg: dict) -> dict:
    from modules.tasks.task_v2 import solve as solve_v2
    payload = {
        "Q_f":        inp["Q_f"],
        "q_inj":      inp["q_inj"],
        "p_pl":       inp["p_pl"],
        "H":          inp["H"],
        "C_gl":       inp["C_gl"],
        "h_ef":       inp["h_ef"],
        "layers_table": inp.get("layers", []),
    }
    return _to_serializable(solve_v2(payload, cfg))


# ───────── В.3: расход и давление при нагнетании ─────────
def calc_v3(inp: dict, cfg: dict) -> dict:
    from modules.tasks.task_v3 import solve as solve_v3
    payload = {
        "H":          inp["H"],
        "p_opr":      inp["p_opr"],
        "rho_fluid":  inp["rho_fluid"],
        "well_type":  inp["well_type"],
        "q_k":        inp["q_k"],
        "p_k":        inp["p_k"],
        "use_v20":    inp.get("use_v20", False),
    }
    return _to_serializable(solve_v3(payload, cfg))


# ───────── В.5: зона растворения ─────────
def calc_v5(inp: dict, cfg: dict) -> dict:
    from modules.tasks.task_v5 import solve as solve_v5
    payload = {
        "r_c":  inp["r_c"], "h_ef": inp["h_ef"], "m0": inp["m0"],
        "k_vo": inp["k_vo"], "k_uf": inp["k_uf"], "k_v": inp["k_v"],
        "rho_sk": inp["rho_sk"], "k_ms_mode": inp.get("k_ms_mode", "напрямую"),
        "k_ms_lab": inp["k_ms_lab"], "dm_s": inp.get("dm_s", 2.8),
        "R_ms": inp["R_ms"], "C0_HCl": inp["C0_HCl"],
        "q_acid": inp["q_k"], "V_zad": inp["V_zad"],
    }
    return _to_serializable(solve_v5(payload, cfg))


# ───────── В.6: растворённая порода по составу ─────────
def calc_v6(inp: dict, cfg: dict, v5_res: dict) -> dict:
    from modules.tasks.task_v6 import solve as solve_v6
    df_v5 = pd.DataFrame(v5_res["df"])
    res = solve_v6(
        {"C_gl": inp["C_gl"], "C_k": inp["C_k"], "rho_p": inp["rho_p"]},
        cfg,
        m0=inp["m0"],
        V_profile=df_v5,
        V_zad=inp["V_zad"],
        k_ms_ref=v5_res["k_ms"],
        rho_sk_ref=inp["rho_sk"],
    )
    return _to_serializable(res)


# ───────── В.7: изменение пористости (косв.) ─────────
def calc_v7(inp: dict, cfg: dict, v5_res: dict) -> dict:
    from modules.tasks.task_v7 import solve as solve_v7
    diss = cfg.get("dissolution_coefficients", {})
    res = solve_v7(
        C_gl=inp["C_gl"], C_k=inp["C_k"],
        rho_p=inp["rho_p"], rho_sk=inp["rho_sk"],
        m0=inp["m0"], V_zad=inp["V_zad"],
        V_profile=pd.DataFrame(v5_res["df"]),
        a=diss.get("a_clay", 0.25), b=diss.get("b_carbonate", 0.5),
        k_ms_v5=v5_res["k_ms"],
    )
    return _to_serializable(res)


# ───────── В.8: проницаемость ─────────
def calc_v8(inp: dict, cfg: dict, k_ms: float, k_mg: float) -> dict:
    from modules.tasks.task_v8 import solve as solve_v8
    res = solve_v8(
        KL_key=inp["KL"], m0=inp["m0"], C_k=inp["C_k"],
        k_ms=k_ms, k_mg=k_mg,
        k0_override=(inp["k0_user"] if inp.get("k0_use_override") else None),
        cfg=cfg,
    )
    return _to_serializable(res)


# ───────── В.9: эффективность ─────────
def calc_v9(inp: dict, v5_res: dict, v8_res: dict) -> dict:
    from modules.tasks.task_v9 import solve as solve_v9
    # eps_ot — упрощённо: считаем по слоям, помеченным treat=True
    layers = inp.get("layers") or []
    eps_obr = sum(L.get("h_ef", 0) * L.get("k0", 0) for L in layers if L.get("treat"))
    eps_skv = sum(L.get("h_ef", 0) * L.get("k0", 0) for L in layers) or 1.0
    eps_ot  = eps_obr / eps_skv

    res = solve_v9(
        r_c=v5_res["df"][0]["r, м"] if v5_res["df"] else inp["r_c"],
        r_zr=v5_res["r_zr"], r_pr=v5_res["r_pr_p"], r_k=inp["r_k"],
        k0=v8_res["k0"], k_s=v8_res["ks"],
        Q_f=inp["Q_f"], eps_ot=eps_ot,
        T_n=inp["T_n"], rho_n_kgm3=inp["rho_n"], W_0=inp["W_0"],
        C_n=inp["C_n"], S_n=inp["S_n"], Z_ko=inp["Z_ko"],
        use_eps_ot=inp["use_eps"],
    )
    res["eps_ot_calc"] = eps_ot
    return _to_serializable(res)


# ───────── В.10: продавочная и вытесняющая ─────────
def calc_v10(inp: dict, v5_res: dict) -> dict:
    """Реализуем формулы (В.56)/(В.57)/(В.58) напрямую — task_v10 в Streamlit-проекте отдельный."""
    # V_зр — V_ks при r=r_зр (по таблице/интерполяцией)
    rs = [row["r, м"] for row in v5_res["df"]]
    Vs = [row["V_ks, м³"] for row in v5_res["df"]]
    V_zr = float(np.interp(v5_res["r_zr"], rs, Vs))
    V_ks_zad = inp["V_zad"]

    V_vts_56 = 1.2 * V_zr
    V_vts_57 = 0.3 * V_ks_zad

    # (В.58) с поправкой: D_к² − d_нар² для кольцевого пространства
    d_in  = inp["d_in_NKT"]
    d_out = inp["d_out_NKT"]
    D_k   = inp["D_k"]
    H_no  = inp["H_no"]
    H_vo  = inp["H_vo"]
    V_prd = 0.785 * (d_in**2 * H_no + (D_k**2 - d_out**2) * (H_no - H_vo))

    return {
        "V_ks":      V_ks_zad,
        "V_zr":      V_zr,
        "V_prd":     V_prd,
        "V_vts_56":  V_vts_56,
        "V_vts_57":  V_vts_57,
        "V_total_56": V_ks_zad + V_prd + V_vts_56,
        "V_total_57": V_ks_zad + V_prd + V_vts_57,
        "t_total_56": (1440.0 * (V_ks_zad + V_prd + V_vts_56)) / inp["q_k"] if inp["q_k"] else 0.0,
        "t_total_57": (1440.0 * (V_ks_zad + V_prd + V_vts_57)) / inp["q_k"] if inp["q_k"] else 0.0,
    }


# ───────── В.11: рецептура ─────────
def calc_v11(inp: dict) -> dict:
    from modules.tasks.task_v11 import solve as solve_v11
    res = solve_v11(
        C_k=inp["C_k"], k0=inp["k0_user"] if inp.get("k0_use_override") else 0.05,
        N_ko=int(inp["N_ko"]), T_pl=inp["T_pl"], Fe3=inp["Fe3"],
        W_vn=int(inp["W_vn"]),
        N_as=inp["N_as"], N_sm=inp["N_sm"], N_nf=inp["N_nf"],
        C_HCl_pct=inp["HCl"], C_HF_pct=inp["HF"],
        ratio_SKR_GKR=inp["ratio_skr_gkr"],
    )
    return _to_serializable(res)


# ───────── В.17: количество реагентов ─────────
def calc_v17(inp: dict, v10_res: dict, v11_res: dict) -> dict:
    from modules.tasks.task_v17 import solve as solve_v17
    surf_obj = None
    surf_name = None
    if v11_res.get("surfactant"):
        pav_list = v11_res["surfactant"].get("PAV_list") or []
        if pav_list:
            surf_name = pav_list[0]
            surf_obj  = {"name": surf_name}

    out = {}
    for tov in inp.get("tovar_HCl_options", [27, 31]):
        res = solve_v17(
            V_ks=v10_res["V_ks"], V_prd=v10_res["V_prd"],
            V_vts_56=v10_res["V_vts_56"], V_vts_57=v10_res["V_vts_57"],
            C_HCl_skr=inp["HCl"], tovar_HCl_pct=int(tov),
            inhibitor=v11_res.get("inhibitor"),
            stabilizer=v11_res.get("stabilizer"),
            surfactant=surf_obj,
            buffer_pav_name=surf_name or "ОП-10",
            C_inhibitor_pct=inp["C_inh"],
            C_stabilizer_pct=inp["C_stab"],
            C_surfactant_pct=inp["C_surf"],
            C_buffer_pav_pct=inp["C_buf"],
        )
        out[str(tov)] = {
            "rho_skr":    res["rho_skr"],
            "tovar_HCl":  res["tovar_HCl"],
            "skr":        _to_serializable(res["skr"]),
            "prd":        _to_serializable(res["prd"]),
            "vts_56":     _to_serializable(res["vts_56"]),
            "vts_57":     _to_serializable(res["vts_57"]),
        }
    return out


# ───────── главная связка ─────────
def calc_all(inp: dict, cfg: dict) -> dict:
    """Запускает все задачи в правильном порядке, прокидывая зависимости."""
    out: dict = {}
    try:
        out["v1"] = calc_v1(inp, cfg)
        out["v2"] = calc_v2(inp, cfg)
        out["v3"] = calc_v3(inp, cfg)
        out["v4"] = {"status": "stub", "note": "Задача В.4 — заглушка (длительность реакции СКР, не реализована)"}
        v5  = calc_v5(inp, cfg);                                out["v5"]  = v5
        v6  = calc_v6(inp, cfg, v5);                            out["v6"]  = v6
        v7  = calc_v7(inp, cfg, v5);                            out["v7"]  = v7
        v8  = calc_v8(inp, cfg, k_ms=v5["k_ms"], k_mg=inp["k_mg_lab"]); out["v8"] = v8
        v9  = calc_v9(inp, v5, v8);                             out["v9"]  = v9
        v10 = calc_v10(inp, v5);                                out["v10"] = v10
        v11 = calc_v11(inp);                                    out["v11"] = v11
        v17 = calc_v17(inp, v10, v11);                          out["v17"] = v17
    except Exception as e:
        import traceback; traceback.print_exc()
        out["__error__"] = f"{type(e).__name__}: {e}"
    return out
