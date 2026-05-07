// Глобальный store: дефолты входных данных, текущий screen, результаты расчёта.
// Чистый React + локальный state без зависимостей. Если нужно — поднимем на Zustand.

export type ScreenId = 'config' | 'inputs' | 'results' | 'task';

export const DEFAULT_INPUTS = {
  // Идентификация
  well_name: 'Скважина №47',
  field_name: 'Предкарпатье',

  // В.1
  K_f:    16.0,
  K_pot:  51.0,
  h_pta:  17.0,
  k_ms_lab: 1.20,
  k_mg_lab: 1.15,
  layers: [
    { interval: '2733-2750', h_ef: 17, porosity: 12.0, k0: 0.020, treat: true },
    { interval: '2750-2762', h_ef: 12, porosity:  9.8, k0: 0.010, treat: true },
    { interval: '2762-2780', h_ef: 18, porosity: 13.0, k0: 0.060, treat: false },
  ],

  // В.2
  Q_f:    86.6,
  q_inj:  150.0,
  p_pl:   25.0,
  H:      2800.0,

  // В.3
  well_type: 'нефтяная' as 'нефтяная' | 'водонагнетательная',
  p_opr:     25.0,
  rho_fluid: 1070.0,
  q_k:       250.0,
  p_k:       12.0,
  use_v20:   false,

  // В.5
  r_c:       0.10,
  h_ef:      78.3,
  m0:        14.0,
  k_vo:      0.35,
  k_uf:      0.28,
  k_v:       0.50,
  rho_sk:    2700.0,
  R_ms:      2.0e-5,
  C0_HCl:    15.0,
  V_zad:     12.0,
  k_ms_mode: 'напрямую' as 'напрямую' | 'по Δm_s',
  dm_s:      2.8,

  // В.6
  C_gl:  6.6,
  C_k:   3.1,
  rho_p: 2250.0,

  // В.8
  KL: 'KL_2' as 'KL_1'|'KL_2'|'KL_3'|'KL_4'|'KL_5',
  k0_use_override: false,
  k0_user: 0.044,

  // В.9
  r_k:    250.0,
  T_n:    100.0,
  rho_n:  840.0,
  W_0:    20.0,
  C_n:    30000.0,
  S_n:    18000.0,
  Z_ko:   150000.0,
  use_eps: true,

  // В.10
  d_in_NKT:  0.062,
  d_out_NKT: 0.073,
  D_k:       0.150,
  H_no:      2820.0,
  H_vo:      2780.0,

  // В.11
  N_ko: 0,
  T_pl: 70.0,
  Fe3:  0.0,
  W_vn: 2 as 1 | 2 | 3,
  N_as: 1.0,
  N_sm: 4.0,
  N_nf: 0.2,
  HCl:  12.0,
  HF:   3.0,
  ratio_skr_gkr: '1:1',

  // В.17
  tovar_HCl_options: [27, 31] as number[],
  C_inh:  0.3,
  C_stab: 0.5,
  C_surf: 0.3,
  C_buf:  0.3,
};

export type Inputs = typeof DEFAULT_INPUTS;
