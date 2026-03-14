import streamlit as st
import pandas as pd
from data_loader import load_data
from metrics_calculator import calculate_kpis
from visualizations import generate_trend_chart, generate_segmentation_chart
from risk_strategies import RiskSegmenter, STRATEGY_MAP

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

# Función Callback
def handle_click(segment_value, grouping_key_value):
    """Procesa el valor del segmento clicado y actualiza el filtro."""
    if segment_value:
        st.session_state['segment_filter'] = segment_value
        st.session_state['grouping_key'] = grouping_key_value
        st.toast(f"Filtro aplicado: {grouping_key_value} = {segment_value}")
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
    st.sidebar.image(LOGO_SIDEBAR, use_container_width=True, caption="Actuarial Cortex")
except Exception:
    st.sidebar.markdown("**Actuarial Cortex**")
st.sidebar.caption("Aplicativo para bancos · Detección de fraude")

# --- Inicio: logo principal y descripción ---
try:
    st.image(LOGO_INICIO, use_container_width=True)
except Exception:
    st.markdown("**Actuarial Cortex**")
st.markdown("""
**Actuarial Cortex** es un hub de conocimiento y tecnología actuarial. Este **demo de detección de fraude** 
forma parte de su oferta para el sector bancario: permite explorar la **exposición al riesgo (IER)** y la 
**tasa de fraude** por segmentos (marca de tarjeta, categoría de comercio), con métricas ejecutivas y 
análisis estratégico para apoyar la toma de decisiones.
""")
st.divider()

# --- Títulos y Navegación Lateral ---
st.title("🛡️ Actuarial Cortex — Banca · Detección de Fraude")
st.caption("Resumen ejecutivo y análisis estratégico de riesgo por segmentación.")

st.sidebar.header("Opciones de Análisis")

# MOVIDO: El selector de estrategia ahora está fuera de las pestañas para asegurar su carga
strategy_name = st.sidebar.radio(
    "Seleccione la Estrategia de Análisis:",
    list(STRATEGY_MAP.keys()),
    index=0,
    help="Cambia la lógica de agrupación (Patrón Strategy)."
)

# --- Pie del menú lateral (unificado Actuarial Cortex) ---
st.sidebar.markdown("---")
st.sidebar.caption("**Elaborado por el Prof. Angel Colmenares**")
st.sidebar.caption("© Actuarial Cortex")
st.sidebar.caption("Conocimiento · Tecnología · Formación")
st.sidebar.caption("actuarial.cortex@gmail.com | @actuarial_cortex")

# --- Pestañas Principales ---
tab1, tab2 = st.tabs(["Resumen Ejecutivo", "Análisis Estratégico de Riesgo"]) 

# =========================================================================
# PESTAÑA 1: RESUMEN EJECUTIVO
# =========================================================================
with tab1:
    st.subheader("Métricas Clave de Exposición Global")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Volumen Total", f"${kpis['Total_Volume']:,.0f}")
    with col2:
        st.metric("Transacciones", f"{kpis['Total_Transactions']:,}")
    with col3:
        st.metric("Tasa de Fraude (TF)", f"{kpis['Fraud_Rate']:.2f}%")
    with col4:
        filter_status = st.session_state['segment_filter']
        st.metric("Filtro Activo", filter_status if filter_status else "Ninguno")

    st.divider()
    
    st.subheader("Tendencia Temporal del IER")
    filtered_segment = st.session_state['segment_filter']
    fig_trend = generate_trend_chart(df, time_period='D', selected_segment=filtered_segment)
    st.plotly_chart(fig_trend, use_container_width=True)

# =========================================================================
# PESTAÑA 2: ANÁLISIS ESTRATÉGICO DE RIESGO
# =========================================================================
with tab2:
    # Lógica de Análisis (se ejecuta siempre que Strategy Name sea válido)
    if strategy_name:
        selected_strategy = STRATEGY_MAP[strategy_name]
        risk_context = RiskSegmenter(selected_strategy)
        
        # Ejecutar análisis
        df_segmentation = risk_context.execute_analysis(df)
        grouping_key = risk_context.get_grouping_key()
        
        st.markdown(f"#### Resultados de la Estrategia: **{strategy_name}**")
        
        # Validación de max_ier_val para evitar errores en st.dataframe
        if not df_segmentation.empty:
            max_val_calc = df_segmentation['IER'].max()
            # Asegurar que sea un float y > 0
            max_ier_val = float(max_val_calc) if pd.notna(max_val_calc) and max_val_calc > 0 else 1.0
        else:
            max_ier_val = 1.0

        # Tabla
        st.dataframe(
            df_segmentation.head(10), 
            column_order=(grouping_key, 'IER', 'Fraud_Rate', 'Total_Volume'),
            hide_index=True, 
            use_container_width=True,
            column_config={
                'IER': st.column_config.ProgressColumn("IER", format="%.2f", min_value=0, max_value=max_ier_val),
                'Fraud_Rate': st.column_config.NumberColumn("TF (%)", format="%.2f%%"),
                'Total_Volume': st.column_config.NumberColumn("Volumen ($)", format="$%.0f")
            }
        )
        
        # Gráfico Interactivo
        fig_segmentation = generate_segmentation_chart(df_segmentation, grouping_key)
        
        st.markdown("---")
        st.caption("Interactividad: Haga clic en una barra para filtrar la Pestaña 1.")

        # Renderizar gráfico con manejo de eventos
        event = st.plotly_chart(fig_segmentation, use_container_width=True, key="segment_chart", on_select="rerun")
        
        # Manejo ROBUSTO de la selección
        if event and event.selection and event.selection.points:
            try:
                # Intentamos obtener el punto de manera segura
                point_data = event.selection.points[0]
                
                # Plotly a veces usa 'point_index' y a veces 'point_number'
                row_index = point_data.get('point_index', point_data.get('point_number'))
                
                if row_index is not None and grouping_key in df_segmentation.columns:
                    selected_val = df_segmentation.iloc[row_index][grouping_key]
                    handle_click(selected_val, grouping_key)
            except Exception as e:
                st.warning(f"Error al procesar la selección: {e}")
                # No detenemos la app, solo mostramos advertencia
        elif event and event.selection and not event.selection.points:
             # Caso donde se limpia la selección
             handle_click(None, None)

        # Botón de limpieza manual
        if st.session_state['segment_filter']:
            if st.button("Limpiar Filtro Activo"):
                st.session_state['segment_filter'] = None
                st.session_state['grouping_key'] = None
                st.rerun()

# --- Pie de página Actuarial Cortex ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
  <p style="margin: 0.25rem 0;"><strong>© Actuarial Cortex</strong></p>
  <p style="margin: 0.25rem 0;">Conocimiento · Tecnología · Formación</p>
  <p style="margin: 0.25rem 0;">actuarial.cortex@gmail.com | @actuarial_cortex</p>
</div>
""", unsafe_allow_html=True)
