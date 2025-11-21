import pandas as pd
import plotly.express as px
import numpy as np

def generate_trend_chart(df: pd.DataFrame, time_period: str, selected_segment: str = None, grouping_key: str = None):
    """
    Genera un gráfico de línea que muestra la tendencia del Índice de Exposición al Riesgo (IER) a lo largo del tiempo.
    Si se proporciona un segmento filtrado, compara la tendencia de ese segmento con la tendencia global.
    """
    
    # --- 1. Calcular IER Global ---
    df_global = df.copy()
    
    # Agrupar por el período de tiempo (Día) y calcular IER global
    df_global_trend = df_global.groupby(df_global['Timestamp'].dt.to_period(time_period).dt.to_timestamp()).apply(
        lambda x: (x['is_fraud'].sum() / len(x)) * 100 * np.log(x['TransactionAmount'].sum() + 1e-6)
    ).reset_index(name='IER')
    
    df_global_trend['Tipo_Tendencia'] = 'Global (Toda la Cartera)'

    df_plot = df_global_trend.copy()
    chart_title = "Tendencia Histórica del Índice de Exposición al Riesgo (IER) - Global"
    
    # --- 2. Calcular IER Filtrado (si aplica) ---
    if selected_segment and grouping_key:
        
        # Filtrar el DataFrame original por el segmento
        df_filtered = df[df[grouping_key] == selected_segment].copy()
        
        if not df_filtered.empty:
            # Agrupar por el período de tiempo (Día) y calcular IER filtrado
            df_segment_trend = df_filtered.groupby(df_filtered['Timestamp'].dt.to_period(time_period).dt.to_timestamp()).apply(
                lambda x: (x['is_fraud'].sum() / len(x)) * 100 * np.log(x['TransactionAmount'].sum() + 1e-6)
            ).reset_index(name='IER')
            
            df_segment_trend['Tipo_Tendencia'] = f'Segmento: {selected_segment}'
            
            # Combinar la tendencia global y la tendencia del segmento para el gráfico de contraste
            df_plot = pd.concat([df_global_trend, df_segment_trend])
            
            chart_title = f"Contraste de Tendencia IER: Segmento '{selected_segment}' vs. Global"

    # --- 3. Generar Gráfico Plotly ---
    
    # Determinar los colores para asegurar el contraste
    color_map = {
        'Global (Toda la Cartera)': 'lightgray',  # Color más tenue para el contexto
        f'Segmento: {selected_segment}': 'red'   # Color vibrante para el foco (si hay filtro)
    } if selected_segment else {'Global (Toda la Cartera)': 'blue'} # Solo azul si es global
    
    # El eje x es la marca de tiempo (Timestamp)
    fig = px.line(
        df_plot, 
        x='Timestamp', 
        y='IER', 
        color='Tipo_Tendencia',
        title=chart_title,
        color_discrete_map=color_map,
        markers=True,
        labels={'IER': 'IER', 'Timestamp': 'Fecha'}
    )

    fig.update_layout(
        xaxis_title="Fecha", 
        yaxis_title="Índice de Exposición al Riesgo (IER)",
        legend_title="Tendencia",
        hovermode="x unified"
    )
    
    # Mejorar la apariencia de la línea del segmento si aplica
    if selected_segment:
        # Asegurarse de que la línea filtrada sea más gruesa para destacar
        fig.update_traces(
            line=dict(width=4), 
            selector=dict(name=f'Segmento: {selected_segment}')
        )
        # Asegurarse de que la línea global sea más delgada
        fig.update_traces(
            line=dict(width=2), 
            selector=dict(name='Global (Toda la Cartera)')
        )


    return fig

