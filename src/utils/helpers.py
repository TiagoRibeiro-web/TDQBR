def get_quarter_info(quarter):
    """Retorna informações sobre um trimestre"""
    quarter_info = {
        'Q1': {'name': 'Q1 FY25', 'fy': 'FY25', 'quarter': 'Q1'},
        'Q2': {'name': 'Q2 FY25', 'fy': 'FY25', 'quarter': 'Q2'},
        'Q3': {'name': 'Q3 FY25', 'fy': 'FY25', 'quarter': 'Q3'},
        'Q4': {'name': 'Q4 FY25', 'fy': 'FY25', 'quarter': 'Q4'},
        'Q1FY26': {'name': 'Q1 FY26', 'fy': 'FY26', 'quarter': 'Q1'},
        'Q2FY26': {'name': 'Q2 FY26', 'fy': 'FY26', 'quarter': 'Q2'},
    }
    return quarter_info.get(quarter, {'name': quarter, 'fy': 'FY26', 'quarter': quarter})

def get_previous_quarter(quarter):
    """Retorna o trimestre anterior"""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'Q1FY26', 'Q2FY26']
    try:
        idx = quarters.index(quarter)
        return quarters[idx - 1] if idx > 0 else None
    except ValueError:
        return None

def get_next_quarter(quarter):
    """Retorna o próximo trimestre"""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'Q1FY26', 'Q2FY26']
    try:
        idx = quarters.index(quarter)
        return quarters[idx + 1] if idx < len(quarters) - 1 else None
    except ValueError:
        return None

def is_fy25(quarter):
    """Verifica se o trimestre é do FY25"""
    return quarter in ['Q1', 'Q2', 'Q3', 'Q4']

def is_fy26(quarter):
    """Verifica se o trimestre é do FY26"""
    return quarter in ['Q1FY26', 'Q2FY26']