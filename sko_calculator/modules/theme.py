"""Тема StimCore — тёмная неоновая тема для Streamlit-приложения СКО.

Дизайн-токены и стиль вдохновлены макетом «StimCore App» (React-прототип).
Применяется через `apply_theme()` в начале `app.py`.
"""
import streamlit as st


# ──────── Дизайн-токены (палитра StimCore) ────────
TOKENS = {
    "bg0":     "#04060a",
    "bg1":     "#0a0d13",
    "bg2":     "#131720",
    "bg3":     "#1a1e28",
    "border":  "#222a38",
    "border2": "#2a3448",
    "text0":   "#eef0f4",
    "text1":   "#8a96a8",
    "text2":   "#4a5568",
    "text3":   "#2a3344",
    "accent":  "#22e2ff",
    "green":   "#7fff6e",
    "orange":  "#ffb74d",
    "red":     "#ff5555",
    "purple":  "#a78bfa",
    "mono":    "'JetBrains Mono', 'SF Mono', Consolas, Menlo, 'Segoe UI Symbol', monospace",
    "sans":    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI Symbol', sans-serif",
}


_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Outlined|Material+Icons+Round" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
:root {{
    --bg0: {bg0};
    --bg1: {bg1};
    --bg2: {bg2};
    --bg3: {bg3};
    --border: {border};
    --border2: {border2};
    --text0: {text0};
    --text1: {text1};
    --text2: {text2};
    --text3: {text3};
    --accent: {accent};
    --green: {green};
    --orange: {orange};
    --red: {red};
    --purple: {purple};
    --mono: {mono};
    --sans: {sans};
}}

/* ─── глобально ─── */
html, body, [class*="st-"], .stApp {{
    background-color: var(--bg0) !important;
    color: var(--text0) !important;
    font-family: var(--sans);
}}

/* ─── Material Symbols / иконки Streamlit — не ломать шрифт ─── */
.material-icons,
.material-icons-outlined,
[class*="material-symbols"],
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
[data-testid*="Icon"] svg,
.stApp [class*="material-symbols"],
.stApp .material-icons {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-weight: normal !important;
    font-style: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
}}

/* фон главной области */
.stApp {{
    background:
        radial-gradient(circle at 0% 0%, rgba(0,229,255,0.04) 0%, transparent 40%),
        radial-gradient(circle at 100% 100%, rgba(167,139,250,0.03) 0%, transparent 40%),
        var(--bg0) !important;
}}

/* ─── скроллбары ─── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border2); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

/* ─── заголовки ─── */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--sans) !important;
    color: var(--text0) !important;
    letter-spacing: -0.02em !important;
    font-weight: 700 !important;
}}
h1 {{ font-size: 22px !important; }}
h2 {{ font-size: 18px !important; border-left: 3px solid var(--accent); padding-left: 12px !important; }}
h3 {{ font-size: 15px !important; color: var(--text1) !important; text-transform: uppercase; letter-spacing: 0.08em !important; font-weight: 600 !important; }}

/* подзаголовки st.subheader */
.stApp h2[class*="StyledHeader"] {{
    color: var(--accent) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em !important;
    font-size: 16px !important;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px !important;
}}

/* ─── caption / Markdown ─── */
[data-testid="stMarkdownContainer"] p, .stMarkdown p {{
    color: var(--text1) !important;
    font-size: 13px;
    line-height: 1.6;
}}
[data-testid="stCaptionContainer"], small {{
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
}}

/* код / inline */
code {{
    background: var(--bg2) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1px 6px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
}}

