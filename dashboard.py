import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from datetime import datetime
import re
import io

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="QBR TD SYNNEX Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)



# ========== TEMA ==========
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    theme_option = st.selectbox(
        "🎨 Tema",
        options=['🌙 Dark', '☀️ Light'],
        index=0 if st.session_state.theme == 'dark' else 1
    )
    if theme_option == '🌙 Dark':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'

    st.markdown("---")
    st.markdown("### ℹ️ Sobre")
    st.markdown("""
    Dashboard QBR TD SYNNEX<br>
    Dados de Performance Marketing<br>
    FY25 - Q1 a Q4
    """, unsafe_allow_html=True)

# ========== CORES BASEADAS NO TEMA ==========
if st.session_state.theme == 'dark':
    COLORS = {
        'primary': '#0066CC',
        'primary_dark': '#004999',
        'primary_light': '#3399FF',
        'secondary': '#FF6B35',
        'secondary_light': '#FF8C5A',
        'accent': '#7B2CBF',
        'accent_light': '#9D4EDD',
        'success': '#2E7D32',
        'danger': '#D32F2F',
        'warning': '#FFB74D',
        'background': '#0A1929',
        'card_bg': 'rgba(15, 43, 61, 0.7)',
        'text': '#FFFFFF',
        'text_muted': 'rgba(255,255,255,0.7)',
        'border': 'rgba(255,255,255,0.15)',
        'kpi_number_bg': 'linear-gradient(135deg, #FFFFFF, #E0E0E0)',
        'kpi_number_color': 'transparent',
    }
    BG_GRADIENT = "linear-gradient(135deg, #0A1929 0%, #0F2B3D 100%)"
else:
    COLORS = {
        'primary': '#0066CC',
        'primary_dark': '#004999',
        'primary_light': '#3399FF',
        'secondary': '#FF6B35',
        'secondary_light': '#FF8C5A',
        'accent': '#7B2CBF',
        'accent_light': '#9D4EDD',
        'success': '#2E7D32',
        'danger': '#D32F2F',
        'warning': '#FFB74D',
        'background': '#F5F7FA',
        'card_bg': 'rgba(255,255,255,0.95)',
        'text': '#1A2634',
        'text_muted': '#6C757D',
        'border': '#DEE2E6',
        'kpi_number_bg': 'none',
        'kpi_number_color': '#0066CC',
    }
    BG_GRADIENT = "linear-gradient(135deg, #F5F7FA 0%, #FFFFFF 100%)"

# ========== DADOS HISTÓRICOS FY24 ==========
HISTORICAL_DATA = {
    'email': {
        'Q1FY24': {'entrega': 99.44, 'abertura': 16.25, 'cliques': 2.03, 'optout': 0.07},
        'Q2FY24': {'entrega': 96.96, 'abertura': 30.01,  'cliques': 1.94, 'optout': 0.14},
        'Q3FY24': {'entrega': 94.0,  'abertura': 42.0,  'cliques': 1.36,  'optout': 0.06},
        'Q4FY24': {'entrega': 94.0,  'abertura': 24.0, 'cliques': 1.3,  'optout': 0.04},
    },
    'redes': {
        'Q1FY24': {'seguidores': 1230, 'engajamentos': 81419, 'cliques': 6117},
        'Q2FY24': {'seguidores': 1688, 'engajamentos': 10237, 'cliques': 8585},
        'Q3FY24': {'seguidores': 1927, 'engajamentos': 76102, 'cliques': 36375},
        'Q4FY24': {'seguidores': 2296, 'engajamentos': 58046, 'cliques': 51119},
    },
    'blog': {
        'Q1FY24': {'visitas': 24926, 'usuarios': 17075, 'abertura_news': 34.19, 'cliques_news': 2.8, 'envios_news': None, 'empresas_news': 416},
        'Q2FY24': {'visitas': 16137, 'usuarios': 11295, 'abertura_news': 65.09, 'cliques_news': 7.96, 'envios_news': 868, 'empresas_news': 427},
        'Q3FY24': {'visitas': 13353, 'usuarios': 7037,  'abertura_news': 62.0,  'cliques_news': 2.12, 'envios_news': 1049, 'empresas_news': 428},
        'Q4FY24': {'visitas': 18910, 'usuarios': 12348, 'abertura_news': 32.0,  'cliques_news': 1.8,  'envios_news': None, 'empresas_news': 488},
    }
}

# ========== DADOS ATUAIS FY25 ==========
CURRENT_EMAIL_DATA = {
    'Q1': {'entrega': 95.7,  'abertura': 35.8, 'cliques': 1.7, 'optout': 0.04},
    'Q2': {'entrega': 98.4,  'abertura': 45.3, 'cliques': 2.6, 'optout': 0.07},
    'Q3': {'entrega': 96.0,  'abertura': 38.0, 'cliques': 6.0, 'optout': 0.05},
    'Q4': {'entrega': 93.0,  'abertura': 24.0, 'cliques': 2.2,'optout': 0.02},
}

CURRENT_BLOG_DATA = {
    'Q1': {'visitas': 37900, 'usuarios': 17075, 'blogposts': 31, 'tempo_medio': 5.0},
    'Q2': {'visitas': 16137, 'usuarios': 11295, 'blogposts': 25, 'tempo_medio': 4.04},
    'Q3': {'visitas': 13353, 'usuarios': 7037,  'blogposts': 26, 'tempo_medio': 2.35},
    'Q4': {'visitas': 18910, 'usuarios': 12348, 'blogposts': 27, 'tempo_medio': 4.6},
}

CURRENT_NEWSLETTER_DATA = {
    'Q1': {'envios': 750,  'empresas': 416, 'abertura': 34.19, 'cliques': 2.8},
    'Q2': {'envios': 750,  'empresas': 427, 'abertura': 35.2,  'cliques': 2.8},
    'Q3': {'envios': 1059, 'empresas': 428, 'abertura': 33.1,  'cliques': 1.5},
    'Q4': {'envios': 426, 'empresas': 488, 'abertura': 32.0,  'cliques': 1.8},
}

# ========== DADOS DE CAMPANHAS HARDCODED (DOS PRINTS) ==========
CURRENT_CAMPANHAS_DATA = {
    'Q1': {
        'solicitadas': 6,
        'veiculadas': 4,
        'taxa_conversao': 7.26,
        'leads_gerados': 62,
        'conversao': 83,
        'branding': 17,
        'top_campanhas': '🏆 Fortinet Roadshow (56 empresas)<br>🏆 NVIDIA IA (6 empresas)'
    },
    'Q2': {
        'solicitadas': 9,
        'veiculadas': 6,
        'taxa_conversao': None,
        'leads_gerados': None,
        'conversao': None,
        'branding': None,
        'top_campanhas': '🏆 IBM IA (55 empresas)<br>🏆 Microsoft Roadshow (40 empresas)<br>🏆 Fortinet Recrutamento (25 empresas)'
    },
    'Q3': {
        'solicitadas': 7,
        'veiculadas': 6,
        'taxa_conversao': None,
        'leads_gerados': None,
        'conversao': None,
        'branding': None,
        'top_campanhas': '🏆 Cloud On the Go (383 empresas)<br>🏆 Fortinet Roadshow (46 empresas)<br>🏆 NVIDIA IA (10 empresas)'
    },
    'Q4': {
        'solicitadas': 6,
        'veiculadas': 3,
        'taxa_conversao': None,
        'leads_gerados': 70,
        'conversao': None,
        'branding': None,
        'top_campanhas': '🏆 Campanha Recrutamento Fortinet (70 empresas)'
    }
}

