"""Streamlit dashboard: predict, compare models, explore data, about."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.preprocessing.crop_preprocessor import load_combined_crop_dataframe  # noqa: E402
from src.preprocessing.yield_preprocessor import load_yield_dataframe  # noqa: E402
from src.utils.paths import load_config, project_root  # noqa: E402


@st.cache_resource
def _load_predictor():
    from app.predictor import ModelPredictor

    cfg = load_config()
    return ModelPredictor(cfg, project_root())


def main() -> None:
    st.set_page_config(page_title="AgroSmart AI", layout="wide")
    st.title("🌾 AgroSmart AI Dashboard")
    tabs = st.tabs(["🌱 Predict", "📊 Model Comparison", "📈 Data Explorer", "ℹ️ About"])

    cfg = load_config()
    raw = project_root() / cfg["paths"]["data_raw"]

    with tabs[0]:
        st.subheader("Predict crop & yield")
        col1, col2 = st.columns(2)
        countries = sorted(cfg.get("country_defaults", {}).keys())
        with col1:
            country = st.selectbox("Country", countries, index=countries.index("India") if "India" in countries else 0)
            soil = st.selectbox("Soil type", ["loam", "clay", "sandy", "loamy", "silt", "peaty", "saline"])
            N = st.number_input("N", 0.0, 140.0, 90.0)
            P = st.number_input("P", 5.0, 145.0, 42.0)
            K = st.number_input("K", 5.0, 205.0, 43.0)
            ph = st.number_input("pH", 3.5, 9.0, 6.5)
        with col2:
            temp = st.number_input("Temperature °C", 8.0, 43.0, 25.0)
            hum = st.number_input("Humidity %", 14.0, 100.0, 70.0)
            rain = st.number_input("Rainfall mm", 20.0, 300.0, 120.0)
            pest = st.number_input("Pesticides (tonnes)", 0.0, 1_000_000.0, 50_000.0)
        if st.button("Run prediction"):
            try:
                pred = _load_predictor()
                out = pred.predict(
                    N=N,
                    P=P,
                    K=K,
                    temperature=temp,
                    humidity=hum,
                    ph=ph,
                    rainfall=rain,
                    soil_type=soil,
                    country=country,
                    pesticides=pest,
                )
                st.success(f"Recommended: **{out['crop']}** — yield **{out['yield']}** tons/ha")
                st.json(out)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))

    with tabs[1]:
        st.subheader("Model comparison (from training metadata)")
        meta_crop_path = project_root() / cfg["models"]["crop"]["metadata_path"]
        meta_yield_path = project_root() / cfg["models"]["yield"]["metadata_path"]
        if meta_crop_path.exists():
            with open(meta_crop_path, encoding="utf-8") as fh:
                mc = json.load(fh)
            rows = []
            for name, m in (mc.get("models") or {}).items():
                rows.append({"task": "crop", "model": name, "score": m.get("f1_macro", 0)})
            st.plotly_chart(px.bar(pd.DataFrame(rows), x="model", y="score", color="task"), use_container_width=True)
            st.dataframe(pd.DataFrame(mc.get("models", {})).T)
        else:
            st.info("Train models first: `python src/training/train_crop.py`")
        if meta_yield_path.exists():
            with open(meta_yield_path, encoding="utf-8") as fh:
                my = json.load(fh)
            rows2 = []
            for name, m in (my.get("models") or {}).items():
                rows2.append({"task": "yield", "model": name, "R2": m.get("r2", 0)})
            st.plotly_chart(px.bar(pd.DataFrame(rows2), x="model", y="R2", color="task"), use_container_width=True)
            st.dataframe(pd.DataFrame(my.get("models", {})).T)

    with tabs[2]:
        st.subheader("Data explorer")
        Xc, yc = load_combined_crop_dataframe(raw)
        st.write("Combined crop rows:", len(Xc), "— distinct labels:", yc.nunique())
        st.plotly_chart(px.histogram(Xc, x="N", nbins=40), use_container_width=True)
        Xy, _ = load_yield_dataframe(raw)
        st.write("Yield rows:", len(Xy))
        num = Xy.select_dtypes(include="number")
        if num.shape[1] > 1:
            st.plotly_chart(px.imshow(num.corr(), text_auto=True), use_container_width=True)

    with tabs[3]:
        st.markdown(
            """
            **AgroSmart AI** compares five crop classifiers and five yield regressors,
            persists the best models, and serves them through Flask + Streamlit.

            **Run locally**
            ```bash
            pip install -r requirements.txt
            python src/training/train_crop.py
            python src/training/train_yield.py
            streamlit run dashboard/streamlit_app.py
            ```
            """
        )


if __name__ == "__main__":
    main()
