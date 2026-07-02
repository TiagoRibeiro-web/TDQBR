import streamlit as st
import pandas as pd
from src.data.loader import DataLoader
from src.components.kpi import render_kpi
from src.components.charts import render_horizontal_bars, render_comparative_charts
from src.components.tables import render_table
from src.config.colors import get_colors

def render_fy25_page():
    """Renderiza a visão anual FY25"""
    loader = DataLoader()
    quarterly = loader.get_quarterly_summary()
    
    render_comparative_charts(quarterly)
    
    colors = get_colors()
    
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Overview Anual FY25</div><div class="section-sub">Indicadores consolidados FY25</div></div></div>', unsafe_allow_html=True)
    
    pecas_tot = sum(quarterly[t]['pecas'] for t in ['Q1','Q2','Q3','Q4'])
    solic_tot = sum(quarterly[t]['solic'] for t in ['Q1','Q2','Q3','Q4'])
    camp_tot = sum(quarterly[t]['camp'] for t in ['Q1','Q2','Q3','Q4'])
    
    k1, k2, k3 = st.columns(3)
    with k1: render_kpi(pecas_tot, "Total Peças FY25", "📦")
    with k2: render_kpi(solic_tot, "Total Solicitações FY25", "📋")
    with k3: render_kpi(camp_tot, "Total Campanhas FY25", "🎯")
    
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">Média anual FY25</div></div></div>', unsafe_allow_html=True)
    
    vert_vals = {}
    for t in ['Q1','Q2','Q3','Q4']:
        df_vert = loader.get_vertical_distribution(t)
        if not df_vert.empty:
            for _, row in df_vert.iterrows():
                vert_vals.setdefault(row['vertical'], []).append(row['percentual'])
    
    if vert_vals:
        df_annual = pd.DataFrame([{'vertical': v, 'percentual': sum(ps)/len(ps)} 
                                  for v, ps in vert_vals.items()]).sort_values('percentual', ascending=False)
        render_horizontal_bars(df_annual, "% Peças por Vertical (Média Anual FY25)")
    
    st.markdown(f'<div class="section-premium"><div class="section-icon">🎯</div><div><div class="section-title-premium">Campanhas</div><div class="section-sub">Métricas por trimestre FY25</div></div></div>', unsafe_allow_html=True)
    
    # Campanhas anuais
    st.markdown(f"""
    <div class="glass-card">
        <div style="text-align:center; margin-bottom:20px;">
            <div style="font-size:20px;font-weight:700;color:{colors['text']};">🎯 Campanhas por Trimestre FY25</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
    """, unsafe_allow_html=True)
    
    for t in ['Q1', 'Q2', 'Q3', 'Q4']:
        camp = loader.get_quarter_data(t).get('campanhas_detalhes', {})
        st.markdown(f"""
            <div style="text-align:center; padding:16px; background:rgba(0,0,0,0.2); border-radius:16px;">
                <div style="font-size:18px;font-weight:700;color:{colors['primary']};margin-bottom:12px;">{t}</div>
                <div style="font-size:13px;color:{colors['text_muted']};margin-bottom:8px;">Solicitadas: <strong style="color:{colors['text']};">{camp.get('solicitadas', '—')}</strong></div>
                <div style="font-size:13px;color:{colors['text_muted']};margin-bottom:8px;">Veiculadas: <strong style="color:{colors['text']};">{camp.get('veiculadas', '—')}</strong></div>
                <div style="font-size:13px;color:{colors['text_muted']};">Leads: <strong style="color:{colors['text']};">{camp.get('leads', '—')}</strong></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-premium"><div class="section-icon">🏭</div><div><div class="section-title-premium">Fabricantes por Vertical</div><div class="section-sub">Destaques FY25 Q4</div></div></div>', unsafe_allow_html=True)
    
    df_fab = loader.get_fabricantes('Q4')
    if not df_fab.empty:
        render_table(df_fab, "🏭 Fabricantes por Vertical (Q4 FY25)")