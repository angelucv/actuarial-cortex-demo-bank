# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from data_loader import load_data
from metrics_calculator import calculate_kpis
# Importación corregida de las clases de estrategia
from visualizations import generate_trend_chart, generate_segmentation_chart, generate_fraud_distribution_chart, generate_top_n_risk_segments 
from risk_strategies import RiskSegmenter, STRATEGY_MAP, CardBrandStrategy 

# --- Configuración Inicial ---
st.set_page_config(
    page_title="Demo de Actuarial Cortex — Detección de Fraude",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Session State para el filtro interactivo
if 'segment_filter' not in st.session_state:
    st.session_state['segment_filter'] = None
if 'grouping_key' not in st.session_state:
    st.session_state['grouping_key'] = None

# Función Callback para gestionar la interacción de clic
def handle_click(segment_value, grouping_key_value):
    """Procesa el valor del segmento clicado en el gráfico de barras y actualiza el filtro."""
    if segment_value and st.session_state['segment_filter'] != segment_value:
        st.session_state['segment_filter'] = segment_value
        st.session_state['grouping_key'] = grouping_key_value
        st.toast(f"Filtro aplicado: {grouping_key_value} = {segment_value}")
    elif st.session_state['segment_filter'] == segment_value:
        # Si se hace clic en el mismo, limpiamos
        st.session_state['segment_filter'] = None
        st.session_state['grouping_key'] = None
        st.toast("Filtro removido.")
    else:
        st.session_state['segment_filter'] = None
        st.session_state['grouping_key'] = None
        st.toast("Filtro removido.")

# --- Carga de Datos ---
df = load_data()
kpis = calculate_kpis(df)

# URLs de logos Actuarial Cortex (sitio oficial)
LOGO_SIDEBAR = "https://actuarial-cortex.pages.dev/logo-AC/logo-AC-AC-vertical-blanco.png"
LOGO_INICIO = "https://actuarial-cortex.pages.dev/logo-AC/logo-actuarial-cortex-principal-blanco.png"

# --- Branding Actuarial Cortex (sidebar: logo vertical) ---
try:
    st.sidebar.image(LOGO_SIDEBAR, width=180, caption="Actuarial Cortex")
except Exception:
    st.sidebar.markdown("**Actuarial Cortex**")
st.sidebar.caption("Aplicativo para bancos · Detección de fraude")
st.sidebar.markdown("[Ir a Actuarial Cortex](https://actuarial-cortex.pages.dev/)" + "  ")

# --- Inicio: logo principal y descripción ---
try:
    st.image(LOGO_INICIO, width=280)
except Exception:
    st.markdown("**Actuarial Cortex**")
st.markdown("""
**[Actuarial Cortex](https://actuarial-cortex.pages.dev/)** es un hub de conocimiento y tecnología actuarial. Este **demo de detección de fraude**
forma parte de su oferta para el sector bancario: permite explorar la **exposición al riesgo (IER)** y la
**tasa de fraude** por segmentos (marca de tarjeta, categoría de comercio), con métricas ejecutivas y
análisis estratégico para apoyar la toma de decisiones.
""")
st.divider()

# --- Títulos y Navegación Lateral ---
st.title("🛡️ Actuarial Cortex — Banca · Detección de Fraude")
st.caption("Resumen ejecutivo y análisis estratégico de riesgo por segmentación.")

st.sidebar.header("Opciones de Análisis")

# Selector de Estrategia (Strategy Pattern)
strategy_name = st.sidebar.radio(
    "Seleccione la Perspectiva de Análisis:",
    list(STRATEGY_MAP.keys()),
    index=0,
    help="Define la lógica de agrupación de riesgo (Marca de Tarjeta o Categoría de Comercio)."
)
st.sidebar.divider()

# Limpiador de filtro en el sidebar
filtered_segment = st.session_state['segment_filter']
current_grouping_key = st.session_state['grouping_key']

if filtered_segment:
    st.sidebar.markdown(f"**Filtro Activo:** `{current_grouping_key} = {filtered_segment}`")
    if st.sidebar.button("Limpiar Filtro Activo"):
        st.session_state['segment_filter'] = None
        st.session_state['grouping_key'] = None
        st.rerun()
else:
    st.sidebar.markdown("**Filtro Activo:** Ninguno")

# --- Pie del menú lateral (unificado Actuarial Cortex) ---
st.sidebar.markdown("---")
st.sidebar.caption("**Elaborado por el Prof. Angel Colmenares**")
st.sidebar.caption("© Actuarial Cortex")
st.sidebar.caption("Conocimiento · Tecnología · Formación")
st.sidebar.caption("actuarial.cortex@gmail.com | @actuarial_cortex")

# --- Pestañas Principales ---
tab1, tab2 = st.tabs(["Resumen Ejecutivo (Junta Directiva)", "Análisis Estratégico de Riesgo (Analistas)"]) 

# =========================================================================
# PESTAÑA 1: RESUMEN EJECUTIVO
# =========================================================================
with tab1:
    
    # -------------------------------------------------------------
    # INTRODUCCIÓN Y TEXTO EXPLICATIVO
    # -------------------------------------------------------------
    st.markdown("### Visión de Alto Nivel y Exposición Global")
    st.info("""
        Este resumen ejecutivo presenta la situación actual de la cartera (Actuarial Cortex — Banca), enfocándose en la **Exposición al Riesgo (IER)** y la **Tasa de Fraude (TF) Global**. 
        El IER es una métrica compuesta que integra la frecuencia y el impacto monetario del fraude, proporcionando un indicador consolidado para la Junta Directiva.
        Utilice los segmentos de riesgo principales para entender dónde concentrar los esfuerzos de mitigación.
    """)
    
    # -------------------------------------------------------------
    # SECCIÓN GLOBAL (Métricas de la Cartera Total)
    # -------------------------------------------------------------
    
    # 1. KPIs principales de negocio (Global)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Volumen Total", f"${kpis['Total_Volume']:,.0f}")
    with col2:
        st.metric("Total Fraude (Monto)", f"${df[df['is_fraud']==1]['TransactionAmount'].sum():,.0f}")
    with col3:
        st.metric("Total Transacciones", f"{kpis['Total_Transactions']:,}")
    with col4:
        st.metric("Tasa de Fraude (TF) Global", f"{kpis['Fraud_Rate']:.2f}%")

    st.divider()
    
    # Calcular IER diario global (necesario para la comparación)
    df_ier_daily_global = df.groupby(df['Timestamp'].dt.date).apply(
        lambda x: (x['is_fraud'].sum() / len(x)) * 100 * np.log(x['TransactionAmount'].sum() + 1e-6)
    )
    ier_global_avg = df_ier_daily_global.mean() if not df_ier_daily_global.empty else 0.0

    # -------------------------------------------------------------
    # SECCIÓN VISUALIZACIONES EJECUTIVAS (GRÁFICO TOP N DINÁMICO + DISTRIBUCIÓN DE VOLUMEN DE FRAUDE)
    # -------------------------------------------------------------
    col_top_risk, col_distribution = st.columns([2, 1])

    # 1. GRÁFICO: TOP 5 SEGMENTOS DE RIESGO (AHORA DINÁMICO)
    with col_top_risk:
        # Lógica para usar la estrategia seleccionada por el usuario en el sidebar
        selected_strategy_exec = STRATEGY_MAP[strategy_name]
        risk_context_exec = RiskSegmenter(selected_strategy_exec)
        df_segmentation_exec = risk_context_exec.execute_analysis(df)
        grouping_key_exec = risk_context_exec.get_grouping_key()
        
        st.markdown("#### Top 5 Segmentos de Mayor Exposición al Riesgo (IER)")
        st.caption(f"Los segmentos de riesgo más altos por IER, usando la agrupación actual por **{grouping_key_exec}**.")
        
        # Generar el gráfico de Top 5
        fig_top_n_risk = generate_top_n_risk_segments(df_segmentation_exec, grouping_key_exec, n=5)
        st.plotly_chart(fig_top_n_risk, use_container_width=True, key="top_n_risk_chart")

    # 2. GRÁFICO DE DISTRIBUCIÓN (Muestra la distribución del VOLUMEN DE FRAUDE por segmento)
    with col_distribution:
        st.markdown(f"#### Distribución del Volumen de Fraude ($) por Segmento")
        st.caption(f"Detalle del volumen de fraude por la agrupación **{grouping_key_exec}**.")
        
        # Gráfico de Pastel mejorado (muestra distribución de FRAUDE por el segmento activo)
        fig_distribution_global = generate_fraud_distribution_chart(df, group_by_col=grouping_key_exec)
        st.plotly_chart(fig_distribution_global, use_container_width=True, key="fraud_distribution_chart_global_exec")

    # -------------------------------------------------------------
    # SECCIÓN FILTRADA (Si hay filtro activo, solo se muestran las métricas de comparación)
    # -------------------------------------------------------------
    if filtered_segment and current_grouping_key:
        
        df_filtered = df[df[current_grouping_key] == filtered_segment].copy()
        
        if not df_filtered.empty:
            
            # Recalcular KPIs específicos para la vista filtrada
            kpis_filtered = calculate_kpis(df_filtered)
            
            # Recalcular IER diario y métricas de riesgo para el filtro
            if kpis_filtered['Total_Transactions'] > 0:
                df_ier_daily_filtered = df_filtered.groupby(df_filtered['Timestamp'].dt.date).apply(
                    lambda x: (x['is_fraud'].sum() / len(x)) * 100 * np.log(x['TransactionAmount'].sum() + 1e-6)
                )
                ier_segment_avg = df_ier_daily_filtered.mean() if not df_ier_daily_filtered.empty else 0.0
                
                if not df_ier_daily_filtered.empty and df_ier_daily_filtered.max() > 0:
                    top_risk_day_filtered = df_ier_daily_filtered.idxmax().strftime('%Y-%m-%d')
                    top_risk_ier_filtered = df_ier_daily_filtered.max()
                else:
                    top_risk_day_filtered = "N/A"
                    top_risk_ier_filtered = 0.0
            else:
                ier_segment_avg = 0.0
                top_risk_day_filtered, top_risk_ier_filtered = "N/A", 0

            # --- Visualización de la Sección Filtrada ---
            st.divider()
            st.markdown(f"## 🎯 En Foco: Segmento `{filtered_segment}`")
            st.caption(f"Análisis detallado de la exposición al riesgo para el segmento **{current_grouping_key}** = **{filtered_segment}**.")
            
            # Fila 1: Indicador de Contraste y Métricas de Segmento
            col_contrast, col_kpi_1, col_kpi_2, col_kpi_3 = st.columns([1.5, 1, 1, 1])
            
            # GRÁFICO DE CONTRASTE (Barras)
            with col_contrast:
                st.markdown("#### Comparativa de Riesgo (IER Promedio)")
                
                contrast_data = pd.DataFrame({
                    'Segmento': [f'En Foco: {filtered_segment}', 'Global (Promedio)'],
                    'IER Promedio': [ier_segment_avg, ier_global_avg]
                })

                fig_contrast = px.bar(
                    contrast_data, 
                    x='Segmento', 
                    y='IER Promedio', 
                    title=f"IER Promedio: Segmento vs. Global",
                    color='Segmento',
                    color_discrete_map={
                        f'En Foco: {filtered_segment}': 'tomato' if ier_segment_avg > ier_global_avg else 'skyblue',
                        'Global (Promedio)': 'lightgray'
                    },
                    height=200
                )
                fig_contrast.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10))
                st.plotly_chart(fig_contrast, use_container_width=True, key="ier_contrast_chart")
            
            # Métricas Clave del Segmento
            with col_kpi_1:
                tf_global = kpis.get('Fraud_Rate', 0)
                tf_segment = kpis_filtered.get('Fraud_Rate', 0)
                tf_delta = tf_segment - tf_global
                
                st.metric(
                    "Tasa de Fraude (TF)", 
                    f"{tf_segment:.2f}%", 
                    delta=f"{tf_delta:.2f} p.p." if pd.notna(tf_delta) else None,
                    help="Tasa de Fraude de este segmento comparada con la tasa global."
                )

            with col_kpi_2:
                st.metric("Volumen Fraude ($)", f"${df_filtered[df_filtered['is_fraud']==1]['TransactionAmount'].sum():,.0f}", help="Monto total perdido por fraude en este segmento.")
            
            with col_kpi_3:
                 st.metric("Día Pico de Riesgo", f"{top_risk_day_filtered}", help=f"Fecha de mayor IER en este segmento: {top_risk_ier_filtered:.2f}")

            st.markdown("---")

            # Gráfico de Distribución Filtrado (sigue usando la lógica mejorada)
            st.markdown("#### Distribución del Volumen de Fraude ($) (Segmento Filtrado)")
            fig_distribution_filtered = generate_fraud_distribution_chart(df_filtered, group_by_col=current_grouping_key)
            st.plotly_chart(fig_distribution_filtered, use_container_width=True, key="fraud_distribution_chart_filtered")
        
        else:
            # Caso: El filtro está activo pero el DF filtrado está vacío
            st.divider()
            st.warning(f"No hay transacciones registradas para el filtro activo: **{current_grouping_key} = {filtered_segment}**.")
            
    # La Pestaña 1 se mantiene simple si NO hay filtro activo (solo KPIs + Top 5 + Torta)

