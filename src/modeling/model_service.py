# model_service.py
"""
Load the trained pipeline and label encoders, then provide a function
`query_care_instructions` that, given a plant_info dict, returns a care guide
using the local ML model.
"""

import joblib
import pandas as pd
from pathlib import Path

# Paths to artifacts
MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"
FEATURE_COLUMNS_PATH = Path(__file__).resolve().parent / "feature_columns.joblib"
LABEL_ENCODERS_PATH = Path(__file__).resolve().parent / "label_encoders.joblib"

# Load artifacts
_pipeline = joblib.load(MODEL_PATH)
_feature_cols = joblib.load(FEATURE_COLUMNS_PATH)
_label_encoders = joblib.load(LABEL_ENCODERS_PATH)

# For temperature, we'll pull directly from plant_info


def query_care_instructions(plant_info: dict) -> str:
    """
    Given plant_info (from dataset row), predict light and watering,
    and include temperature range from the raw info.
    Returns a formatted care guide string.
    """
    # Build input DataFrame for model
    data = {col: [plant_info.get(col, None)] for col in _feature_cols}
    X = pd.DataFrame(data)

    # Predict encoded labels
    preds = _pipeline.predict(X)[0]

    # Decode labels back to original strings
    decoded = {}
    for i, col in enumerate(_label_encoders.keys()):
        le = _label_encoders[col]
        decoded[col] = le.inverse_transform([preds[i]])[0]

    # Fetch temperature from plant_info if present
    temp_min = plant_info.get("tempmin.fahrenheit") or plant_info.get("tempmin.celsius")
    temp_max = plant_info.get("tempmax.fahrenheit") or plant_info.get("tempmax.celsius")
    temp_unit = "°F" if "fahrenheit" in plant_info else "°C"

    # Format care guide
    guide = [
        f"☀️ Light: {decoded.get('ideallight', 'N/A')}",
        f"💧 Watering: {decoded.get('watering', 'N/A')}",
    ]

    if temp_min is not None and temp_max is not None:
        guide.append(f"🌡️ Temperature: {temp_min}{temp_unit} to {temp_max}{temp_unit}")

    return "\n".join(guide)
