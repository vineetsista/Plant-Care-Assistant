# train.py

import pandas as pd
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report, accuracy_score

# Paths to data and artifacts
data_path = Path(__file__).resolve().parent.parent / "house_plants.json"
model_path = Path(__file__).resolve().parent / "model.joblib"
feature_columns_path = Path(__file__).resolve().parent / "feature_columns.joblib"
label_encoders_path = Path(__file__).resolve().parent / "label_encoders.joblib"

# 1. Load dataset
df = pd.read_json(data_path)
print(f"Loaded {len(df)} records from {data_path}")

# 2. Select features and raw targets
feature_cols = ["family", "category", "origin", "climate"]
raw_label_col = "watering"
label_cols = ["ideallight", raw_label_col]

# 3. Clean dataset
df = df.dropna(subset=feature_cols + label_cols)
print(f"After dropping NA: {len(df)} records remain.")


# 3a. Consolidate watering classes for balance
def map_watering(text):
    t = str(text).lower()
    if "dry" in t:
        return "dry"
    if "moist" in t:
        return "moist"
    return "regular"


df[raw_label_col] = df[raw_label_col].apply(map_watering)
print(f"Watering labels consolidated into: {df[raw_label_col].unique().tolist()}")

# 4. Prepare X and y
X = df[feature_cols]
y = df[["ideallight", raw_label_col]]

# 5. Encode labels
label_encoders = {}
y_encoded = pd.DataFrame(index=df.index)
for col in y.columns:
    le = LabelEncoder()
    y_encoded[col] = le.fit_transform(y[col].astype(str))
    label_encoders[col] = le
print(
    "Encoded label classes:",
    {col: le.classes_.tolist() for col, le in label_encoders.items()},
)

# 6. Build preprocessing & model pipeline
cat_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
preprocessor = ColumnTransformer(
    transformers=[("cat", cat_encoder, feature_cols)], remainder="drop"
)

base_clf = RandomForestClassifier(
    n_estimators=200, class_weight="balanced", random_state=42
)
multi_clf = MultiOutputClassifier(base_clf)
pipeline = Pipeline([("preprocess", preprocessor), ("classifier", multi_clf)])
print("Pipeline created with balanced RandomForest and OneHotEncoder.")

# 7. Split into train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

# 8. Train final model
pipeline.fit(X_train, y_train)
print("Model training complete.")

# 9. Evaluate
y_pred = pipeline.predict(X_test)
print("\nTest evaluation:")
for idx, col in enumerate(y.columns):
    print(f"\n-- {col} --")
    print(classification_report(y_test[col], y_pred[:, idx]))
    print(f"Accuracy: {accuracy_score(y_test[col], y_pred[:, idx]):.2f}")

# 10. Save artifacts
joblib.dump(pipeline, model_path)
joblib.dump(feature_cols, feature_columns_path)
joblib.dump(label_encoders, label_encoders_path)
print(f"Saved model to {model_path}")
print(f"Saved feature columns to {feature_columns_path}")
print(f"Saved label encoders to {label_encoders_path}")