# =========================================================================
# PESTAÑA 2: ANÁLISIS ESTRATÉGICO DE RIESGO
# =========================================================================
with tab2:
    st.markdown(f"### Desglose del Riesgo por Segmentación de Negocio")
    st.info(f"Aquí se analiza la exposición al riesgo (IER) utilizando la estrategia seleccionada en el menú lateral: **{strategy_name}**. Haga clic en cualquier barra del gráfico para aplicar el filtro de segmento.")
    
    # Lógica de Análisis (se ejecuta siempre que Strategy Name sea válido)
    if strategy_name:
        selected_strategy = STRATEGY_MAP[strategy_name]
        risk_context = RiskSegmenter(selected_strategy)
        
        # Ejecutar análisis
        df_segmentation = risk_context.execute_analysis(df)
        grouping_key = risk_context.get_grouping_key()
        
        st.markdown(f"#### Distribución del IER para `{grouping_key}`")

        # Validación de max_ier_val para la barra de progreso
        if not df_segmentation.empty:
            max_val_calc = df_segmentation['IER'].max()
            max_ier_val = float(max_val_calc) if pd.notna(max_val_calc) and max_val_calc > 0 else 1.0
        else:
            max_ier_val = 1.0

        # Tabla (Top 10 segmentos de riesgo)
        st.dataframe(
            df_segmentation.head(10), 
            column_order=(grouping_key, 'IER', 'Fraud_Rate', 'Total_Volume'),
            hide_index=True, 
            use_container_width=True,
            column_config={
                grouping_key: st.column_config.TextColumn("Segmento de Riesgo"),
                'IER': st.column_config.ProgressColumn(
                    "Índice de Exposición (IER)", 
                    format="%.2f", 
                    min_value=0, 
                    max_value=max_ier_val
                ),
                'Fraud_Rate': st.column_config.NumberColumn("TF (%)", format="%.2f%%"),
                'Total_Volume': st.column_config.NumberColumn("Volumen ($)", format="$%.0f")
            }
        )
        
        # Gráfico Interactivo
        fig_segmentation = generate_segmentation_chart(df_segmentation, grouping_key)
        
        st.markdown("---")
        st.caption("Interacción: Haga clic en una barra para aplicar el filtro de segmento.")

        # Renderizar gráfico con manejo de eventos para el clic (Usando clave: "segment_chart")
        event = st.plotly_chart(fig_segmentation, use_container_width=True, key="segment_chart", on_select="rerun") 

        # Manejo ROBUSTO de la selección del punto de datos
        if event and event.selection and event.selection.points:
            try:
                point_data = event.selection.points[0]
                row_index = point_data.get('point_index', point_data.get('point_number'))
                
                if row_index is not None and grouping_key in df_segmentation.columns:
                    selected_val = df_segmentation.iloc[row_index][grouping_key]
                    handle_click(selected_val, grouping_key)
            except Exception as e:
                st.warning(f"Error al procesar la selección del gráfico: {e}")
        elif event and event.selection and not event.selection.points:
             # Caso donde se limpia la selección al hacer clic fuera
             handle_click(None, None)

        st.markdown("---")

        # GRÁFICO DE TENDENCIA (MOVIMIENTO A PESTAÑA 2)
        st.markdown(f"#### 📈 Tendencia Histórica del IER (Análisis de Profundidad)")
        st.caption("Gráfico comparativo del IER diario para el segmento activo vs. la cartera global (si hay filtro activo).")

        fig_trend_filtered = generate_trend_chart(
            df, 
            time_period='D', 
            selected_segment=st.session_state['segment_filter'],
            grouping_key=st.session_state['grouping_key']
        )
        st.plotly_chart(fig_trend_filtered, use_container_width=True, key="trend_chart_filtered_tab2")

# --- Pie de página Actuarial Cortex ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
  <p style="margin: 0.25rem 0;"><strong>© Actuarial Cortex</strong></p>
  <p style="margin: 0.25rem 0;">Conocimiento · Tecnología · Formación</p>
  <p style="margin: 0.25rem 0;">actuarial.cortex@gmail.com | @actuarial_cortex</p>
</div>
""", unsafe_allow_html=True)
