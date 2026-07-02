import streamlit as st

def init_session():
    """Inicializa todas as variáveis de sessão"""
    defaults = {
        'theme': 'dark',
        'ano_selecionado': 'FY25',
        'view': 'Q1FY26',
        'sidebar_expanded': True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value