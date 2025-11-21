# data_loader.py
import streamlit as st
import pandas as pd
import kagglehub
import os
import json

# ---------------------------------------------------------
# FUNCIONES DE LIMPIEZA Y CARGA
# ---------------------------------------------------------

def clean_currency(x):
    """Convierte strings como '$ -77.00' a floats -77.0"""
    if isinstance(x, str):
        return float(x.replace('$', '').replace(',', '').strip())
    return x

@st.cache_data(show_spinner="Descargando y procesando dataset de Kaggle...", ttl="2h")
def load_data(rows_limit=20000000):
    """
    Carga datos uniendo CSVs y JSONs desde KaggleHub y adapta las columnas
    al formato esperado por la aplicación (NovaBank).
    """
    try:
        # 1. Descargar/Ubicar dataset
        path = kagglehub.dataset_download("computingvictor/transactions-fraud-datasets")
        
        # 2. Cargar Transacciones
        transactions_path = os.path.join(path, "transactions_data.csv")
        if not os.path.exists(transactions_path):
            st.error("No se encontró transactions_data.csv en la ruta descargada.")
            return pd.DataFrame()

        transactions = pd.read_csv(
            transactions_path, 
            nrows=rows_limit,
            converters={'amount': clean_currency} 
        )
        transactions['date'] = pd.to_datetime(transactions['date'])
        
        # 3. Cargar Etiquetas de Fraude y Mapeo
        with open(os.path.join(path, "train_fraud_labels.json")) as f:
            labels_data = json.load(f)
            
        if isinstance(labels_data, dict) and 'target' in labels_data:
            fraud_series = pd.Series(labels_data['target'], name='is_fraud')
        else:
            fraud_series = pd.Series(labels_data, name='is_fraud')
            
        # Mapeo de valores de texto/booleano a binario (0, 1)
        mapping = {
            'No': 0, 'no': 0, 
            'Yes': 1, 'yes': 1,
            0: 0, 1: 1, 
            False: 0, True: 1
        }
        fraud_series = fraud_series.map(mapping)
        
        fraud_df = fraud_series.reset_index()
        fraud_df.columns = ['id', 'is_fraud']
        # Asegurar coincidencia de tipos para el merge
        fraud_df['id'] = fraud_df['id'].astype(transactions['id'].dtype)

        # 4. MERGE con Etiquetas de Fraude
        df = transactions.merge(fraud_df, on='id', how='left')
        df['is_fraud'] = df['is_fraud'].fillna(0).astype(int)

        # 5. Cargar Datos de Tarjetas
        cards = pd.read_csv(os.path.join(path, "cards_data.csv")).rename(columns={'id': 'card_id'})
        df = df.merge(cards[['card_id', 'card_brand', 'card_type']], on='card_id', how='left')

        # 6. Cargar Códigos MCC (Categorías)
        try:
            with open(os.path.join(path, "mcc_codes.json")) as f:
                mcc_data = json.load(f)
            df['mcc'] = df['mcc'].astype(str)
            df['Category'] = df['mcc'].map(mcc_data).fillna("Other")
        except Exception as e:
            print(f"Warning loading MCC: {e}")
            df['Category'] = "Unknown"

        # ---------------------------------------------------------
        # ADAPTACIÓN AL ESQUEMA DE LA APP (Renombrar columnas)
        # ---------------------------------------------------------
        # La app espera: TransactionAmount, Timestamp, CardBrand, Category, is_fraud
        df = df.rename(columns={
            'amount': 'TransactionAmount',
            'date': 'Timestamp',
            'card_brand': 'CardBrand'
        })

        # Optimización final de tipos para PyArrow (opcional pero recomendado)
        try:
            df['TransactionAmount'] = df['TransactionAmount'].astype('float32')
            df['CardBrand'] = df['CardBrand'].astype('category')
            df['Category'] = df['Category'].astype('category')
        except Exception as e:
            pass # Si falla la optimización, seguimos con los tipos normales

        return df

    except Exception as e:
        st.error(f"Error crítico cargando datos: {e}")
        return pd.DataFrame()

