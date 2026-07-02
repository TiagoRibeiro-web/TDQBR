import streamlit as st
from src.config.colors import get_colors

def render_table(df, title=None):
    """Renderiza uma tabela estilizada"""
    if df.empty:
        return
    
    colors = get_colors()
    
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div style="font-size:18px;font-weight:700;color:{colors["text"]};margin-bottom:16px;">{title}</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)