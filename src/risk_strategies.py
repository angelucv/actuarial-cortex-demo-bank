# risk_strategies.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import streamlit as st 

# --- 1. Definición de la Interfaz Strategy (ABC) ---
class RiskStrategy(ABC):
    """
    Define la interfaz común para todas las estrategias de segmentación de riesgo.
    """
    @abstractmethod
    def get_grouping_key_names(self) -> list:
        """Retorna una lista de posibles nombres de columna para la agrupación."""
        pass

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """Realiza el cálculo del IER por el segmento definido (Fraud_Rate * log(Volume))."""
        pass

    def _find_actual_grouping_key(self, df: pd.DataFrame) -> str | None:
        """
        Busca la columna de agrupación real en el DataFrame, probando nombres comunes.
        """
        for key in self.get_grouping_key_names():
            if key in df.columns:
                return key
        return None # No se encontró ninguna columna de agrupación válida

    def _ensure_segment_column(self, df: pd.DataFrame, grouping_key: str, default_values: list):
        """
        Función auxiliar para asegurar que la columna de segmentación exista. 
        Si no existe, crea datos mock y emite una advertencia, evitando el KeyError.
        """
        # Nota: grouping_key aquí es el nombre conceptual que se usará para el mock si falla.
        if grouping_key not in df.columns:
            st.warning(f"⚠️ **{grouping_key}** no se encontró en el DataFrame. Se están usando datos de segmentación *mock* temporales para evitar el error. Por favor, actualice su `data_loader.py` o la lista de nombres comunes en la estrategia.")
            
            # Crear datos mock robustos para que el agrupamiento funcione
            if not df.empty:
                df[grouping_key] = np.random.choice(default_values, size=len(df))
                return grouping_key # Retorna la clave mock creada
            else:
                return None # Indica que no se pudo procesar

        return grouping_key # Retorna la clave real encontrada

# --- 2. Implementaciones Concretas de Strategy ---

class CardBrandStrategy(RiskStrategy):
    """Estrategia para segmentar el riesgo por Marca de Tarjeta (ej. Visa, Mastercard)."""
    def get_grouping_key_names(self) -> list:
        # Nombres comunes para la columna de marca de tarjeta. 'CardBrand' es el nombre final en data_loader.py.
        return ['CardBrand', 'card_brand', 'brand', 'card_type'] 

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 1. Determinar la clave de agrupación real
        grouping_key = self._find_actual_grouping_key(df)
        
        # 2. Si no se encuentra, usar el nombre por defecto y crear mock data si es necesario
        if not grouping_key:
            # Usar 'CardBrand' como nombre por defecto/mock
            grouping_key = self._ensure_segment_column(df, 'CardBrand', ['VISA', 'Mastercard', 'AMEX', 'Discover'])
        
        if not grouping_key:
             return pd.DataFrame() # Retorna DF vacío si no hay datos para procesar

        # Calcular las métricas por segmento
        df_metrics = df.groupby(grouping_key).apply(
            lambda x: pd.Series({
                'Total_Transactions': len(x),
                'Fraud_Count': x['is_fraud'].sum(),
                'Total_Volume': x['TransactionAmount'].sum()
            })
        ).reset_index()

        # Calcular Tasa de Fraude (Fraud_Rate) y IER
        df_metrics['Fraud_Rate'] = (df_metrics['Fraud_Count'] / df_metrics['Total_Transactions']) * 100
        df_metrics['Fraud_Rate'] = df_metrics['Fraud_Rate'].fillna(0) 

        # IER = (Fraud_Rate / 100) * log(Total_Volume + epsilon)
        df_metrics['IER'] = (df_metrics['Fraud_Rate'] / 100) * np.log(df_metrics['Total_Volume'] + 1e-6)
        
        # Ordenar por IER descendente
        df_metrics = df_metrics.sort_values(by='IER', ascending=False)
        
        return df_metrics

