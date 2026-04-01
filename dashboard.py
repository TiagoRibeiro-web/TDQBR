import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import io
import zipfile
from pathlib import Path
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="TD SYNNEX Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==================== TEMA ====================
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

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
    st.markdown("### ℹ️ Sobre")
    st.markdown("""
    Dashboard QBR TD SYNNEX<br>
    Dados de Performance Marketing<br>
    FY25 - Q1 a Q4
    """, unsafe_allow_html=True)

# ==================== CORES BASEADAS NO TEMA ====================
if st.session_state.theme == 'dark':
    COLORS = {
        'primary': '#0066CC',
        'primary_dark': '#004999',
        'primary_light': '#3399FF',
        'secondary': '#FF6B35',
        'secondary_light': '#FF8C5A',
        'accent': '#7B2CBF',
        'accent_light': '#9D4EDD',
        'success': '#2E7D32',
        'danger': '#D32F2F',
        'warning': '#FFB74D',
        'background': '#0A1929',
        'card_bg': 'rgba(15, 43, 61, 0.85)',
        'text': '#FFFFFF',
        'text_muted': 'rgba(255,255,255,0.75)',
        'border': 'rgba(255,255,255,0.2)',
        'kpi_number_bg': 'linear-gradient(135deg, #FFFFFF, #E0E0E0)',
        'kpi_number_color': 'transparent',
        'button_bg': 'rgba(0,102,204,0.3)',
        'button_hover': '#0066CC',
    }
    BG_GRADIENT = "linear-gradient(135deg, #0A1929 0%, #0F2B3D 100%)"
else:
    COLORS = {
        'primary': '#0066CC',
        'primary_dark': '#004999',
        'primary_light': '#3399FF',
        'secondary': '#FF6B35',
        'secondary_light': '#FF8C5A',
        'accent': '#7B2CBF',
        'accent_light': '#9D4EDD',
        'success': '#2E7D32',
        'danger': '#D32F2F',
        'warning': '#FFB74D',
        'background': '#F5F7FA',
        'card_bg': 'rgba(255,255,255,0.95)',
        'text': '#1A2634',
        'text_muted': '#6C757D',
        'border': '#DEE2E6',
        'kpi_number_bg': 'none',
        'kpi_number_color': '#0066CC',
        'button_bg': 'rgba(0,102,204,0.1)',
        'button_hover': '#0066CC',
    }
    BG_GRADIENT = "linear-gradient(135deg, #F5F7FA 0%, #FFFFFF 100%)"

