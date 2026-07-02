import streamlit as st

THEMES = {
    'dark': {
        'primary': '#07bed5',
        'primary_dark': '#0099b3',
        'primary_light': '#4ad1e8',
        'secondary': '#CCD814',
        'secondary_light': '#e0eb4d',
        'accent': '#005758',
        'accent_light': '#008080',
        'success': '#003031',
        'danger': '#D32F2F',
        'warning': '#FFB74D',
        'background': '#0A1929',
        'card_bg': 'rgba(0, 48, 49, 0.85)',
        'text': '#FFFFFF',
        'text_muted': 'rgba(255,255,255,0.75)',
        'border': 'rgba(255,255,255,0.2)',
        'kpi_number_bg': 'linear-gradient(135deg, #07bed5, #CCD814)',
        'kpi_number_color': 'transparent',
        'button_bg': 'rgba(7, 190, 213, 0.3)',
    },
    'light': {
        'primary': '#07bed5',
        'primary_dark': '#0099b3',
        'primary_light': '#4ad1e8',
        'secondary': '#CCD814',
        'secondary_light': '#e0eb4d',
        'accent': '#005758',
        'accent_light': '#008080',
        'success': '#003031',
        'danger': '#D32F2F',
        'warning': '#FFB74D',
        'background': '#F5F7FA',
        'card_bg': 'rgba(255,255,255,0.95)',
        'text': '#1A2634',
        'text_muted': '#6C757D',
        'border': '#DEE2E6',
        'kpi_number_bg': 'none',
        'kpi_number_color': '#07bed5',
        'button_bg': 'rgba(7, 190, 213, 0.1)',
    }
}

def get_theme():
    """Retorna o tema atual"""
    return st.session_state.get('theme', 'dark')

def get_colors():
    """Retorna as cores do tema atual"""
    return THEMES[get_theme()]

def get_background():
    """Retorna o gradiente de fundo"""
    theme = get_theme()
    if theme == 'dark':
        return "linear-gradient(135deg, #003031 0%, #005758 50%, #0A1929 100%)"
    return "linear-gradient(135deg, #F5F7FA 0%, #E8F0F2 100%)"
def get_vertical_colors():
    """Retorna cores padronizadas para verticais"""
    return {
        'Segurança': '#07bed5',
        'Networking': '#07bed5',
        'Cloud': '#4ad1e8',
        'Data & AI': '#07bed5',
        'Data Center': '#4ad1e8',
        'Institucional': '#4ad1e8',
    }