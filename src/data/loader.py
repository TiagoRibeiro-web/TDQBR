import json
import pandas as pd
from pathlib import Path
from typing import Any, Dict, Optional

class DataLoader:
    """Carregador centralizado de dados"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / 'data'
        self.fy25_data = self._load_json('fy25_data.json')
        self.fy26_data = self._load_json('fy26_data.json')
        self.fy25_fallback = self._get_fy25_fallback()
        self.fy26_fallback = self._get_fy26_fallback()
    
    def _load_json(self, filename: str) -> Dict:
        """Carrega um arquivo JSON"""
        filepath = self.data_path / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _get_fy25_fallback(self) -> Dict:
        """Retorna dados de fallback do FY25"""
        return {
            'pecas': {'Q1': 518, 'Q2': 692, 'Q3': 674, 'Q4': 647},
            'solicitacoes': {'Q1': 108, 'Q2': 159, 'Q3': 100, 'Q4': 131},
            'campanhas': {'Q1': 4, 'Q2': 9, 'Q3': 7, 'Q4': 6},
            'email': {
                'Q1': {'entrega': 95.7, 'abertura': 35.8, 'cliques': 1.7, 'optout': 0.04},
                'Q2': {'entrega': 98.4, 'abertura': 45.3, 'cliques': 2.6, 'optout': 0.07},
                'Q3': {'entrega': 96.0, 'abertura': 38.0, 'cliques': 6.0, 'optout': 0.05},
                'Q4': {'entrega': 93.0, 'abertura': 24.0, 'cliques': 2.2, 'optout': 0.02},
            },
            'email_envios': {'Q1': 169948, 'Q2': 122639, 'Q3': 134035, 'Q4': 349487},
            'redes': {
                'Q1': {'seguidores': 1230, 'engajamentos': 81419, 'cliques': 6117},
                'Q2': {'seguidores': 1688, 'engajamentos': 10237, 'cliques': 8585},
                'Q3': {'seguidores': 1927, 'engajamentos': 76102, 'cliques': 36375},
                'Q4': {'seguidores': 2296, 'engajamentos': 58046, 'cliques': 51119},
            },
            'blog': {
                'Q1': {'visitas': 24926, 'usuarios': 17075, 'blogposts': 31, 'tempo_medio': '5:00'},
                'Q2': {'visitas': 16137, 'usuarios': 11295, 'blogposts': 25, 'tempo_medio': '4:04'},
                'Q3': {'visitas': 13353, 'usuarios': 7037, 'blogposts': 26, 'tempo_medio': '2:35'},
                'Q4': {'visitas': 18910, 'usuarios': 12348, 'blogposts': 27, 'tempo_medio': '4:36'},
            },
            'newsletter': {
                'Q1': {'empresas': 416, 'envios': 544, 'abertura': 34.19, 'cliques': 2.8},
                'Q2': {'empresas': 427, 'envios': 750, 'abertura': 35.2, 'cliques': 2.8},
                'Q3': {'empresas': 428, 'envios': 1059, 'abertura': 33.1, 'cliques': 1.5},
                'Q4': {'empresas': 488, 'envios': 426, 'abertura': 32.0, 'cliques': 1.8},
            },
            'vertical_distribution': {
                'Q1': [('Segurança', 27.0), ('Networking', 13.0), ('Cloud', 13.0), 
                       ('Data & AI', 10.0), ('Data Center', 9.0), ('Institucional', 15.0)],
                'Q2': [('Cloud', 27.0), ('Segurança', 22.0), ('Networking', 19.0), 
                       ('Data & AI', 14.0), ('Data Center', 10.0), ('Institucional', 8.0)],
                'Q3': [('Segurança', 31.0), ('Cloud', 19.0), ('Networking', 16.0), 
                       ('Institucional', 15.0), ('Data & AI', 14.0), ('Data Center', 6.0)],
                'Q4': [('Segurança', 40.0), ('Cloud', 21.0), ('Institucional', 14.0), 
                       ('Networking', 9.0), ('Data Center', 8.0), ('Data & AI', 7.0)],
            },
            'fabricantes': {
                'Q1': [
                    {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 120 peças', 
                     'menor_solicitante': 'Palo Alto — 1 peça', 'top_3_pecas': '9520 - Fortinet'},
                    # ... mais dados
                ],
                # ... mais trimestres
            },
            'campanhas_detalhes': {
                'Q1': {'solicitadas': 6, 'veiculadas': 4, 'taxa_conversao': 7.26, 
                       'leads': 62, 'top': '🏆 Fortinet Roadshow (56 empresas)'},
                'Q2': {'solicitadas': 9, 'veiculadas': 6, 'taxa_conversao': 6.5, 
                       'leads': 205, 'top': '🏆 IBM IA (55 empresas)'},
                'Q3': {'solicitadas': 7, 'veiculadas': 6, 'taxa_conversao': 0.54, 
                       'leads': 439, 'top': '🏆 Cloud On the Go (383 empresas)'},
                'Q4': {'solicitadas': 6, 'veiculadas': 3, 'taxa_conversao': 0.04, 
                       'leads': 70, 'top': '🏆 Campanha Recrutamento Fortinet'},
            }
        }
    
    def _get_fy26_fallback(self) -> Dict:
        """Retorna dados de fallback do FY26"""
        return {
            'Q1': {
                'pecas': 411,
                'solicitacoes': 125,
                'campanhas': 4,
                'email': {'entrega': 97, 'abertura': 31, 'cliques': 1.8, 'optout': 0.01},
                'email_envios': None,
                'redes': {'seguidores': 1123, 'engajamentos': 9804, 'cliques': 24552},
                'blog': {'visitas': 22980, 'usuarios': 12077, 'blogposts': 25, 'tempo_medio': '4.2'},
                'newsletter': {'empresas': 522, 'envios': 1065, 'abertura': 33, 'cliques': 3.4},
                'vertical_distribution': [
                    ('Cloud', 28), ('Segurança', 26), ('Data Center', 14),
                    ('Networking', 12), ('Institucional', 11), ('Data & AI', 8)
                ],
                'fabricantes': [
                    {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 42 peças',
                     'menor_solicitante': 'Netscout — 1 peça', 'top_3_pecas': 'EMKT (47)'},
                    # ... mais dados
                ],
                'campanhas_detalhes': {
                    'solicitadas': 4, 'veiculadas': 3, 'taxa_conversao_com_investimento': 0.01,
                    'taxa_conversao_sem_investimento': 0, 'leads': 26,
                    'top': '🏆 Campanha VCF VMware (26 empresas)',
                    'objetivo_conversao': 100, 'objetivo_branding': 0
                }
            },
            'Q2': {
                'pecas': 643,
                'solicitacoes': 133,
                'campanhas': 12,
                'email': {'entrega': 94, 'abertura': 32, 'cliques': 2, 'optout': 0.01},
                'email_envios': 171817,
                'redes': {'seguidores': 1776, 'engajamentos': 11332, 'cliques': 27292},
                'blog': {'visitas': 30040, 'usuarios': 22150, 'blogposts': 31, 'tempo_medio': '4.7'},
                'newsletter': {'empresas': 536, 'envios': 1620, 'abertura': 34, 'cliques': 2.9},
                'vertical_distribution': [
                    ('Segurança', 28), ('Institucional', 24), ('Cloud', 23),
                    ('Data Center', 12), ('Networking', 11), ('Data & AI', 3)
                ],
                'fabricantes': [
                    {'vertical': 'Segurança', 'maior_solicitante': 'Fortinet — 113 peças',
                     'menor_solicitante': 'Splunk / Tenable / Zscaler — 1 peça',
                     'top_3_pecas': 'EMKT (57), POST RS (33), Peça Avulsa (29)'},
                    # ... mais dados
                ],
                'campanhas_detalhes': {
                    'solicitadas': 12, 'veiculadas': 7, 'taxa_conversao_com_investimento': 0.29,
                    'taxa_conversao_sem_investimento': 0, 'leads': 17,
                    'top': '🏆 Campanha de Recrutamento Fortinet<br>🏆 Campanha NVidia',
                    'objetivo_conversao': 70, 'objetivo_branding': 30
                }
            }
        }
    
    def get_quarter_data(self, quarter: str) -> Dict:
        """Retorna dados de um trimestre específico"""
        # FY25
        if quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            return {
                'pecas': self.fy25_data.get('pecas', {}).get(quarter, 
                         self.fy25_fallback['pecas'].get(quarter, 0)),
                'solicitacoes': self.fy25_data.get('solicitacoes', {}).get(quarter,
                              self.fy25_fallback['solicitacoes'].get(quarter, 0)),
                'campanhas': self.fy25_data.get('campanhas', {}).get(quarter,
                            self.fy25_fallback['campanhas'].get(quarter, 0)),
                'email': self.fy25_data.get('email', {}).get(quarter,
                        self.fy25_fallback['email'].get(quarter, {})),
                'email_envios': self.fy25_data.get('email_envios', {}).get(quarter,
                             self.fy25_fallback['email_envios'].get(quarter, None)),
                'redes': self.fy25_data.get('redes', {}).get(quarter,
                        self.fy25_fallback['redes'].get(quarter, {})),
                'blog': self.fy25_data.get('blog', {}).get(quarter,
                       self.fy25_fallback['blog'].get(quarter, {})),
                'newsletter': self.fy25_data.get('newsletter', {}).get(quarter,
                            self.fy25_fallback['newsletter'].get(quarter, {})),
                'vertical_distribution': self.fy25_data.get('vertical_distribution', {}).get(quarter,
                                        self.fy25_fallback['vertical_distribution'].get(quarter, [])),
                'fabricantes': self.fy25_data.get('fabricantes', {}).get(quarter,
                              self.fy25_fallback['fabricantes'].get(quarter, [])),
                'campanhas_detalhes': self.fy25_data.get('campanhas_detalhes', {}).get(quarter,
                                     self.fy25_fallback['campanhas_detalhes'].get(quarter, {}))
            }
        
        # FY26
        elif quarter in ['Q1FY26', 'Q2FY26']:
            q = quarter.replace('FY26', '')
            return self.fy26_data.get(q, self.fy26_fallback.get(q, {}))
        
        return {}
    
    def get_quarterly_summary(self) -> Dict:
        """Retorna resumo de todos os trimestres para KPIs"""
        quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'Q1FY26', 'Q2FY26']
        summary = {}
        for q in quarters:
            data = self.get_quarter_data(q)
            summary[q] = {
                'pecas': data.get('pecas', 0),
                'solic': data.get('solicitacoes', 0),
                'camp': data.get('campanhas', 0)
            }
        return summary
    
    def get_vertical_distribution(self, quarter: str) -> pd.DataFrame:
        """Retorna distribuição vertical como DataFrame"""
        data = self.get_quarter_data(quarter)
        vertical_data = data.get('vertical_distribution', [])
        if vertical_data:
            return pd.DataFrame(vertical_data, columns=['vertical', 'percentual'])
        return pd.DataFrame()
    
    def get_fabricantes(self, quarter: str) -> pd.DataFrame:
        """Retorna dados de fabricantes como DataFrame"""
        data = self.get_quarter_data(quarter)
        fabricantes = data.get('fabricantes', [])
        if fabricantes:
            return pd.DataFrame(fabricantes)
        return pd.DataFrame()