# ==================== DADOS FALLBACK HARDCODED ====================
FALLBACK_DATA = {
    'pecas': {'Q1': 518, 'Q2': 692, 'Q3': 674, 'Q4': 647},
    'solicitacoes': {'Q1': 108, 'Q2': 159, 'Q3': 100, 'Q4': 131},
    'campanhas': {'Q1': 4, 'Q2': 9, 'Q3': 7, 'Q4': 6},
    'pecas_fy24': {'Q1': None, 'Q2': None, 'Q3': None, 'Q4': 838},
    'solicitacoes_fy24': {'Q1': None, 'Q2': None, 'Q3': None, 'Q4': 193},
    'campanhas_fy24': {'Q1': None, 'Q2': None, 'Q3': None, 'Q4': 4},
    'email': {
        'Q1': {'entrega': 95.7, 'abertura': 35.8, 'cliques': 1.7, 'optout': 0.04},
        'Q2': {'entrega': 98.4, 'abertura': 45.3, 'cliques': 2.6, 'optout': 0.07},
        'Q3': {'entrega': 96.0, 'abertura': 38.0, 'cliques': 6.0, 'optout': 0.05},
        'Q4': {'entrega': 93.0, 'abertura': 24.0, 'cliques': 2.2, 'optout': 0.02},
    },
    'email_envios': {'Q1': 169948, 'Q2': 122639, 'Q3': 134035, 'Q4': 349487},
    'email_fy24': {
        'Q1': {'entrega': 99.44, 'abertura': 44.11, 'cliques': 2.03, 'optout': 0.07},
        'Q2': {'entrega': 96.96, 'abertura': 30.01, 'cliques': 1.94, 'optout': 0.14},
        'Q3': {'entrega': 94.0, 'abertura': 42.0, 'cliques': 1.36, 'optout': 0.06},
        'Q4': {'entrega': 94.0, 'abertura': 24.0, 'cliques': 1.3, 'optout': 0.04},
    },
    'email_envios_fy24': {'Q1': 169948, 'Q2': 122639, 'Q3': 134035, 'Q4': 349487},
    'redes': {
        'Q1': {'seguidores': 1230, 'engajamentos': 81419, 'cliques': 6117},
        'Q2': {'seguidores': 1688, 'engajamentos': 10237, 'cliques': 8585},
        'Q3': {'seguidores': 1927, 'engajamentos': 76102, 'cliques': 36375},
        'Q4': {'seguidores': 2296, 'engajamentos': 58046, 'cliques': 51119},
    },
    'redes_fy24': {
        'Q1': {'seguidores': 1361, 'engajamentos': 17583, 'cliques': 12983},
        'Q2': {'seguidores': 1361, 'engajamentos': 17583, 'cliques': 12983},
        'Q3': {'seguidores': 1361, 'engajamentos': 17583, 'cliques': 12983},
        'Q4': {'seguidores': 764, 'engajamentos': 19348, 'cliques': 23131},
    },
    'blog': {
        'Q1': {'visitas': 24926, 'usuarios': 17075, 'blogposts': 31, 'tempo_medio': '5:00'},
        'Q2': {'visitas': 16137, 'usuarios': 11295, 'blogposts': 25, 'tempo_medio': '4:04'},
        'Q3': {'visitas': 13353, 'usuarios': 7037, 'blogposts': 26, 'tempo_medio': '2:35'},
        'Q4': {'visitas': 18910, 'usuarios': 12348, 'blogposts': 27, 'tempo_medio': '4:36'},
    },
    'blog_fy24': {
        'Q1': {'visitas': None, 'usuarios': 794, 'blogposts': None, 'tempo_medio': None},
        'Q2': {'visitas': None, 'usuarios': 868, 'blogposts': None, 'tempo_medio': None},
        'Q3': {'visitas': None, 'usuarios': 1049, 'blogposts': None, 'tempo_medio': None},
        'Q4': {'visitas': None, 'usuarios': 1049, 'blogposts': None, 'tempo_medio': None},
    },
    'newsletter': {
        'Q1': {'empresas': 416, 'envios': 544, 'abertura': 34.19, 'cliques': 2.8},
        'Q2': {'empresas': 427, 'envios': 750, 'abertura': 35.2, 'cliques': 2.8},
        'Q3': {'empresas': 428, 'envios': 1059, 'abertura': 33.1, 'cliques': 1.5},
        'Q4': {'empresas': 488, 'envios': 426, 'abertura': 32.0, 'cliques': 1.8},
    },
    'newsletter_fy24': {
        'Q1': {'empresas': None, 'envios': None, 'abertura': 71.03, 'cliques': 3.90},
        'Q2': {'empresas': None, 'envios': None, 'abertura': 65.09, 'cliques': 7.96},
        'Q3': {'empresas': None, 'envios': 1049, 'abertura': 62.0, 'cliques': 2.12},
        'Q4': {'empresas': None, 'envios': 1049, 'abertura': 62.0, 'cliques': 2.2},
    },
    'vertical_distribution': {
        'Q1': [('Segurança',27.0),('Networking',13.0),('Cloud',13.0),('Data & AI',10.0),('Data Center',9.0),('Institucional',15.0)],
        'Q2': [('Cloud',27.0),('Segurança',22.0),('Networking',19.0),('Data & AI',14.0),('Data Center',10.0),('Institucional',8.0)],
        'Q3': [('Segurança',31.0),('Cloud',19.0),('Networking',16.0),('Institucional',15.0),('Data & AI',14.0),('Data Center',6.0)],
        'Q4': [('Segurança',40.0),('Cloud',21.0),('Institucional',14.0),('Networking',9.0),('Data Center',8.0),('Data & AI',7.0)],
    },
    'fabricantes': {
        'Q1': [
            {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 120 peças', 'menor_solicitante': 'Palo Alto — 1 peça', 'top_3_pecas': '9520 - Fortinet'},
            {'vertical': 'Cloud', 'maior_solicitante': 'AWS — 43 peças', 'menor_solicitante': 'Microsoft — 11 peças', 'top_3_pecas': '--'},
            {'vertical': 'Data & AI', 'maior_solicitante': 'IBM — 40 peças', 'menor_solicitante': 'Red Hat — 3 peças', 'top_3_pecas': '9466 - IBM / 9483 - NVIDIA'},
            {'vertical': 'Data Center', 'maior_solicitante': 'Dell — 15 peças', 'menor_solicitante': 'Pure Storage — 2 peças', 'top_3_pecas': '--'},
            {'vertical': 'Networking', 'maior_solicitante': 'Cisco — 132 peças', 'menor_solicitante': 'Juniper — 2 peças', 'top_3_pecas': '9488 - Cisco'},
        ],
        'Q2': [
            {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 117 peças', 'menor_solicitante': 'Trend Micro — 1 peça', 'top_3_pecas': 'E-mail Deriv. 76 | E-mail Novo 32 | Avulsa 30'},
            {'vertical': 'Cloud', 'maior_solicitante': 'Microsoft — 115 peças', 'menor_solicitante': 'Google Cloud — 35 peças', 'top_3_pecas': 'E-mail Deriv. 109 | Avulsa 30 | Post RS Deriv. 22'},
            {'vertical': 'Data & AI', 'maior_solicitante': 'IBM — 59 peças', 'menor_solicitante': 'NVIDIA — 27 peças', 'top_3_pecas': 'E-mail Novo 14 | Avulsa 6 | LP+TKY 4'},
            {'vertical': 'Data Center', 'maior_solicitante': 'Dell — 117 peças', 'menor_solicitante': 'HPE Aruba — 1 peça', 'top_3_pecas': 'Avulsa 42 | E-mail Deriv. 28 | E-mail Novo 16'},
            {'vertical': 'Networking', 'maior_solicitante': 'Cisco — 63 peças', 'menor_solicitante': 'Ciena — 7 peças', 'top_3_pecas': 'E-mail Novo 25 | E-mail Deriv. 15 | Avulsa 12'},
        ],
        'Q3': [
            {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 129 peças', 'menor_solicitante': 'Trend Micro — 1 peça', 'top_3_pecas': 'E-mail Deriv. 69 | Avulsa 34 | E-mail Novo 30'},
            {'vertical': 'Cloud', 'maior_solicitante': 'Microsoft — 69 peças', 'menor_solicitante': 'Google Cloud — 20 peças', 'top_3_pecas': 'E-mail Deriv. 52 | Avulsa 41 | E-mail Novo 8'},
            {'vertical': 'Data & AI', 'maior_solicitante': 'Red Hat — 44 peças', 'menor_solicitante': 'SAS — 1 peça', 'top_3_pecas': 'Avulsa 14 | Camp. Anúncio 12 | Post RS Deriv. 12'},
            {'vertical': 'Data Center', 'maior_solicitante': 'TD SYNNEX — 12 peças', 'menor_solicitante': 'Pure Storage — 1 peça', 'top_3_pecas': 'E-mail Novo 19 | Avulsa 14 | LP+TKY 4'},
            {'vertical': 'Networking', 'maior_solicitante': 'Cisco — 82 peças', 'menor_solicitante': 'Ciena — 4 peças', 'top_3_pecas': 'E-mail Deriv. 49 | Avulsa 23 | E-mail Novo 11'},
        ],
        'Q4': [
            {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 75 peças', 'menor_solicitante': 'Tenable — 1 peça', 'top_3_pecas': 'EMKT Deriv. 42 | EMKT Novo 36 | Avulsa 17'},
            {'vertical': 'Cloud', 'maior_solicitante': 'Google Cloud — 28 peças', 'menor_solicitante': 'AWS — 11 peças', 'top_3_pecas': 'EMKT Deriv. 36 | EMKT Novo 20 | Post RS Deriv. 13'},
            {'vertical': 'Data & AI', 'maior_solicitante': 'IBM — 25 peças', 'menor_solicitante': 'NVIDIA — 10 peças', 'top_3_pecas': 'Avulsa Deriv. 10 | EMKT Deriv. 6 | EMKT Novo 6'},
            {'vertical': 'Data Center', 'maior_solicitante': 'HPE — 10 peças', 'menor_solicitante': 'Commvault / Dell / Pure — 1 peça', 'top_3_pecas': 'Avulsa 9 | EMKT Novo 6 | EMKT Deriv. 2'},
            {'vertical': 'Networking', 'maior_solicitante': 'Cisco — 17 peças', 'menor_solicitante': 'Ciena — 1 peça', 'top_3_pecas': 'EMKT Novo 6 | EMKT Deriv. 4 | Avulsa 2'},
        ],
    },
    'campanhas_detalhes': {
        'Q1': {'solicitadas': 6, 'veiculadas': 4, 'taxa_conversao': 7.26, 'leads': 62, 'top': '🏆 Fortinet Roadshow (56 empresas)<br>🏆 NVIDIA IA (6 empresas)'},
        'Q2': {'solicitadas': 9, 'veiculadas': 6, 'taxa_conversao': 6.5, 'leads': 205, 'top': '🏆 IBM IA (55 empresas)<br>🏆 Microsoft Roadshow (40 empresas)<br>🏆 Fortinet Recrutamento (25 empresas)'},
        'Q3': {'solicitadas': 7, 'veiculadas': 6, 'taxa_conversao': 0.54, 'leads': 439, 'top': '🏆 Cloud On the Go (383 empresas)<br>🏆 Fortinet Roadshow (46 empresas)<br>🏆 NVIDIA IA (10 empresas)'},
        'Q4': {'solicitadas': 6, 'veiculadas': 3, 'taxa_conversao': 0.04, 'leads': 70, 'top': '🏆 Campanha Recrutamento Fortinet (70 empresas)'},
    }
}

# ==================== DADOS DETALHADOS DE EMAIL MARKETING ====================
EMAIL_VERTICAL_DATA = {
    'Q1': pd.DataFrame([
        {'vertical_tipo': 'Segurança', 'percent_envio': '48,30%', 'entrega': '97,78%', 'abertura': '45,05%', 'clique': '2,7%', 'opt_out': '0,03%'},
        {'vertical_tipo': 'Networking', 'percent_envio': '29,93%', 'entrega': '94,92%', 'abertura': '31,15%', 'clique': '1,24%', 'opt_out': '0,04%'},
        {'vertical_tipo': 'Cloud', 'percent_envio': '8,84%', 'entrega': '95,95%', 'abertura': '41,27%', 'clique': '1,59%', 'opt_out': '0,05%'},
        {'vertical_tipo': 'Data Center', 'percent_envio': '7,48%', 'entrega': '94,74%', 'abertura': '41,80%', 'clique': '1,59%', 'opt_out': '0%'},
        {'vertical_tipo': 'Data & AI', 'percent_envio': '5,44%', 'entrega': '99,35%', 'abertura': '53,87%', 'clique': '3,17%', 'opt_out': '0%'},
    ]),
    'Q2': pd.DataFrame([
        {'vertical_tipo': 'Segurança', 'percent_envio': '46,39%', 'entrega': '99,20%', 'abertura': '48,21%', 'clique': '3,50%', 'opt_out': '0,06%'},
        {'vertical_tipo': 'Cloud', 'percent_envio': '26,80%', 'entrega': '99,23%', 'abertura': '51,48%', 'clique': '3,57%', 'opt_out': '0,06%'},
        {'vertical_tipo': 'Networking', 'percent_envio': '10,05%', 'entrega': '96,72%', 'abertura': '37,81%', 'clique': '1,59%', 'opt_out': '0,10%'},
        {'vertical_tipo': 'Data Center', 'percent_envio': '7,73%', 'entrega': '97,93%', 'abertura': '40,20%', 'clique': '2,30%', 'opt_out': '0,30%'},
        {'vertical_tipo': 'Data & AI', 'percent_envio': '6,70%', 'entrega': '98,27%', 'abertura': '39,97%', 'clique': '1,53%', 'opt_out': '0,01%'},
    ]),
    'Q3': pd.DataFrame([
        {'vertical_tipo': 'Segurança', 'percent_envio': '48,8%', 'entrega': '98%', 'abertura': '36%', 'clique': '6%', 'opt_out': '0,01%'},
        {'vertical_tipo': 'Cloud', 'percent_envio': '21,9%', 'entrega': '97%', 'abertura': '46%', 'clique': '12%', 'opt_out': '0%'},
        {'vertical_tipo': 'Data & AI', 'percent_envio': '14,6%', 'entrega': '95%', 'abertura': '24%', 'clique': '2%', 'opt_out': '0,02%'},
        {'vertical_tipo': 'Data Center', 'percent_envio': '7,9%', 'entrega': '96%', 'abertura': '35%', 'clique': '6%', 'opt_out': '0,01%'},
        {'vertical_tipo': 'Networking', 'percent_envio': '6,6%', 'entrega': '99%', 'abertura': '33%', 'clique': '2%', 'opt_out': '0%'},
    ]),
    'Q4': pd.DataFrame([
        {'vertical_tipo': 'Segurança', 'percent_envio': '48,8%', 'entrega': '98%', 'abertura': '36%', 'clique': '6%', 'opt_out': '0,01%'},
        {'vertical_tipo': 'Cloud', 'percent_envio': '21,9%', 'entrega': '97%', 'abertura': '46%', 'clique': '12%', 'opt_out': '0%'},
        {'vertical_tipo': 'Data & AI', 'percent_envio': '14,6%', 'entrega': '95%', 'abertura': '24%', 'clique': '2%', 'opt_out': '0,02%'},
        {'vertical_tipo': 'Data Center', 'percent_envio': '7,9%', 'entrega': '96%', 'abertura': '35%', 'clique': '6%', 'opt_out': '0,01%'},
        {'vertical_tipo': 'Networking', 'percent_envio': '6,6%', 'entrega': '99%', 'abertura': '33%', 'clique': '2%', 'opt_out': '0%'},
    ]),
}

EMAIL_TIPO_DATA = {
    'Q1': pd.DataFrame([
        {'tipo_email': 'Eventos', 'percent_envio': '62,89%', 'entrega': '94,86%', 'abertura': '30,92%', 'clique': '1,39%', 'opt_out': '0,03%'},
        {'tipo_email': 'Camp. Digital', 'percent_envio': '14,47%', 'entrega': '95,10%', 'abertura': '35%', 'clique': '2,15%', 'opt_out': '0,07%'},
        {'tipo_email': 'Promocional e Estoque', 'percent_envio': '13,21%', 'entrega': '97,55%', 'abertura': '43,77%', 'clique': '1,92%', 'opt_out': '0,04%'},
        {'tipo_email': 'Comunicado', 'percent_envio': '6,29%', 'entrega': '98,72%', 'abertura': '52,06%', 'clique': '2,38%', 'opt_out': '0,04%'},
        {'tipo_email': 'Camp. Incentivo', 'percent_envio': '3,14%', 'entrega': '99,54%', 'abertura': '51,17%', 'clique': '1,48%', 'opt_out': '0%'},
    ]),
    'Q2': pd.DataFrame([
        {'tipo_email': 'Eventos', 'percent_envio': '67,27%', 'entrega': '98,69%', 'abertura': '44,61%', 'clique': '2,72%', 'opt_out': '0,05%'},
        {'tipo_email': 'Camp. Digital', 'percent_envio': '23,71%', 'entrega': '97,84%', 'abertura': '45,34%', 'clique': '2,57%', 'opt_out': '0,07%'},
        {'tipo_email': 'Prom. e Estoque', 'percent_envio': '5,15%', 'entrega': '99,57%', 'abertura': '54,39%', 'clique': '4,10%', 'opt_out': '0,07%'},
        {'tipo_email': 'Camp. Incentivo', 'percent_envio': '2,32%', 'entrega': '97,49%', 'abertura': '40,78%', 'clique': '4,58%', 'opt_out': '0,12%'},
        {'tipo_email': 'Comunicado', 'percent_envio': '1,55%', 'entrega': '99,40%', 'abertura': '53,36%', 'clique': '1,51%', 'opt_out': '0,06%'},
    ]),
    'Q3': pd.DataFrame([
        {'tipo_email': 'Eventos', 'percent_envio': '61,4%', 'entrega': '97%', 'abertura': '35%', 'clique': '7%', 'opt_out': '0,01%'},
        {'tipo_email': 'Comunicado', 'percent_envio': '14,9%', 'entrega': '97%', 'abertura': '42%', 'clique': '1%', 'opt_out': '0%'},
        {'tipo_email': 'Camp. Digital', 'percent_envio': '11,6%', 'entrega': '97%', 'abertura': '31%', 'clique': '3%', 'opt_out': '0%'},
        {'tipo_email': 'Prom. e Estoque', 'percent_envio': '9,3%', 'entrega': '97%', 'abertura': '43%', 'clique': '5%', 'opt_out': '0%'},
        {'tipo_email': 'Camp. Incentivo', 'percent_envio': '2,9%', 'entrega': '97%', 'abertura': '38%', 'clique': '2%', 'opt_out': '0%'},
    ]),
    'Q4': pd.DataFrame([
        {'tipo_email': 'Eventos', 'percent_envio': '61,4%', 'entrega': '97%', 'abertura': '35%', 'clique': '7%', 'opt_out': '0,01%'},
        {'tipo_email': 'Comunicado', 'percent_envio': '14,9%', 'entrega': '97%', 'abertura': '42%', 'clique': '1%', 'opt_out': '0%'},
        {'tipo_email': 'Camp. Digital', 'percent_envio': '11,6%', 'entrega': '97%', 'abertura': '31%', 'clique': '3%', 'opt_out': '0%'},
        {'tipo_email': 'Prom. e Estoque', 'percent_envio': '9,3%', 'entrega': '97%', 'abertura': '43%', 'clique': '5%', 'opt_out': '0%'},
        {'tipo_email': 'Camp. Incentivo', 'percent_envio': '2,9%', 'entrega': '97%', 'abertura': '38%', 'clique': '2%', 'opt_out': '0%'},
    ]),
}

# ==================== DADOS DETALHADOS DE REDES SOCIAIS ====================
REDES_POR_REDE_DATA = {
    'Q1': pd.DataFrame([
        {'rede': 'Instagram', 'seguidores': 323, 'media_seguidores': 450, 'engajamentos': 78040, 'cliques': 192},
        {'rede': 'LinkedIn', 'seguidores': 830, 'media_seguidores': 871, 'engajamentos': 3175, 'cliques': 5893},
        {'rede': 'Facebook', 'seguidores': 35, 'media_seguidores': 40, 'engajamentos': 204, 'cliques': 32},
        {'rede': 'YouTube', 'seguidores': 42, 'media_seguidores': 32, 'engajamentos': 0, 'cliques': 0},
    ]),
    'Q2': pd.DataFrame([
        {'rede': 'Instagram', 'seguidores': 628, 'media_seguidores': 450, 'engajamentos': 6813, 'cliques': 94},
        {'rede': 'LinkedIn', 'seguidores': 1036, 'media_seguidores': 871, 'engajamentos': 3150, 'cliques': 8488},
        {'rede': 'Facebook', 'seguidores': 20, 'media_seguidores': 40, 'engajamentos': 274, 'cliques': 3},
    ]),
    'Q3': pd.DataFrame([
        {'rede': 'Instagram', 'seguidores': 949, 'media_seguidores': 450, 'engajamentos': 64210, 'cliques': 15906},
        {'rede': 'LinkedIn', 'seguidores': 973, 'media_seguidores': 871, 'engajamentos': 10591, 'cliques': 10269},
        {'rede': 'Facebook', 'seguidores': 5, 'media_seguidores': 40, 'engajamentos': 1301, 'cliques': 10200},
    ]),
    'Q4': pd.DataFrame([
        {'rede': 'Instagram', 'seguidores': 1223, 'media_seguidores': 407, 'engajamentos': 46500, 'cliques': 27900},
        {'rede': 'LinkedIn', 'seguidores': 1028, 'media_seguidores': 342, 'engajamentos': 5379, 'cliques': 18594},
        {'rede': 'Facebook', 'seguidores': 45, 'media_seguidores': 15, 'engajamentos': 6167, 'cliques': 22900},
    ]),
}

TOP_FABRICANTES_DATA = {
    'Q1': {
        'mais_publicados': 'Fortinet (18), AWS (13), Zscaler (5)',
        'mais_engajados': 'IBM (384 cliques), Fortinet (208 cliques), AWS (192 cliques)',
        'distribuicao_vertical': 'Institucional 67%, Segurança 15%, Cloud 8%, Networking 5%, Data & AI 4%, Data Center 1%'
    },
    'Q2': {
        'mais_publicados': 'Broadcom (11), Microsoft (10), Fortinet (9)',
        'mais_engajados': 'Microsoft (1.767 cliques), Google Cloud (187), Broadcom (182)',
        'distribuicao_vertical': 'Institucional 56%, Cloud 20%, Data & AI 18%, Data Center 3%, Segurança 2%, Networking 1%'
    },
    'Q3': {
        'mais_publicados': 'AWS (15), Fortinet (11), RedHat (8)',
        'mais_engajados': 'AWS (194 cliques), Fortinet (193), RedHat (78)',
        'distribuicao_vertical': 'Institucional 34%, Segurança 33%, Data & AI 17%, Cloud 10%, Networking 5%, Data Center 2%'
    },
    'Q4': {
        'mais_publicados': 'Cisco (10), Checkpoint (9), Microsoft (8)',
        'mais_engajados': 'Cisco, Microsoft, Fortinet',
        'distribuicao_vertical': 'Institucional 58%, Cloud 20%, Segurança 14%, Data & AI 5%, Data Center 2%, Networking 2%'
    },
}

# ==================== DADOS DE COMPARATIVOS DE CAMPANHAS ====================
CAMPANHAS_COMPARATIVOS = {
    'taxa_conversao_historico': {
        'Q1': {'com_investimento': 7.26, 'sem_investimento': None, 'referencia_mercado': '0,5% a 2%', 'q4fy24': 7.09, 'q1fy24': 4.65},
        'Q2': {'com_investimento': 6.5, 'sem_investimento': 10.5, 'referencia_mercado': '0,5% a 2%', 'q4fy24': None, 'q1fy24': None},
        'Q3': {'com_investimento': 0.54, 'sem_investimento': None, 'referencia_mercado': '0,5% a 2%', 'q4fy24': None, 'q1fy24': None},
        'Q4': {'com_investimento': 0.04, 'sem_investimento': 0.3, 'referencia_mercado': '0,5% a 2%', 'q4fy24': None, 'q1fy24': None},
    },
    'distribuicao_objetivo': {
        'Q1': {'conversao': 83, 'branding': 17},
        'Q2': {'conversao': 83, 'branding': 17},
        'Q3': {'conversao': 83, 'branding': 17},
        'Q4': {'conversao': 66, 'branding': 33},
    },
    'distribuicao_vertical_solicitadas': {
        'Q1': {'Cloud': 42.9, 'Data & AI': 28.6, 'Segurança': 28.6},
        'Q2': {'Cloud': 50, 'Segurança': 33, 'Data & AI': 16},
        'Q3': {'Cloud': 66, 'Segurança': 33},
        'Q4': {'Cloud': 66, 'Segurança': 33},
    },
    'distribuicao_vertical_veiculadas': {
        'Q1': {'Cloud': 33, 'Data & AI': 33, 'Segurança': 11, 'Institucional': 11, 'Networking': 11},
        'Q2': {'Cloud': 43, 'Segurança': 43, 'Data & AI': 14},
        'Q3': {'Cloud': 17, 'Segurança': 50, 'Data & AI': 17, 'Networking': 17},
        'Q4': {'Cloud': 17, 'Segurança': 50, 'Data & AI': 17, 'Networking': 17},
    },
}

# ==================== DADOS DOS SLIDES POR TRIMESTRE ====================
SLIDES_CONTENT = {
    'Q1': {
        'titulo': 'Q1 FY25 - Análise de Performance',
        'secoes': {
            'Visão Geral': {
                'titulo': '📊 Visão Geral',
                'conteudo': '''
                O primeiro trimestre do FY25 apresentou resultados sólidos, com destaque para:
                • 518 peças produzidas, demonstrando alta capacidade de produção de conteúdo
                • 108 solicitações de campanhas, indicando forte demanda dos parceiros
                • 4 campanhas veiculadas com sucesso
                • Taxa de conversão de 7,26% - superando a média de mercado de 0,5% a 2%
                
                A vertical de Segurança liderou em produção de peças com 27% do total, seguida por Institucional (15%) e Networking (13%). Fortinet se destacou como o maior solicitante com 120 peças.
                '''
            },
            'Campanhas': {
                'titulo': '🎯 Campanhas',
                'conteudo': '''
                Principais campanhas do trimestre:
                
                🏆 Fortinet Roadshow: 56 empresas participantes
                - Formato: Roadshow presencial
                - Objetivo: Recrutamento de parceiros
                - Resultado: Alta adesão e leads qualificados
                
                🏆 NVIDIA IA: 6 empresas qualificadas
                - Formato: Campanha digital focada em Inteligência Artificial
                - Objetivo: Geração de demanda
                - Resultado: Conversão de 7,26%
                
                Distribuição por objetivo: 83% campanhas de conversão, 17% branding.
                '''
            },
            'Email Marketing': {
                'titulo': '📧 E-mail Marketing',
                'conteudo': '''
                Performance de e-mail marketing no Q1:
                
                • Total de envios: 169.948
                • Taxa de entrega: 95,7% (vs 94,30% no Q4FY24)
                • Taxa de abertura: 35,8% (vs 24,50% no Q4FY24)
                • Taxa de cliques: 1,7% (vs 1,30% no Q4FY24)
                
                Destaques por vertical:
                • Data & AI: Maior taxa de abertura (53,87%)
                • Segurança: Maior volume de envios (48,30%)
                
                Por tipo de e-mail:
                • Comunicados: Melhor taxa de abertura (52,06%)
                • Campanhas de incentivo: Melhor taxa de entrega (99,54%)
                
                Recomendação: Otimizar filtros de disparo para maior relevância.
                '''
            },
            'Redes Sociais': {
                'titulo': '🌐 Redes Sociais',
                'conteudo': '''
                Performance nas redes sociais:
                
                • Novos seguidores: 1.230
                • Total de engajamentos: 81.419
                • Total de cliques: 6.117
                
                Destaques por rede:
                • Instagram: 323 seguidores, 78.040 engajamentos
                • LinkedIn: 830 seguidores, 5.893 cliques
                
                Top fabricantes mais publicados:
                1. Fortinet (18 publicações)
                2. AWS (13 publicações)
                3. Zscaler (5 publicações)
                
                Top fabricantes mais engajados (cliques):
                1. IBM (384 cliques)
                2. Fortinet (208 cliques)
                3. AWS (192 cliques)
                
                Distribuição por vertical: Institucional 67%, Segurança 15%, Cloud 8%
                
                Insight: Final e início de ano apresentam queda de engajamento. Sugestão de campanhas institucionais para manter o engajamento.
                '''
            },
            'Blog & Newsletter': {
                'titulo': '📝 Blog & Newsletter',
                'conteudo': '''
                Blog:
                • Visitas: 24.926
                • Usuários: 17.075
                • Blogposts publicados: 31
                • Tempo médio na página: 5:00
                
                Newsletter:
                • Empresas inscritas: 416
                • Envios: 544
                • Taxa de abertura: 34,19%
                • Taxa de cliques: 2,8%
                
                Público qualificado: 60% ensino superior, 53% classe A/B com forte intenção de compra.
                '''
            },
            'Aprendizados': {
                'titulo': '📚 Aprendizados e Recomendações',
                'conteudo': '''
                ✅ QUE BOM:
                • PowerUP: Plataforma de inscrição, estratégias online e metas diárias
                • Case Recrutamento Fortinet: 80 Leads — virou referência
                • Segmentação Microsoft: Timing nos e-mails aumentou quórum
                • Campanha BU Networking: Insights valiosos para futuras BUs
                
                ⚠️ QUE PENA:
                • Qualidade das bases: Necessidade de segmentar melhor os parceiros
                • Análise constante de resultados: Todos os jobs precisam ser acompanhados
                
                💡 QUE TAL — 2026:
                • Intercâmbio de treinamentos: Calendário ao longo do ano
                • Alinhamentos estratégicos recorrentes: Incluir agência no planejamento
                • Metodologia EDGE: Otimização do formulário de briefing
                '''
            }
        }
    },
    'Q2': {
        'titulo': 'Q2 FY25 - Análise de Performance',
        'secoes': {
            'Visão Geral': {
                'titulo': '📊 Visão Geral',
                'conteudo': '''
                O segundo trimestre consolidou o crescimento com números expressivos:
                • 692 peças produzidas (+33,6% vs Q1)
                • 159 solicitações de campanhas (+47,2% vs Q1)
                • 9 campanhas veiculadas (+125% vs Q1)
                
                A vertical Cloud liderou com 27% das peças, seguida por Segurança (22%) e Networking (19%). Microsoft se destacou como maior solicitante na vertical Cloud com 115 peças.
                '''
            },
            'Campanhas': {
                'titulo': '🎯 Campanhas',
                'conteudo': '''
                Principais campanhas do trimestre:
                
                🏆 IBM IA: 55 empresas qualificadas
                - Formato: Campanha digital focada em Inteligência Artificial
                - Resultado: Alto engajamento e leads qualificados
                
                🏆 Microsoft Roadshow: 40 empresas participantes
                - Formato: Evento presencial e online
                - Objetivo: Geração de demanda e recrutamento
                
                🏆 Fortinet Recrutamento: 25 empresas
                - Formato: Campanha de recrutamento
                - Resultado: 25 novos parceiros qualificados
                
                Distribuição por vertical solicitadas: Cloud 50%, Segurança 33%, Data & AI 16%
                Distribuição por vertical veiculadas: Cloud 43%, Segurança 43%, Data & AI 14%
                '''
            },
            'Email Marketing': {
                'titulo': '📧 E-mail Marketing',
                'conteudo': '''
                Performance de e-mail marketing no Q2:
                
                • Total de envios: 122.639
                • Taxa de entrega: 98,4% (↑ 2,7 p.p. vs Q1)
                • Taxa de abertura: 45,3% (↑ 9,5 p.p. vs Q1)
                • Taxa de cliques: 2,6% (↑ 0,9 p.p. vs Q1)
                
                Destaques por vertical:
                • Cloud: Maior taxa de abertura (51,48%)
                • Segurança: Maior volume de envios (46,39%)
                
                Recomendação: Otimizar os filtros de disparo, considerando segmentações mais assertivas.
                '''
            },
            'Redes Sociais': {
                'titulo': '🌐 Redes Sociais',
                'conteudo': '''
                Performance nas redes sociais:
                
                • Novos seguidores: 1.688
                • Total de engajamentos: 10.237
                • Total de cliques: 8.585
                
                Destaques por rede:
                • LinkedIn: 1.036 seguidores, 8.488 cliques
                • Instagram: 628 seguidores, 6.813 engajamentos
                
                Top fabricantes mais publicados:
                1. Broadcom (11 publicações)
                2. Microsoft (10 publicações)
                3. Fortinet (9 publicações)
                
                Top fabricantes mais engajados:
                1. Microsoft (1.767 cliques)
                2. Google Cloud (187 cliques)
                3. Broadcom (182 cliques)
                
                Insight: Postagens de vendors que fogem do padrão estático + comercial costumam ter melhor desempenho.
                '''
            },
            'Blog & Newsletter': {
                'titulo': '📝 Blog & Newsletter',
                'conteudo': '''
                Blog:
                • Visitas: 16.137
                • Usuários: 11.295
                • Blogposts publicados: 25
                • Tempo médio na página: 4:04
                
                Newsletter:
                • Empresas inscritas: 427
                • Envios: 750
                • Taxa de abertura: 35,2%
                • Taxa de cliques: 2,8%
                
                Crescimento no número de envios e manutenção das taxas de engajamento.
                '''
            },
            'Aprendizados': {
                'titulo': '📚 Aprendizados e Recomendações',
                'conteudo': '''
                ✅ QUE BOM:
                • IBM IA gerou 55 leads qualificados
                • Microsoft Roadshow com alta adesão (40 empresas)
                • Fortinet Recrutamento consolidado como formato eficaz
                • Taxa de abertura de e-mail atingiu 45,3%
                
                ⚠️ QUE PENA:
                • Necessidade de segmentação mais precisa das bases
                • Algumas campanhas tiveram execução atrasada
                
                💡 QUE TAL:
                • Utilizar conteúdo humanizado em vídeo com colaboradores
                • Para eventos: usar fotos, chamadas em vídeo ou depoimentos
                • Otimizar segmentação por vertical nos e-mails
                '''
            }
        }
    },
    'Q3': {
        'titulo': 'Q3 FY25 - Análise de Performance',
        'secoes': {
            'Visão Geral': {
                'titulo': '📊 Visão Geral',
                'conteudo': '''
                Terceiro trimestre com foco em grandes eventos:
                • 674 peças produzidas (-2,6% vs Q2)
                • 100 solicitações de campanhas (-37,1% vs Q2)
                • 7 campanhas veiculadas
                
                A vertical Segurança liderou com 31% das peças, seguida por Cloud (19%) e Networking (16%). Red Hat se destacou em Data & AI com 44 peças.
                '''
            },
            'Campanhas': {
                'titulo': '🎯 Campanhas',
                'conteudo': '''
                Principais campanhas do trimestre:
                
                🏆 Cloud On the Go: 383 empresas participantes
                - Formato: Roadshow multi-cidades
                - Objetivo: Recrutamento e qualificação
                - Resultado: Maior campanha do ano em número de leads
                
                🏆 Fortinet Roadshow: 46 empresas
                - Formato: Evento técnico
                - Resultado: Leads qualificados para a vertical
                
                🏆 NVIDIA IA: 10 empresas
                - Formato: Campanha digital
                - Resultado: Qualificação de parceiros para IA
                
                Destaque: Cloud On the Go foi a campanha de maior impacto do ano.
                '''
            },
            'Email Marketing': {
                'titulo': '📧 E-mail Marketing',
                'conteudo': '''
                Performance de e-mail marketing no Q3:
                
                • Total de envios: 134.035
                • Taxa de entrega: 96%
                • Taxa de abertura: 38%
                • Taxa de cliques: 6% (melhor do ano!)
                
                Destaques:
                • Taxa de cliques atingiu 6% - recorde do ano
                • Cloud: Maior taxa de cliques (12%)
                • Eventos: Maior volume de envios (61,4%)
                
                Recomendação: Manter cadências nos disparos de Eventos (mostrou bons resultados em cliques).
                '''
            },
            'Redes Sociais': {
                'titulo': '🌐 Redes Sociais',
                'conteudo': '''
                Performance nas redes sociais:
                
                • Novos seguidores: 1.927
                • Total de engajamentos: 76.102
                • Total de cliques: 36.375 (crescimento expressivo!)
                
                Destaques por rede:
                • Instagram: 949 seguidores, 64.210 engajamentos, 15.906 cliques
                • LinkedIn: 973 seguidores, 10.591 engajamentos, 10.269 cliques
                • Facebook: Cliques saltaram para 10.200
                
                Top fabricantes mais publicados:
                1. AWS (15 publicações)
                2. Fortinet (11 publicações)
                3. RedHat (8 publicações)
                
                Top fabricantes mais engajados:
                1. AWS (194 cliques)
                2. Fortinet (193 cliques)
                3. RedHat (78 cliques)
                
                Insight: Oportunidade de otimização com vídeos e GIFs para campanhas Institucionais e de Vendors.
                '''
            },
            'Blog & Newsletter': {
                'titulo': '📝 Blog & Newsletter',
                'conteudo': '''
                Blog:
                • Visitas: 13.353
                • Usuários: 7.037
                • Blogposts publicados: 26
                • Tempo médio na página: 2:35
                
                Newsletter:
                • Empresas inscritas: 428
                • Envios: 1.059
                • Taxa de abertura: 33,1%
                • Taxa de cliques: 1,5%
                
                Aumento significativo no volume de envios de newsletter (+41% vs Q2).
                '''
            },
            'Aprendizados': {
                'titulo': '📚 Aprendizados e Recomendações',
                'conteudo': '''
                ✅ QUE BOM:
                • Cloud On the Go - maior campanha do ano (383 leads)
                • Taxa de cliques em e-mail atingiu 6%
                • Crescimento expressivo em redes sociais
                
                ⚠️ QUE PENA:
                • Queda nas solicitações de campanhas
                • Taxa de conversão com investimento reduziu para 0,54%
                
                💡 QUE TAL:
                • Diversificar formatos de anúncios: inclusão de vídeos e GIFs
                • Balancear planejamento com mais campanhas de produtos
                • Criar conteúdos para incentivar usuários a seguir os perfis
                '''
            }
        }
    },
    'Q4': {
        'titulo': 'Q4 FY25 - Análise de Performance',
        'secoes': {
            'Visão Geral': {
                'titulo': '📊 Visão Geral',
                'conteudo': '''
                Encerramento do ano fiscal com resultados consolidados:
                • 647 peças produzidas (-4% vs Q3)
                • 131 solicitações de campanhas (+31% vs Q3)
                • 6 campanhas veiculadas
                
                A vertical Segurança liderou com 40% das peças, seguida por Cloud (21%) e Institucional (14%). Google Cloud se destacou como maior solicitante em Cloud com 28 peças.
                '''
            },
            'Campanhas': {
                'titulo': '🎯 Campanhas',
                'conteudo': '''
                Principais campanhas do trimestre:
                
                🏆 Campanha Recrutamento Fortinet: 70 empresas
                - Formato: Campanha de recrutamento digital
                - Resultado: 70 novos parceiros qualificados
                
                Destaques:
                • Distribuição por objetivo: 66% conversão, 33% branding
                • Taxa de conversão com investimento: 0,04%
                • Taxa de conversão sem investimento: 0,3%
                
                Distribuição por vertical solicitadas: Cloud 66%, Segurança 33%
                Distribuição por vertical veiculadas: Segurança 50%, Cloud 17%, Data & AI 17%, Networking 17%
                '''
            },
            'Email Marketing': {
                'titulo': '📧 E-mail Marketing',
                'conteudo': '''
                Performance de e-mail marketing no Q4:
                
                • Total de envios: 349.487 (maior volume do ano)
                • Taxa de entrega: 93%
                • Taxa de abertura: 24%
                • Taxa de cliques: 2,2%
                
                Destaques por vertical:
                • Segurança: Maior volume de envios (48,8%)
                • Cloud: Maior taxa de abertura (46%)
                
                Recomendação: Atualização e higienização contínua da base de e-mails. Variar os layouts dos e-mails, explorando diferentes formatos.
                '''
            },
            'Redes Sociais': {
                'titulo': '🌐 Redes Sociais',
                'conteudo': '''
                Performance nas redes sociais:
                
                • Novos seguidores: 2.296 (melhor do ano)
                • Total de engajamentos: 58.046
                • Total de cliques: 51.119 (recorde!)
                
                Destaques por rede:
                • Instagram: 1.223 seguidores, 46.500 engajamentos, 27.900 cliques
                • LinkedIn: 1.028 seguidores, 5.379 engajamentos, 18.594 cliques
                • Facebook: 45 seguidores, 6.167 engajamentos, 22.900 cliques
                
                Top fabricantes mais publicados:
                1. Cisco (10 publicações)
                2. Checkpoint (9 publicações)
                3. Microsoft (8 publicações)
                
                Insight: Fortinet está mais estratégico: postando menos, porém com conteúdos mais eficazes.
                '''
            },
            'Blog & Newsletter': {
                'titulo': '📝 Blog & Newsletter',
                'conteudo': '''
                Blog:
                • Visitas: 18.910
                • Usuários: 12.348
                • Blogposts publicados: 27
                • Tempo médio na página: 4:36
                
                Newsletter:
                • Empresas inscritas: 488
                • Envios: 426
                • Taxa de abertura: 32%
                • Taxa de cliques: 1,8%
                
                Recuperação nas visitas e usuários do blog após queda no Q3.
                '''
            },
            'Aprendizados': {
                'titulo': '📚 Aprendizados e Recomendações',
                'conteudo': '''
                ✅ QUE BOM:
                • Maior número de seguidores no ano (2.296)
                • Recorde de cliques em redes sociais (51.119)
                • 488 empresas inscritas na newsletter
                
                ⚠️ QUE PENA:
                • Queda nas taxas de abertura e cliques de e-mail
                • Apenas 3 campanhas ativas no período
                
                💡 QUE TAL:
                • Diversificar formatos de anúncios (vídeos humanizados)
                • Intensificar campanhas pagas e orgânicas
                • Elaborar conteúdos para incentivar usuários a seguir os perfis
                '''
            }
        }
    }
}

def get_slides_content(q):
    """Retorna o conteúdo completo dos slides para o trimestre selecionado"""
    return SLIDES_CONTENT.get(q, {})

# ==================== FUNÇÕES AUXILIARES ====================
def clean_value(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return '—'
    val_str = str(val).strip()
    if val_str in ['', 'nan', 'NaN', 'None', '—', '--']:
        return '—'
    return val_str

def format_number(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return '—'
    try:
        num = float(str(val).replace('%', '').replace('.', '').replace(',', '.'))
        if num > 1000:
            return f"{int(num):,}".replace(',', '.')
        return f"{int(num)}" if num == int(num) else f"{num:.1f}".replace('.', ',')
    except:
        return str(val)

def calc_variacao(atual, anterior):
    if atual in (None, '—') or anterior in (None, '—'):
        return None
    try:
        a = float(str(atual).replace('.', '').replace(',', '.').replace('%', ''))
        b = float(str(anterior).replace('.', '').replace(',', '.').replace('%', ''))
        return ((a - b) / b) * 100 if b != 0 else None
    except:
        return None

def get_pecas_value(q):
    return FALLBACK_DATA['pecas'].get(q, 0)

def get_solicitacoes_value(q):
    return FALLBACK_DATA['solicitacoes'].get(q, 0)

def get_campanhas_value(q):
    return FALLBACK_DATA['campanhas'].get(q, 0)

def get_pecas_fy24(q):
    return FALLBACK_DATA['pecas_fy24'].get(q)

def get_solicitacoes_fy24(q):
    return FALLBACK_DATA['solicitacoes_fy24'].get(q)

def get_campanhas_fy24(q):
    return FALLBACK_DATA['campanhas_fy24'].get(q)

def get_vertical_distribution(q):
    return pd.DataFrame(FALLBACK_DATA['vertical_distribution'].get(q, FALLBACK_DATA['vertical_distribution']['Q1']), columns=['vertical', 'percentual'])

def get_fabricantes_data(q):
    return pd.DataFrame(FALLBACK_DATA['fabricantes'].get(q, []))

def get_campanhas_detalhes(q):
    return FALLBACK_DATA['campanhas_detalhes'].get(q, {})

def get_campanhas_comparativos(q, tipo):
    if tipo == 'taxa_conversao':
        return CAMPANHAS_COMPARATIVOS['taxa_conversao_historico'].get(q, {})
    elif tipo == 'objetivo':
        return CAMPANHAS_COMPARATIVOS['distribuicao_objetivo'].get(q, {})
    elif tipo == 'vertical_solicitadas':
        return CAMPANHAS_COMPARATIVOS['distribuicao_vertical_solicitadas'].get(q, {})
    elif tipo == 'vertical_veiculadas':
        return CAMPANHAS_COMPARATIVOS['distribuicao_vertical_veiculadas'].get(q, {})
    return {}

def get_email_value(q, metric):
    if q and q in FALLBACK_DATA['email']:
        if metric == 'envios':
            return format_number(FALLBACK_DATA['email_envios'].get(q, '—'))
        return FALLBACK_DATA['email'][q].get(metric, '—')
    return '—'

def get_email_fy24(q, metric):
    if metric == 'envios':
        return format_number(FALLBACK_DATA['email_envios_fy24'].get(q, '—'))
    if q and q in FALLBACK_DATA['email_fy24']:
        return FALLBACK_DATA['email_fy24'][q].get(metric)
    return None

def get_blog_value(q, metric):
    if q and q in FALLBACK_DATA['blog']:
        val = FALLBACK_DATA['blog'][q].get(metric, '—')
        if metric == 'tempo_medio':
            return val
        return format_number(val)
    return '—'

def get_blog_fy24(q, metric):
    if q and q in FALLBACK_DATA['blog_fy24']:
        return FALLBACK_DATA['blog_fy24'][q].get(metric)
    return None

def get_newsletter_value(q, metric):
    if q and q in FALLBACK_DATA['newsletter']:
        val = FALLBACK_DATA['newsletter'][q].get(metric, '—')
        if metric in ['abertura', 'cliques']:
            return f"{val}%"
        return format_number(val)
    return '—'

def get_newsletter_fy24(q, metric):
    if q and q in FALLBACK_DATA['newsletter_fy24']:
        val = FALLBACK_DATA['newsletter_fy24'][q].get(metric)
        if val is not None:
            if metric in ['abertura', 'cliques']:
                return f"{val}%"
            return format_number(val)
    return None

def get_redes_value(q, metric):
    if q and q in FALLBACK_DATA['redes']:
        return format_number(FALLBACK_DATA['redes'][q].get(metric, '—'))
    return '—'

def get_redes_fy24(q, metric):
    if q and q in FALLBACK_DATA['redes_fy24']:
        return format_number(FALLBACK_DATA['redes_fy24'][q].get(metric, '—'))
    return '—'

def get_email_vertical_data(q):
    return EMAIL_VERTICAL_DATA.get(q, pd.DataFrame())

def get_email_tipo_data(q):
    return EMAIL_TIPO_DATA.get(q, pd.DataFrame())

def get_redes_por_rede_data(q):
    return REDES_POR_REDE_DATA.get(q, pd.DataFrame())

def get_top_fabricantes_data(q):
    return TOP_FABRICANTES_DATA.get(q, {})

# ==================== BADGE HELPERS ====================
def _var_badge(variacao, prefix=''):
    if variacao is None:
        return ''
    if variacao > 0:
        return f'<div class="kpi-variation kpi-up">↑ {variacao:.1f}% {prefix}</div>'
    elif variacao < 0:
        return f'<div class="kpi-variation kpi-down">↓ {abs(variacao):.1f}% {prefix}</div>'
    return f'<div class="kpi-variation kpi-neutral">→ 0% {prefix}</div>'

# ==================== FUNÇÕES DE RENDERIZAÇÃO ====================
def render_kpi_premium(valor, label, icone, variacao=None, trimestre_ref=None, variacao_fy24=None, q_fy24_label=None):
    badge_fy25 = ''
    badge_fy24 = ''

    valor_formatado = format_number(valor)
    if isinstance(valor_formatado, str) and valor_formatado.endswith('%'):
        valor_formatado = valor_formatado[:-1]
    
    is_percentage = '%' in str(valor) or label in ['Taxa de Abertura', 'Taxa de Cliques', 'Entregas', 'Aberturas', 'Cliques', 'Opt-Out']
    display_value = f"{valor_formatado}%" if is_percentage and valor_formatado != '—' else valor_formatado

    if variacao is not None and trimestre_ref:
        badge_fy25 = _var_badge(variacao, f'<span style="font-size:9px;">vs {trimestre_ref}</span>')

    if variacao_fy24 is not None and q_fy24_label:
        if variacao_fy24 > 0:
            badge_fy24 = f'<div class="kpi-variation kpi-fy24-up">↑ {variacao_fy24:.1f}% <span style="font-size:9px;">vs {q_fy24_label}</span></div>'
        elif variacao_fy24 < 0:
            badge_fy24 = f'<div class="kpi-variation kpi-fy24-down">↓ {abs(variacao_fy24):.1f}% <span style="font-size:9px;">vs {q_fy24_label}</span></div>'
        else:
            badge_fy24 = f'<div class="kpi-variation kpi-fy24-neutral">→ 0% <span style="font-size:9px;">vs {q_fy24_label}</span></div>'

    st.html(f"""
    <div class="glass-card kpi-premium">
        <div class="kpi-icon">{icone}</div>
        <div class="kpi-number">{display_value}</div>
        <div class="kpi-label">{label}</div>
        {badge_fy25}
        {badge_fy24}
    </div>
    """)

def render_metric_card(metric_name, icon, current_value, prev_fy25_value, prev_fy25_name, prev_fy24_value=None, prev_fy24_name=None, tooltip=None):
    cur_raw = clean_value(current_value)
    if isinstance(cur_raw, str) and cur_raw.endswith('%'):
        cur_raw = cur_raw[:-1]
    
    prev25 = clean_value(prev_fy25_value) if prev_fy25_value not in ('—', None) else '—'
    if isinstance(prev25, str) and prev25.endswith('%'):
        prev25 = prev25[:-1]

    var25 = calc_variacao(cur_raw, prev25) if prev25 != '—' else None

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
        var24 = calc_variacao(cur_raw, prev24_raw)
        fy24_row = f"""
        <div class="comparison-row">
            <span class="comp-label fy24-label">📅 {prev_fy24_name}</span>
            <span class="comp-value fy24-value">{prev24_str}</span>
            {comp_badge(var24)}
        </div>"""

    st.html(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:34px;margin-bottom:8px;">{icon}</div>
        <div style="font-size:36px;font-weight:800;color:{COLORS['text']};">{display_cur}</div>
        <div style="font-size:13px;color:{COLORS['text_muted']};margin-bottom:14px;">{metric_name}{tip_html}</div>
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

def render_blog_item(label, value, prev_value, prev_name, fy24_value=None, fy24_label=None, is_percentage=False, icon="📊"):
    val_raw = clean_value(value)
    prev_raw = clean_value(prev_value) if prev_value not in ('—', None) else '—'
    
    if isinstance(val_raw, str) and val_raw.endswith('%'):
        val_raw = val_raw[:-1]
    if isinstance(prev_raw, str) and prev_raw.endswith('%'):
        prev_raw = prev_raw[:-1]

    var = calc_variacao(val_raw, prev_raw) if prev_raw != '—' else None
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
        var24 = calc_variacao(val_raw, fy24_raw)
        fy24_html = f'<div class="blog-compare-fy24"><span>📅 vs {fy24_label}: <strong>{fy24_str}</strong></span>{badge(var24,"blog-change-up","blog-change-down")}</div>'

    st.html(f"""
    <div class="blog-item-premium">
        <div class="blog-label-premium">{icon} {label}</div>
        <div class="blog-value-premium">{display_val}</div>
        <div class="blog-compare-premium">
            <span>🔄 vs {prev_name}: {display_prev}</span>
            {badge(var)}
        </div>
        {fy24_html}
    </div>
    """)

def render_horizontal_bars(df, title):
    if df is None or df.empty:
        return
    vertical_colors = {
        'Segurança':'#D32F2F','Networking':'#0066CC','Cloud':'#3399FF',
        'Data & AI':'#7B2CBF','Data Center':'#FF6B35','Institucional':'#2E7D32'
    }
    df = df.copy()
    df = df.sort_values('percentual', ascending=False)

    st.markdown(f'<div class="glass-card"><div style="font-size:18px;font-weight:700;color:{COLORS["text"]};margin-bottom:20px;">📊 {title}</div>', unsafe_allow_html=True)
    for _, row in df.iterrows():
        pct = row['percentual']
        color = vertical_colors.get(row['vertical'], '#0066CC')
        st.markdown(f"""
        <div class="bar-premium">
            <div class="bar-label-premium">
                <span style="color:{COLORS['text']};">{row['vertical']}</span>
                <span style="color:{color}; font-weight:600;">{pct:.1f}%</span>
            </div>
            <div class="bar-track-premium">
                <div class="bar-fill-premium" style="width:{pct}%;background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_table(df, title=None):
    if df.empty:
        return
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div style="font-size:18px;font-weight:700;color:{COLORS["text"]};margin-bottom:16px;">{title}</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_comparative_charts(quarterly_data):
    st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Comparativo Trimestral</div><div class="section-sub">Análise Q1 a Q4</div></div></div>', unsafe_allow_html=True)

    for key, label, color in [('pecas','Peças',COLORS['primary']),('solic','Solicitações',COLORS['secondary']),('camp','Campanhas',COLORS['success'])]:
        df_c = pd.DataFrame([{'trimestre': t, 'valor': quarterly_data[t][key]} for t in ['Q1','Q2','Q3','Q4']])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_c['trimestre'], y=df_c['valor'], name=label,
                             marker=dict(color=color), text=df_c['valor'], textposition='outside',
                             textfont=dict(color=COLORS['text'])))
        fig.add_trace(go.Scatter(x=df_c['trimestre'], y=df_c['valor'], mode='lines+markers',
                                 name='Tendência', line=dict(color=COLORS['secondary'] if key!='solic' else COLORS['primary'], width=3),
                                 marker=dict(size=10)))
        fig.update_layout(title=f'{label} por Trimestre', title_font_color=COLORS['text'],
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(tickfont_color=COLORS['text'], gridcolor=COLORS['border']),
                          yaxis=dict(tickfont_color=COLORS['text'], gridcolor=COLORS['border']),
                          legend=dict(font_color=COLORS['text']), height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_campanhas_card(q, is_annual=False):
    if is_annual:
        st.markdown(f"""
        <div class="glass-card">
            <div style="text-align:center; margin-bottom:20px;">
                <div style="font-size:20px;font-weight:700;color:{COLORS['text']};">🎯 Campanhas por Trimestre</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;">
        """, unsafe_allow_html=True)

        for t in ['Q1', 'Q2', 'Q3', 'Q4']:
            camp = get_campanhas_detalhes(t)
            st.markdown(f"""
                <div style="text-align:center; padding:16px; background:rgba(0,0,0,0.2); border-radius:16px;">
                    <div style="font-size:18px;font-weight:700;color:{COLORS['primary']};margin-bottom:12px;">{t}</div>
                    <div style="font-size:13px;color:{COLORS['text_muted']};margin-bottom:8px;">Solicitadas: <strong style="color:{COLORS['text']};">{camp.get('solicitadas', '—')}</strong></div>
                    <div style="font-size:13px;color:{COLORS['text_muted']};margin-bottom:8px;">Veiculadas: <strong style="color:{COLORS['text']};">{camp.get('veiculadas', '—')}</strong></div>
                    <div style="font-size:13px;color:{COLORS['text_muted']};">Leads: <strong style="color:{COLORS['text']};">{camp.get('leads', '—')}</strong></div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        camp = get_campanhas_detalhes(q)
        obj_dist = get_campanhas_comparativos(q, 'objetivo')
        
        cc1, cc2 = st.columns(2)
        with cc1:
            st.html(f"""
            <div class="glass-card">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;">
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">📋 Solicitadas</div>
                        <div style="font-size:42px;font-weight:800;color:{COLORS['text']};">{camp.get('solicitadas', '—')}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">🚀 Veiculadas</div>
                        <div style="font-size:42px;font-weight:800;color:{COLORS['text']};">{camp.get('veiculadas', '—')}</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">📊 Taxa Conversão</div>
                        <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{camp.get('taxa_conversao', '—')}%</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">👥 Leads Gerados</div>
                        <div style="font-size:28px;font-weight:800;color:{COLORS['text']};">{camp.get('leads', '—')}</div>
                    </div>
                </div>
            </div>
            """)
        
        with cc2:
            st.html(f"""
            <div class="glass-card">
                <div style="font-size:18px;font-weight:700;color:{COLORS['text']};margin-bottom:16px;">🏆 Top Campanhas</div>
                <div style="font-size:13px;line-height:1.6;color:{COLORS['text']};margin-bottom:20px;">{camp.get('top', '—')}</div>
                <div style="font-size:14px;font-weight:600;color:{COLORS['text']};margin:20px 0 12px;">📊 Distribuição por Objetivo</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                    <div style="background:rgba(46,125,50,0.2);border-radius:16px;padding:12px;text-align:center;">
                        <div style="font-size:11px;color:{COLORS['text_muted']};">Conversão</div>
                        <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{obj_dist.get('conversao', '83')}%</div>
                    </div>
                    <div style="background:rgba(255,107,53,0.2);border-radius:16px;padding:12px;text-align:center;">
                        <div style="font-size:11px;color:{COLORS['text_muted']};">Branding</div>
                        <div style="font-size:28px;font-weight:800;color:#FF8C5A;">{obj_dist.get('branding', '17')}%</div>
                    </div>
                </div>
            </div>
            """)

# ==================== FUNÇÃO DE EXPORTAÇÃO COMPLETA ====================
def export_quarter_data(q, quarterly_data):
    """Exporta todos os dados do trimestre selecionado para CSV/Excel"""
    
    overview_data = {
        'Categoria': ['Peças Produzidas', 'Solicitações', 'Campanhas'],
        'Valor FY25': [
            quarterly_data[q]['pecas'],
            quarterly_data[q]['solic'],
            quarterly_data[q]['camp']
        ],
        'Valor FY24 (mesmo trimestre)': [
            get_pecas_fy24(q) if get_pecas_fy24(q) else '—',
            get_solicitacoes_fy24(q) if get_solicitacoes_fy24(q) else '—',
            get_campanhas_fy24(q) if get_campanhas_fy24(q) else '—'
        ]
    }
    df_overview = pd.DataFrame(overview_data)
    
    df_vertical = get_vertical_distribution(q)
    df_vertical.columns = ['Vertical', 'Percentual (%)']
    
    camp_data = get_campanhas_detalhes(q)
    df_campanhas = pd.DataFrame([
        {'Indicador': 'Campanhas Solicitadas', 'Valor': camp_data.get('solicitadas', '—')},
        {'Indicador': 'Campanhas Veiculadas', 'Valor': camp_data.get('veiculadas', '—')},
        {'Indicador': 'Taxa de Conversão (%)', 'Valor': camp_data.get('taxa_conversao', '—')},
        {'Indicador': 'Leads Gerados', 'Valor': camp_data.get('leads', '—')},
        {'Indicador': 'Top Campanhas', 'Valor': camp_data.get('top', '—').replace('<br>', ' | ')},
    ])
    
    taxa_comp = get_campanhas_comparativos(q, 'taxa_conversao')
    obj_dist = get_campanhas_comparativos(q, 'objetivo')
    
    df_campanhas_comp = pd.DataFrame([
        {'Indicador': 'Taxa Conversão (c/ investimento)', 'Valor': f"{taxa_comp.get('com_investimento', '—')}%"},
        {'Indicador': 'Taxa Conversão (s/ investimento)', 'Valor': f"{taxa_comp.get('sem_investimento', '—')}%" if taxa_comp.get('sem_investimento') else '—'},
        {'Indicador': 'Referência Mercado', 'Valor': taxa_comp.get('referencia_mercado', '—')},
        {'Indicador': 'Distribuição - Conversão (%)', 'Valor': f"{obj_dist.get('conversao', '83')}%"},
        {'Indicador': 'Distribuição - Branding (%)', 'Valor': f"{obj_dist.get('branding', '17')}%"},
    ])
    
    df_email = pd.DataFrame([
        {'Métrica': 'Total de Envios', 'Valor FY25': get_email_value(q, 'envios'), 'Valor FY24 (mesmo trimestre)': get_email_fy24(q, 'envios')},
        {'Métrica': 'Taxa de Entrega (%)', 'Valor FY25': get_email_value(q, 'entrega'), 'Valor FY24 (mesmo trimestre)': get_email_fy24(q, 'entrega')},
        {'Métrica': 'Taxa de Abertura (%)', 'Valor FY25': get_email_value(q, 'abertura'), 'Valor FY24 (mesmo trimestre)': get_email_fy24(q, 'abertura')},
        {'Métrica': 'Taxa de Cliques (%)', 'Valor FY25': get_email_value(q, 'cliques'), 'Valor FY24 (mesmo trimestre)': get_email_fy24(q, 'cliques')},
        {'Métrica': 'Taxa de Opt-Out (%)', 'Valor FY25': get_email_value(q, 'optout'), 'Valor FY24 (mesmo trimestre)': get_email_fy24(q, 'optout')},
    ])
    
    df_redes_geral = pd.DataFrame([
        {'Métrica': 'Novos Seguidores', 'Valor FY25': get_redes_value(q, 'seguidores'), 'Valor FY24 (mesmo trimestre)': get_redes_fy24(q, 'seguidores')},
        {'Métrica': 'Total de Engajamentos', 'Valor FY25': get_redes_value(q, 'engajamentos'), 'Valor FY24 (mesmo trimestre)': get_redes_fy24(q, 'engajamentos')},
        {'Métrica': 'Total de Cliques', 'Valor FY25': get_redes_value(q, 'cliques'), 'Valor FY24 (mesmo trimestre)': get_redes_fy24(q, 'cliques')},
    ])
    
    df_blog = pd.DataFrame([
        {'Métrica': 'Visitas', 'Valor FY25': get_blog_value(q, 'visitas'), 'Valor FY24 (mesmo trimestre)': get_blog_fy24(q, 'visitas') if get_blog_fy24(q, 'visitas') else '—'},
        {'Métrica': 'Usuários', 'Valor FY25': get_blog_value(q, 'usuarios'), 'Valor FY24 (mesmo trimestre)': get_blog_fy24(q, 'usuarios') if get_blog_fy24(q, 'usuarios') else '—'},
        {'Métrica': 'Blogposts Publicados', 'Valor FY25': get_blog_value(q, 'blogposts'), 'Valor FY24 (mesmo trimestre)': get_blog_fy24(q, 'blogposts') if get_blog_fy24(q, 'blogposts') else '—'},
        {'Métrica': 'Tempo Médio na Página', 'Valor FY25': get_blog_value(q, 'tempo_medio'), 'Valor FY24 (mesmo trimestre)': get_blog_fy24(q, 'tempo_medio') if get_blog_fy24(q, 'tempo_medio') else '—'},
    ])
    
    df_newsletter = pd.DataFrame([
        {'Métrica': 'Empresas Inscritas', 'Valor FY25': get_newsletter_value(q, 'empresas'), 'Valor FY24 (mesmo trimestre)': get_newsletter_fy24(q, 'empresas') if get_newsletter_fy24(q, 'empresas') else '—'},
        {'Métrica': 'Total de Envios', 'Valor FY25': get_newsletter_value(q, 'envios'), 'Valor FY24 (mesmo trimestre)': get_newsletter_fy24(q, 'envios') if get_newsletter_fy24(q, 'envios') else '—'},
        {'Métrica': 'Taxa de Abertura (%)', 'Valor FY25': get_newsletter_value(q, 'abertura'), 'Valor FY24 (mesmo trimestre)': get_newsletter_fy24(q, 'abertura') if get_newsletter_fy24(q, 'abertura') else '—'},
        {'Métrica': 'Taxa de Cliques (%)', 'Valor FY25': get_newsletter_value(q, 'cliques'), 'Valor FY24 (mesmo trimestre)': get_newsletter_fy24(q, 'cliques') if get_newsletter_fy24(q, 'cliques') else '—'},
    ])
    
    df_fabricantes = get_fabricantes_data(q)
    
    insights_map = {
        'Q1': ["Fortinet foi o maior solicitante com 120 peças na vertical Segurança", "AWS liderou em Cloud com 43 peças", "IBM teve destaque em Data & AI com 40 peças", "Taxa de conversão de campanhas atingiu 7,26%"],
        'Q2': ["Fortinet liderou em Segurança com 117 peças", "Microsoft foi destaque em Cloud com 115 peças", "Campanha IBM IA gerou 55 leads", "Taxa de abertura de e-mail atingiu 45,3%"],
        'Q3': ["Fortinet manteve liderança em Segurança com 129 peças", "Cloud On the Go gerou 383 leads", "Taxa de cliques em e-mail atingiu 6%"],
        'Q4': ["Fortinet continuou líder em Segurança com 75 peças", "Campanha de recrutamento Fortinet gerou 70 leads", "Total de envios de e-mail atingiu 349.487"],
    }
    df_insights = pd.DataFrame({'Insights e Recomendações FY25': insights_map.get(q, ['Nenhum insight disponível'])})
    
    df_email_vertical = get_email_vertical_data(q)
    df_email_tipo = get_email_tipo_data(q)
    df_redes_por_rede = get_redes_por_rede_data(q)
    
    top_fab = get_top_fabricantes_data(q)
    if top_fab:
        df_top_fabricantes = pd.DataFrame([
            {'Categoria': 'Mais Publicados', 'Detalhes': top_fab.get('mais_publicados', '—')},
            {'Categoria': 'Mais Engajados', 'Detalhes': top_fab.get('mais_engajados', '—')},
            {'Categoria': 'Distribuição por Vertical', 'Detalhes': top_fab.get('distribuicao_vertical', '—')},
        ])
    else:
        df_top_fabricantes = pd.DataFrame({'Mensagem': ['Sem dados disponíveis']})
    
    all_data = {
        '1_Overview': df_overview,
        '2_Distribuicao_Vertical': df_vertical,
        '3_Campanhas_Resumo': df_campanhas,
        '4_Campanhas_Comparativos': df_campanhas_comp,
        '5_Email_Marketing': df_email,
        '6_Redes_Sociais_Geral': df_redes_geral,
        '7_Blog': df_blog,
        '8_Newsletter': df_newsletter,
        '9_Fabricantes': df_fabricantes if not df_fabricantes.empty else pd.DataFrame({'Mensagem': ['Sem dados disponíveis']}),
        '10_Insights': df_insights,
        '11_Email_Por_Vertical': df_email_vertical if not df_email_vertical.empty else pd.DataFrame({'Mensagem': ['Sem dados disponíveis']}),
        '12_Email_Por_Tipo': df_email_tipo if not df_email_tipo.empty else pd.DataFrame({'Mensagem': ['Sem dados disponíveis']}),
        '13_Redes_Por_Rede': df_redes_por_rede if not df_redes_por_rede.empty else pd.DataFrame({'Mensagem': ['Sem dados disponíveis']}),
        '14_Top_Fabricantes_Redes': df_top_fabricantes
    }
    
    return all_data

# ==================== CSS ====================
CSS_STATIC = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main .block-container { padding: 0; max-width: 100%; }
    #MainMenu, header, footer { visibility: hidden; }

    .premium-header {
        background: linear-gradient(135deg, rgba(0,102,204,0.95) 0%, rgba(123,44,191,0.85) 50%, rgba(255,107,53,0.75) 100%);
        backdrop-filter: blur(10px);
        padding: 48px 56px 40px 56px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    .premium-title {
        font-size: 52px; font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF, #E0E0E0);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0; letter-spacing: -1px;
    }
    .premium-sub { font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 8px; }
    .premium-quarter {
        font-size: 24px; font-weight: 600; margin-top: 16px; display: inline-block;
        background: rgba(0,0,0,0.4); padding: 6px 24px; border-radius: 40px;
        color: #FFFFFF;
    }

    .glass-card {
        border-radius: 24px; padding: 24px;
        transition: all 0.3s ease;
        margin-bottom: 24px; height: 100%;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }

    .kpi-premium { text-align: center; }
    .kpi-icon { font-size: 40px; margin-bottom: 12px; }
    .kpi-number { font-size: 48px; font-weight: 800; line-height: 1; }
    .kpi-label { font-size: 13px; margin-top: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 500; }
    .kpi-variation {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 11px; font-weight: 600; margin-top: 8px;
    }
    .kpi-up   { background: rgba(46,125,50,0.3);   color: #6FBF6F; border: 1px solid rgba(76,175,80,0.4); }
    .kpi-down { background: rgba(211,47,47,0.3);   color: #FF8A80; border: 1px solid rgba(239,83,80,0.4); }
    .kpi-neutral { background: rgba(136,146,160,0.3); color: #B0BEC5; border: 1px solid rgba(136,146,160,0.4); }
    .kpi-fy24-up      { background: rgba(255,183,77,0.2);  color: #FFD54F; border: 1px solid rgba(255,183,77,0.4); }
    .kpi-fy24-down    { background: rgba(255,112,67,0.2);  color: #FFAB91; border: 1px solid rgba(255,112,67,0.4); }
    .kpi-fy24-neutral { background: rgba(189,189,189,0.2); color: #E0E0E0; border: 1px solid rgba(189,189,189,0.4); }

    .comparison-premium { border-radius: 16px; padding: 12px; text-align: left; margin-top: 12px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); }
    .comparison-header { font-size: 10px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.6); }
    .comparison-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; font-size: 12px; }
    .comp-label { color: rgba(255,255,255,0.7); }
    .comp-value { font-weight: 700; color: #FFFFFF; }
    .fy24-label { color: #FFD54F !important; }
    .fy24-value { color: #FFD54F !important; }
    .comp-badge { display: inline-flex; align-items: center; gap: 3px; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; }
    .badge-up   { background: rgba(46,125,50,0.35);  color: #6FBF6F; }
    .badge-down { background: rgba(211,47,47,0.35);  color: #FF8A80; }
    .badge-flat { background: rgba(136,146,160,0.3); color: #B0BEC5; }

    .section-premium {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 48px 0 24px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 12px;
    }
    .section-premium:first-of-type {
        margin-top: 0;
    }
    .section-icon { font-size: 32px; background: rgba(0,102,204,0.25); padding: 12px; border-radius: 16px; }
    .section-title-premium { font-size: 24px; font-weight: 700; letter-spacing: -0.5px; color: #FFFFFF; }
    .section-sub { font-size: 13px; margin-top: 4px; color: rgba(255,255,255,0.7); }

    .bar-premium { margin-bottom: 20px; }
    .bar-track-premium { border-radius: 12px; height: 40px; overflow: hidden; background: rgba(0,0,0,0.3); }
    .bar-fill-premium { height: 100%; border-radius: 12px; display: flex; align-items: center; justify-content: flex-end; padding-right: 16px; color: white; font-size: 14px; font-weight: 600; }
    .bar-label-premium { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; font-weight: 500; }

    .blog-premium { border-radius: 24px; padding: 28px; transition: all 0.4s ease; height: 100%; position: relative; overflow: hidden; margin-bottom: 24px; background: rgba(15,43,61,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.15); }
    .blog-premium::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #0066CC, #FF6B35, #7B2CBF); }
    .blog-premium:hover { transform: translateY(-4px); }
    .blog-header-premium { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.15); }
    .blog-icon-premium { font-size: 36px; }
    .blog-title-premium { font-size: 20px; font-weight: 700; color: #FFFFFF; }
    .blog-sub-premium { font-size: 11px; margin-top: 2px; color: rgba(255,255,255,0.7); }
    .blog-item-premium { margin-bottom: 24px; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .blog-item-premium:last-child { margin-bottom: 0; border-bottom: none; }
    .blog-label-premium { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; color: rgba(255,255,255,0.7); }
    .blog-value-premium { font-size: 32px; font-weight: 800; line-height: 1.1; margin-bottom: 8px; color: #FFFFFF; }
    .blog-compare-premium { font-size: 11px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; color: rgba(255,255,255,0.7); }
    .blog-compare-fy24 { font-size: 11px; display: flex; align-items: center; gap: 8px; margin-top: 4px; color: #FFD54F; }
    .blog-change-premium { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px; display: inline-flex; align-items: center; gap: 4px; }
    .blog-change-up   { background: rgba(46,125,50,0.4);  color: #6FBF6F; }
    .blog-change-down { background: rgba(211,47,47,0.4);  color: #FF8A80; }

    .footer-premium { margin-top: 60px; padding: 24px; text-align: center; font-size: 12px; border-top: 1px solid rgba(255,255,255,0.15); color: rgba(255,255,255,0.7); }

    .stDataFrame { border-radius: 16px !important; overflow: hidden !important; }
    .stDataFrame thead th { background: linear-gradient(135deg, rgba(0,102,204,0.4), rgba(123,44,191,0.3)) !important; color: #FFFFFF !important; font-weight: 600 !important; }
    .stDataFrame tbody td { background: rgba(15,43,61,0.6) !important; color: #FFFFFF !important; }

    .glass-card [style*="border-left"] {
        transition: all 0.2s ease;
    }
    .glass-card:hover [style*="border-left"] {
        padding-left: 16px;
    }
    .stColumns {
        gap: 20px;
    }
    .kpi-premium, .glass-card {
        animation: fadeInUp 0.4s ease-out;
    }
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
"""

# ==================== MAIN ====================
def main():
    CSS_THEME = f"""
    <style>
        .stApp {{ background: {BG_GRADIENT}; }}
        [data-testid="stSidebar"] {{
            background: {COLORS['card_bg']};
            border-right: 1px solid {COLORS['border']};
        }}
        [data-testid="stSidebar"] * {{ color: {COLORS['text']}; }}
        .glass-card {{
            background: {COLORS['card_bg']};
            backdrop-filter: blur(12px);
            border: 1px solid {COLORS['border']};
        }}
        .kpi-number {{
            background: {COLORS['kpi_number_bg']};
            -webkit-background-clip: text; background-clip: text;
            color: {COLORS['kpi_number_color']};
        }}
        .kpi-label, .section-sub, .comparison-header, .blog-label-premium {{ color: {COLORS['text_muted']}; }}
        .section-title-premium, .blog-title-premium, .blog-value-premium {{ color: {COLORS['text']}; }}
        .bar-label-premium span:first-child {{ color: {COLORS['text']}; }}
    </style>
    """

    st.markdown(CSS_STATIC, unsafe_allow_html=True)
    st.markdown(CSS_THEME, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="premium-header">
        <div class="premium-title">TD SYNNEX BR</div>
        <div class="premium-sub">Quarterly Business Review · Performance Analytics</div>
        <div class="premium-quarter">{st.session_state.get('view', 'Q1')} FY25</div>
    </div>
    """, unsafe_allow_html=True)

    if 'view' not in st.session_state:
        st.session_state.view = 'Q1'

    # Botões trimestrais - 8 colunas
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
    
    with col2:
        if st.button('Q1', key='q1', use_container_width=True):
            st.session_state.view = 'Q1'
            st.rerun()
    
    with col3:
        if st.button('Q2', key='q2', use_container_width=True):
            st.session_state.view = 'Q2'
            st.rerun()
    
    with col4:
        if st.button('Q3', key='q3', use_container_width=True):
            st.session_state.view = 'Q3'
            st.rerun()
    
    with col5:
        if st.button('Q4', key='q4', use_container_width=True):
            st.session_state.view = 'Q4'
            st.rerun()
    
    with col6:
        if st.button('🏆 FY25', key='fy25', use_container_width=True):
            st.session_state.view = 'FY25'
            st.rerun()
    
    with col7:
        if st.button('📄 Slides', key='slides', use_container_width=True):
            st.session_state.view = 'Slides'
            st.rerun()

    st.markdown('<div style="padding:0 56px 56px 56px;">', unsafe_allow_html=True)

    q = st.session_state.view
    quarterly_data = {
        t: {'pecas': get_pecas_value(t), 'solic': get_solicitacoes_value(t), 'camp': get_campanhas_value(t)}
        for t in ['Q1', 'Q2', 'Q3', 'Q4']
    }

    # ==================== VIEW SLIDES ====================
    if q == 'Slides':
        st.markdown(f'<div class="section-premium"><div class="section-icon">📄</div><div><div class="section-title-premium">Conteúdo dos Slides QBR</div><div class="section-sub">Transcrição completa das apresentações por trimestre</div></div></div>', unsafe_allow_html=True)
        
        slide_trimestre = st.selectbox(
            "Selecione o trimestre para visualizar o conteúdo dos slides",
            ['Q1', 'Q2', 'Q3', 'Q4'],
            index=0,
            key='slide_selector'
        )
        
        slides = get_slides_content(slide_trimestre)
        
        if slides:
            st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <div style="font-size:28px;font-weight:800;color:{COLORS['primary']};margin-bottom:8px;">{slides.get('titulo', '')}</div>
                <div style="font-size:14px;color:{COLORS['text_muted']};">Documentação completa das análises e insights do trimestre</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Exibe cada seção
            for secao_key, secao in slides.get('secoes', {}).items():
                titulo_secao = secao.get('titulo', secao_key.replace('_', ' ').title())
                conteudo = secao.get('conteudo', '')
                # Remove apenas tags </div> e limpa espaços extras
                conteudo_limpo = conteudo.replace('</div>', '').replace('<div>', '').strip()
                
                with st.expander(f"{titulo_secao}", expanded=True):
                    st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.2);border-radius:16px;padding:20px;margin-bottom:8px;">
                        <div style="font-size:14px;line-height:1.8;color:{COLORS['text']};white-space:pre-wrap;">
                            {conteudo_limpo}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Botão para baixar todo o conteúdo
            all_content = ""
            for secao_key, secao in slides.get('secoes', {}).items():
                titulo = secao.get('titulo', secao_key)
                conteudo = secao.get('conteudo', '')
                conteudo_limpo = conteudo.replace('</div>', '').replace('<div>', '').strip()
                all_content += f"=== {titulo} ===\n{conteudo_limpo}\n\n"
            
            st.download_button(
                label="📥 Baixar Conteúdo dos Slides (TXT)",
                data=all_content,
                file_name=f"slides_qbr_{slide_trimestre}_fy25.txt",
                mime="text/plain",
                key='download_slides'
            )
        else:
            st.info(f"Conteúdo dos slides não disponível para {slide_trimestre}.")
    
    # ==================== VIEW FY25 ====================
    elif q == 'FY25':
        render_comparative_charts(quarterly_data)

        st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Overview Anual</div><div class="section-sub">Indicadores consolidados FY25</div></div></div>', unsafe_allow_html=True)
        pecas_tot = sum(quarterly_data[t]['pecas'] for t in ['Q1','Q2','Q3','Q4'])
        solic_tot = sum(quarterly_data[t]['solic'] for t in ['Q1','Q2','Q3','Q4'])
        camp_tot = sum(quarterly_data[t]['camp'] for t in ['Q1','Q2','Q3','Q4'])

        k1, k2, k3 = st.columns(3)
        with k1: render_kpi_premium(pecas_tot, "Total Peças", "📦")
        with k2: render_kpi_premium(solic_tot, "Total Solicitações", "📋")
        with k3: render_kpi_premium(camp_tot, "Total Campanhas", "🎯")

        st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">Média anual</div></div></div>', unsafe_allow_html=True)
        vert_vals = {}
        for t in ['Q1','Q2','Q3','Q4']:
            for _, row in get_vertical_distribution(t).iterrows():
                vert_vals.setdefault(row['vertical'], []).append(row['percentual'])
        df_annual = pd.DataFrame([{'vertical': v, 'percentual': sum(ps)/len(ps)} for v, ps in vert_vals.items()]).sort_values('percentual', ascending=False)
        render_horizontal_bars(df_annual, "% Peças por Vertical (Média Anual)")

        st.markdown(f'<div class="section-premium"><div class="section-icon">🎯</div><div><div class="section-title-premium">Campanhas</div><div class="section-sub">Métricas por trimestre</div></div></div>', unsafe_allow_html=True)
        render_campanhas_card(q, is_annual=True)

        st.markdown(f'<div class="section-premium"><div class="section-icon">🏭</div><div><div class="section-title-premium">Fabricantes por Vertical</div><div class="section-sub">Destaques do ano</div></div></div>', unsafe_allow_html=True)
        df_fab = get_fabricantes_data('Q4')
        if not df_fab.empty:
            render_table(df_fab, "🏭 Fabricantes por Vertical (Q4)")

        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📥 Exportar Dados")
            dl_fmt = st.selectbox("Formato", ["CSV", "Excel"], key="dl_fy25")
            export_completo = st.checkbox("📋 Exportar todas as abas (completo)", value=True)
            
            if st.button("📥 Baixar FY25", key="btn_dl_fy25"):
                if export_completo:
                    all_data = export_quarter_data('Q4', quarterly_data)
                    
                    if dl_fmt == "CSV":
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for sheet_name, df in all_data.items():
                                csv_data = df.to_csv(index=False)
                                zip_file.writestr(f"{sheet_name}.csv", csv_data)
                        st.download_button(
                            "✅ Baixar Todos (ZIP)", 
                            zip_buffer.getvalue(), 
                            "qbr_fy25_completo.zip", 
                            "application/zip"
                        )
                    else:
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                            for sheet_name, df in all_data.items():
                                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                        st.download_button(
                            "✅ Baixar Excel Completo", 
                            buf.getvalue(), 
                            "qbr_fy25_completo.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    dl_rows = [{'Trimestre':t,'Peças':quarterly_data[t]['pecas'],'Solicitações':quarterly_data[t]['solic'],'Campanhas':quarterly_data[t]['camp']} for t in ['Q1','Q2','Q3','Q4']]
                    df_dl = pd.DataFrame(dl_rows)
                    if dl_fmt == "CSV":
                        st.download_button("✅ Baixar CSV", df_dl.to_csv(index=False), "qbr_fy25.csv", "text/csv")
                    else:
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine='openpyxl') as w: df_dl.to_excel(w, index=False)
                        st.download_button("✅ Baixar Excel", buf.getvalue(), "qbr_fy25.xlsx")

    # ==================== VIEW Q1-Q4 ====================
    elif q in ['Q1', 'Q2', 'Q3', 'Q4']:
        q_num = int(q[1])
        prev_fy25_q = f'Q{q_num - 1}' if q_num > 1 else None
        prev_fy25_name = f'{prev_fy25_q} FY25' if prev_fy25_q else '—'
        fy24_q_label = f'{q} FY24'

        pecas_val = quarterly_data[q]['pecas']
        solic_val = quarterly_data[q]['solic']
        camp_val = quarterly_data[q]['camp']

        if prev_fy25_q:
            pecas_var = calc_variacao(pecas_val, quarterly_data[prev_fy25_q]['pecas'])
            solic_var = calc_variacao(solic_val, quarterly_data[prev_fy25_q]['solic'])
            camp_var = calc_variacao(camp_val, quarterly_data[prev_fy25_q]['camp'])
            kpi_ref = prev_fy25_name
        else:
            pecas_var = solic_var = camp_var = None
            kpi_ref = None

        pecas_fy24 = get_pecas_fy24(q)
        solic_fy24 = get_solicitacoes_fy24(q)
        camp_fy24 = get_campanhas_fy24(q)

        pecas_var_fy24 = calc_variacao(pecas_val, pecas_fy24) if pecas_fy24 else None
        solic_var_fy24 = calc_variacao(solic_val, solic_fy24) if solic_fy24 else None
        camp_var_fy24 = calc_variacao(camp_val, camp_fy24) if camp_fy24 else None

        # Overview KPIs
        st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Overview</div><div class="section-sub">Indicadores de performance · {q} FY25</div></div></div>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        with k1:
            render_kpi_premium(pecas_val, "Peças Produzidas", "📦",
                               pecas_var, kpi_ref,
                               pecas_var_fy24, fy24_q_label if pecas_fy24 else None)
        with k2:
            render_kpi_premium(solic_val, "Solicitações", "📋",
                               solic_var, kpi_ref,
                               solic_var_fy24, fy24_q_label if solic_fy24 else None)
        with k3:
            render_kpi_premium(camp_val, "Campanhas", "🎯",
                               camp_var, kpi_ref,
                               camp_var_fy24, fy24_q_label if camp_fy24 else None)

        # Distribuição por Vertical
        st.markdown(f'<div class="section-premium"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">% Peças por vertical</div></div></div>', unsafe_allow_html=True)
        render_horizontal_bars(get_vertical_distribution(q), "% Peças por Vertical")

        # ==================== CAMPANHAS ====================
        st.markdown(f'<div class="section-premium"><div class="section-icon">🎯</div><div><div class="section-title-premium">Campanhas</div><div class="section-sub">Métricas, comparativos e destaques</div></div></div>', unsafe_allow_html=True)
        
        camp = get_campanhas_detalhes(q)
        obj_dist = get_campanhas_comparativos(q, 'objetivo')
        
        cc1, cc2 = st.columns(2)
        with cc1:
            st.html(f"""
            <div class="glass-card">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;">
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">📋 Solicitadas</div>
                        <div style="font-size:42px;font-weight:800;color:{COLORS['text']};">{camp.get('solicitadas', '—')}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">🚀 Veiculadas</div>
                        <div style="font-size:42px;font-weight:800;color:{COLORS['text']};">{camp.get('veiculadas', '—')}</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">📊 Taxa Conversão</div>
                        <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{camp.get('taxa_conversao', '—')}%</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px;color:{COLORS['text_muted']};margin-bottom:8px;">👥 Leads Gerados</div>
                        <div style="font-size:28px;font-weight:800;color:{COLORS['text']};">{camp.get('leads', '—')}</div>
                    </div>
                </div>
            </div>
            """)
        
        with cc2:
            st.html(f"""
            <div class="glass-card">
                <div style="font-size:18px;font-weight:700;color:{COLORS['text']};margin-bottom:16px;">🏆 Top Campanhas</div>
                <div style="font-size:13px;line-height:1.6;color:{COLORS['text']};margin-bottom:20px;">{camp.get('top', '—')}</div>
                <div style="font-size:14px;font-weight:600;color:{COLORS['text']};margin:20px 0 12px;">📊 Distribuição por Objetivo</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                    <div style="background:rgba(46,125,50,0.2);border-radius:16px;padding:12px;text-align:center;">
                        <div style="font-size:11px;color:{COLORS['text_muted']};">Conversão</div>
                        <div style="font-size:28px;font-weight:800;color:#6FBF6F;">{obj_dist.get('conversao', '83')}%</div>
                    </div>
                    <div style="background:rgba(255,107,53,0.2);border-radius:16px;padding:12px;text-align:center;">
                        <div style="font-size:11px;color:{COLORS['text_muted']};">Branding</div>
                        <div style="font-size:28px;font-weight:800;color:#FF8C5A;">{obj_dist.get('branding', '17')}%</div>
                    </div>
                </div>
            </div>
            """)
        
        # Comparativo de Taxa de Conversão
        st.markdown(f'<div class="section-premium" style="margin-top: 16px;"><div class="section-icon">📈</div><div><div class="section-title-premium">Comparativo de Taxa de Conversão</div><div class="section-sub">Histórico e referência de mercado</div></div></div>', unsafe_allow_html=True)
        
        taxa_comp = get_campanhas_comparativos(q, 'taxa_conversao')
        if taxa_comp:
            col_comp1, col_comp2, col_comp3 = st.columns(3)
            
            with col_comp1:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:{COLORS['primary']};">💰 Com Investimento</div>
                    <div style="font-size:32px;font-weight:800;color:#6FBF6F;">{taxa_comp.get('com_investimento', '—')}%</div>
                    <div style="font-size:11px;color:{COLORS['text_muted']};margin-top:8px;">Referência mercado: {taxa_comp.get('referencia_mercado', '—')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_comp2:
                sem_invest = taxa_comp.get('sem_investimento')
                if sem_invest is not None and sem_invest != '—':
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:{COLORS['secondary']};">📢 Sem Investimento</div>
                        <div style="font-size:32px;font-weight:800;color:#FF8C5A;">{sem_invest}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:{COLORS['secondary']};">📢 Sem Investimento</div>
                        <div style="font-size:32px;font-weight:800;color:{COLORS['text_muted']};">—</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_comp3:
                comparativos = []
                if taxa_comp.get('q4fy24') is not None and taxa_comp.get('q4fy24') != '—':
                    comparativos.append(f'<div>vs Q4 FY24: {taxa_comp.get("q4fy24")}%</div>')
                if taxa_comp.get('q1fy24') is not None and taxa_comp.get('q1fy24') != '—':
                    comparativos.append(f'<div>vs Q1 FY24: {taxa_comp.get("q1fy24")}%</div>')
                
                comparativos_html = ''.join(comparativos) if comparativos else '<div>Sem dados disponíveis</div>'
                
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:{COLORS['accent']};">📅 Comparativo FY24</div>
                    <div style="font-size:13px;line-height:1.8;">
                        {comparativos_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Distribuição por Vertical - Campanhas
        st.markdown(f'<div class="section-premium" style="margin-top: 16px;"><div class="section-icon">📊</div><div><div class="section-title-premium">Distribuição por Vertical</div><div class="section-sub">Comparativo entre solicitadas e veiculadas</div></div></div>', unsafe_allow_html=True)
        
        col_solic, col_veic = st.columns(2)
        
        with col_solic:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:{COLORS['primary']};border-left:3px solid {COLORS['primary']};padding-left:12px;">📋 Campanhas Solicitadas</div>
            """, unsafe_allow_html=True)
            
            solicitadas_data = get_campanhas_comparativos(q, 'vertical_solicitadas')
            if solicitadas_data:
                for vertical, percent in solicitadas_data.items():
                    st.markdown(f"""
                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="font-size:13px;color:{COLORS['text']};">{vertical}</span>
                            <span style="font-size:13px;font-weight:600;color:{COLORS['primary']};">{percent}%</span>
                        </div>
                        <div style="background:rgba(0,0,0,0.2);border-radius:8px;height:8px;overflow:hidden;">
                            <div style="width:{percent}%;height:100%;background:{COLORS['primary']};border-radius:8px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:13px;color:rgba(255,255,255,0.5);">Sem dados disponíveis</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_veic:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:{COLORS['secondary']};border-left:3px solid {COLORS['secondary']};padding-left:12px;">🚀 Campanhas Veiculadas</div>
            """, unsafe_allow_html=True)
            
            veiculadas_data = get_campanhas_comparativos(q, 'vertical_veiculadas')
            if veiculadas_data:
                for vertical, percent in veiculadas_data.items():
                    st.markdown(f"""
                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="font-size:13px;color:{COLORS['text']};">{vertical}</span>
                            <span style="font-size:13px;font-weight:600;color:{COLORS['secondary']};">{percent}%</span>
                        </div>
                        <div style="background:rgba(0,0,0,0.2);border-radius:8px;height:8px;overflow:hidden;">
                            <div style="width:{percent}%;height:100%;background:{COLORS['secondary']};border-radius:8px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:13px;color:rgba(255,255,255,0.5);">Sem dados disponíveis</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Fabricantes
        st.markdown(f'<div class="section-premium"><div class="section-icon">🏭</div><div><div class="section-title-premium">Fabricantes por Vertical</div><div class="section-sub">Principais fornecedores</div></div></div>', unsafe_allow_html=True)
        df_fab = get_fabricantes_data(q)
        if not df_fab.empty:
            render_table(df_fab, "🏭 Fabricantes por Vertical")

        # ==================== EMAIL MARKETING ====================
        st.markdown(f'<div class="section-premium"><div class="section-icon">📧</div><div><div class="section-title-premium">E-mail Marketing</div><div class="section-sub">Métricas de performance e análise detalhada</div></div></div>', unsafe_allow_html=True)
        
        entrega_atual = get_email_value(q, 'entrega')
        abertura_atual = get_email_value(q, 'abertura')
        cliques_atual = get_email_value(q, 'cliques')
        optout_atual = get_email_value(q, 'optout')

        prev_entrega = get_email_value(prev_fy25_q, 'entrega') if prev_fy25_q else '—'
        prev_abertura = get_email_value(prev_fy25_q, 'abertura') if prev_fy25_q else '—'
        prev_cliques = get_email_value(prev_fy25_q, 'cliques') if prev_fy25_q else '—'
        prev_optout = get_email_value(prev_fy25_q, 'optout') if prev_fy25_q else '—'

        ent_fy24 = get_email_fy24(q, 'entrega')
        abe_fy24 = get_email_fy24(q, 'abertura')
        cli_fy24 = get_email_fy24(q, 'cliques')
        opt_fy24 = get_email_fy24(q, 'optout')

        def fmt_pct(v): return f"{v}%" if v not in ('—', None, '') else '—'

        e1, e2, e3, e4 = st.columns(4)
        with e1:
            render_metric_card("Entregas", "✅",
                               fmt_pct(entrega_atual), fmt_pct(prev_entrega), prev_fy25_name,
                               ent_fy24, fy24_q_label if ent_fy24 else None)
        with e2:
            render_metric_card("Aberturas", "👁️",
                               fmt_pct(abertura_atual), fmt_pct(prev_abertura), prev_fy25_name,
                               abe_fy24, fy24_q_label if abe_fy24 else None)
        with e3:
            render_metric_card("Cliques", "🖱️",
                               fmt_pct(cliques_atual), fmt_pct(prev_cliques), prev_fy25_name,
                               cli_fy24, fy24_q_label if cli_fy24 else None)
        with e4:
            render_metric_card("Opt-Out", "🚫",
                               fmt_pct(optout_atual), fmt_pct(prev_optout), prev_fy25_name,
                               opt_fy24, fy24_q_label if opt_fy24 else None)
        
        # Tabelas detalhadas de Email Marketing
        st.markdown(f'<div class="section-premium" style="margin-top: 16px;"><div class="section-icon">📊</div><div><div class="section-title-premium">Análise Detalhada</div><div class="section-sub">Métricas por Vertical e Tipo de E-mail</div></div></div>', unsafe_allow_html=True)
        
        col_email_vert, col_email_tipo = st.columns(2)
        
        with col_email_vert:
            df_email_vertical = get_email_vertical_data(q)
            if not df_email_vertical.empty:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:{COLORS['primary']};border-left:3px solid {COLORS['primary']};padding-left:12px;">📊 Por Vertical</div>
                """, unsafe_allow_html=True)
                st.dataframe(df_email_vertical, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_email_tipo:
            df_email_tipo = get_email_tipo_data(q)
            if not df_email_tipo.empty:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:{COLORS['primary']};border-left:3px solid {COLORS['primary']};padding-left:12px;">📧 Por Tipo de E-mail</div>
                """, unsafe_allow_html=True)
                st.dataframe(df_email_tipo, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # ==================== REDES SOCIAIS ====================
        st.markdown(f'<div class="section-premium"><div class="section-icon">📱</div><div><div class="section-title-premium">Redes Sociais</div><div class="section-sub">Engajamento, alcance e análise por rede</div></div></div>', unsafe_allow_html=True)
        
        seg_atual = get_redes_value(q, 'seguidores')
        eng_atual = get_redes_value(q, 'engajamentos')
        cli_atual = get_redes_value(q, 'cliques')
        prev_seg = get_redes_value(prev_fy25_q, 'seguidores') if prev_fy25_q else '—'
        prev_eng = get_redes_value(prev_fy25_q, 'engajamentos') if prev_fy25_q else '—'
        prev_cli = get_redes_value(prev_fy25_q, 'cliques') if prev_fy25_q else '—'

        seg_fy24 = get_redes_fy24(q, "seguidores")
        eng_fy24 = get_redes_fy24(q, "engajamentos")
        cli_rs_fy24 = get_redes_fy24(q, "cliques")

        r1, r2, r3 = st.columns(3)
        with r1: render_metric_card("Novos Seguidores", "👥", seg_atual, prev_seg, prev_fy25_name, seg_fy24, fy24_q_label if seg_fy24 else None)
        with r2: render_metric_card("Engajamentos", "❤️", eng_atual, prev_eng, prev_fy25_name, eng_fy24, fy24_q_label if eng_fy24 else None)
        with r3: render_metric_card("Cliques", "🖱️", cli_atual, prev_cli, prev_fy25_name, cli_rs_fy24, fy24_q_label if cli_rs_fy24 else None)
        
        # Tabelas detalhadas de Redes Sociais
        st.markdown(f'<div class="section-premium" style="margin-top: 16px;"><div class="section-icon">📊</div><div><div class="section-title-premium">Análise Detalhada</div><div class="section-sub">Performance por rede e destaques de fabricantes</div></div></div>', unsafe_allow_html=True)
        
        df_redes_por_rede = get_redes_por_rede_data(q)
        if not df_redes_por_rede.empty:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:{COLORS['primary']};border-left:3px solid {COLORS['primary']};padding-left:12px;">📈 Performance por Rede Social</div>
            """, unsafe_allow_html=True)
            st.dataframe(df_redes_por_rede, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        top_fab = get_top_fabricantes_data(q)
        if top_fab:
            col_fab1, col_fab2 = st.columns(2)
            with col_fab1:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:#FFD966;border-left:3px solid #FFD966;padding-left:12px;">📸 Top Fabricantes Mais Publicados</div>
                    <div style="font-size:14px;line-height:1.6;color:{COLORS['text']};">{top_fab.get('mais_publicados', '—')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_fab2:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:#FF8C5A;border-left:3px solid #FF8C5A;padding-left:12px;">🔥 Top Fabricantes Mais Engajados</div>
                    <div style="font-size:14px;line-height:1.6;color:{COLORS['text']};">{top_fab.get('mais_engajados', '—')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:16px;font-weight:600;margin-bottom:16px;color:#6FBF6F;border-left:3px solid #6FBF6F;padding-left:12px;">📊 Distribuição de Publicações por Vertical</div>
                <div style="font-size:14px;line-height:1.6;color:{COLORS['text']};">{top_fab.get('distribuicao_vertical', '—')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Blog & Newsletter
        st.markdown(f'<div class="section-premium"><div class="section-icon">📝</div><div><div class="section-title-premium">Blog &amp; Newsletter</div><div class="section-sub">Conteúdo e engajamento</div></div></div>', unsafe_allow_html=True)

        bl_col, nw_col = st.columns(2)

        with bl_col:
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

            blog_visitas = get_blog_value(q, 'visitas')
            blog_usuarios = get_blog_value(q, 'usuarios')
            blog_posts = get_blog_value(q, 'blogposts')
            blog_tempo = get_blog_value(q, 'tempo_medio')

            prev_visitas = get_blog_value(prev_fy25_q, 'visitas') if prev_fy25_q else '—'
            prev_usuarios = get_blog_value(prev_fy25_q, 'usuarios') if prev_fy25_q else '—'
            prev_posts = get_blog_value(prev_fy25_q, 'blogposts') if prev_fy25_q else '—'
            prev_tempo = get_blog_value(prev_fy25_q, 'tempo_medio') if prev_fy25_q else '—'

            vis_fy24 = get_blog_fy24(q, 'visitas')
            usu_fy24 = get_blog_fy24(q, 'usuarios')
            pos_fy24 = get_blog_fy24(q, 'blogposts')
            tmp_fy24 = get_blog_fy24(q, 'tempo_medio')

            render_blog_item("Visitas", blog_visitas, prev_visitas, prev_fy25_name, vis_fy24, fy24_q_label if vis_fy24 else None, icon="👁️")
            render_blog_item("Usuários", blog_usuarios, prev_usuarios, prev_fy25_name, usu_fy24, fy24_q_label if usu_fy24 else None, icon="👥")
            render_blog_item("Blogposts Publicados", blog_posts, prev_posts, prev_fy25_name, pos_fy24, fy24_q_label if pos_fy24 else None, icon="📝")
            render_blog_item("Tempo Médio na Página", blog_tempo, prev_tempo, prev_fy25_name, tmp_fy24, fy24_q_label if tmp_fy24 else None, icon="⏱️")

        with nw_col:
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

            nw_empresas = get_newsletter_value(q, 'empresas')
            nw_envios = get_newsletter_value(q, 'envios')
            nw_abertura = get_newsletter_value(q, 'abertura')
            nw_cliques = get_newsletter_value(q, 'cliques')

            prev_empresas = get_newsletter_value(prev_fy25_q, 'empresas') if prev_fy25_q else '—'
            prev_envios = get_newsletter_value(prev_fy25_q, 'envios') if prev_fy25_q else '—'
            prev_abertura = get_newsletter_value(prev_fy25_q, 'abertura') if prev_fy25_q else '—'
            prev_cliques = get_newsletter_value(prev_fy25_q, 'cliques') if prev_fy25_q else '—'

            emp_fy24 = get_newsletter_fy24(q, 'empresas')
            env_fy24 = get_newsletter_fy24(q, 'envios')
            abe_nw_fy24 = get_newsletter_fy24(q, 'abertura')
            cli_nw_fy24 = get_newsletter_fy24(q, 'cliques')

            render_blog_item("Empresas", nw_empresas, prev_empresas, prev_fy25_name, emp_fy24, fy24_q_label if emp_fy24 else None, icon="🏢")
            render_blog_item("Envios", nw_envios, prev_envios, prev_fy25_name, env_fy24, fy24_q_label if env_fy24 else None, icon="📨")
            render_blog_item("Taxa de Abertura", nw_abertura, prev_abertura, prev_fy25_name, abe_nw_fy24, fy24_q_label if abe_nw_fy24 else None, is_percentage=True, icon="📊")
            render_blog_item("Taxa de Cliques", nw_cliques, prev_cliques, prev_fy25_name, cli_nw_fy24, fy24_q_label if cli_nw_fy24 else None, is_percentage=True, icon="🖱️")

        # Aprendizados
        st.markdown(f'<div class="section-premium"><div class="section-icon">📚</div><div><div class="section-title-premium">Aprendizados FY25</div><div class="section-sub">Principais lições do ano</div></div></div>', unsafe_allow_html=True)
        ap1, ap2, ap3 = st.columns(3)
        with ap1:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:18px;font-weight:700;color:#6FBF6F;margin-bottom:16px;">✅ QUE BOM</div>
                <div style="font-size:12px;line-height:1.6;color:{COLORS['text_muted']};">
                    • <strong>PowerUP</strong>: Plataforma de inscrição, estratégias online e metas diárias<br>
                    • <strong>Case Recrutamento Fortinet</strong>: 80 Leads — virou referência<br>
                    • <strong>Segmentação Microsoft</strong>: Timing nos e-mails aumentou quórum<br>
                    • <strong>Campanha BU Networking</strong>: Insights valiosos para futuras BUs
                </div>
            </div>
            """, unsafe_allow_html=True)
        with ap2:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:18px;font-weight:700;color:#FF8C5A;margin-bottom:16px;">⚠️ QUE PENA</div>
                <div style="font-size:12px;line-height:1.6;color:{COLORS['text_muted']};">
                    • <strong>Qualidade das bases</strong>: Necessidade de segmentar melhor os parceiros<br>
                    • <strong>Análise constante de resultados</strong>: Todos os jobs precisam ser acompanhados
                </div>
            </div>
            """, unsafe_allow_html=True)
        with ap3:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:18px;font-weight:700;color:#3399FF;margin-bottom:16px;">💡 QUE TAL — 2026</div>
                <div style="font-size:12px;line-height:1.6;color:{COLORS['text_muted']};">
                    • <strong>Intercâmbio de treinamentos</strong>: Calendário ao longo do ano<br>
                    • <strong>Alinhamentos estratégicos recorrentes</strong>: Incluir agência no planejamento<br>
                    • <strong>Metodologia EDGE</strong>: Otimização do formulário de briefing
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Download sidebar
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📥 Exportar Dados")
            dl_fmt = st.selectbox("Formato", ["CSV", "Excel"], key="dl_q")
            export_completo = st.checkbox("📋 Exportar todas as abas (completo)", value=True)
            
            if st.button(f"📥 Baixar {q}", key="btn_dl_q"):
                if export_completo:
                    all_data = export_quarter_data(q, quarterly_data)
                    
                    if dl_fmt == "CSV":
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for sheet_name, df in all_data.items():
                                csv_data = df.to_csv(index=False)
                                zip_file.writestr(f"{sheet_name}.csv", csv_data)
                        st.download_button(
                            "✅ Baixar Todos (ZIP)", 
                            zip_buffer.getvalue(), 
                            f"qbr_{q}_completo.zip", 
                            "application/zip"
                        )
                    else:
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                            for sheet_name, df in all_data.items():
                                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                        st.download_button(
                            "✅ Baixar Excel Completo", 
                            buf.getvalue(), 
                            f"qbr_{q}_completo.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    rows = [
                        {'Categoria':'Peças Produzidas','Valor':pecas_val},
                        {'Categoria':'Solicitações','Valor':solic_val},
                        {'Categoria':'Campanhas','Valor':camp_val},
                        {'Categoria':'Taxa Entrega E-mail','Valor':entrega_atual},
                        {'Categoria':'Taxa Abertura E-mail','Valor':abertura_atual},
                        {'Categoria':'Taxa Cliques E-mail','Valor':cliques_atual},
                        {'Categoria':'Novos Seguidores','Valor':seg_atual},
                        {'Categoria':'Total Engajamentos','Valor':eng_atual},
                        {'Categoria':'Total Cliques','Valor':cli_atual},
                    ]
                    df_dl = pd.DataFrame(rows)
                    
                    if dl_fmt == "CSV":
                        st.download_button("✅ Baixar CSV", df_dl.to_csv(index=False), f"qbr_{q}.csv", "text/csv")
                    else:
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine='openpyxl') as w: 
                            df_dl.to_excel(w, index=False, sheet_name=q)
                        st.download_button("✅ Baixar Excel", buf.getvalue(), f"qbr_{q}.xlsx")

    else:
        st.warning(f"View '{q}' não reconhecida. Selecionando Q1 como padrão.")
        st.session_state.view = 'Q1'
        st.rerun()

    # Footer
    st.markdown(f"""
    <div class="footer-premium">
        ⚡ QBR TD SYNNEX — Powered by Ideatore · Dados atualizados em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()