class MerchantCategoryStrategy(RiskStrategy):
    """Estrategia para segmentar el riesgo por Categoría de Comercio (MCC)."""
    def get_grouping_key_names(self) -> list:
        # CORRECCIÓN CLAVE: 'Category' se agrega, ya que es el nombre final que usa data_loader.py
        return ['Category', 'MerchantCategory', 'MCC', 'merchant_category', 'merchant_category_code']

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # 1. Determinar la clave de agrupación real
        grouping_key = self._find_actual_grouping_key(df)

        # 2. Si no se encuentra, usar el nombre por defecto y crear mock data si es necesario
        if not grouping_key:
            # Usar 'MerchantCategory' como nombre por defecto/mock
            grouping_key = self._ensure_segment_column(df, 'MerchantCategory', ['Retail', 'Digital Goods', 'Travel', 'Services'])

        if not grouping_key:
            return pd.DataFrame() # Retorna DF vacío si no hay datos para procesar

        # Mismo cálculo de métricas: Total Transactions, Fraud Count, Total Volume
        df_metrics = df.groupby(grouping_key).apply(
            lambda x: pd.Series({
                'Total_Transactions': len(x),
                'Fraud_Count': x['is_fraud'].sum(),
                'Total_Volume': x['TransactionAmount'].sum()
            })
        ).reset_index()

        # Calcular Tasa de Fraude (Fraud_Rate) y IER
        df_metrics['Fraud_Rate'] = (df_metrics['Fraud_Count'] / df_metrics['Total_Transactions']) * 100
        df_metrics['Fraud_Rate'] = df_metrics['Fraud_Rate'].fillna(0)

        # IER = (Fraud_Rate / 100) * log(Total_Volume + epsilon)
        df_metrics['IER'] = (df_metrics['Fraud_Rate'] / 100) * np.log(df_metrics['Total_Volume'] + 1e-6)
        
        # Ordenar por IER descendente
        df_metrics = df_metrics.sort_values(by='IER', ascending=False)
        
        return df_metrics

# --- 3. Definición del Contexto (Segmenter) ---

class RiskSegmenter:
    """
    Clase de Contexto (Context) que utiliza una estrategia para ejecutar el análisis.
    """
    def __init__(self, strategy: RiskStrategy):
        self._strategy = strategy
        self._last_grouping_key = None # Almacena la clave real usada

    @property
    def strategy(self) -> RiskStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: RiskStrategy):
        self._strategy = strategy
        self._last_grouping_key = None # Resetear al cambiar de estrategia
        
    def get_grouping_key(self) -> str:
        """Obtiene la clave de agrupación de la estrategia activa (la última usada o la principal)."""
        # Si se usó una clave real, devolver esa, si no, devolver el primer nombre en la lista de la estrategia (el nombre conceptual)
        if self._last_grouping_key:
            return self._last_grouping_key
        return self._strategy.get_grouping_key_names()[0]


    def execute_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta el análisis de riesgo utilizando la estrategia seleccionada.
        Actualiza el _last_grouping_key con la clave que realmente se usó para el análisis.
        """
        # La clave real usada está implícitamente determinada dentro de analyze
        df_result = self._strategy.analyze(df)
        
        # Intentar determinar la clave usada para la tabla de resultados (la primera columna que no es métrica)
        if not df_result.empty:
            metric_cols = ['Total_Transactions', 'Fraud_Count', 'Total_Volume', 'Fraud_Rate', 'IER']
            # Encontrar la columna que no es métrica (debe ser la de agrupación)
            grouping_col = [col for col in df_result.columns if col not in metric_cols]
            if grouping_col:
                self._last_grouping_key = grouping_col[0]

        return df_result

# --- 4. Mapa de Estrategias para Streamlit (Referencia Global) ---

STRATEGY_MAP = {
    "Marca de Tarjeta (CardBrand)": CardBrandStrategy(),
    "Categoría de Comercio (MCC)": MerchantCategoryStrategy(),
}
