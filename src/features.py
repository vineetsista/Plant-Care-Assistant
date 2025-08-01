from dataset import load_plants
import random


def get_plant_list():
    df = load_plants()
    return df["common"].str.split(", ").str[0].sort_values().unique().tolist()


def get_plant_info(common_name: str) -> dict:
    df = load_plants()
    mask = df["common"].str.contains(common_name, na=False)
    if not mask.any():
        return {}
    row = df[mask].iloc[0]
    return row.to_dict()


def recommend_plant(light, experience, kids_pets, time):
    df = load_plants()

    # Filter out toxic plants if user has kids or pets
    if kids_pets == "Yes":
        df = df[~df["use"].str.contains("Toxic", case=False, na=False)]

    # Define columns that hold lighting info
    light_cols = ["ideallight", "toleratedlight"]

    # Try to filter by lighting preference using each light-related column
    match_df = None
    for col in light_cols:
        if col in df.columns:
            if light == "Low":
                filtered = df[df[col].str.contains("low", case=False, na=False)]
            elif light == "Bright":
                filtered = df[df[col].str.contains("bright", case=False, na=False)]
            else:
                filtered = df

            if not filtered.empty:
                match_df = filtered
                break  # stop once we find a matching group

    # If no match at all, fallback to random plant
    if match_df is None or match_df.empty:
        match_df = df

    return match_df.sample(1).iloc[0].to_dict() if not match_df.empty else None
