import pandas as pd

def format_number(value):
    """Formata números de forma consistente"""
    if value is None or value == '—':
        return '—'
    try:
        # Converte string para float
        if isinstance(value, str):
            value = value.replace('%', '').replace('.', '').replace(',', '.')
        num = float(value)
        
        if num > 1000:
            return f"{int(num):,}".replace(',', '.')
        return f"{int(num)}" if num == int(num) else f"{num:.1f}".replace('.', ',')
    except (ValueError, TypeError):
        return str(value)

def calc_variation(current, previous):
    """Calcula variação percentual entre dois valores"""
    if current is None or previous is None or current == '—' or previous == '—':
        return None
    try:
        # Limpa os valores
        if isinstance(current, str):
            current = current.replace('%', '').replace('.', '').replace(',', '.')
        if isinstance(previous, str):
            previous = previous.replace('%', '').replace('.', '').replace(',', '.')
        
        curr = float(current)
        prev = float(previous)
        
        if prev == 0:
            return None
        return ((curr - prev) / prev) * 100
    except (ValueError, TypeError):
        return None

def clean_value(value):
    """Limpa valores para exibição"""
    if value is None:
        return '—'
    if isinstance(value, float) and pd.isna(value):
        return '—'
    
    val_str = str(value).strip()
    if val_str in ['', 'nan', 'NaN', 'None', '—', '--', 'null']:
        return '—'
    return val_str

def format_percentage(value, decimals=1):
    """Formata valor como porcentagem"""
    if value is None or value == '—':
        return '—'
    try:
        num = float(value)
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)