import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.config.colors import get_colors, get_vertical_colors
from src.utils.formatters import calc_variation, clean_value

def render_horizontal_bars(df, title):
    """Renderiza gráfico de barras horizontais"""
    if df is None or df.empty:
        return
    
    colors = get_colors()
    vertical_colors = get_vertical_colors()
    
    df = df.copy()
    df = df.sort_values('percentual', ascending=False)
    
    st.markdown(f'<div class="glass-card"><div style="font-size:18px;font-weight:700;color:{colors["text"]};margin-bottom:20px;">📊 {title}</div>', unsafe_allow_html=True)
    
    for _, row in df.iterrows():
        pct = row['percentual']
        color = vertical_colors.get(row['vertical'], '#07bed5')
        
        st.markdown(f"""
        <div class="bar-premium">
            <div class="bar-label-premium">
                <span style="color:{colors['text']};">{row['vertical']}</span>
                <span style="color:{color}; font-weight:600;">{pct:.1f}%</span>
            </div>
            <div class="bar-track-premium">
                <div class="bar-fill-premium" style="width:{pct}%;background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_comparative_charts(quarterly_data):
    """Renderiza gráficos comparativos trimestrais"""
    colors = get_colors()
    
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Comparativo Trimestral FY25</div><div class="section-sub">Análise Q1 a Q4 FY25</div></div></div>', unsafe_allow_html=True)
    
    fy25_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    
    for key, label, color in [('pecas','Peças',colors['primary']),
                              ('solic','Solicitações',colors['secondary']),
                              ('camp','Campanhas',colors['success'])]:
        df_c = pd.DataFrame([{'trimestre': t, 'valor': quarterly_data[t][key]} for t in fy25_quarters])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_c['trimestre'], y=df_c['valor'], name=label,
                             marker=dict(color=color), text=df_c['valor'], textposition='outside',
                             textfont=dict(color=colors['text'])))
        fig.add_trace(go.Scatter(x=df_c['trimestre'], y=df_c['valor'], mode='lines+markers',
                                 name='Tendência', line=dict(color=colors['secondary'] if key!='solic' else colors['primary'], width=3),
                                 marker=dict(size=10)))
        fig.update_layout(title=f'{label} por Trimestre', title_font_color=colors['text'],
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(tickfont_color=colors['text'], gridcolor=colors['border']),
                          yaxis=dict(tickfont_color=colors['text'], gridcolor=colors['border']),
                          legend=dict(font_color=colors['text']), height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_blog_item(label, value, prev_value, prev_name, fy24_value=None, 
                     fy24_label=None, is_percentage=False, icon="📊"):
    """Renderiza um item do blog com comparações"""
    val_raw = clean_value(value)
    prev_raw = clean_value(prev_value) if prev_value not in ('—', None) else '—'
    
    if isinstance(val_raw, str) and val_raw.endswith('%'):
        val_raw = val_raw[:-1]
    if isinstance(prev_raw, str) and prev_raw.endswith('%'):
        prev_raw = prev_raw[:-1]
    
    var = calc_variation(val_raw, prev_raw) if prev_raw != '—' else None
    suffix = '%' if is_percentage and val_raw != '—' else ''
    
    display_val = f"{val_raw}{suffix}"
    display_prev = f"{prev_raw}{suffix}" if prev_raw != '—' else '—'
    
    def badge(v, cls_up='blog-change-up', cls_down='blog-change-down'):
        if v is None: return ''
        arrow = '▲' if v > 0 else '▼'
        cls = cls_up if v > 0 else cls_down
        return f'<span class="blog-change-premium {cls}">{arrow} {abs(v):.1f}%</span>'
    
    fy24_html = ''
    if fy24_value is not None and fy24_label:
        fy24_raw = str(fy24_value)
        if isinstance(fy24_raw, str) and fy24_raw.endswith('%'):
            fy24_raw = fy24_raw[:-1]
        fy24_str = f"{fy24_raw}{suffix}"
        var24 = calc_variation(val_raw, fy24_raw)
        fy24_html = f'<div class="blog-compare-fy24"><span>📅 vs {fy24_label}: <strong>{fy24_str}</strong></span>{badge(var24,"blog-change-up","blog-change-down")}</div>'
    
    st.markdown(f"""
    <div class="blog-item-premium">
        <div class="blog-label-premium">{icon} {label}</div>
        <div class="blog-value-premium">{display_val}</div>
        <div class="blog-compare-premium">
            <span>🔄 vs {prev_name}: {display_prev}</span>
            {badge(var)}
        </div>
        {fy24_html}
    </div>
    """, unsafe_allow_html=True)