import streamlit as st
from src.config.colors import get_colors
from src.utils.formatters import format_number, calc_variation, clean_value

def render_kpi(value, label, icon, variation=None, variation_label=None, 
               comparison_value=None, comparison_label=None):
    """Renderiza um card KPI com variações"""
    colors = get_colors()
    
    display_value = format_number(value)
    if isinstance(display_value, str) and display_value.endswith('%'):
        display_value = display_value[:-1]
    
    is_percentage = '%' in str(value) or label in ['Taxa de Abertura', 'Taxa de Cliques', 'Entregas', 'Aberturas', 'Cliques', 'Opt-Out']
    final_display = f"{display_value}%" if is_percentage and display_value != '—' else display_value
    
    badges = []
    
    if variation is not None and variation_label:
        if variation > 0:
            cls = 'kpi-up'
            arrow = '↑'
        elif variation < 0:
            cls = 'kpi-down'
            arrow = '↓'
        else:
            cls = 'kpi-neutral'
            arrow = '→'
        badges.append(f'<div class="{cls}">{arrow} {abs(variation):.1f}% <span style="font-size:9px;">vs {variation_label}</span></div>')
    
    if comparison_value is not None and comparison_label:
        comp_var = calc_variation(value, comparison_value)
        if comp_var is not None:
            if comp_var > 0:
                cls = 'kpi-fy24-up'
                arrow = '↑'
            elif comp_var < 0:
                cls = 'kpi-fy24-down'
                arrow = '↓'
            else:
                cls = 'kpi-fy24-neutral'
                arrow = '→'
            badges.append(f'<div class="{cls}">{arrow} {abs(comp_var):.1f}% <span style="font-size:9px;">vs {comparison_label}</span></div>')
    
    badge_html = ''.join(badges)
    
    st.html(f"""
    <div class="glass-card kpi-premium">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-number">{final_display}</div>
        <div class="kpi-label">{label}</div>
        {badge_html}
    </div>
    """)

