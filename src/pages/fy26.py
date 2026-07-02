import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.data.loader import DataLoader
from src.components.kpi import render_kpi
from src.components.charts import render_horizontal_bars
from src.utils.formatters import calc_variation
from src.config.colors import get_colors

def render_fy26_page():
    """Renderiza a visão anual FY26 em andamento"""
    loader = DataLoader()
    quarterly = loader.get_quarterly_summary()
    colors = get_colors()
    
    st.markdown(f"""
    <div class="section-premium">
        <div class="section-icon">📊</div>
        <div>
            <div class="section-title-premium">FY26 em Andamento</div>
            <div class="section-sub">Q1 e Q2 - Acompanhamento de Performance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dados disponíveis
    available = ['Q1FY26', 'Q2FY26']
    
    # KPIs de progresso - Peças
    pecas_q1 = quarterly['Q1FY26']['pecas']
    pecas_q2 = quarterly['Q2FY26']['pecas']
    pecas_total = pecas_q1 + pecas_q2
    pecas_var = calc_variation(pecas_q2, pecas_q1)
    
    st.markdown("### 📦 Peças")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi(pecas_q1, "Q1 FY26", "📦")
    with col2:
        render_kpi(pecas_q2, "Q2 FY26", "📦", pecas_var, "Q1FY26")
    with col3:
        render_kpi(pecas_total, "Total YTD", "📊")
    
    # Solicitações
    solic_q1 = quarterly['Q1FY26']['solic']
    solic_q2 = quarterly['Q2FY26']['solic']
    solic_total = solic_q1 + solic_q2
    solic_var = calc_variation(solic_q2, solic_q1)
    
    st.markdown("### 📋 Solicitações")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi(solic_q1, "Q1 FY26", "📋")
    with col2:
        render_kpi(solic_q2, "Q2 FY26", "📋", solic_var, "Q1FY26")
    with col3:
        render_kpi(solic_total, "Total YTD", "📊")
    
    # Campanhas
    camp_q1 = quarterly['Q1FY26']['camp']
    camp_q2 = quarterly['Q2FY26']['camp']
    camp_total = camp_q1 + camp_q2
    camp_var = calc_variation(camp_q2, camp_q1)
    
    st.markdown("### 🎯 Campanhas")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi(camp_q1, "Q1 FY26", "🎯")
    with col2:
        render_kpi(camp_q2, "Q2 FY26", "🎯", camp_var, "Q1FY26")
    with col3:
        render_kpi(camp_total, "Total YTD", "📊")
    
    # Gráfico comparativo
    st.markdown(f"""
    <div class="section-premium">
        <div class="section-icon">📈</div>
        <div>
            <div class="section-title-premium">Comparativo Q1 vs Q2 FY26</div>
            <div class="section-sub">Evolução das métricas principais</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Q1FY26', 'Q2FY26'],
        y=[pecas_q1, pecas_q2],
        name='Peças',
        marker_color=colors['primary'],
        text=[pecas_q1, pecas_q2],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=['Q1FY26', 'Q2FY26'],
        y=[solic_q1, solic_q2],
        name='Solicitações',
        marker_color=colors['secondary'],
        text=[solic_q1, solic_q2],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=['Q1FY26', 'Q2FY26'],
        y=[camp_q1, camp_q2],
        name='Campanhas',
        marker_color=colors['primary_light'],
        text=[camp_q1, camp_q2],
        textposition='outside'
    ))
    
    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont_color=colors['text'], gridcolor=colors['border']),
        yaxis=dict(tickfont_color=colors['text'], gridcolor=colors['border']),
        legend=dict(font_color=colors['text']),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Distribuição vertical do Q2
    st.markdown(f"""
    <div class="section-premium">
        <div class="section-icon">📊</div>
        <div>
            <div class="section-title-premium">Distribuição por Vertical - Q2 FY26</div>
            <div class="section-sub">% Peças por vertical</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df_vertical = loader.get_vertical_distribution('Q2FY26')
    if not df_vertical.empty:
        render_horizontal_bars(df_vertical, "% Peças por Vertical - Q2 FY26")
    
    # Projeção Anual
    st.markdown(f"""
    <div class="section-premium">
        <div class="section-icon">🔮</div>
        <div>
            <div class="section-title-premium">Projeção Anual FY26</div>
            <div class="section-sub">Baseado nos dados de Q1 e Q2</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Projeção (multiplica por 2 para estimar ano completo)
    with col1:
        projecao_pecas = pecas_total * 2
        st.metric(
            "Projeção Peças",
            f"{projecao_pecas:,}".replace(',', '.'),
            delta=f"+{projecao_pecas - pecas_total:,}".replace(',', '.'),
            delta_color="normal"
        )
    
    with col2:
        projecao_solic = solic_total * 2
        st.metric(
            "Projeção Solicitações",
            f"{projecao_solic:,}".replace(',', '.'),
            delta=f"+{projecao_solic - solic_total:,}".replace(',', '.'),
            delta_color="normal"
        )
    
    with col3:
        projecao_camp = camp_total * 2
        st.metric(
            "Projeção Campanhas",
            f"{projecao_camp:,}".replace(',', '.'),
            delta=f"+{projecao_camp - camp_total:,}".replace(',', '.'),
            delta_color="normal"
        )