def generate_top_n_risk_segments(df_segmentation: pd.DataFrame, grouping_key: str, n: int = 5):
    """
    Genera un gráfico de barras simple para mostrar los Top N segmentos de riesgo por IER.
    Usado en la vista ejecutiva.
    """
    if df_segmentation.empty:
        return px.bar(title="No hay datos de segmentación para mostrar.")

    df_top_n = df_segmentation.head(n).sort_values(by='IER', ascending=True) # Ordenar ascendente para gráfico de barras horizontal

    fig = px.bar(
        df_top_n,
        y=grouping_key, # Eje Y para barras horizontales
        x='IER',
        orientation='h',
        color='IER',
        color_continuous_scale='Reds', # Escala de color simple basada en IER
        title=f"Top {n} Segmentos de Mayor Exposición al Riesgo (IER)",
        labels={'IER': 'Índice de Exposición al Riesgo (IER)', grouping_key: 'Segmento'},
        hover_data={'Fraud_Rate': ':.2f%', 'Total_Volume': '$,.0f'}
    )

    fig.update_layout(
        yaxis_title="", # No necesitamos título en el eje Y ya que son los nombres de los segmentos
        xaxis_title="Índice de Exposición al Riesgo (IER)",
        coloraxis_showscale=False, # Ocultar la barra de color
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Añadir el valor de IER en las barras
    fig.update_traces(texttemplate='%{x:.2f}', textposition='outside', marker_color='red')

    return fig

def generate_segmentation_chart(df_segmentation: pd.DataFrame, grouping_key: str):
    """
    Genera un gráfico de barras interactivo para la segmentación del riesgo (Pestaña 2).
    """
    if df_segmentation.empty:
        return px.bar(title="No hay datos de segmentación para mostrar.")

    # Normalizar IER para usar el color
    max_ier = df_segmentation['IER'].max()
    min_ier = df_segmentation['IER'].min()
    
    # Prevenir división por cero si max == min
    denom = max_ier - min_ier
    if denom == 0: denom = 1.0
        
    df_segmentation['Normalized_IER'] = (df_segmentation['IER'] - min_ier) / (denom + 1e-6)

    fig = px.bar(df_segmentation, x=grouping_key, y='IER', 
                 color='Normalized_IER',
                 color_continuous_scale='rdbu_r', # Rojo para alto riesgo (Normalized_IER alto)
                 color_continuous_midpoint=0.5,
                 title=f"Distribución del IER por {grouping_key} (Clic para Filtrar)",
                 labels={'IER': 'Índice de Exposición al Riesgo', grouping_key: 'Segmento'},
                 hover_data={'Fraud_Rate': ':.2f%', 'Total_Volume': '$,.0f'}
                 )

    fig.update_xaxes(tickangle=45)
    fig.update_traces(marker_line_width=1.0, marker_line_color='black')
    fig.update_layout(coloraxis_colorbar=dict(title="Nivel de Riesgo"))
    
    return fig

def generate_fraud_distribution_chart(df: pd.DataFrame, group_by_col: str = None):
    """
    Genera un gráfico de pastel o distribución.
    Si group_by_col está definido, muestra la distribución del VOLUMEN DE FRAUDE por ese segmento.
    De lo contrario, muestra la distribución de Fraude vs. Legítima (el 99% vs 1% original).
    """
    if group_by_col and group_by_col in df.columns:
        # Modo: Distribución del VOLUMEN DE FRAUDE por SEGMENTO (Nueva y más útil)
        
        # 1. Filtrar solo transacciones fraudulentas
        df_fraud = df[df['is_fraud'] == 1].copy()
        
        if df_fraud.empty:
            return px.pie(title="No hay transacciones fraudulentas para mostrar el desglose.")

        # 2. Agrupar por la columna del segmento y sumar el volumen
        fraud_volume_by_segment = df_fraud.groupby(group_by_col)['TransactionAmount'].sum().reset_index(name='Total_Fraud_Volume')
        
        # 3. Crear el gráfico de pastel
        fig = px.pie(
            fraud_volume_by_segment, 
            values='Total_Fraud_Volume', 
            names=group_by_col, 
            title=f'Distribución del Volumen de Fraude por Segmento: {group_by_col}',
            hole=.3
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent', 
            marker=dict(line=dict(color='#000000', width=1)),
            hovertemplate="<b>%{label}</b><br>Volumen Fraude: %{value:$,.0f}<br>Proporción: %{percent}<extra></extra>"
        )
        fig.update_layout(margin=dict(t=50, b=10, l=10, r=10), showlegend=True, legend_title=group_by_col)
        
        return fig
        
    else:
        # Modo: Distribución de Fraude vs. Legítima (Original, como fallback)
        fraud_counts = df['is_fraud'].value_counts().reset_index()
        fraud_counts.columns = ['is_fraud', 'Count']
        fraud_counts['Label'] = fraud_counts['is_fraud'].apply(lambda x: 'Fraude (1)' if x == 1 else 'Legítima (0)')

        fig = px.pie(
            fraud_counts, 
            values='Count', 
            names='Label', 
            title='Distribución de Transacciones (Fraude vs. Legítima)',
            color='Label',
            color_discrete_map={'Fraude (1)': 'red', 'Legítima (0)': 'lightgray'},
            hole=.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=50, b=10, l=10, r=10), showlegend=False)

        return fig
