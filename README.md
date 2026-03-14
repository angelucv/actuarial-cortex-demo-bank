---
title: Demo de Actuarial Cortex - Deteccion de Fraude
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
- actuarial-cortex
pinned: false
short_description: Actuarial Cortex - Banca, deteccion de fraude (Streamlit)
license: unknown
---

# Demo de Actuarial Cortex - Deteccion de Fraude

Dashboard de analisis de fraude en Streamlit: exposicion al riesgo (IER), tasa de fraude y segmentacion por marca de tarjeta o categoria de comercio. Datos de demostracion (Kaggle). Codigo en [GitHub (actuarial-cortex-demo-bank)](https://github.com/angelucv/actuarial-cortex-demo-bank); se despliega en [Hugging Face Spaces](https://huggingface.co/spaces/angelucv/actuarial-cortex-bank-fraud).

**Sitio web:** [Actuarial Cortex](https://actuarial-cortex.pages.dev/) — Hub de conocimiento y tecnologia actuarial. Este demo forma parte de su oferta para el sector bancario.

## Como ejecutar en local

```bash
pip install -r requirements.txt
streamlit run src/streamlit_app.py
```

O `streamlit run app.py` si tu entrada es `app.py`. La primera vez se descargan los datos de Kaggle (puede tardar unos segundos).

## Repo y despliegue

- **GitHub:** origen del codigo (push a `main` sincroniza con el Space).
- **Space:** [angelucv/actuarial-cortex-bank-fraud](https://huggingface.co/spaces/angelucv/actuarial-cortex-bank-fraud).

Para sincronizacion automatica GitHub a HF: en el repo de GitHub, Settings, Secrets, `HF_TOKEN` (token de HF con permiso Write).