/* ─── sidebar ─── */
[data-testid="stSidebar"] {{
    background: var(--bg1) !important;
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label {{
    font-family: var(--mono) !important;
    font-size: 12px !important;
    color: var(--text1) !important;
    position: relative;
    padding-left: 14px !important;
    transition: color .15s;
}}
/* индикатор-кружок слева от пункта меню */
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: transparent;
    border: 1.5px solid var(--border2);
    transition: all .2s ease;
}}
/* активный пункт: подсвеченный кружок + цвет текста */
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:has(input:checked) {{
    color: var(--accent) !important;
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:has(input:checked)::before {{
    background: var(--accent);
    border-color: var(--accent);
    box-shadow: 0 0 8px var(--accent);
}}
[data-testid="stSidebar"] [class*="stRadio"] [role="radiogroup"] label:hover::before {{
    border-color: var(--accent);
}}
/* спрятать дефолтный radio-кружок Streamlit */
[data-testid="stSidebar"] [class*="stRadio"] [data-baseweb="radio"] > div:first-child {{
    display: none !important;
}}

/* ─── number/text input ─── */
.stNumberInput input, .stTextInput input, .stTextArea textarea {{
    background-color: var(--bg0) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 4px !important;
    font-family: var(--mono) !important;
    font-weight: 600;
    font-size: 13px !important;
    transition: border-color 0.15s;
}}
.stNumberInput input:focus, .stTextInput input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
    outline: none !important;
}}
.stNumberInput label, .stTextInput label, .stTextArea label,
.stSelectbox label, .stCheckbox label, .stRadio label, .stSlider label {{
    font-family: var(--mono) !important;
    font-size: 11px !important;
    color: var(--text1) !important;
    font-weight: 500 !important;
    text-transform: none !important;
}}

/* ─── selectbox ─── */
.stSelectbox > div > div {{
    background-color: var(--bg0) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 4px !important;
}}
.stSelectbox div[role="combobox"] {{
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    font-weight: 600 !important;
}}

/* ─── slider ─── */
.stSlider [data-baseweb="slider"] > div > div > div {{
    background: var(--accent) !important;
}}
.stSlider [data-baseweb="slider"] > div > div {{
    background: var(--border2) !important;
}}
.stSlider [role="slider"] {{
    background: var(--accent) !important;
    box-shadow: 0 0 12px var(--accent) !important;
}}

/* ─── checkbox / radio ─── */
.stCheckbox [role="checkbox"][data-checked="true"],
.stRadio [data-baseweb="radio"][data-checked="true"] > div {{
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}}

/* ─── buttons ─── */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{
    background: var(--accent) !important;
    color: var(--bg0) !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 8px 18px !important;
    box-shadow: 0 0 14px rgba(0,229,255,0.25) !important;
    transition: all 0.15s !important;
}}
.stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {{
    box-shadow: 0 0 22px rgba(0,229,255,0.5) !important;
    transform: translateY(-1px);
}}

/* ────────────────────────────────────────────────────────────────
   HUD/Sci-Fi Buttons
   primary  → neon     (двойная обводка + halo + inset-glow)
   secondary → brackets (уголки-маркеры + scan-line)
   ──────────────────────────────────────────────────────────────── */

/* общий сброс для обоих kind-ов */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{
    position: relative !important;
    height: 52px !important;
    border-radius: 4px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    transition: transform .18s ease, filter .18s ease,
                box-shadow .25s ease, border-color .18s ease,
                color .18s ease, background-color .18s ease !important;
    overflow: hidden !important;
}}
.stButton button:active {{ transform: translateY(1px) !important; }}
.stButton button:focus-visible {{
    outline: 2px dashed var(--accent) !important;
    outline-offset: 6px !important;
}}
.stButton button:disabled {{
    filter: saturate(.2) brightness(.55) !important;
    cursor: not-allowed !important;
}}

/* ───────── PRIMARY — variant: neon ───────── */
.stButton button[kind="primary"], button[kind="primary"] {{
    background: #02060a !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    outline: none !important;
    box-shadow:
        0 0 0 1px rgba(34,226,255,0.18) inset,
        0 0 22px rgba(34,226,255,0.38),
        0 0 6px rgba(34,226,255,0.5) inset !important;
    text-shadow: 0 0 8px rgba(34,226,255,0.7) !important;
}}
.stButton button[kind="primary"]:hover, button[kind="primary"]:hover {{
    color: #ecffff !important;
    background: #02060a !important;
    border-color: #7af3ff !important;
    box-shadow:
        0 0 0 1px rgba(34,226,255,0.28) inset,
        0 0 36px rgba(34,226,255,0.65),
        0 0 10px rgba(34,226,255,0.85) inset !important;
    text-shadow: 0 0 14px var(--accent) !important;
    letter-spacing: 0.22em !important;
}}

