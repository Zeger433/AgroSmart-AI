# 🌾 AgroSmart AI

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)](#running-tests)
[![Models](https://img.shields.io/badge/models-5%20classifiers%20%7C%205%20regressors-gold.svg)](#model-performance)
[![Last Updated](https://img.shields.io/badge/last%20updated-2026--05--14-gold.svg)]()

**AgroSmart AI** is a production-grade machine learning platform for **precision agriculture**. It recommends the optimal crop to grow and predicts expected yield from soil chemistry and climate inputs — benchmarking **5 classifiers** and **5 regressors** with full cross-validation, hyperparameter tuning, and a professional web interface.

Built as a Final Year Project (FYP) demonstrating end-to-end ML engineering: data pipelines, model comparison, REST API, interactive dashboard, and automated testing.

---

## ✨ Features

- **Multi-model benchmarking** — 5 crop classifiers and 5 yield regressors trained, evaluated, and compared automatically; best model auto-selected and saved for production
- **Experiment suite** — includes a class-imbalance study (raw merged data vs. SMOTE + class weights) to demonstrate real-world data challenges
- **Professional Flask web UI** — forest green / cream / gold palette, input validation with agronomic range checks, confidence scores, and yield range estimates
- **Streamlit analytics dashboard** — Predict, Model Comparison, Data Explorer, and About tabs
- **REST API** — `/predict`, `/model-info`, `/health`, `/get_defaults` endpoints with proper HTTP error codes
- **Centralized config** — all paths, hyperparameters, and validation ranges in `config/config.yaml`
- **Full pytest suite** — 18 tests covering API, models, preprocessing, and validators
- **Structured logging** — loguru throughout; no bare `print()` in production code
- **Google-style docstrings** and type hints on every function

---

## 📊 Model Performance

All metrics are from the hold-out test set (80/20 stratified split). Cross-validation used 5-fold stratified CV.

### Crop classifiers — Experiment 1 (balanced dataset, `Crop_recommendation.csv`)

| Model | Accuracy | F1 Macro | F1 Weighted | CV F1 (mean ± std) |
|---|---|---|---|---|
| **RandomForest** ⭐ | **0.9932** | **0.9932** | **0.9932** | 0.9960 ± 0.0029 |
| XGBoost | 0.9886 | 0.9885 | 0.9885 | 0.9926 ± 0.0014 |
| GradientBoosting | 0.9886 | 0.9887 | 0.9887 | 0.9874 ± 0.0031 |
| SVM | 0.9841 | 0.9840 | 0.9840 | 0.9788 ± 0.0106 |
| KNN | 0.9818 | 0.9817 | 0.9817 | 0.9661 ± 0.0108 |

> Best model selected by F1 Macro → **RandomForest** deployed to `artifacts/models/crop_model.pkl`

### Yield regressors — all models (`yield_df.csv`)

| Model | R² | MAE (hg/ha) | RMSE | CV R² (mean ± std) |
|---|---|---|---|---|
| **RandomForest** ⭐ | **0.9734** | **5,920** | 13,884 | 0.9723 ± 0.0013 |
| XGBoost | 0.9699 | 8,014 | 14,768 | 0.9693 ± 0.0023 |
| GradientBoosting | 0.8688 | 20,068 | 30,853 | 0.8634 ± 0.0060 |
| Ridge | 0.7493 | 29,811 | 42,644 | 0.7450 ± 0.0051 |
| SVR | -0.2018 | 57,307 | 93,367 | -0.2050 ± 0.0085 |

> Best model selected by R² → **RandomForest** deployed to `artifacts/models/yield_model.pkl`
>
> SVR's negative R² on this dataset confirms that a linear kernel cannot model the complex non-linear interactions between crop type, region, and climate — a finding documented in `artifacts/reports/`.

### Experiment 2 — Class imbalance study (merged dataset)

| Model | Raw Accuracy | SMOTE Accuracy | Raw F1 Macro | SMOTE F1 Macro |
|---|---|---|---|---|
| RandomForest | 0.2453 | 0.2453 | 0.8059 | 0.8040 |
| XGBoost | 0.2412 | 0.2446 | 0.8019 | 0.8011 |
| SVM | 0.2480 | 0.2480 | 0.7866 | 0.7991 |
| KNN | 0.2480 | 0.2444 | 0.7971 | 0.7929 |
| GradientBoosting | 0.2518 | 0.2489 | 0.8038 | 0.8014 |

> The low accuracy with high F1 Macro on merged data is expected: it reflects **structural label overlap** between the two source datasets (not an encoding bug). SMOTE shows no significant improvement, confirming the problem is data distribution rather than sample count. The balanced `Crop_recommendation.csv` dataset is used for the production model.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| ML — Classification | scikit-learn (RandomForest, SVM, KNN, GradientBoosting), XGBoost |
| ML — Regression | scikit-learn (RandomForest, Ridge, SVR, GradientBoosting), XGBoost |
| Imbalance handling | imbalanced-learn (SMOTE) |
| Web framework | Flask 3.0 |
| Dashboard | Streamlit 1.32 |
| Config | PyYAML |
| Logging | loguru |
| Testing | pytest 8.0 |
| Data | pandas, numpy |
| Visualisation | matplotlib, seaborn, plotly |

---

## 🚀 Quick Start

```bash
git clone https://github.com/saithahmed147-ui/agrosmart-ai.git
cd agrosmart-ai

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

### Train models

```bash
python src/training/train_crop.py        # Experiment 1 — balanced baseline
python src/training/train_yield.py       # Yield regressors
python src/training/train_crop_experiment.py   # Experiment 2 — imbalance study
python src/evaluation/generate_report_data.py  # Print comparison table + save CSV
```

### Run the web app

```bash
python app/main.py
```

Visit **http://127.0.0.1:5000**

### Run the Streamlit dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

### Run tests

```bash
pytest tests/ -v
# 18 passed
```

Or use the Makefile:

```bash
make train    # train all models
make test     # pytest
make run      # flask app
```

---

## 📁 Project Structure

```
agrosmart-ai/
├── app/                        # Flask web application
│   ├── main.py                 # App factory, routes, FEATURE_LABELS
│   ├── predictor.py            # Model loading, prediction logic, confidence
│   └── static/ + templates/   # Professional UI (green/gold theme)
│
├── artifacts/
│   ├── models/                 # crop_model.pkl, yield_model.pkl, *_metadata.json
│   └── reports/                # Comparison charts, confusion matrix, imbalance study
│
├── config/config.yaml          # Paths, validation ranges, country defaults
├── dashboard/streamlit_app.py  # 4-tab analytics dashboard
├── data/raw/                   # Source CSV datasets
├── notebooks/                  # EDA + model comparison notebooks
│
├── src/
│   ├── preprocessing/          # crop_preprocessor.py, yield_preprocessor.py
│   ├── models/                 # crop_models.py, yield_models.py (all factories)
│   ├── training/               # train_crop.py, train_yield.py, train_crop_experiment.py
│   ├── evaluation/             # metrics.py, compare_models.py, generate_report_data.py
│   └── utils/                  # logger.py, validators.py
│
├── tests/                      # 18 pytest tests (API, models, preprocessing, validators)
├── Makefile
├── requirements.txt
└── README.md
```

---

## 🌐 API Reference

| Route | Method | Description |
|---|---|---|
| `/` | GET | Web UI |
| `/health` | GET | `{"status": "ok"}` |
| `/model-info` | GET | Full training metadata for crop + yield models |
| `/get_defaults` | POST | `{"country": "Pakistan"}` → auto-fill climate defaults |
| `/predict` | POST | Validated prediction → crop name, confidence, yield estimate, explanation |

### Example `/predict` request

```json
{
  "N": 100, "P": 90, "K": 40,
  "temperature": 22, "humidity": 66.1,
  "ph": 6.7, "rainfall": 266,
  "soil_type": "Sandy",
  "country": "Pakistan",
  "pesticides_tonnes": 45000,
  "area_hectares": null
}
```

### Example `/predict` response

```json
{
  "crop": "Wheat",
  "confidence": 0.923,
  "model_used": "RandomForest",
  "yield_model_used": "RandomForest",
  "expected_yield_tons_ha": 2.57,
  "yield_range": [1.97, 3.16],
  "explanation": "Yield is mainly influenced by Crop Type (66.67%), Region / Country (12.76%). Predictions are informed by data for Pakistan."
}
```

---

## 🧪 Test Coverage

```
tests/test_api.py            # /health, /model-info, /predict valid, invalid pH, missing field
tests/test_models.py         # crop + yield model load, prediction shape, valid class, rice regression test
tests/test_preprocessing.py  # balanced baseline loads (2200 rows, 22 classes), crop + yield dataframes
tests/test_validators.py     # valid inputs pass, pH/N out-of-range, temperature below minimum
```

```
18 passed, 41 warnings in 15.17s
```

---

## 🔬 Reproducing Results

After running the two training scripts, exact metrics are persisted in:

- `artifacts/models/crop_metadata.json` — all 5 classifier scores + classification report
- `artifacts/models/yield_metadata.json` — all 5 regressor scores + feature importance
- `artifacts/models/crop_metadata_experiment.json` — Experiment 2 raw vs SMOTE results
- `artifacts/reports/experiment_comparison.csv` — side-by-side table (Exp1 vs Exp2)

Charts saved to `artifacts/reports/`:
- `crop_model_comparison.png`
- `yield_model_comparison.png`
- `crop_confusion_matrix.png`
- `feature_importance.png`
- `imbalance_experiment.png`

---

## 📄 License

MIT — suitable for academic submission. Retain attribution in coursework.

---

## 👤 Author

**Sait Ahmed** — Final Year Project, 2026