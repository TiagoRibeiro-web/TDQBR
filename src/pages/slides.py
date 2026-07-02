import streamlit as st
from src.config.colors import get_colors

# Conteúdo dos slides - vamos manter o que já existe
SLIDES_CONTENT = {
    'Q1': {
        'titulo': 'Q1 FY25 - Análise de Performance',
        'secoes': {
            'Visão Geral': {
                'titulo': '📊 Visão Geral',
                'conteudo': '**Destaques do Q1 FY25:**\n\n• 518 peças produzidas\n• 108 solicitações de campanhas\n• 4 campanhas veiculadas\n• Taxa de conversão de 7,26%'
            }
            # ... mais seções
        }
    }
    # ... mais trimestres
}

def render_slides_page():
    """Renderiza a página de slides"""
    colors = get_colors()
    
    st.markdown(f"""
    <div class="section-premium">
        <div class="section-icon">📄</div>
        <div>
            <div class="section-title-premium">Conteúdo dos Slides QBR</div>
            <div class="section-sub">Transcrição completa das apresentações por trimestre</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Seleção do trimestre
    if st.session_state.ano_selecionado == 'FY25':
        slide_opcoes = ['Q1', 'Q2', 'Q3', 'Q4']
    else:
        slide_opcoes = ['Q1FY26', 'Q2FY26']
    
    slide_trimestre = st.selectbox(
        "Selecione o trimestre para visualizar o conteúdo dos slides",
        slide_opcoes,
        index=0,
        key='slide_selector'
    )
    
    slides = SLIDES_CONTENT.get(slide_trimestre, {})
    
    if slides:
        st.markdown(f"""
        <div style="margin-bottom: 32px;">
            <div style="font-size:28px;font-weight:800;color:{colors['primary']};margin-bottom:8px;">{slides.get('titulo', '')}</div>
            <div style="font-size:14px;color:{colors['text_muted']};">Documentação completa das análises e insights do trimestre</div>
        </div>
        """, unsafe_allow_html=True)
        
        for secao_key, secao in slides.get('secoes', {}).items():
            titulo_secao = secao.get('titulo', secao_key.replace('_', ' ').title())
            conteudo = secao.get('conteudo', '')
            
            with st.expander(f"{titulo_secao}", expanded=True):
                st.markdown(conteudo)
        
        # Botão para baixar slides
        all_content = ""
        for secao_key, secao in slides.get('secoes', {}).items():
            titulo = secao.get('titulo', secao_key)
            conteudo = secao.get('conteudo', '')
            conteudo_limpo = conteudo.replace('**', '').replace('🏆', '[TOP]').replace('✅', '[BOM]').replace('⚠️', '[PENA]').replace('💡', '[TAL]')
            all_content += f"=== {titulo} ===\n{conteudo_limpo}\n\n"
        
        st.download_button(
            label="📥 Baixar Conteúdo dos Slides (TXT)",
            data=all_content,
            file_name=f"slides_qbr_{slide_trimestre}.txt",
            mime="text/plain",
            key='download_slides'
        )
    else:
        st.info(f"Conteúdo dos slides não disponível para {slide_trimestre}.")