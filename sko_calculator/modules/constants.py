"""Загрузка/сохранение констант месторождения."""
import json
from pathlib import Path
from copy import deepcopy

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict, path: Path | str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def reset_to_default() -> dict:
    return load_config(DEFAULT_CONFIG_PATH)


def empty_config() -> dict:
    """Пустой каркас конфигурации — все числовые поля = 0, строки пустые.
    Структура совпадает с config.json, чтобы UI не падал на отсутствующих ключах."""
    return {
        "field_name": "",
        "well_selection": {
            "m_pr_min": 0, "m_pr_max": 0, "m_pr_default": 0,
            "h_pr_min": 0, "C_k_pr": 0, "C_gl_pr": 0,
            "k_s_np": 0, "q_pr": 0,
        },
        "pressure_gradients": {
            "grad_p_grp_oil": 0, "grad_p_grp_water": 0,
            "grad_p_k_oil": 0, "grad_p_k_water": 0,
            "p_opr_production_min": 0, "p_opr_production_max": 0,
            "p_opr_exploration_min": 0, "p_opr_exploration_max": 0,
        },
        "reaction_kinetics": {"alpha_kgo": 0, "comment_alpha": ""},
        "rock_properties": {
            "rho_sk_min": 0, "rho_sk_max": 0, "rho_sk_default": 0,
            "rho_p_min": 0, "rho_p_max": 0, "rho_p_default": 0,
            "k_ms_min": 0, "k_ms_max": 0, "k_ms_default": 0,
            "R_ms_min": 0, "R_ms_max": 0, "R_ms_default": 0,
        },
        "dissolution_coefficients": {"a_clay": 0, "b_carbonate": 0, "comment": ""},
        "permeability_regressions": {
            "comment": "",
            "KL_1": {"A": 0, "B": 0}, "KL_2": {"A": 0, "B": 0},
            "KL_3": {"A": 0, "B": 0}, "KL_4": {"A": 0, "B": 0},
            "KL_5": {"A": 0, "B": 0},
        },
        "permeability_change_after_sko": {"comment": "", "A": 0, "B": 0},
        "specific_debit_table": {"comment": "", "rows": []},
        "collector_types": {
            "comment": "",
            "KL_1": {"name": "", "cement": "", "clay": 0, "k_uf": 0},
            "KL_2": {"name": "", "cement": "", "clay": 0, "k_uf": 0},
            "KL_3": {"name": "", "cement": "", "clay": 0, "k_uf": 0},
            "KL_4": {"name": "", "cement": "", "clay": 0, "k_uf": 0},
            "KL_5": {"name": "", "cement": "", "clay": 0, "k_uf": 0},
        },
    }


def deep_copy(config: dict) -> dict:
    return deepcopy(config)
