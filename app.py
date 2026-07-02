import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="TD SYNNEX Dashboard",
    page_icon="📊",
    layout="wide"
)

# Importações dos módulos refatorados
from src.config import init_session, get_colors, get_background, get_theme
from src.styles import CSS, get_theme_css
from src.components import render_sidebar
from src.pages import render_fy25_page, render_fy26_page, render_quarter_page, render_slides_page
from src.data import DataLoader

def main():
    # Inicialização
    init_session()
    
    # Aplicar CSS base
    st.markdown(CSS, unsafe_allow_html=True)
    
    # Aplicar CSS do tema
    colors = get_colors()
    background = get_background()
    st.markdown(get_theme_css(colors, background), unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="premium-header" style="background: linear-gradient(135deg, #003031 0%, #005758 50%, #07bed5 100%);">
        <div class="premium-title">TD SYNNEX BR</div>
        <div class="premium-sub">Quarterly Business Review · Performance Analytics</div>
        <div class="premium-quarter">{st.session_state.get('view', 'Q1FY26')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # ========== NOVO: Botão toggle sidebar ==========
    col_toggle1, col_toggle2 = st.columns([0.96, 0.04])
    with col_toggle2:
        if st.button('☰' if not st.session_state.sidebar_expanded else '✕', 
                     key='btn_toggle_sidebar',
                     help='Mostrar/Ocultar menu lateral',
                     use_container_width=True):
            st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded
            st.rerun()
    # =================================================
    
    if 'view' not in st.session_state:
        st.session_state.view = 'Q1FY26'
    
    # ==================== BOTÕES DE NAVEGAÇÃO ====================
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    if st.session_state.ano_selecionado == 'FY25':
        st.markdown("### 📆 Navegação FY25")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            if st.button('📌 Q1', key='q1_25', use_container_width=True):
                st.session_state.view = 'Q1'
                st.rerun()
        with col2:
            if st.button('📌 Q2', key='q2_25', use_container_width=True):
                st.session_state.view = 'Q2'
                st.rerun()
        with col3:
            if st.button('📌 Q3', key='q3_25', use_container_width=True):
                st.session_state.view = 'Q3'
                st.rerun()
        with col4:
            if st.button('📌 Q4', key='q4_25', use_container_width=True):
                st.session_state.view = 'Q4'
                st.rerun()
        with col5:
            if st.button('🏆 Visão Anual', key='annual_25', use_container_width=True):
                st.session_state.view = 'FY25'
                st.rerun()
        with col6:
            if st.button('📄 Slides', key='slides_25', use_container_width=True):
                st.session_state.view = 'Slides'
                st.rerun()
    else:  # FY26
        st.markdown("### 🔷 Navegação FY26")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button('🔷 Q1 FY26', key='q1_26', use_container_width=True):
                st.session_state.view = 'Q1FY26'
                st.rerun()
        with col2:
            if st.button('🔷 Q2 FY26', key='q2_26', use_container_width=True):
                st.session_state.view = 'Q2FY26'
                st.rerun()
        with col3:
            if st.button('🏆 Visão Anual', key='annual_26', use_container_width=True):
                st.session_state.view = 'FY26'
                st.rerun()
        with col4:
            if st.button('📄 Slides', key='slides_26', use_container_width=True):
                st.session_state.view = 'Slides'
                st.rerun()
    
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    # ==================== ROTEAMENTO ====================
    view = st.session_state.get('view', 'Q1FY26')
    
    if view == 'Slides':
        render_slides_page()
    elif view == 'FY25':
        render_fy25_page()
    elif view == 'FY26':
        render_fy26_page()
    elif view in ['Q1', 'Q2', 'Q3', 'Q4', 'Q1FY26', 'Q2FY26']:
        render_quarter_page(view)
    else:
        st.warning(f"View '{view}' não reconhecida. Selecionando Q1FY26 como padrão.")
        st.session_state.view = 'Q1FY26'
        st.rerun()
    
    # ==================== FOOTER ====================
    st.markdown(f"""
    <div class="footer-premium">
        ⚡ QBR TD SYNNEX — Powered by Ideatore · Dados atualizados em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()