/* ───────── SECONDARY — тот же neon-вариант, что и primary ───────── */
.stButton button[kind="secondary"], button[kind="secondary"] {{
    background: #02060a !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    outline: none !important;
    box-shadow:
        0 0 0 1px rgba(34,226,255,0.18) inset,
        0 0 22px rgba(34,226,255,0.38),
        0 0 6px rgba(34,226,255,0.5) inset !important;
    text-shadow: 0 0 8px rgba(34,226,255,0.7) !important;
}}
.stButton button[kind="secondary"]:hover, button[kind="secondary"]:hover {{
    color: #ecffff !important;
    background: #02060a !important;
    border-color: #7af3ff !important;
    box-shadow:
        0 0 0 1px rgba(34,226,255,0.28) inset,
        0 0 36px rgba(34,226,255,0.65),
        0 0 10px rgba(34,226,255,0.85) inset !important;
    text-shadow: 0 0 14px var(--accent) !important;
    letter-spacing: 0.22em !important;
}}

@media (prefers-reduced-motion: reduce) {{
    .stButton button {{ transition: none !important; }}
}}

/* ─── metric ─── */
[data-testid="stMetric"] {{
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 0 0 transparent;
    transition: border-color .2s, box-shadow .2s;
}}
[data-testid="stMetric"]:hover {{
    border-color: var(--accent);
    box-shadow: 0 0 18px rgba(0,229,255,0.12);
}}
[data-testid="stMetricLabel"] {{
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
}}
[data-testid="stMetricValue"] {{
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: var(--mono) !important;
    font-size: 10px !important;
    letter-spacing: 0.05em !important;
}}

/* ─── expander ─── */
[data-testid="stExpander"] {{
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    margin-bottom: 8px;
    /* без overflow:hidden скруглённая рамка не «замыкается» снизу,
       когда внутри есть широкие блоки (формулы / таблицы) */
    overflow: hidden !important;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
    overflow-x: auto;
}}
[data-testid="stExpander"] summary {{
    font-family: var(--mono) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    color: var(--text1) !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 12px 16px !important;
}}
[data-testid="stExpander"] summary:hover {{
    color: var(--accent) !important;
}}
[data-testid="stExpander"][open] summary {{
    border-bottom: 1px solid var(--border);
    color: var(--accent) !important;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
    padding: 14px 16px !important;
}}

/* ─── alerts (info / warning / error / success) ─── */
[data-testid="stAlert"] {{
    border-radius: 6px !important;
    border-left-width: 3px !important;
    font-family: var(--sans) !important;
    font-size: 12px !important;
    padding: 10px 14px !important;
}}
[data-testid="stAlert"][data-baseweb="notification"] {{
    background: var(--bg2) !important;
}}
div[data-testid="stAlert"][kind="info"] {{ border-left-color: var(--accent) !important; }}
div[data-testid="stAlert"][kind="warning"] {{ border-left-color: var(--orange) !important; }}
div[data-testid="stAlert"][kind="error"] {{ border-left-color: var(--red) !important; }}
div[data-testid="stAlert"][kind="success"] {{ border-left-color: var(--green) !important; }}

/* ─── dataframe / table ─── */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
}}
[data-testid="stDataFrame"] [data-testid="stTable"] {{ border: none; }}
.dataframe, [data-testid="stDataFrame"] table {{
    font-family: var(--mono) !important;
    font-size: 11.5px !important;
    color: var(--text0) !important;
}}
[data-testid="stDataFrame"] thead tr th {{
    background: var(--bg1) !important;
    color: var(--text2) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 10px !important;
    border-bottom: 1px solid var(--border2) !important;
}}

/* ─── tabs ─── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--bg1);
    border-radius: 6px;
    padding: 4px;
    gap: 2px;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: var(--mono) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text2) !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: var(--bg2) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 10px rgba(0,229,255,0.15);
}}

/* ─── plotly чарты — фон ─── */
.stPlotlyChart, .js-plotly-plot {{
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px;
    padding: 4px;
}}

/* ─── LaTeX блоки ─── */
.katex {{
    color: var(--text0) !important;
    font-size: 14px !important;
}}
/* Убираем индивидуальные «коробки» вокруг каждой формулы:
   - отдельная рамка/левый акцент/bg2 у каждой st.latex выглядит
     тяжело и создаёт тёмные подложки под subscript-спанами (когда
     внутрь KaTeX попадают streamlit-обёртки с фоном bg0).
   - без рамки формулы плотно сидят внутри родительского экспандера
     и не вылезают за его правый край. */