def render_metric_card(metric_name, icon, current_value, prev_fy25_value, prev_fy25_name, 
                       prev_fy24_value=None, prev_fy24_name=None, tooltip=None):
    """Renderiza um card de métrica com comparativos"""
    colors = get_colors()
    
    cur_raw = clean_value(current_value)
    if isinstance(cur_raw, str) and cur_raw.endswith('%'):
        cur_raw = cur_raw[:-1]
    
    prev25 = clean_value(prev_fy25_value) if prev_fy25_value not in ('—', None) else '—'
    if isinstance(prev25, str) and prev25.endswith('%'):
        prev25 = prev25[:-1]
    
    var25 = calc_variation(cur_raw, prev25) if prev25 != '—' else None
    
    is_percentage = '%' in str(current_value) or metric_name in ['Entregas', 'Aberturas', 'Cliques', 'Opt-Out', 'Taxa de Abertura', 'Taxa de Cliques']
    suffix = '%' if is_percentage and cur_raw != '—' else ''
    display_cur = f"{cur_raw}{suffix}"
    display_prev25 = f"{prev25}{suffix}" if prev25 != '—' else '—'
    
    tip_html = f'<span style="font-size:10px;opacity:0.6;margin-left:4px;" title="{tooltip}">ⓘ</span>' if tooltip else ''
    
    def comp_badge(v):
        if v is None: return ''
        if v > 0: return f'<span class="comp-badge badge-up">▲ {v:.1f}%</span>'
        if v < 0: return f'<span class="comp-badge badge-down">▼ {abs(v):.1f}%</span>'
        return f'<span class="comp-badge badge-flat">→ 0%</span>'
    
    fy24_row = ''
    if prev_fy24_value is not None and prev_fy24_name:
        prev24_raw = str(prev_fy24_value)
        if prev24_raw.endswith('%'):
            prev24_raw = prev24_raw[:-1]
        prev24_str = f"{prev24_raw}{suffix}"
        var24 = calc_variation(cur_raw, prev24_raw)
        fy24_row = f"""
        <div class="comparison-row">
            <span class="comp-label fy24-label">📅 {prev_fy24_name}</span>
            <span class="comp-value fy24-value">{prev24_str}</span>
            {comp_badge(var24)}
        </div>"""
    
    st.html(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:34px;margin-bottom:8px;">{icon}</div>
        <div style="font-size:36px;font-weight:800;color:{colors['text']};">{display_cur}</div>
        <div style="font-size:13px;color:{colors['text_muted']};margin-bottom:14px;">{metric_name}{tip_html}</div>
        <div class="comparison-premium">
            <div class="comparison-header">📊 Comparativo</div>
            <div class="comparison-row">
                <span class="comp-label">🔄 {prev_fy25_name}</span>
                <span class="comp-value">{display_prev25}</span>
                {comp_badge(var25)}
            </div>
            {fy24_row}
        </div>
    </div>
    """)

def render_campanhas_card(quarter, is_annual=False):
    """Renderiza o card de campanhas para um trimestre específico"""
    from src.data.loader import DataLoader
    loader = DataLoader()
    data = loader.get_quarter_data(quarter)
    camp = data.get('campanhas_detalhes', {})
    colors = get_colors()
    
    if is_annual:
        html_content = f"""
        <div class="glass-card">
            <div style="text-align:center; margin-bottom:20px;">
                <div style="font-size:20px;font-weight:700;color:{colors['text']};">🎯 Campanhas por Trimestre FY25</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
        """
        
        for t in ['Q1', 'Q2', 'Q3', 'Q4']:
            camp_data = loader.get_quarter_data(t).get('campanhas_detalhes', {})
            html_content += f"""
                <div style="text-align:center; padding:16px; background:rgba(0,0,0,0.2); border-radius:16px;">
                    <div style="font-size:18px;font-weight:700;color:{colors['primary']};margin-bottom:12px;">{t}</div>
                    <div style="font-size:13px;color:{colors['text_muted']};margin-bottom:8px;">Solicitadas: <strong style="color:{colors['text']};">{camp_data.get('solicitadas', '—')}</strong></div>
                    <div style="font-size:13px;color:{colors['text_muted']};margin-bottom:8px;">Veiculadas: <strong style="color:{colors['text']};">{camp_data.get('veiculadas', '—')}</strong></div>
                    <div style="font-size:13px;color:{colors['text_muted']};">Leads: <strong style="color:{colors['text']};">{camp_data.get('leads', '—')}</strong></div>
                </div>
            """
        
        html_content += """
            </div>
        </div>
        """
        st.html(html_content)
        return
    
    if not camp:
        st.info("Nenhum dado de campanha disponível para este trimestre.")
        return
    
    # Distribuição por objetivo
    obj_dist = {
        'conversao': camp.get('objetivo_conversao', 100),
        'branding': camp.get('objetivo_branding', 0)
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.html(f"""
        <div class="glass-card">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;">
                <div style="text-align:center;">
                    <div style="font-size:12px;color:{colors['text_muted']};margin-bottom:8px;">📋 Solicitadas</div>
                    <div style="font-size:42px;font-weight:800;color:{colors['text']};">{camp.get('solicitadas', '—')}</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:12px;color:{colors['text_muted']};margin-bottom:8px;">🚀 Veiculadas</div>
                    <div style="font-size:42px;font-weight:800;color:{colors['text']};">{camp.get('veiculadas', '—')}</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                <div style="text-align:center;">
                    <div style="font-size:12px;color:{colors['text_muted']};margin-bottom:8px;">📊 Taxa Conversão (c/ inv)</div>
                    <div style="font-size:24px;font-weight:800;color:#6FBF6F;">{camp.get('taxa_conversao_com_investimento', camp.get('taxa_conversao', '—'))}%</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:12px;color:{colors['text_muted']};margin-bottom:8px;">👥 Leads Gerados</div>
                    <div style="font-size:28px;font-weight:800;color:{colors['text']};">{camp.get('leads', '—')}</div>
                </div>
            </div>
        </div>
        """)
    
    with col2:
        st.html(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:700;color:{colors['text']};margin-bottom:16px;">🏆 Top Campanhas</div>
            <div style="font-size:13px;line-height:1.6;color:{colors['text']};margin-bottom:20px;">{camp.get('top', '—')}</div>
            <div style="font-size:14px;font-weight:600;color:{colors['text']};margin:20px 0 12px;">📊 Distribuição por Objetivo</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="background:rgba(46,125,50,0.2);border-radius:16px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:{colors['text_muted']};">Conversão</div>
                    <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{obj_dist.get('conversao', '100')}%</div>
                </div>
                <div style="background:rgba(255,107,53,0.2);border-radius:16px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:{colors['text_muted']};">Branding</div>
                    <div style="font-size:28px;font-weight:800;color:#FF8C5A;">{obj_dist.get('branding', '0')}%</div>
                </div>
            </div>
        </div>
        """)