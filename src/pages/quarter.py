import streamlit as st
import pandas as pd
from src.data.loader import DataLoader
from src.components.kpi import render_kpi, render_metric_card, render_campanhas_card
from src.components.charts import render_horizontal_bars, render_blog_item
from src.components.tables import render_table
from src.utils.formatters import calc_variation, format_number
from src.utils.helpers import get_previous_quarter, get_quarter_info
from src.config.colors import get_colors

def render_quarter_page(quarter):
    """Renderiza página de um trimestre específico"""
    loader = DataLoader()
    data = loader.get_quarter_data(quarter)
    quarterly_summary = loader.get_quarterly_summary()
    colors = get_colors()
    
    # Informações do trimestre
    q_info = get_quarter_info(quarter)
    prev_quarter = get_previous_quarter(quarter)
    prev_name = get_quarter_info(prev_quarter)['name'] if prev_quarter else '—'
    
    # Título
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">📊</div>
        <div>
            <div class="section-title-premium">Overview {quarter}</div>
            <div class="section-sub">Indicadores de performance</div>
        </div>
    </div>
    """)
    
    # ==================== KPIs PRINCIPAIS ====================
    pecas = data.get('pecas', 0)
    solicitacoes = data.get('solicitacoes', 0)
    campanhas = data.get('campanhas', 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_kpi(pecas, "Peças Produzidas", "📦")
    with col2:
        render_kpi(solicitacoes, "Solicitações", "📋")
    with col3:
        render_kpi(campanhas, "Campanhas", "🎯")
    
    # ==================== DISTRIBUIÇÃO POR VERTICAL ====================
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">📊</div>
        <div>
            <div class="section-title-premium">Distribuição por Vertical</div>
            <div class="section-sub">% Peças por vertical</div>
        </div>
    </div>
    """)
    
    df_vertical = loader.get_vertical_distribution(quarter)
    if not df_vertical.empty:
        render_horizontal_bars(df_vertical, "% Peças por Vertical")
    
    # ==================== CAMPANHAS ====================
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">🎯</div>
        <div>
            <div class="section-title-premium">Campanhas</div>
            <div class="section-sub">Métricas e destaques</div>
        </div>
    </div>
    """)
    
    render_campanhas_card(quarter)
    
    # ==================== FABRICANTES ====================
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">🏭</div>
        <div>
            <div class="section-title-premium">Fabricantes por Vertical</div>
            <div class="section-sub">Principais fornecedores</div>
        </div>
    </div>
    """)
    
    df_fab = loader.get_fabricantes(quarter)
    if not df_fab.empty:
        render_table(df_fab, "🏭 Fabricantes por Vertical")
    
    # ==================== EMAIL MARKETING ====================
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">📧</div>
        <div>
            <div class="section-title-premium">E-mail Marketing</div>
            <div class="section-sub">Métricas de performance</div>
        </div>
    </div>
    """)
    
    email_data = data.get('email', {})
    if email_data:
        entrega = email_data.get('entrega', '—')
        abertura = email_data.get('abertura', '—')
        cliques = email_data.get('cliques', '—')
        optout = email_data.get('optout', '—')
        
        # Buscar dados anteriores
        prev_data = {}
        if prev_quarter:
            prev_q_data = loader.get_quarter_data(prev_quarter)
            prev_email = prev_q_data.get('email', {})
            prev_data = {
                'entrega': prev_email.get('entrega', '—'),
                'abertura': prev_email.get('abertura', '—'),
                'cliques': prev_email.get('cliques', '—'),
                'optout': prev_email.get('optout', '—')
            }
        
        col1, col2, col3, col4 = st.columns(4)
        
        def fmt(v): return f"{v}%" if v != '—' else '—'
        
        with col1:
            render_metric_card("Entregas", "✅", fmt(entrega), fmt(prev_data.get('entrega', '—')), prev_name)
        with col2:
            render_metric_card("Aberturas", "👁️", fmt(abertura), fmt(prev_data.get('abertura', '—')), prev_name)
        with col3:
            render_metric_card("Cliques", "🖱️", fmt(cliques), fmt(prev_data.get('cliques', '—')), prev_name)
        with col4:
            render_metric_card("Opt-Out", "🚫", fmt(optout), fmt(prev_data.get('optout', '—')), prev_name)
        
        # Envios
        envios = data.get('email_envios', None)
        if envios:
            st.metric("Total de Envios", format_number(envios))
    
    # ==================== REDES SOCIAIS ====================
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">📱</div>
        <div>
            <div class="section-title-premium">Redes Sociais</div>
            <div class="section-sub">Engajamento e alcance</div>
        </div>
    </div>
    """)
    
    redes_data = data.get('redes', {})
    if redes_data:
        seguidores = redes_data.get('seguidores', '—')
        engajamentos = redes_data.get('engajamentos', '—')
        cliques_redes = redes_data.get('cliques', '—')
        
        # Dados anteriores
        prev_redes = {}
        if prev_quarter:
            prev_q_data = loader.get_quarter_data(prev_quarter)
            prev_redes = prev_q_data.get('redes', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Novos Seguidores", "👥", seguidores, 
                             prev_redes.get('seguidores', '—'), prev_name)
        with col2:
            render_metric_card("Engajamentos", "❤️", engajamentos,
                             prev_redes.get('engajamentos', '—'), prev_name)
        with col3:
            render_metric_card("Cliques", "🖱️", cliques_redes,
                             prev_redes.get('cliques', '—'), prev_name)
    
    # ==================== BLOG E NEWSLETTER ====================
    st.html(f"""
    <div class="section-premium">
        <div class="section-icon">📝</div>
        <div>
            <div class="section-title-premium">Blog &amp; Newsletter</div>
            <div class="section-sub">Conteúdo e engajamento</div>
        </div>
    </div>
    """)
    
    blog_data = data.get('blog', {})
    newsletter_data = data.get('newsletter', {})
    
    if blog_data or newsletter_data:
        col_blog, col_news = st.columns(2)
        
        with col_blog:
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
            
            # Dados do blog
            blog_items = [
                ('visitas', 'Visitas', '👁️'),
                ('usuarios', 'Usuários', '👥'),
                ('blogposts', 'Blogposts Publicados', '📝'),
                ('tempo_medio', 'Tempo Médio', '⏱️')
            ]
            
            for key, label, icon in blog_items:
                value = blog_data.get(key, '—')
                # Buscar valor anterior
                prev_val = '—'
                if prev_quarter:
                    prev_q_data = loader.get_quarter_data(prev_quarter)
                    prev_blog = prev_q_data.get('blog', {})
                    prev_val = prev_blog.get(key, '—')
                
                render_blog_item(label, value, prev_val, prev_name, 
                               icon=icon, is_percentage=False)
        
        with col_news:
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
            
            # Dados da newsletter
            news_items = [
                ('empresas', 'Empresas', '🏢'),
                ('envios', 'Envios', '📨'),
                ('abertura', 'Taxa de Abertura', '📊'),
                ('cliques', 'Taxa de Cliques', '🖱️')
            ]
            
            for key, label, icon in news_items:
                value = newsletter_data.get(key, '—')
                prev_val = '—'
                if prev_quarter:
                    prev_q_data = loader.get_quarter_data(prev_quarter)
                    prev_news = prev_q_data.get('newsletter', {})
                    prev_val = prev_news.get(key, '—')
                
                is_percentage = key in ['abertura', 'cliques']
                render_blog_item(label, value, prev_val, prev_name, 
                               icon=icon, is_percentage=is_percentage)