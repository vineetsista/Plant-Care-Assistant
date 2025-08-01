import json
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "house_plants.json"


def load_plants() -> pd.DataFrame:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    for col in ["common", "insects", "use", "diseases"]:
        if col in df:
            df[col] = df[col].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else x or ""
            )
    return df
