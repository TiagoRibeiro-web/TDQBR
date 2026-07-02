CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    /* Ajuste principal do container */
    .main .block-container {
        padding: 0 1rem 1rem 1rem;
        max-width: 100%;
    }
    
    /* Esconde header e footer padrão */
    header[data-testid="stHeader"] { display: none; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg, rgba(0, 48, 49, 0.85));
        border-right: 1px solid var(--border, rgba(255,255,255,0.2));
    }
    
    section.main > div {
        padding-top: 0;
    }

    /* Header Premium */
    .premium-header {
        background: linear-gradient(135deg, #003031 0%, #005758 50%, #07bed5 100%);
        padding: 32px 48px 28px 48px;
        margin-bottom: 24px;
        border-radius: 0 0 20px 20px;
        position: relative;
        overflow: hidden;
    }
    .premium-title {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF, #E0E0E0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -1px;
    }
    .premium-sub {
        font-size: 13px;
        color: rgba(255,255,255,0.9);
        margin-top: 6px;
    }
    .premium-quarter {
        font-size: 20px;
        font-weight: 600;
        margin-top: 12px;
        display: inline-block;
        background: rgba(0,0,0,0.3);
        padding: 4px 20px;
        border-radius: 40px;
        color: #FFFFFF;
    }

    /* Cards */
    .glass-card {
        border-radius: 20px;
        padding: 20px;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        height: 100%;
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border);
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    /* KPIs */
    .kpi-premium { text-align: center; }
    .kpi-icon { font-size: 36px; margin-bottom: 10px; }
    .kpi-number {
        font-size: 44px;
        font-weight: 800;
        line-height: 1;
    }
    .kpi-label {
        font-size: 12px;
        margin-top: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    .kpi-variation {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 600;
        margin-top: 6px;
    }
    .kpi-up {
        background: rgba(46,125,50,0.3);
        color: #6FBF6F;
        border: 1px solid rgba(76,175,80,0.4);
    }
    .kpi-down {
        background: rgba(211,47,47,0.3);
        color: #FF8A80;
        border: 1px solid rgba(239,83,80,0.4);
    }
    .kpi-neutral {
        background: rgba(136,146,160,0.3);
        color: #B0BEC5;
        border: 1px solid rgba(136,146,160,0.4);
    }
    .kpi-fy24-up {
        background: rgba(255,183,77,0.2);
        color: #FFD54F;
        border: 1px solid rgba(255,183,77,0.4);
    }
    .kpi-fy24-down {
        background: rgba(255,112,67,0.2);
        color: #FFAB91;
        border: 1px solid rgba(255,112,67,0.4);
    }
    .kpi-fy24-neutral {
        background: rgba(189,189,189,0.2);
        color: #E0E0E0;
        border: 1px solid rgba(189,189,189,0.4);
    }

    /* Seções */
    .section-premium {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 32px 0 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
    }
    .section-premium:first-of-type {
        margin-top: 0;
    }
    .section-icon {
        font-size: 28px;
        background: rgba(7,190,213,0.2);
        padding: 8px;
        border-radius: 14px;
    }
    .section-title-premium {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: var(--text);
    }
    .section-sub {
        font-size: 12px;
        margin-top: 3px;
        color: var(--text-muted);
    }

    /* Barras */
    .bar-premium { margin-bottom: 16px; }
    .bar-track-premium {
        border-radius: 10px;
        height: 36px;
        overflow: hidden;
        background: rgba(0,0,0,0.3);
    }
    .bar-fill-premium {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 14px;
        color: white;
        font-size: 13px;
        font-weight: 600;
    }
    .bar-label-premium {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 13px;
        font-weight: 500;
    }

    /* Blog e Newsletter */
    .blog-premium {
        border-radius: 20px;
        padding: 24px;
        transition: all 0.4s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
        background: rgba(15,43,61,0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.15);
    }
    .blog-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #07bed5, #CCD814, #005758);
    }
    .blog-item-premium {
        margin-bottom: 20px;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .blog-item-premium:last-child {
        margin-bottom: 0;
        border-bottom: none;
    }
    .blog-label-premium {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
        color: rgba(255,255,255,0.7);
    }
    .blog-value-premium {
        font-size: 28px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 6px;
        color: #FFFFFF;
    }
    .blog-change-premium {
        font-size: 9px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }
    .blog-change-up {
        background: rgba(46,125,50,0.4);
        color: #6FBF6F;
    }
    .blog-change-down {
        background: rgba(211,47,47,0.4);
        color: #FF8A80;
    }

    /* Footer */
    .footer-premium {
        margin-top: 40px;
        padding: 20px;
        text-align: center;
        font-size: 11px;
        border-top: 1px solid rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.7);
    }

    /* Animações */
    .kpi-premium, .glass-card {
        animation: fadeInUp 0.4s ease-out;
    }
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
"""

def get_theme_css(colors, background):
    """Retorna CSS com variáveis do tema"""
    return f"""
    <style>
        .stApp {{ background: {background}; }}
        [data-testid="stSidebar"] {{
            background: {colors['card_bg']};
            border-right: 1px solid {colors['border']};
        }}
        [data-testid="stSidebar"] * {{ color: {colors['text']}; }}
        .glass-card {{
            background: {colors['card_bg']};
            backdrop-filter: blur(12px);
            border: 1px solid {colors['border']};
        }}
        .kpi-number {{
            background: {colors['kpi_number_bg']};
            -webkit-background-clip: text;
            background-clip: text;
            color: {colors['kpi_number_color']};
        }}
        .kpi-label, .section-sub {{
            color: {colors['text_muted']};
        }}
        .section-title-premium, .blog-value-premium {{
            color: {colors['text']};
        }}
        .bar-label-premium span:first-child {{
            color: {colors['text']};
        }}
        .stButton button {{
            background: {colors['button_bg']} !important;
            border: 1px solid rgba(7, 190, 213, 0.3) !important;
            color: {colors['text']} !important;
        }}
        .stButton button:hover {{
            background: rgba(7, 190, 213, 0.35) !important;
            border: 1px solid {colors['primary']} !important;
            color: {colors['text']} !important;
        }}
    </style>
    """