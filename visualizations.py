# visualizations.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import Optional

def generate_trend_chart(df: pd.DataFrame, time_period: str = 'D', selected_segment: Optional[str] = None) -> go.Figure:
    """
    Genera el gráfico de tendencia del IER con Range Slider integrado.
    """
    df_filtered = df.copy()
    
    # Asegurarse de que Timestamp sea datetime (por seguridad)
    if not pd.api.types.is_datetime64_any_dtype(df_filtered['Timestamp']):
        df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Timestamp'])

    # Intentar crear columna auxiliar Date al inicio
    if 'Date' not in df_filtered.columns:
        df_filtered['Date'] = df_filtered['Timestamp'].dt.date

    grouping_column = None

    if selected_segment and selected_segment != 'Ninguno':
        if 'CardBrand' in df_filtered.columns and selected_segment in df_filtered['CardBrand'].unique():
            df_filtered = df_filtered[df_filtered['CardBrand'] == selected_segment].copy()
            grouping_column = 'CardBrand'
        elif 'Category' in df_filtered.columns and selected_segment in df_filtered['Category'].unique():
             df_filtered = df_filtered[df_filtered['Category'] == selected_segment].copy()
             grouping_column = 'Category'

    if df_filtered.empty:
        fig = go.Figure().add_annotation(
            text="No hay datos para el filtro seleccionado.",
            xref="paper", yref="paper", showarrow=False, font={"size": 18})
        return fig
        
    time_col = 'Date' if time_period == 'D' else 'Timestamp'
    
    # --- CORRECCIÓN DEL ERROR ---
    # Si la columna de tiempo no existe, la creamos dinámicamente
    if time_col not in df_filtered.columns:
        if time_col == 'Timestamp':
             df_filtered['TimeGroup'] = df_filtered['Timestamp'].dt.to_period(time_period).dt.to_timestamp()
        else:
             # ERROR PREVIO: df_filtered['TimeGroup'] = df_filtered['Date']
             # CORRECCIÓN: Calcularla desde Timestamp si 'Date' no existe
             df_filtered['TimeGroup'] = df_filtered['Timestamp'].dt.date
    else:
         # Si ya existe, la usamos directamente
         df_filtered['TimeGroup'] = df_filtered[time_col]
        
    df_trend = df_filtered.groupby('TimeGroup').agg(
        Total_Volume=('TransactionAmount', 'sum'),
        Fraud_Count=('is_fraud', 'sum'),
        Total_Transactions=('TransactionAmount', 'count')
    ).reset_index()

    df_trend['Fraud_Rate'] = (df_trend['Fraud_Count'] / df_trend['Total_Transactions']) * 100
    df_trend['IER'] = df_trend['Fraud_Rate'] * np.log(df_trend['Total_Volume'].astype(float) + 1e-6)
    
    fig = px.line(df_trend, x='TimeGroup', y='IER', 
                  title=f"Tendencia del IER ({'Segmento: ' + selected_segment if selected_segment else 'Global'})",
                  labels={'TimeGroup': 'Tiempo', 'IER': 'IER (Índice)'})

    fig.update_traces(mode='lines+markers', line=dict(color='#007BFF'))

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis_title="IER"
    )

    return fig

def generate_segmentation_chart(df_metrics: pd.DataFrame, grouping_key: str) -> go.Figure:
    """
    Genera el gráfico de barras del IER segmentado.
    """
    if df_metrics.empty:
         fig = go.Figure().add_annotation(
            text="No hay datos disponibles.",
            xref="paper", yref="paper", showarrow=False, font={"size": 18})
         return fig

    max_ier = df_metrics['IER'].max()
    min_ier = df_metrics['IER'].min()
    
    # Prevenir división por cero si max == min
    denom = max_ier - min_ier
    if denom == 0: denom = 1.0
        
    df_metrics['Normalized_IER'] = (df_metrics['IER'] - min_ier) / (denom + 1e-6)

    fig = px.bar(df_metrics, x=grouping_key, y='IER', 
                 color='Normalized_IER',
                 color_continuous_scale='rdbu_r', 
                 color_continuous_midpoint=0.5,
                 title=f"Distribución del IER por {grouping_key}",
                 labels={'IER': 'Índice de Exposición al Riesgo', grouping_key: 'Segmento'})

    fig.update_xaxes(tickangle=45)
    fig.update_traces(marker_line_width=1.5, marker_line_color='black')
    
    return fig