.katex-display {{
    background: transparent !important;
    border: none !important;
    border-left: none !important;
    border-radius: 0 !important;
    padding: 4px 0 !important;
    margin: 6px 0 !important;
    max-width: 100%;
    box-sizing: border-box;
    overflow-x: auto;
}}
.katex, .katex *,
.katex-display *,
[data-testid="stMarkdownContainer"] .katex,
[data-testid="stMarkdownContainer"] .katex * {{
    background: transparent !important;
}}

/* ─── divider ─── */
hr {{
    border-color: var(--border) !important;
    margin: 14px 0 !important;
}}

/* ─── link ─── */
a {{
    color: var(--accent) !important;
    text-decoration: none;
}}
a:hover {{
    text-shadow: 0 0 6px var(--accent);
}}

/* ─── баджи в заголовках через emoji ─── */
.stApp h2:has(.emoji), .stApp h3:has(.emoji) {{
    border-left: 3px solid var(--accent);
    padding-left: 10px;
}}

/* ─── скрытие default Streamlit-меню (по желанию) ─── */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stStatusWidget"] {{ display: none; }}

/* эмодзи на кнопках — моно-glyph, чтобы подхватили цвет лейбла */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{
    font-variant-emoji: text;
}}
</style>
""".format(**TOKENS)


def apply_theme():
    """Применяет визуальную тему StimCore — вызывать сразу после st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)
    _apply_plotly_template()


def _apply_plotly_template():
    """Регистрирует и активирует тёмный шаблон Plotly в стиле StimCore."""
    try:
        import plotly.io as pio
        import plotly.graph_objects as go

        tpl = go.layout.Template()
        tpl.layout = dict(
            paper_bgcolor=TOKENS["bg2"],
            plot_bgcolor=TOKENS["bg2"],
            font=dict(family=TOKENS["mono"], size=11, color=TOKENS["text1"]),
            colorway=[
                TOKENS["accent"], TOKENS["green"], TOKENS["orange"],
                TOKENS["purple"], TOKENS["red"], "#fbbf24", "#34d399",
            ],
            xaxis=dict(
                gridcolor=TOKENS["border"],
                linecolor=TOKENS["border2"],
                zerolinecolor=TOKENS["border2"],
                tickfont=dict(color=TOKENS["text2"], size=10),
                title_font=dict(color=TOKENS["text1"], size=11),
            ),
            yaxis=dict(
                gridcolor=TOKENS["border"],
                linecolor=TOKENS["border2"],
                zerolinecolor=TOKENS["border2"],
                tickfont=dict(color=TOKENS["text2"], size=10),
                title_font=dict(color=TOKENS["text1"], size=11),
            ),
            legend=dict(
                bgcolor=TOKENS["bg1"],
                bordercolor=TOKENS["border"],
                borderwidth=1,
                font=dict(color=TOKENS["text1"], size=10),
            ),
            title=dict(font=dict(color=TOKENS["text0"], size=14)),
            hoverlabel=dict(
                bgcolor=TOKENS["bg1"],
                bordercolor=TOKENS["accent"],
                font=dict(color=TOKENS["text0"], family=TOKENS["mono"]),
            ),
        )
        pio.templates["stimcore"] = tpl
        pio.templates.default = "stimcore"
    except Exception:
        pass


def stimcore_header(title: str = "StimCore", subtitle: str = "СКО"):
    """Шапка приложения в стиле StimCore."""
    st.markdown(f"""
<div style="
    background: linear-gradient(180deg, var(--bg1) 0%, var(--bg0) 100%);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: inset 0 1px 0 rgba(0,229,255,0.08);
">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div style="
            width: 10px; height: 10px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 14px var(--accent);
            animation: stimPulse 2s ease-in-out infinite;
        "></div>
        <div>
            <div style="
                font-family: var(--sans);
                font-size: 22px;
                font-weight: 700;
                color: var(--text0);
                letter-spacing: -0.02em;
            ">{title}</div>
            <div style="
                font-family: var(--mono);
                font-size: 11px;
                font-weight: 700;
                color: var(--text2);
                letter-spacing: 0.18em;
                text-transform: uppercase;
                margin-top: 2px;
            ">{subtitle}</div>
        </div>
    </div>
</div>
<style>
@keyframes stimPulse {{
    0%, 100% {{ opacity: 1; box-shadow: 0 0 14px var(--accent); }}
    50% {{ opacity: 0.4; box-shadow: 0 0 4px var(--accent); }}
}}
</style>
    """, unsafe_allow_html=True)
