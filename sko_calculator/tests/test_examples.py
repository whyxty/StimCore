"""Юнит-тесты по контрольным примерам В.1.1 ... В.17.1."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import math
import pytest

from modules.constants import load_config
from modules.tasks import (
    task_v1, task_v2, task_v3, task_v4, task_v5,
    task_v6, task_v7, task_v8, task_v9, task_v10, task_v17,
)

CFG = load_config()


def approx(actual, expected, tol=0.02):
    return abs(actual - expected) <= tol * abs(expected)


def base_inputs():
    return {
        "K_f": 16.0, "K_pot": 51.0, "Q_f": 86.6, "q_inj": 150.0,
        "p_pl": 25.0, "H": 2800.0, "h_ef": 78.3, "h_pta": 17.0,
        "C_k": 3.1, "C_gl": 6.6, "k_ms_lab": 1.2, "m0": 14.0,
        "k0": 0.044, "T_pl": 85.0, "k_vo": 0.35, "k_uf": 0.28, "k_v": 0.5,
        "q_acid": 260.0, "C0_HCl": 15.0, "rho_sk": 2700.0, "rho_p": 2300.0,
        "R_ms": 2.0e-5, "Fe3": 0.1, "N_as": 1.0, "N_sm": 5.0, "N_nf": 0.1,
        "rho_fluid": 1000.0, "p_opr": 25.0, "well_type": "нефтяная",
        "r_c": 0.1, "r_k": 200.0, "T_n": 100.0, "rho_n": 0.84,
        "W_0": 81.9, "Tsena_n": 15.0, "Sebest_n": 8.0,
        "H_no": 2823.0, "H_vo": 2733.0, "D_k": 0.124, "d_vn": 0.073, "d_v": 0.062,
        "K_collector_type": 2,
        "layers_table": [
            {"interval": "1", "h_ef": 17, "porosity": 12},
            {"interval": "2", "h_ef": 12, "porosity": 9.8},
            {"interval": "3", "h_ef": 18, "porosity": 13},
            {"interval": "4", "h_ef": 22, "porosity": 10.5},
            {"interval": "5", "h_ef": 21, "porosity": 9.6},
        ],
    }


def test_v1_example():
    res = task_v1.solve(base_inputs(), CFG)
    assert approx(res["OP"], 0.3137, tol=0.05)
    assert res["cond_OP"]
    assert res["cond_h_pta"]
    assert res["cond_C_k"]
    assert res["cond_k_ms"]
    assert approx(res["k_vo"], 17/78.3, tol=0.05)


def test_v2_example():
    inp = base_inputs()
    res = task_v2.solve(inp, CFG)
    assert res["Q_oj"] > 0
    assert approx(res["k_enr"], 25.0/(1000*9.8*2800*1e-6), tol=0.02)


def test_v3_example():
    inp = base_inputs()
    res = task_v3.solve(inp, CFG, q0=260.0, p0=18.0)
    assert res["p_rst"] > 0
    assert res["grad_p_grp"] == CFG["pressure_gradients"]["grad_p_grp_oil"]


def test_v4_example():
    inp = base_inputs()
    res = task_v4.solve(inp, CFG, radii=[1.0])
    # τ ~ секунды
    tau = res["rows"][0]["tau"]
    assert 0.1 < tau < 1000


def test_v5_example():
    inp = base_inputs()
    res = task_v5.solve(inp, CFG, V_targets=[6])
    t = res["targets"][0]
    assert t["r_zr"] > 0.0
    assert len(res["profile"]) > 10


def test_v6_example():
    inp = base_inputs()
    res = task_v6.solve(inp, CFG, V_ks_list=[1])
    # DG_s = 0.25*6.6 + 0.5*3.2 (≈3.2 принимаем 3.1) ≈ 3.2
    assert approx(res["DG_s"], 0.25*6.6 + 0.5*3.1)
    # G_s для V=1: ρ_п=2300, m_0=14% → 2300*1*0.0321/0.14 ≈ 5273
    assert res["rows"][0]["G_s_kg"] > 5000


def test_v7_example():
    inp = base_inputs()
    res = task_v7.solve(inp, CFG)
    assert approx(res["k_ms"], 1.2, tol=0.05)


def test_v8_example():
    inp = base_inputs()
    res = task_v8.solve(inp, CFG)
    # k_s* = 0.9 * exp(0.2*3.1) ≈ 1.673
    assert approx(res["k_s_star"], 0.9*math.exp(0.2*3.1), tol=0.01)
    # k_s ≈ 0.044 * 1.673 ≈ 0.0736
    assert approx(res["k_s"], 0.044 * 0.9 * math.exp(0.2*3.1), tol=0.02)


def test_v9_example():
    inp = base_inputs()
    res = task_v9.solve(inp, CFG, V_targets=[3], Z_ko=[3000])
    row = res["rows"][0]
    assert row["A_s1"] > 1.0
    assert row["Q_s1"] > inp["Q_f"]


def test_v10_example():
    inp = base_inputs()
    res = task_v10.solve(inp, V_ks=6.0, V_zrs=0.9)
    assert approx(res["V_vts"], 1.08, tol=0.05)
    # V_прд из примера ≈ 9.42
    assert approx(res["V_prd"], 9.42, tol=0.1)


def test_v17_example():
    inp = base_inputs()
    res = task_v17.solve(inp, CFG, V_k=6.0, C_target=15.0, C_commercial=28.0)
    # V_тк ~ 504 л/м³
    assert 400 < res["V_tk"] < 600
