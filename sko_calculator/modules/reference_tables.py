"""Справочные физико-химические таблицы (универсальные)."""
import numpy as np

# Таблица B.4 — коэффициент диффузии HCl при 0°C по концентрации (м²/с)
# C, %  -> D_os * 1e-9
TABLE_B4_HCl = {
    # концентрация % : D_os (м²/с)
    5:  2.44e-9,
    10: 2.50e-9,
    15: 2.55e-9,
    20: 2.60e-9,
    25: 2.65e-9,
    30: 2.70e-9,
}
# Молярная концентрация HCl (кг/л) для расчётов
TABLE_B4_C_ms = {
    5: 0.052,
    10: 0.108,
    15: 0.167,
    20: 0.230,
    25: 0.297,
    30: 0.367,
}


def get_D_os(C0_percent: float) -> float:
    """Коэффициент диффузии HCl при 0°C, м²/с — линейная интерполяция."""
    keys = sorted(TABLE_B4_HCl.keys())
    vals = [TABLE_B4_HCl[k] for k in keys]
    return float(np.interp(C0_percent, keys, vals))


def get_C_ms(C0_percent: float) -> float:
    """Молярная концентрация HCl, кг/л."""
    keys = sorted(TABLE_B4_C_ms.keys())
    vals = [TABLE_B4_C_ms[k] for k in keys]
    return float(np.interp(C0_percent, keys, vals))


# Таблица B.5 — кинематическая вязкость воды (м²/с) от температуры °C
TABLE_B5_WATER_NU = {
    0:   1.789e-6,
    10:  1.306e-6,
    20:  1.006e-6,
    30:  0.805e-6,
    40:  0.659e-6,
    50:  0.556e-6,
    60:  0.478e-6,
    70:  0.415e-6,
    80:  0.366e-6,
    90:  0.326e-6,
    100: 0.295e-6,
}


def get_nu_water(T_celsius: float) -> float:
    keys = sorted(TABLE_B5_WATER_NU.keys())
    vals = [TABLE_B5_WATER_NU[k] for k in keys]
    return float(np.interp(T_celsius, keys, vals))


# Таблица B.26 — плотность HCl при 20°C от концентрации (кг/л)
TABLE_B26_HCl = {
    5:  1.023,
    10: 1.047,
    15: 1.073,
    20: 1.098,
    25: 1.124,
    28: 1.139,
    30: 1.149,
    31: 1.155,
}


def get_rho_HCl(C_percent: float) -> float:
    keys = sorted(TABLE_B26_HCl.keys())
    vals = [TABLE_B26_HCl[k] for k in keys]
    return float(np.interp(C_percent, keys, vals))


# Таблица B.28 — плотность уксусной кислоты при 20°C (кг/л)
TABLE_B28_AcOH = {
    10: 1.013,
    20: 1.026,
    30: 1.038,
    40: 1.049,
    50: 1.058,
    60: 1.064,
    70: 1.069,
    80: 1.070,
    90: 1.062,
    99: 1.055,
}


def get_rho_AcOH(C_percent: float) -> float:
    keys = sorted(TABLE_B28_AcOH.keys())
    vals = [TABLE_B28_AcOH[k] for k in keys]
    return float(np.interp(C_percent, keys, vals))


# Таблица B.29 — характеристики типовых реагентов
TABLE_B29_REAGENTS = [
    {"name": "Катапин КИ-1 (ингибитор)",  "C_t": 100, "rho_t": 1.020, "active": 100},
    {"name": "Уротропин (ингибитор)",     "C_t": 100, "rho_t": 1.330, "active": 100},
    {"name": "Б-2 (ингибитор)",            "C_t": 100, "rho_t": 1.030, "active": 100},
    {"name": "И-2-А (ингибитор)",          "C_t": 100, "rho_t": 1.040, "active": 100},
    {"name": "Уксусная кислота (стаб.)",   "C_t": 80,  "rho_t": 1.070, "active": 80},
    {"name": "Лимонная кислота (стаб.)",   "C_t": 100, "rho_t": 1.660, "active": 100},
    {"name": "Сульфат натрия (стаб.)",     "C_t": 100, "rho_t": 2.700, "active": 100},
    {"name": "КРАСТ (стаб.)",              "C_t": 100, "rho_t": 1.250, "active": 100},
    {"name": "Сульфонол (ПАВ)",            "C_t": 100, "rho_t": 1.050, "active": 100},
    {"name": "ОП-10 (ПАВ)",                "C_t": 100, "rho_t": 1.020, "active": 100},
    {"name": "Превоцелл W-OF-7 (ПАВ)",     "C_t": 100, "rho_t": 1.030, "active": 100},
]

# Таблица B.15 — выбор типа кислотного раствора (только ветка СКО, y=0)
TABLE_B15_SKO_BRANCH = {
    "comment": "При y=0 (HF не нужен) — для любой карбонатности применяется СКО раствором 10–15% HCl",
    "recommended_HCl_min": 10,
    "recommended_HCl_max": 15,
}

# Таблица B.16 — типы кислотных растворов
TABLE_B16 = [
    {"type": "Ингибированный КР", "conditions": "Защита от коррозии, T_пл > 40°C"},
    {"type": "Стабилизированный КР", "conditions": "Высокое содержание Fe³⁺, осадкообразование"},
    {"type": "С добавкой ПАВ", "conditions": "Высокая обводнённость, парафинистая нефть"},
    {"type": "Замедленный КР", "conditions": "Глубокая обработка, низкая проницаемость"},
]

# Таблица B.17 — ингибиторы
TABLE_B17_INHIBITORS = [
    {"name": "Катапин КИ-1", "T_max": 80,  "C_HCl_max": 20, "dose_percent": "0.05–0.1"},
    {"name": "Уротропин",    "T_max": 60,  "C_HCl_max": 15, "dose_percent": "0.5–1.0"},
    {"name": "Б-2",          "T_max": 100, "C_HCl_max": 25, "dose_percent": "0.1–0.3"},
    {"name": "И-2-А",        "T_max": 130, "C_HCl_max": 30, "dose_percent": "0.3–0.5"},
]

# Таблица B.18 — стабилизаторы
TABLE_B18_STABILIZERS = [
    {"name": "Уксусная кислота", "T_pl_range": "до 80°C", "Fe3_max": 0.5, "dose_percent": "1–3"},
    {"name": "Лимонная кислота", "T_pl_range": "до 100°C", "Fe3_max": 1.0, "dose_percent": "1–2"},
    {"name": "Сульфат натрия",   "T_pl_range": "любая",    "Fe3_max": 0.3, "dose_percent": "0.5–1"},
    {"name": "КРАСТ",            "T_pl_range": "до 120°C", "Fe3_max": 1.5, "dose_percent": "0.5–1.5"},
]

# Таблица B.19 — ПАВ
TABLE_B19_SURFACTANTS = [
    {"name": "Сульфонол",         "for_water": "пресная/минерализ.", "for_oil": "любая",        "dose_percent": "0.3–0.5"},
    {"name": "ОП-10",             "for_water": "пресная",            "for_oil": "парафинистая", "dose_percent": "0.3–0.5"},
    {"name": "Превоцелл W-OF-7",  "for_water": "минерализованная",   "for_oil": "смолистая",    "dose_percent": "0.2–0.4"},
]
