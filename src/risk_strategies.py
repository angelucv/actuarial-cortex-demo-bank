# risk_strategies.py
from abc import ABC, abstractmethod
import pandas as pd
from metrics_calculator import calculate_risk_exposure_index 

# 1. Strategy Interface
class AbstractRiskStrategy(ABC):
    """Interfaz para todas las estrategias de segmentación de riesgo."""      
    @abstractmethod
    def get_name(self) -> str:
        pass
            
    @abstractmethod
    def get_grouping_key(self) -> str:
        pass     
        
    @abstractmethod
    def analyze_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

# 2. Concrete Strategies
class RiskByCardBrandStrategy(AbstractRiskStrategy):
    """Estrategia: Análisis de riesgo por Marca de Tarjeta."""
    def get_name(self) -> str:
        return "Riesgo por Marca de Tarjeta"
        
    def get_grouping_key(self) -> str:
        return "CardBrand"

    def analyze_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        CORRECCIÓN: Pasamos el DF crudo y la clave de agrupación.
        No hacemos df.groupby() aquí para evitar el error 'DataFrameGroupBy has no attribute empty'.
        """
        return calculate_risk_exposure_index(df, grouping_col="CardBrand") 

class RiskByCategoryStrategy(AbstractRiskStrategy):
    """Estrategia: Análisis de riesgo por Categoría de Comercio."""
    def get_name(self) -> str:
        return "Riesgo por Categoría de Comercio"
        
    def get_grouping_key(self) -> str:
        return "Category"

    def analyze_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        CORRECCIÓN: Pasamos el DF crudo y la clave de agrupación.
        """
        return calculate_risk_exposure_index(df, grouping_col="Category")

# 3. Context
class RiskSegmenter:
    """Contexto que mantiene una referencia a la estrategia y delega la ejecución."""
    def __init__(self, strategy: AbstractRiskStrategy):
        self._strategy = strategy    
        
    @property
    def strategy(self) -> AbstractRiskStrategy:
        return self._strategy    
        
    @strategy.setter
    def strategy(self, strategy: AbstractRiskStrategy) -> None:
        self._strategy = strategy

    def execute_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._strategy.analyze_risk(df)
        
    def get_grouping_key(self) -> str:
        return self._strategy.get_grouping_key()

# Mapeo de estrategias
STRATEGY_MAP = {
    "Marca de Tarjeta": RiskByCardBrandStrategy(),
    "Categoría de Comercio": RiskByCategoryStrategy()
}