# ========== CSS ==========
# CSS em variável str pura (não f-string) para evitar conflito com % do CSS.
# Cores dinâmicas são injetadas nos style="" inline das funções.
CSS_STATIC = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main .block-container { padding: 0; max-width: 100%; }
    #MainMenu, header, footer { visibility: hidden; }

    .premium-header {
        background: linear-gradient(135deg, rgba(0,102,204,0.9) 0%, rgba(123,44,191,0.8) 50%, rgba(255,107,53,0.7) 100%);
        backdrop-filter: blur(10px);
        padding: 48px 56px 40px 56px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .premium-title {
        font-size: 52px; font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF, #E0E0E0);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0; letter-spacing: -1px;
    }
    .premium-sub { font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 8px; }

    /* KPI cards */
    .kpi-premium { text-align: center; }
    .kpi-icon { font-size: 40px; margin-bottom: 12px; }
    .kpi-label { font-size: 12px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-variation { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-top: 12px; }
    .kpi-up      { background: rgba(46,125,50,0.3);   color: #6FBF6F; border: 1px solid rgba(76,175,80,0.4); }
    .kpi-down    { background: rgba(211,47,47,0.3);   color: #FF8A80; border: 1px solid rgba(239,83,80,0.4); }
    .kpi-neutral { background: rgba(136,146,160,0.3); color: #B0BEC5; border: 1px solid rgba(136,146,160,0.4); }

    /* Metric comparison card */
    .comparison-premium {
        border-radius: 16px; padding: 12px;
        text-align: left; margin-top: 12px;
    }
    .comparison-header {
        font-size: 10px; margin-bottom: 10px;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .comparison-row {
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 11px;
    }
    .comparison-row:last-child { margin-bottom: 0; }
    .comp-label { white-space: nowrap; }
    .comp-value { font-weight: 700; text-align: right; }
    .comp-badge {
        display: inline-flex; align-items: center; gap: 3px;
        padding: 2px 8px; border-radius: 20px;
        font-size: 10px; font-weight: 700;
        white-space: nowrap;
    }
    .badge-up   { background: rgba(46,125,50,0.35);  color: #6FBF6F; }
    .badge-down { background: rgba(211,47,47,0.35);  color: #FF8A80; }
    .badge-flat { background: rgba(136,146,160,0.3); color: #B0BEC5; }

    /* Section headers */
    .section-premium { display: flex; align-items: center; gap: 12px; margin: 48px 0 24px 0; }
    .section-icon { font-size: 32px; background: rgba(0,102,204,0.25); padding: 12px; border-radius: 16px; }

    /* Bars */
    .bar-premium { margin-bottom: 20px; }
    .bar-track-premium { background: rgba(0,0,0,0.1); border-radius: 12px; height: 40px; overflow: hidden; }
    .bar-fill-premium {
        height: 100%; border-radius: 12px;
        display: flex; align-items: center; justify-content: flex-end;
        padding-right: 16px; color: white; font-size: 14px; font-weight: 600;
    }

    /* Blog cards */
    .blog-item-premium { margin-bottom: 24px; padding: 12px 0; }
    .blog-item-premium:last-child { margin-bottom: 0; padding-bottom: 0; }
    .blog-label-premium { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .blog-value-premium { font-size: 32px; font-weight: 800; line-height: 1.1; margin-bottom: 8px; }
    .blog-compare-premium { font-size: 11px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .blog-change-premium {
        font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px;
        display: inline-flex; align-items: center; gap: 4px;
    }
    .blog-change-up   { background: rgba(46,125,50,0.4);  color: #6FBF6F; }
    .blog-change-down { background: rgba(211,47,47,0.4); color: #FF8A80; }

    /* Buttons */
    div.stButton > button {
        padding: 10px 28px; border-radius: 40px;
        background: rgba(0,0,0,0.2); backdrop-filter: blur(5px);
        font-size: 14px; font-weight: 600; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background: #0066CC; color: white; transform: translateY(-2px); }

    /* Footer */
    .footer-premium { margin-top: 60px; padding: 24px; text-align: center; font-size: 12px; }

    .stDataFrame { border-radius: 16px !important; overflow: hidden !important; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 24px; }
</style>
"""

# Inject theme-dependent CSS variables via f-string (no % in CSS here)
CSS_THEME = f"""
<style>
    .stApp {{ background: {BG_GRADIENT}; }}
    [data-testid="stSidebar"] {{
        background: {COLORS['card_bg']};
        border-right: 1px solid {COLORS['border']};
    }}
    [data-testid="stSidebar"] * {{ color: {COLORS['text']}; }}
    .glass-card {{
        background: {COLORS['card_bg']};
        backdrop-filter: blur(12px);
        border-radius: 24px; padding: 24px;
        border: 1px solid {COLORS['border']};
        transition: all 0.4s ease;
        margin-bottom: 24px; height: 100%;
    }}
    .glass-card:hover {{
        transform: translateY(-6px);
        border-color: {COLORS['primary']};
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }}
    .kpi-number {{
        font-size: 48px; font-weight: 800; line-height: 1;
        background: {COLORS['kpi_number_bg']};
        -webkit-background-clip: text; background-clip: text;
        color: {COLORS['kpi_number_color']};
    }}
    .kpi-label {{ color: {COLORS['text_muted']}; }}
    .section-title-premium {{ font-size: 24px; font-weight: 700; color: {COLORS['text']}; letter-spacing: -0.5px; }}
    .section-sub {{ font-size: 13px; color: {COLORS['text_muted']}; margin-top: 4px; }}
    .premium-quarter {{
        font-size: 24px; font-weight: 600; color: {COLORS['secondary']};
        margin-top: 16px; display: inline-block;
        background: rgba(0,0,0,0.3); padding: 6px 20px;
        border-radius: 40px;
    }}
    .comparison-premium {{
        background: rgba(0,0,0,0.12);
        border: 1px solid {COLORS['border']};
    }}
    .comparison-header {{ color: {COLORS['text_muted']}; }}
    .comparison-row {{ color: {COLORS['text_muted']}; }}
    .comp-label {{ color: {COLORS['text_muted']}; }}
    .comp-value {{ color: {COLORS['text']}; }}
    .bar-label-premium {{ display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: {COLORS['text']}; }}
    .blog-premium {{
        background: {COLORS['card_bg']};
        backdrop-filter: blur(12px);
        border-radius: 24px; padding: 28px;
        border: 1px solid {COLORS['border']};
        transition: all 0.4s ease; height: 100%;
        position: relative; overflow: hidden; margin-bottom: 24px;
    }}
    .blog-premium::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent']});
    }}
    .blog-premium:hover {{ transform: translateY(-4px); border-color: {COLORS['primary']}; }}
    .blog-header-premium {{
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 24px; padding-bottom: 16px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    .blog-icon-premium {{ font-size: 36px; }}
    .blog-title-premium {{ font-size: 20px; font-weight: 700; color: {COLORS['text']}; }}
    .blog-sub-premium {{ font-size: 11px; color: {COLORS['text_muted']}; margin-top: 2px; }}
    .blog-label-premium {{ color: {COLORS['text_muted']}; }}
    .blog-value-premium {{ color: {COLORS['text']}; }}
    .blog-compare-premium {{ color: {COLORS['text_muted']}; }}
    .blog-item-premium {{ border-bottom: 1px solid {COLORS['border']}; }}
    .footer-premium {{ border-top: 1px solid {COLORS['border']}; color: {COLORS['text_muted']}; }}
    .stDataFrame thead th {{
        background: linear-gradient(135deg, rgba(0,102,204,0.3), rgba(123,44,191,0.2)) !important;
        color: {COLORS['text']} !important; font-weight: 600 !important;
    }}
    .stDataFrame tbody td {{
        background: rgba(15,43,61,0.3) !important;
        color: {COLORS['text']} !important;
        border-bottom: 1px solid {COLORS['border']} !important;
    }}
    .stDataFrame tbody tr:hover td {{
        background: rgba(0,102,204,0.2) !important;
    }}
    div.stButton > button {{
        border: 1px solid {COLORS['border']};
        color: {COLORS['text']};
    }}
</style>
"""

st.markdown(CSS_STATIC, unsafe_allow_html=True)
st.markdown(CSS_THEME, unsafe_allow_html=True)

# ========== FUNÇÕES AUXILIARES ==========
def clean_percentage(value):
    if value is None or pd.isna(value):
        return '—'
    value_str = str(value).strip()
    if '%' not in value_str:
        return value_str
    clean_str = value_str.replace('%', '').strip()
    return '—' if clean_str == '' else f"{clean_str}%"

def format_number(val):
    if val is None or pd.isna(val):
        return '—'
    try:
        num = float(str(val).replace('%', '').replace('.', '').replace(',', '.'))
        return f"{int(num):,}".replace(',', '.') if num.is_integer() else f"{num:.1f}".replace('.', ',')
    except:
        return str(val)

def clean_value(val):
    if val is None or pd.isna(val):
        return '—'
    val_str = str(val).strip()
    if val_str in ['', 'nan', 'NaN', 'None']:
        return '—'
    
    # Remove todos os % da string
    val_str = val_str.replace('%', '').strip()
    
    if val_str == '':
        return '—'
    
    return val_str

def render_metric_card(metric_name, icon, current_value,
                       prev_fy25_value, prev_fy25_name,
                       same_fy24_value, same_fy24_name,
                       is_percentage=True, tooltip=None):
    """
    Card de métrica com 2 linhas de comparativo:
      Linha 1 → Q anterior do FY25  (ex: Q1FY25 para Q2FY25)
      Linha 2 → Mesmo Q do FY24     (ex: Q2FY24 para Q2FY25)
    """
    # Limpa os valores (remove %)
    cur       = clean_value(current_value)
    prev_str  = clean_value(prev_fy25_value) if prev_fy25_value not in ('—', None) else '—'
    same_str  = clean_value(same_fy24_value) if same_fy24_value not in ('—', None) else '—'

    var_prev  = calc_variacao(cur, prev_str) if prev_str != '—' else None
    var_same  = calc_variacao(cur, same_str) if same_str != '—' else None

    # Adiciona o sufixo APENAS uma vez, se for porcentagem
    suffix     = '%' if is_percentage and cur != '—' else ''
    prev_suffix = '%' if is_percentage and prev_str != '—' else ''
    same_suffix = '%' if is_percentage and same_str != '—' else ''
    
    tip_html   = f'<span style="font-size:10px;opacity:0.6;margin-left:4px;" title="{tooltip}">ⓘ</span>' if tooltip else ''

    row1 = f"""
    <div class="comparison-row">
        <span class="comp-label">{prev_fy25_name}</span>
        <span class="comp-value">{prev_str}{prev_suffix}</span>
        {_comp_badge(var_prev)}
    </div>"""

    row2 = f"""
    <div class="comparison-row">
        <span class="comp-label">{same_fy24_name}</span>
        <span class="comp-value">{same_str}{same_suffix}</span>
        {_comp_badge(var_same)}
    </div>"""

    st.html(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:34px;margin-bottom:8px;">{icon}</div>
        <div style="font-size:36px;font-weight:800;color:{COLORS['text']};">{cur}{suffix}</div>
        <div style="font-size:13px;color:{COLORS['text_muted']};margin-bottom:14px;">{metric_name}{tip_html}</div>
        <div class="comparison-premium">
            <div class="comparison-header">📊 Comparativos</div>
            {row1}
            {row2}
        </div>
    </div>
    """)

def render_blog_item(label, value,
                     prev_fy25_value, prev_fy25_name,
                     same_fy24_value, same_fy24_name,
                     is_percentage=False, icon="📊"):
    """
    Item de blog/newsletter com 2 linhas de comparativo:
      Linha 1 → Q anterior do FY25
      Linha 2 → Mesmo Q do FY24
    """
    # Limpa os valores (remove %)
    val_str  = clean_value(value)
    prev_str = clean_value(prev_fy25_value) if prev_fy25_value not in ('—', None) else '—'
    same_str = clean_value(same_fy24_value) if same_fy24_value not in ('—', None) else '—'

    var_prev = calc_variacao(val_str, prev_str) if prev_str != '—' else None
    var_same = calc_variacao(val_str, same_str) if same_str != '—' else None
    
    # Adiciona o sufixo APENAS uma vez, se for porcentagem
    suffix     = '%' if is_percentage and val_str != '—' else ''
    prev_suffix = '%' if is_percentage and prev_str != '—' else ''
    same_suffix = '%' if is_percentage and same_str != '—' else ''

    def badge(v):
        if v is None: return ''
        arrow = '▲' if v > 0 else '▼'
        cls   = 'blog-change-up' if v > 0 else 'blog-change-down'
        return f'<span class="blog-change-premium {cls}">{arrow} {abs(v):.1f}%</span>'

    st.html(f"""
    <div class="blog-item-premium">
        <div class="blog-label-premium">{icon} {label}</div>
        <div class="blog-value-premium">{val_str}{suffix}</div>
        <div class="blog-compare-premium">
            <span>vs {prev_fy25_name}: {prev_str}{prev_suffix}</span>
            {badge(var_prev)}
        </div>
        <div class="blog-compare-premium" style="margin-top:4px;">
            <span>vs {same_fy24_name}: {same_str}{same_suffix}</span>
            {badge(var_same)}
        </div>
    </div>
    """)

def extract_percentage(val):
    if val is None or pd.isna(val):
        return 0
    try:
        return float(re.sub(r'[^\d,\.]', '', str(val)).replace(',', '.'))
    except:
        return 0

def remove_duplicates(df, subset_columns):
    return df if df.empty else df.drop_duplicates(subset=subset_columns, keep='first')

def get_pecas_value(df, q):
    rows = df[(df['trimestre'] == q) & df['metrica'].isin(['Peças Produzidas', 'Peças'])]['valor']
    try: return int(rows.values[0]) if len(rows) > 0 else 0
    except: return 0

def get_solicitacoes_value(df, q):
    rows = df[(df['trimestre'] == q) & (df['metrica'] == 'Solicitações')]['valor']
    try: return int(rows.values[0]) if len(rows) > 0 else 0
    except: return 0

def get_campanhas_value(df, q):
    rows = df[(df['trimestre'] == q) & (df['metrica'] == 'Campanhas')]['valor']
    try: return int(rows.values[0]) if len(rows) > 0 else 0
    except: return 0

def calc_variacao(atual, anterior):
    if atual in (None, '—') or anterior in (None, '—'):
        return None
    try:
        a = float(str(atual).replace('.', '').replace(',', '.').replace('%', ''))
        b = float(str(anterior).replace('.', '').replace(',', '.').replace('%', ''))
        return ((a - b) / b) * 100 if b != 0 else None
    except:
        return None

def get_campanha_valor(df, indicador_exato, q):
    rows = df[(df['trimestre'] == q) & (df['indicador'] == indicador_exato)]
    return clean_value(rows['valor'].values[0]) if not rows.empty else '—'

def get_vertical_distribution(q):
    hardcoded = {
        'Q1': [('Segurança',27.0),('Networking',13.0),('Cloud',13.0),('Data & AI',10.0),('Data Center',9.0),('Institucional',15.0)],
        'Q2': [('Cloud',27.0),('Segurança',22.0),('Networking',19.0),('Data & AI',14.0),('Data Center',10.0),('Institucional',8.0)],
        'Q3': [('Segurança',31.0),('Cloud',19.0),('Networking',16.0),('Institucional',15.0),('Data & AI',14.0),('Data Center',6.0)],
        'Q4': [('Segurança',40.0),('Cloud',21.0),('Institucional',14.0),('Networking',9.0),('Data Center',8.0),('Data & AI',7.0)],
    }
    return pd.DataFrame(hardcoded.get(q, hardcoded['Q1']), columns=['vertical', 'percentual'])

def get_current_email_value(q, metric):
    if q and q in CURRENT_EMAIL_DATA:
        val = CURRENT_EMAIL_DATA[q].get(metric)
        if val is not None:
            return f"{val}%"
    return '—'

def get_current_blog_value(q, metric):
    if q and q in CURRENT_BLOG_DATA:
        val = CURRENT_BLOG_DATA[q].get(metric)
        if val is not None:
            if metric == 'tempo_medio':
                mapping = {5.0: "5:00", 4.07: "4:04", 2.35: "2:35", 4.6: "4:36"}
                return mapping.get(val, f"{val}min")
            return f"{val:,}".replace(',', '.')
    return '—'

def get_current_newsletter_value(q, metric):
    if q and q in CURRENT_NEWSLETTER_DATA:
        val = CURRENT_NEWSLETTER_DATA[q].get(metric)
        if val is not None:
            return f"{val}%" if metric in ['abertura', 'cliques'] else f"{val:,}".replace(',', '.')
    return '—'

def get_campanha_hardcoded(q, metric):
    """Busca dados de campanha hardcoded quando não disponíveis no banco"""
    if q in CURRENT_CAMPANHAS_DATA and metric in CURRENT_CAMPANHAS_DATA[q]:
        val = CURRENT_CAMPANHAS_DATA[q][metric]
        if val is not None:
            if metric in ['taxa_conversao']:
                return f"{val}%"
            elif metric in ['conversao', 'branding']:
                return f"{val}%"
            return str(val)
    return None

# ========== FUNÇÕES DE RENDERIZAÇÃO ==========
def render_kpi_premium(valor, label, icone, variacao=None, trimestre_ref=None, tooltip=None):
    badge = ''
    if variacao is not None and trimestre_ref:
        if variacao > 0:
            badge = f'<div class="kpi-variation kpi-up">↑ {variacao:.1f}% <span style="font-size:9px;">vs {trimestre_ref}</span></div>'
        elif variacao < 0:
            badge = f'<div class="kpi-variation kpi-down">↓ {abs(variacao):.1f}% <span style="font-size:9px;">vs {trimestre_ref}</span></div>'
        else:
            badge = f'<div class="kpi-variation kpi-neutral">→ 0% <span style="font-size:9px;">vs {trimestre_ref}</span></div>'
    st.html(f"""
    <div class="glass-card kpi-premium">
        <div class="kpi-icon">{icone}</div>
        <div class="kpi-number">{format_number(valor)}</div>
        <div class="kpi-label">{label}</div>
        {badge}
    </div>
    """)

def _comp_badge(variacao):
    """Gera o badge colorido de variação para o bloco comparison."""
    if variacao is None:
        return '<span class="comp-badge badge-flat">—</span>'
    arrow = '▲' if variacao > 0 else '▼'
    cls   = 'badge-up' if variacao > 0 else 'badge-down'
    return f'<span class="comp-badge {cls}">{arrow} {abs(variacao):.2f}%</span>'

def render_metric_card(metric_name, icon, current_value,
                       prev_fy25_value, prev_fy25_name,
                       same_fy24_value, same_fy24_name,
                       is_percentage=True, tooltip=None):
    """
    Card de métrica com 2 linhas de comparativo:
      Linha 1 → Q anterior do FY25  (ex: Q1FY25 para Q2FY25)
      Linha 2 → Mesmo Q do FY24     (ex: Q2FY24 para Q2FY25)
    """
    cur       = clean_value(current_value)
    prev_str  = clean_value(prev_fy25_value)  if prev_fy25_value  not in ('—', None) else '—'
    same_str  = clean_value(same_fy24_value)  if same_fy24_value  not in ('—', None) else '—'

    var_prev  = calc_variacao(cur, prev_str) if prev_str  != '—' else None
    var_same  = calc_variacao(cur, same_str) if same_str  != '—' else None

    suffix     = '%' if is_percentage else ''
    tip_html   = f'<span style="font-size:10px;opacity:0.6;margin-left:4px;" title="{tooltip}">ⓘ</span>' if tooltip else ''

    row1 = f"""
    <div class="comparison-row">
        <span class="comp-label">{prev_fy25_name}</span>
        <span class="comp-value">{prev_str}{suffix}</span>
        {_comp_badge(var_prev)}
    </div>"""

    row2 = f"""
    <div class="comparison-row">
        <span class="comp-label">{same_fy24_name}</span>
        <span class="comp-value">{same_str}{suffix}</span>
        {_comp_badge(var_same)}
    </div>"""

    st.html(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:34px;margin-bottom:8px;">{icon}</div>
        <div style="font-size:36px;font-weight:800;color:{COLORS['text']};">{cur}{suffix}</div>
        <div style="font-size:13px;color:{COLORS['text_muted']};margin-bottom:14px;">{metric_name}{tip_html}</div>
        <div class="comparison-premium">
            <div class="comparison-header">📊 Comparativos</div>
            {row1}
            {row2}
        </div>
    </div>
    """)

def render_blog_item(label, value,
                     prev_fy25_value, prev_fy25_name,
                     same_fy24_value, same_fy24_name,
                     is_percentage=False, icon="📊"):
    """
    Item de blog/newsletter com 2 linhas de comparativo:
      Linha 1 → Q anterior do FY25
      Linha 2 → Mesmo Q do FY24
    """
    val_str  = clean_value(value)
    prev_str = clean_value(prev_fy25_value) if prev_fy25_value not in ('—', None) else '—'
    same_str = clean_value(same_fy24_value) if same_fy24_value not in ('—', None) else '—'

    var_prev = calc_variacao(val_str, prev_str) if prev_str != '—' else None
    var_same = calc_variacao(val_str, same_str) if same_str != '—' else None
    suffix   = '%' if is_percentage else ''

    def badge(v):
        if v is None: return ''
        arrow = '▲' if v > 0 else '▼'
        cls   = 'blog-change-up' if v > 0 else 'blog-change-down'
        return f'<span class="blog-change-premium {cls}">{arrow} {abs(v):.1f}%</span>'

    st.html(f"""
    <div class="blog-item-premium">
        <div class="blog-label-premium">{icon} {label}</div>
        <div class="blog-value-premium">{val_str}{suffix}</div>
        <div class="blog-compare-premium">
            <span>vs {prev_fy25_name}: {prev_str}{suffix}</span>
            {badge(var_prev)}
        </div>
        <div class="blog-compare-premium" style="margin-top:4px;">
            <span>vs {same_fy24_name}: {same_str}{suffix}</span>
            {badge(var_same)}
        </div>
    </div>
    """)

def render_horizontal_bars(df, title):
    if df is None or df.empty:
        return
    vertical_colors = {
        'Segurança':'#D32F2F','Networking':'#0066CC','Cloud':'#3399FF',
        'Data & AI':'#7B2CBF','Data Center':'#FF6B35','Institucional':'#2E7D32'
    }
    df = df.copy()
    df.columns = ['vertical', 'percentual'] + list(df.columns[2:])
    df = df.sort_values('percentual', ascending=False)

    st.markdown(f'<div class="glass-card"><div style="font-size:16px;font-weight:600;color:{COLORS["text"]};margin-bottom:20px;">📊 {title}</div>', unsafe_allow_html=True)
    for _, row in df.iterrows():
        pct   = row['percentual']
        color = vertical_colors.get(row['vertical'], '#0066CC')
        st.markdown(f"""
        <div class="bar-premium">
            <div class="bar-label-premium">
                <span>{row['vertical']}</span>
                <span style="color:{color};">{pct:.1f}%</span>
            </div>
            <div class="bar-track-premium">
                <div class="bar-fill-premium" style="width:{pct}%;background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_table(df, title=None):
    if df.empty:
        return
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div style="font-size:16px;font-weight:600;color:{COLORS["text"]};margin-bottom:16px;">{title}</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_comparative_charts(quarterly_data):
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Comparativo Trimestral</div><div class="section-sub">Análise Q1 a Q4</div></div></div>', unsafe_allow_html=True)

    for key, label, color in [('pecas','Peças',COLORS['primary']),('solic','Solicitações',COLORS['secondary']),('camp','Campanhas',COLORS['success'])]:
        df_c = pd.DataFrame([{'trimestre': t, 'valor': quarterly_data[t][key]} for t in ['Q1','Q2','Q3','Q4']])
        fig  = go.Figure()
        fig.add_trace(go.Bar(x=df_c['trimestre'], y=df_c['valor'], name=label,
                             marker=dict(color=color), text=df_c['valor'], textposition='outside',
                             textfont=dict(color=COLORS['text'])))
        fig.add_trace(go.Scatter(x=df_c['trimestre'], y=df_c['valor'], mode='lines+markers',
                                 name='Tendência', line=dict(color=COLORS['secondary'] if key!='solic' else COLORS['primary'], width=3),
                                 marker=dict(size=10)))
        fig.update_layout(title=f'{label} por Trimestre', title_font_color=COLORS['text'],
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(tickfont_color=COLORS['text'], gridcolor=COLORS['border']),
                          yaxis=dict(tickfont_color=COLORS['text'], gridcolor=COLORS['border']),
                          legend=dict(font_color=COLORS['text']), height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Distribuição por vertical
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">Evolução por trimestre</div></div></div>', unsafe_allow_html=True)
    vertical_data = []
    for t in ['Q1','Q2','Q3','Q4']:
        for _, row in get_vertical_distribution(t).iterrows():
            vertical_data.append({'trimestre': t, 'vertical': row['vertical'], 'percentual': row['percentual']})
    if vertical_data:
        fig = px.bar(pd.DataFrame(vertical_data), x='trimestre', y='percentual', color='vertical',
                     title='% Peças por Vertical por Trimestre', barmode='group',
                     color_discrete_map={'Segurança':'#D32F2F','Networking':'#0066CC','Cloud':'#3399FF',
                                         'Data & AI':'#7B2CBF','Data Center':'#FF6B35','Institucional':'#2E7D32'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(tickfont_color=COLORS['text'], gridcolor=COLORS['border']),
                          yaxis=dict(tickfont_color=COLORS['text'], gridcolor=COLORS['border']),
                          legend=dict(font_color=COLORS['text']), title_font_color=COLORS['text'], height=450)
        st.plotly_chart(fig, use_container_width=True)

# ========== CONEXÃO COM BANCO ==========
@st.cache_resource
def get_engine():
    return create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require")

@st.cache_data(ttl=3600)
def query_db(sql):
    with get_engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn)

@st.cache_data(ttl=3600)
def load_all_data():
    fabricantes = remove_duplicates(
        query_db(f"SELECT * FROM {SCHEMA}.fabricantes_campanhas ORDER BY trimestre"),
        ['trimestre', 'vertical']
    )
    return {
        'overview': query_db(f"SELECT trimestre, metrica, valor FROM {SCHEMA}.overview WHERE metrica IN ('Peças Produzidas','Peças','Solicitações','Campanhas') ORDER BY trimestre"),
        'overview_full': query_db(f"SELECT * FROM {SCHEMA}.overview ORDER BY trimestre"),
        'pecas': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.pecas_por_vertical WHERE vertical IS NOT NULL AND vertical != '' ORDER BY trimestre, vertical"), ['trimestre','vertical','objetivo']),
        'fabricantes': fabricantes,
        'campanhas': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.campanhas ORDER BY trimestre"), ['trimestre','indicador']),
        'email_geral': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.email_marketing WHERE categoria='geral' ORDER BY trimestre"), ['trimestre','indicador']),
        'email_vertical': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.email_marketing WHERE categoria='vertical' ORDER BY trimestre"), ['trimestre','vertical_tipo']),
        'email_tipo': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.email_marketing WHERE categoria='tipo_email' ORDER BY trimestre"), ['trimestre','vertical_tipo']),
        'redes_geral': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.redes_sociais WHERE categoria='geral' ORDER BY trimestre"), ['trimestre','indicador']),
        'redes_rede': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.redes_sociais WHERE categoria='rede_social' ORDER BY trimestre"), ['trimestre','rede']),
        'blog_blog': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.blog_newsletter WHERE tipo='blog' ORDER BY trimestre"), ['trimestre','indicador']),
        'blog_news': remove_duplicates(query_db(f"SELECT * FROM {SCHEMA}.blog_newsletter WHERE tipo='newsletter' ORDER BY trimestre"), ['trimestre','indicador']),
    }

data       = load_all_data()
trimestres = ['Q1', 'Q2', 'Q3', 'Q4', 'FY25']

if 'view' not in st.session_state:
    st.session_state.view = 'Q1'

# ========== HEADER ==========
st.markdown(f"""
<div class="premium-header">
    <div class="premium-title">TD SYNNEX BR</div>
    <div class="premium-sub">Quarterly Business Review · Performance Analytics</div>
    <div class="premium-quarter">{st.session_state.view} FY25</div>
</div>
""", unsafe_allow_html=True)

# ========== BOTÕES ==========
_, c1, c2, c3, c4, c5, _ = st.columns([1.5, 0.8, 0.8, 0.8, 0.8, 0.8, 1.5])
for col, label, key in [(c1,'Q1','q1'),(c2,'Q2','q2'),(c3,'Q3','q3'),(c4,'Q4','q4'),(c5,'🏆 FY25','fy25')]:
    with col:
        if st.button(label, key=key, use_container_width=True):
            st.session_state.view = label.replace('🏆 ', '')
            st.rerun()

st.markdown('<div style="padding:0 56px 56px 56px;">', unsafe_allow_html=True)

# ========== DADOS TRIMESTRAIS ==========
q = st.session_state.view
quarterly_data = {
    t: {
        'pecas': get_pecas_value(data['overview'], t),
        'solic': get_solicitacoes_value(data['overview'], t),
        'camp':  get_campanhas_value(data['overview'], t),
    }
    for t in ['Q1', 'Q2', 'Q3', 'Q4']
}

# ============================================================
# ABA FY25
# ============================================================
if q == 'FY25':
    render_comparative_charts(quarterly_data)

    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Overview Anual</div><div class="section-sub">Indicadores consolidados FY25</div></div></div>', unsafe_allow_html=True)
    pecas_tot = sum(quarterly_data[t]['pecas'] for t in ['Q1','Q2','Q3','Q4'])
    solic_tot = sum(quarterly_data[t]['solic'] for t in ['Q1','Q2','Q3','Q4'])
    camp_tot  = sum(quarterly_data[t]['camp']  for t in ['Q1','Q2','Q3','Q4'])

    k1, k2, k3 = st.columns(3)
    with k1: render_kpi_premium(pecas_tot, "Total Peças",        "📦")
    with k2: render_kpi_premium(solic_tot, "Total Solicitações", "📋")
    with k3: render_kpi_premium(camp_tot,  "Total Campanhas",    "🎯")

    # Vertical média anual
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">Média anual</div></div></div>', unsafe_allow_html=True)
    vert_vals = {}
    for t in ['Q1','Q2','Q3','Q4']:
        for _, row in get_vertical_distribution(t).iterrows():
            vert_vals.setdefault(row['vertical'], []).append(row['percentual'])
    df_annual = pd.DataFrame([{'vertical': v, 'percentual': sum(ps)/len(ps)} for v, ps in vert_vals.items()]).sort_values('percentual', ascending=False)
    render_horizontal_bars(df_annual, "% Peças por Vertical (Média Anual)")

    # Top campanhas
    st.markdown(f'<div class="section-premium"><div class="section-icon">🏆</div><div><div class="section-title-premium">Top Campanhas do Ano</div><div class="section-sub">Destaques por trimestre</div></div></div>', unsafe_allow_html=True)
    top_camp = {
        'Q1':'Fortinet Roadshow (56 empresas) | NVIDIA IA (6 empresas)',
        'Q2':'IBM IA (55) | Microsoft Roadshow (40) | Fortinet Recrutamento (25)',
        'Q3':'Cloud On the Go (383) | Fortinet Roadshow (46) | NVIDIA IA (10)',
        'Q4':'Campanha Recrutamento Fortinet (70 empresas)'
    }
    c1a, c2a, c3a, c4a = st.columns(4)
    for col, (t, camp) in zip([c1a,c2a,c3a,c4a], top_camp.items()):
        with col:
            st.markdown(f'<div class="glass-card"><div style="font-size:14px;font-weight:600;color:{COLORS["primary"]};margin-bottom:12px;">{t} FY25</div><div style="font-size:12px;line-height:1.5;color:{COLORS["text"]};">{camp}</div></div>', unsafe_allow_html=True)

    # E-mail anual
    st.markdown(f'<div class="section-premium"><div class="section-icon">📧</div><div><div class="section-title-premium">E-mail Marketing</div><div class="section-sub">Médias anuais</div></div></div>', unsafe_allow_html=True)
    email_means = {'entrega':[],'abertura':[],'cliques':[],'optout':[]}
    for t in ['Q1','Q2','Q3','Q4']:
        for m in email_means:
            v = get_current_email_value(t, m)
            if v != '—': email_means[m].append(extract_percentage(v))
    e1,e2,e3,e4 = st.columns(4)
    for col, (m, icon, label) in zip([e1,e2,e3,e4], [('entrega','✅','Média Entregas'),('abertura','👁️','Média Aberturas'),('cliques','🖱️','Média Cliques'),('optout','🚫','Média Opt-Out')]):
        with col:
            avg = sum(email_means[m])/len(email_means[m]) if email_means[m] else 0
            fmt = f"{avg:.2f}%" if m=='optout' else f"{avg:.1f}%"
            st.markdown(f'<div class="glass-card" style="text-align:center;"><div style="font-size:36px;">{icon}</div><div style="font-size:32px;font-weight:700;color:{COLORS["text"]};">{fmt}</div><div style="font-size:12px;color:{COLORS["text_muted"]};">{label}</div></div>', unsafe_allow_html=True)

    # Download sidebar FY25
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        dl_fmt = st.selectbox("Formato", ["CSV", "Excel"], key="dl_fy25")
        dl_rows = [{'Trimestre':t,'Peças':quarterly_data[t]['pecas'],'Solicitações':quarterly_data[t]['solic'],'Campanhas':quarterly_data[t]['camp']} for t in ['Q1','Q2','Q3','Q4']]
        df_dl   = pd.DataFrame(dl_rows)
        if st.button("📥 Baixar FY25", key="btn_dl_fy25"):
            if dl_fmt == "CSV":
                st.download_button("✅ Baixar CSV", df_dl.to_csv(index=False), "qbr_fy25.csv", "text/csv")
            else:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as w: df_dl.to_excel(w, index=False)
                st.download_button("✅ Baixar Excel", buf.getvalue(), "qbr_fy25.xlsx")

# ============================================================
# ABAS Q1–Q4
# ============================================================
else:
    q_num = int(q[1])   # 1, 2, 3 ou 4

    # ── Trimestre anterior do FY25 (Q anterior do mesmo ano) ──
    prev_fy25_q    = f'Q{q_num - 1}' if q_num > 1 else None   # None para Q1
    prev_fy25_name = f'{prev_fy25_q} FY25' if prev_fy25_q else '—'

    # ── Mesmo trimestre do FY24 ──
    same_fy24_name = f'{q} FY24'

    # ── Trimestre anterior do FY24 (apenas para overview KPI) ──
    prev_fy24_q    = f'Q{q_num - 1}' if q_num > 1 else 'Q4'
    prev_fy24_name = f'{prev_fy24_q} FY24'

    pecas_val = quarterly_data[q]['pecas']
    solic_val = quarterly_data[q]['solic']
    camp_val  = quarterly_data[q]['camp']

    # Para os KPIs de overview, compara com Q anterior FY25 (se existir) senão FY24
    if prev_fy25_q:
        pecas_var = calc_variacao(pecas_val, quarterly_data[prev_fy25_q]['pecas'])
        solic_var = calc_variacao(solic_val, quarterly_data[prev_fy25_q]['solic'])
        camp_var  = calc_variacao(camp_val,  quarterly_data[prev_fy25_q]['camp'])
        kpi_ref   = prev_fy25_name
    else:
        pecas_var = solic_var = camp_var = None
        kpi_ref   = None

    tooltips = {
        'entrega': 'Percentual de e-mails entregues com sucesso',
        'abertura': 'Percentual de e-mails abertos pelos destinatários',
        'cliques': 'Percentual de cliques nos e-mails enviados',
    }

    # ── 1. OVERVIEW ──────────────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Overview</div><div class="section-sub">Indicadores de performance</div></div></div>', unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    with k1: render_kpi_premium(pecas_val, "Peças Produzidas", "📦", pecas_var, kpi_ref)
    with k2: render_kpi_premium(solic_val, "Solicitações",     "📋", solic_var, kpi_ref)
    with k3: render_kpi_premium(camp_val,  "Campanhas",        "🎯", camp_var,  kpi_ref)

    # ── 2. DISTRIBUIÇÃO POR VERTICAL ─────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">% Peças por vertical</div></div></div>', unsafe_allow_html=True)
    render_horizontal_bars(get_vertical_distribution(q), "% Peças por Vertical")

    # ── 3. CAMPANHAS (COM FALLBACK HARDCODED) ─────────────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">🎯</div><div><div class="section-title-premium">Campanhas</div><div class="section-sub">Métricas e destaques</div></div></div>', unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)

    with cc1:
        # Primeiro tenta buscar do banco, depois usa hardcoded
        camp_solic = get_campanha_valor(data['campanhas'], 'Solicitadas', q)
        if camp_solic == '—':
            camp_solic = get_campanha_valor(data['campanhas'], 'Campanhas Solicitadas', q)
        if camp_solic == '—':
            hardcoded = get_campanha_hardcoded(q, 'solicitadas')
            camp_solic = hardcoded if hardcoded else '—'
        
        camp_veic = get_campanha_valor(data['campanhas'], 'Veiculadas', q)
        if camp_veic == '—':
            camp_veic = get_campanha_valor(data['campanhas'], 'Campanhas Veiculadas', q)
        if camp_veic == '—':
            hardcoded = get_campanha_hardcoded(q, 'veiculadas')
            camp_veic = hardcoded if hardcoded else '—'
        
        conv_invest = get_campanha_valor(data['campanhas'], 'Taxa de Conversão (com investimento)', q)
        if conv_invest == '—':
            conv_invest = get_campanha_valor(data['campanhas'], 'Taxa de Conversão (c/ invest.)', q)
        if conv_invest == '—':
            hardcoded = get_campanha_hardcoded(q, 'taxa_conversao')
            conv_invest = hardcoded if hardcoded else '—'
        
        leads = get_campanha_valor(data['campanhas'], 'MQLs Gerados (empresas)', q)
        if leads == '—':
            leads = get_campanha_valor(data['campanhas'], 'Leads / Empresas Gerados', q)
        if leads == '—':
            hardcoded = get_campanha_hardcoded(q, 'leads_gerados')
            leads = hardcoded if hardcoded else '—'
        
        st.html(f"""
        <div class="glass-card">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
                <div style="text-align:center;">
                    <div style="font-size:11px;color:{COLORS['text_muted']};">Solicitadas</div>
                    <div style="font-size:36px;font-weight:800;color:{COLORS['text']};">{camp_solic}</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:11px;color:{COLORS['text_muted']};">Veiculadas</div>
                    <div style="font-size:36px;font-weight:800;color:{COLORS['text']};">{camp_veic}</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                <div style="text-align:center;">
                    <div style="font-size:11px;color:{COLORS['text_muted']};">Taxa Conversão</div>
                    <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{conv_invest}</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:11px;color:{COLORS['text_muted']};">Leads Gerados</div>
                    <div style="font-size:28px;font-weight:800;color:{COLORS['text']};">{leads}</div>
                </div>
            </div>
        </div>
        """)

    with cc2:
        # Top Campanhas
        top_hardcoded = get_campanha_hardcoded(q, 'top_campanhas')
        if top_hardcoded:
            top_text = top_hardcoded
        else:
            top_q = {
                'Q1':'🏆 Fortinet Roadshow (56 empresas)<br>🏆 NVIDIA IA (6 empresas)',
                'Q2':'🏆 IBM IA (55 empresas)<br>🏆 Microsoft Roadshow (40 empresas)<br>🏆 Fortinet Recrutamento (25 empresas)',
                'Q3':'🏆 Cloud On the Go (383 empresas)<br>🏆 Fortinet Roadshow (46 empresas)<br>🏆 NVIDIA IA (10 empresas)',
                'Q4':'🏆 Campanha Recrutamento Fortinet (70 empresas)',
            }
            top_text = top_q.get(q, '—')
        
        # Distribuição por Objetivo
        obj_conv = get_campanha_valor(data['campanhas'], 'Conversão', q)
        if obj_conv == '—':
            obj_conv = get_campanha_valor(data['campanhas'], 'Objetivo Conversão', q)
        if obj_conv == '—':
            hardcoded = get_campanha_hardcoded(q, 'conversao')
            obj_conv = hardcoded if hardcoded else '—'
        
        obj_brand = get_campanha_valor(data['campanhas'], 'Branding', q)
        if obj_brand == '—':
            obj_brand = get_campanha_valor(data['campanhas'], 'Objetivo Branding', q)
        if obj_brand == '—':
            hardcoded = get_campanha_hardcoded(q, 'branding')
            obj_brand = hardcoded if hardcoded else '—'
        
        st.html(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:700;color:{COLORS['text']};margin-bottom:16px;">🏆 Top Campanhas</div>
            <div style="font-size:13px;line-height:1.6;color:{COLORS['text_muted']};margin-bottom:20px;">{top_text}</div>
            <div style="font-size:14px;font-weight:600;color:{COLORS['text']};margin:16px 0 12px;">📊 Distribuição por Objetivo</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="background:rgba(0,0,0,0.05);border-radius:16px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:{COLORS['text_muted']};">Conversão</div>
                    <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{obj_conv}</div>
                </div>
                <div style="background:rgba(0,0,0,0.05);border-radius:16px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:{COLORS['text_muted']};">Branding</div>
                    <div style="font-size:28px;font-weight:800;color:#FF8C5A;">{obj_brand}</div>
                </div>
            </div>
        </div>
        """)

    # ── 4. FABRICANTES ───────────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">🏭</div><div><div class="section-title-premium">Fabricantes por Vertical</div><div class="section-sub">Principais fornecedores</div></div></div>', unsafe_allow_html=True)
    df_fab = data['fabricantes'][data['fabricantes']['trimestre'] == q].copy()
    if not df_fab.empty:
        df_fab = df_fab.drop_duplicates(subset=['vertical'], keep='first')
        ordem  = ['Segurança','Cloud','Data & AI','Data Center','Networking','Institucional']
        df_fab['ord'] = df_fab['vertical'].apply(lambda x: ordem.index(x) if x in ordem else 999)
        df_fab = df_fab.sort_values('ord').drop('ord', axis=1)
        render_table(pd.DataFrame({
            'Vertical':         [clean_value(r['vertical'])          for _, r in df_fab.iterrows()],
            'Maior Solicitante': [clean_value(r['maior_solicitante']) for _, r in df_fab.iterrows()],
            'Menor Solicitante': [clean_value(r['menor_solicitante']) for _, r in df_fab.iterrows()],
            'Top 3 Peças':      [clean_value(r['top_3_pecas'])       for _, r in df_fab.iterrows()],
            'Campanha Ativa':   [clean_value(r['campanha_ativa']) if r['campanha_ativa'] not in ['—',None] else '—' for _, r in df_fab.iterrows()],
        }), "🏭 Fabricantes por Vertical")

    # ── 5. E-MAIL MARKETING ──────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">📧</div><div><div class="section-title-premium">E-mail Marketing</div><div class="section-sub">Métricas de performance</div></div></div>', unsafe_allow_html=True)

    # Atual FY25
    entrega_atual  = get_current_email_value(q, 'entrega')
    abertura_atual = get_current_email_value(q, 'abertura')
    cliques_atual  = get_current_email_value(q, 'cliques')
    optout_atual   = get_current_email_value(q, 'optout')

    # ── Linha 1: Q anterior do FY25 ──
    prev_entrega  = get_current_email_value(prev_fy25_q, 'entrega')  if prev_fy25_q else '—'
    prev_abertura = get_current_email_value(prev_fy25_q, 'abertura') if prev_fy25_q else '—'
    prev_cliques  = get_current_email_value(prev_fy25_q, 'cliques')  if prev_fy25_q else '—'
    prev_optout   = get_current_email_value(prev_fy25_q, 'optout')   if prev_fy25_q else '—'

    # ── Linha 2: Mesmo Q do FY24 ──
    same_fy24_email = HISTORICAL_DATA['email'].get(f'{q}FY24', {})
    same_entrega    = same_fy24_email.get('entrega',  '—')
    same_abertura   = same_fy24_email.get('abertura', '—')
    same_cliques    = same_fy24_email.get('cliques',  '—')
    same_optout     = same_fy24_email.get('optout',   '—')

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        render_metric_card("Entregas",  "✅",  entrega_atual,  prev_entrega,  prev_fy25_name, same_entrega,  same_fy24_name, tooltip=tooltips['entrega'])
    with e2:
        render_metric_card("Aberturas", "👁️", abertura_atual, prev_abertura, prev_fy25_name, same_abertura, same_fy24_name, tooltip=tooltips['abertura'])
    with e3:
        render_metric_card("Cliques",   "🖱️", cliques_atual,  prev_cliques,  prev_fy25_name, same_cliques,  same_fy24_name, tooltip=tooltips['cliques'])
    with e4:
        render_metric_card("Opt-Out",   "🚫", optout_atual,   prev_optout,   prev_fy25_name, same_optout,   same_fy24_name)

    df_ev = data['email_vertical'][data['email_vertical']['trimestre'] == q]
    if not df_ev.empty:
        render_table(df_ev[['vertical_tipo','percent_envio','entrega','abertura','clique','opt_out']], "📊 Métricas de E-mail por Vertical")

    df_et = data['email_tipo'][data['email_tipo']['trimestre'] == q]
    if not df_et.empty:
        render_table(df_et[['vertical_tipo','percent_envio','entrega','abertura','clique','opt_out']], "📊 Métricas de E-mail por Tipo")

    # ── 6. REDES SOCIAIS ─────────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">📱</div><div><div class="section-title-premium">Redes Sociais</div><div class="section-sub">Engajamento e alcance</div></div></div>', unsafe_allow_html=True)

    def _get_rede(df, ind):
        rows = df[df['indicador'] == ind]
        return clean_value(rows['valor'].values[0]) if not rows.empty else '—'

    df_rg = data['redes_geral'][data['redes_geral']['trimestre'] == q]
    seg_atual = _get_rede(df_rg, 'Novos Seguidores')
    eng_atual = _get_rede(df_rg, 'Total de Engajamentos')
    cli_atual = _get_rede(df_rg, 'Total de Cliques')

    # Linha 1: Q anterior FY25
    if prev_fy25_q:
        df_rg_prev = data['redes_geral'][data['redes_geral']['trimestre'] == prev_fy25_q]
        prev_seg = _get_rede(df_rg_prev, 'Novos Seguidores')
        prev_eng = _get_rede(df_rg_prev, 'Total de Engajamentos')
        prev_cli = _get_rede(df_rg_prev, 'Total de Cliques')
    else:
        prev_seg = prev_eng = prev_cli = '—'

    # Linha 2: Mesmo Q FY24
    same_fy24_redes = HISTORICAL_DATA['redes'].get(f'{q}FY24', {})
    same_seg = same_fy24_redes.get('seguidores',  '—')
    same_eng = same_fy24_redes.get('engajamentos','—')
    same_cli = same_fy24_redes.get('cliques',     '—')

    r1, r2, r3 = st.columns(3)
    with r1: render_metric_card("Novos Seguidores", "👥", seg_atual, prev_seg, prev_fy25_name, same_seg, same_fy24_name, is_percentage=False)
    with r2: render_metric_card("Engajamentos",     "❤️", eng_atual, prev_eng, prev_fy25_name, same_eng, same_fy24_name, is_percentage=False)
    with r3: render_metric_card("Cliques",          "🖱️", cli_atual, prev_cli, prev_fy25_name, same_cli, same_fy24_name, is_percentage=False)

    df_rr = data['redes_rede'][data['redes_rede']['trimestre'] == q]
    if not df_rr.empty:
        render_table(df_rr[['rede','seguidores','media_seguidores','engajamentos','cliques']], "📊 Métricas por Rede Social")

    top_pub = data['redes_geral'][data['redes_geral']['trimestre'] == q]
    top_pub = top_pub[top_pub['indicador'].str.contains('Top 3 fabricantes mais publicados', na=False)]
    top_eng_fab = data['redes_geral'][data['redes_geral']['trimestre'] == q]
    top_eng_fab = top_eng_fab[top_eng_fab['indicador'].str.contains('Top 3 fabricantes mais engajados', na=False)]
    if not top_pub.empty or not top_eng_fab.empty:
        tp1, tp2 = st.columns(2)
        with tp1:
            if not top_pub.empty: render_table(top_pub[['indicador','valor','observacao']], "📸 Top Fabricantes Mais Publicados")
        with tp2:
            if not top_eng_fab.empty: render_table(top_eng_fab[['indicador','valor','observacao']], "🔥 Top Fabricantes Mais Engajados")

    # ── 7. BLOG & NEWSLETTER ─────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">📝</div><div><div class="section-title-premium">Blog &amp; Newsletter</div><div class="section-sub">Conteúdo e engajamento</div></div></div>', unsafe_allow_html=True)

    same_fy24_blog = HISTORICAL_DATA['blog'].get(f'{q}FY24', {})

    bl_col, nw_col = st.columns(2)

    with bl_col:
        st.html(f"""
        <div class="blog-premium">
            <div class="blog-header-premium">
                <div class="blog-icon-premium">📖</div>
                <div>
                    <div class="blog-title-premium">Blog</div>
                    <div class="blog-sub-premium">Conteúdos e performance</div>
                </div>
            </div>
        </div>
        """)
        for metric, label, icon, same_fy24_key in [
            ('visitas',    'Visitas',              '👁️', 'visitas'),
            ('usuarios',   'Usuários',             '👥', 'usuarios'),
            ('blogposts',  'Blogposts Publicados', '📝', None),
            ('tempo_medio','Tempo Médio na Página','⏱️', None),
        ]:
            render_blog_item(
                label=label,
                value=get_current_blog_value(q, metric),
                prev_fy25_value=get_current_blog_value(prev_fy25_q, metric) if prev_fy25_q else '—',
                prev_fy25_name=prev_fy25_name,
                same_fy24_value=same_fy24_blog.get(same_fy24_key, '—') if same_fy24_key else '—',
                same_fy24_name=same_fy24_name if same_fy24_key else '—',
                icon=icon,
            )

    with nw_col:
        st.html(f"""
        <div class="blog-premium">
            <div class="blog-header-premium">
                <div class="blog-icon-premium">📬</div>
                <div>
                    <div class="blog-title-premium">Newsletter</div>
                    <div class="blog-sub-premium">Comunicação direta</div>
                </div>
            </div>
        </div>
        """)
        for metric, label, icon, same_fy24_key, is_pct in [
            ('empresas', 'Empresas',        '🏢', None,             False),
            ('envios',   'Envios',          '📨', None,             False),
            ('abertura', 'Taxa de Abertura','📊', 'abertura_news',  True),
            ('cliques',  'Taxa de Cliques', '🖱️', 'cliques_news',  True),
        ]:
            render_blog_item(
                label=label,
                value=get_current_newsletter_value(q, metric),
                prev_fy25_value=get_current_newsletter_value(prev_fy25_q, metric) if prev_fy25_q else '—',
                prev_fy25_name=prev_fy25_name,
                same_fy24_value=same_fy24_blog.get(same_fy24_key, '—') if same_fy24_key else '—',
                same_fy24_name=same_fy24_name if same_fy24_key else '—',
                is_percentage=is_pct,
                icon=icon,
            )

    # ── 8. APRENDIZADOS ──────────────────────────────────────
    st.markdown(f'<div class="section-premium"><div class="section-icon">📚</div><div><div class="section-title-premium">Aprendizados FY25</div><div class="section-sub">Principais lições do ano</div></div></div>', unsafe_allow_html=True)
    ap1, ap2, ap3 = st.columns(3)
    with ap1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:700;color:#6FBF6F;margin-bottom:16px;">✅ QUE BOM</div>
            <div style="font-size:12px;line-height:1.6;color:{COLORS['text_muted']};">
                • <strong>PowerUP</strong>: Plataforma de inscrição, estratégias online e metas diárias<br>
                • <strong>Case Recrutamento Fortinet</strong>: 80 Leads — virou referência<br>
                • <strong>Segmentação Microsoft</strong>: Timing nos e-mails aumentou quórum<br>
                • <strong>Campanha BU Networking</strong>: Insights valiosos para futuras BUs<br>
                • <strong>Melhora nas cadências</strong>: Contato mais frequente para alinhar jobs
            </div>
        </div>
        """, unsafe_allow_html=True)
    with ap2:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:700;color:#FF8C5A;margin-bottom:16px;">⚠️ QUE PENA</div>
            <div style="font-size:12px;line-height:1.6;color:{COLORS['text_muted']};">
                • <strong>Qualidade das bases</strong>: Necessidade de segmentar melhor os parceiros<br>
                • <strong>Análise constante de resultados</strong>: Todos os jobs precisam ser acompanhados
            </div>
        </div>
        """, unsafe_allow_html=True)
    with ap3:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:700;color:#3399FF;margin-bottom:16px;">💡 QUE TAL — 2026</div>
            <div style="font-size:12px;line-height:1.6;color:{COLORS['text_muted']};">
                • <strong>Intercâmbio de treinamentos</strong>: Calendário ao longo do ano (ID ↔ TDS)<br>
                • <strong>Alinhamentos estratégicos recorrentes</strong>: Incluir agência no planejamento<br>
                • <strong>Metodologia EDGE</strong>: Otimização do formulário de briefing<br>
                • <strong>Retomar alinhamentos institucionais</strong>: Contato próximo com assessoria
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Download sidebar trimestre
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        dl_fmt = st.selectbox("Formato", ["CSV", "Excel"], key="dl_q")
        if st.button(f"📥 Baixar {q}", key="btn_dl_q"):
            rows = [
                {'Categoria':'Peças Produzidas','Valor':pecas_val},
                {'Categoria':'Solicitações','Valor':solic_val},
                {'Categoria':'Campanhas','Valor':camp_val},
                {'Categoria':'Campanhas Solicitadas','Valor':camp_solic},
                {'Categoria':'Campanhas Veiculadas','Valor':camp_veic},
                {'Categoria':'Taxa Conversão','Valor':conv_invest},
                {'Categoria':'Leads Gerados','Valor':leads},
                {'Categoria':'Taxa Entrega E-mail','Valor':entrega_atual},
                {'Categoria':'Taxa Abertura E-mail','Valor':abertura_atual},
                {'Categoria':'Taxa Cliques E-mail','Valor':cliques_atual},
                {'Categoria':'Novos Seguidores','Valor':seg_atual},
                {'Categoria':'Total Engajamentos','Valor':eng_atual},
                {'Categoria':'Total Cliques','Valor':cli_atual},
            ]
            df_dl = pd.DataFrame(rows)
            if dl_fmt == "CSV":
                st.download_button("✅ Baixar CSV", df_dl.to_csv(index=False), f"qbr_{q}.csv", "text/csv")
            else:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as w: df_dl.to_excel(w, index=False, sheet_name=q)
                st.download_button("✅ Baixar Excel", buf.getvalue(), f"qbr_{q}.xlsx")

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="footer-premium">
    ⚡ QBR TD SYNNEX — Powered by Ideatore · Dados atualizados em {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)