# metrics_calculator.py
import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional

@st.cache_data
def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calcula KPIs globales básicos: Volumen Total, Conteo de Transacciones, Tasa de Fraude."""
    total_volume = df['TransactionAmount'].sum()
    total_transactions = len(df)
    fraud_count = df['is_fraud'].sum() 
    
    # Tasa de Fraude (TF)
    fraud_rate = (fraud_count / total_transactions) * 100 if total_transactions > 0 else 0
    
    return {
        "Total_Volume": total_volume,
        "Total_Transactions": total_transactions,
        "Fraud_Count": fraud_count,
        "Fraud_Rate": fraud_rate
    }

def calculate_risk_exposure_index(df: pd.DataFrame, grouping_col: Optional[str] = None) -> pd.DataFrame:
    """
    Calcula el Índice de Exposición al Riesgo (IER) para un DataFrame.
    
    Args:
        df: DataFrame ORIGINAL de transacciones (NO un objeto GroupBy).
        grouping_col: Nombre de la columna por la cual agrupar (ej. 'CardBrand').
                      Si es None, calcula para el total.
    """
    # CORRECCIÓN: Ahora comprobamos .empty sobre un DataFrame real
    if df.empty:
        cols = [grouping_col, 'Total_Volume', 'Fraud_Count', 'Total_Transactions', 'Fraud_Rate', 'IER'] if grouping_col else ['Total_Volume', 'Fraud_Count', 'Total_Transactions', 'Fraud_Rate', 'IER']
        return pd.DataFrame(columns=cols)
        
    if grouping_col:
        # Realizamos el agrupamiento AQUÍ, sobre el DataFrame crudo
        df_metrics = df.groupby(grouping_col).agg(
            Total_Volume=('TransactionAmount', 'sum'),
            Fraud_Count=('is_fraud', 'sum'),
            Total_Transactions=('TransactionAmount', 'count')
        ).reset_index()
    else:
         # Cálculo global sin agrupación
        df_metrics = pd.DataFrame({
            'Total_Volume': [df['TransactionAmount'].sum()],
            'Fraud_Count': [df['is_fraud'].sum()],
            'Total_Transactions': [len(df)]
        })
        df_metrics['Segment'] = ['Total']

    # Calcular Tasa de Fraude
    df_metrics['Fraud_Rate'] = (df_metrics['Fraud_Count'] / df_metrics['Total_Transactions']) * 100

    # Calcular IER = Tasa_de_Fraude * log(Volumen)
    log_volume = np.log(df_metrics['Total_Volume'].astype(float) + 1e-6)
    df_metrics['IER'] = df_metrics['Fraud_Rate'] * log_volume
    
    # Ordenar por IER descendente
    df_metrics = df_metrics.sort_values(by='IER', ascending=False).reset_index(drop=True)
    
    return df_metrics

