import streamlit as st
from src.config.colors import get_colors

def render_sidebar():
    """Renderiza a barra lateral completa"""
    colors = get_colors()
    
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
        st.markdown("### 📅 Navegação")
        
        ano_selecionado = st.radio(
            "Ano Fiscal",
            options=['FY25', 'FY26'],
            index=0 if st.session_state.ano_selecionado == 'FY25' else 1,
            horizontal=True,
            key='ano_selector'
        )
        st.session_state.ano_selecionado = ano_selecionado
        
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        
        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.markdown("""
        Dashboard QBR TD SYNNEX<br>
        Dados de Performance Marketing<br>
        FY25 - Q1 a Q4 | FY26 - Q1 e Q2
        """, unsafe_allow_html=True)