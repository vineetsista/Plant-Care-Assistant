import streamlit as st
from dataset import load_plants
from features import get_plant_list, get_plant_info, recommend_plant
from modeling.model_service import query_care_instructions

# Application configuration
st.set_page_config(page_title="Plant Care Assistant", page_icon="🌿", layout="wide")

# Load plant data once
plants_df = load_plants()

# Header
st.markdown(
    "<div style='text-align: center; padding: 20px;'>"
    "<h1 style='color: #2e7d32; margin:0;'>🌿 Plant Care Assistant</h1>"
    "<p style='font-size:16px; margin-top:4px;'>Explore a collection of house plants and get personalized care guidance.</p>"
    "</div>",
    unsafe_allow_html=True,
)
st.write("---")

# Tabs
tab1, tab2 = st.tabs(["🌱 Plant Info", "🪴 Plant Recommender"])

# ------------------------------------
# Tab 1: Collection Overview & Plant Info
# ------------------------------------
with tab1:
    st.subheader("🌐 Category Distribution Overview")
    st.markdown(
        "Explore the rarity of a select group of different houseplant types and discover areas to expand your collection."
    )
    counts = plants_df["category"].value_counts()
    st.bar_chart(counts)
    total = len(plants_df)
    categories = counts.count()
    top_cat, top_count = counts.index[0], counts.iloc[0]
    st.markdown(
        f"**Total Plants:** {total}   |   **Categories:** {categories}   |   "
        f"**Top Category:** {top_cat} ({top_count})"
    )
    st.write("---")

    st.subheader("🌱 Explore Individual Plant")
    plant_choice = st.selectbox("Select a plant:", get_plant_list())
    if plant_choice and st.button("Generate Care Guide", key=f"guide_{plant_choice}"):
        # 1) Fetch info
        info = get_plant_info(plant_choice)

        # 2) Unpack into Python vars
        light = info.get("ideallight", "N/A")
        watering = info.get("watering", "N/A")

        # ← switched to Celsius
        tmin = info.get("tempmin.celsius")
        tmax = info.get("tempmax.celsius")

        # 3) Header
        st.markdown(f"#### {plant_choice}")

        # 4) Metrics row with centered HTML cards
        mcol1, mcol2, mcol3 = st.columns(3, gap="medium")

        with mcol1:
            st.markdown(
                f"""
                <div style="text-align:center; padding:8px 4px;">
                  <h4 style="margin:0 0 6px; font-size:18px;">☀️ Light Requirement</h4>
                  <p style="margin:0; line-height:1.5;">{light}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with mcol2:
            st.markdown(
                f"""
                <div style="text-align:center; padding:8px 4px;">
                  <h4 style="margin:0 0 6px; font-size:18px;">💧 Watering Frequency</h4>
                  <p style="margin:0; line-height:1.5;">{watering}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with mcol3:
            # ← changed symbol to °C
            temp_range = f"{tmin}°C – {tmax}°C"
            st.markdown(
                f"""
                <div style="text-align:center; padding:8px 4px;">
                  <h4 style="margin:0 0 6px; font-size:18px;">🌡️ Temperature (°C)</h4>
                  <p style="margin:0; line-height:1.5;">{temp_range}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 5) Divider + raw JSON
        st.markdown(
            "<hr style='border:none; border-top:1px solid #444; margin:24px 0;'>",
            unsafe_allow_html=True,
        )
        with st.expander("🔍 Show Raw Data", expanded=False):
            st.json(info)

# ------------------------------------
# Tab 2: Personalized Plant Recommender
# ------------------------------------
with tab2:
    st.markdown("## 🌟 Your Preferences")
    st.markdown(
        "Answer a few quick questions and we'll recommend your perfect plant! 🪴"
    )
    st.markdown("---")

    form_col, result_col = st.columns([1, 1], gap="large")

    # ——— Preferences Form ———
    with form_col:
        with st.form("recommender_form", clear_on_submit=False):
            light_pref = st.selectbox(
                "🌞 Lighting at home", ["Low", "Medium", "Bright"], index=1
            )
            exp_level = st.selectbox(
                "🌿 Your plant care experience",
                ["Beginner", "Intermediate", "Expert"],
                index=0,
            )
            kids_pets = st.radio("👶 Do you have kids or pets?", ["No", "Yes"], index=0)
            care_time = st.selectbox(
                "⏱️ Weekly care time", ["Low", "Medium", "High"], index=1
            )
            submitted = st.form_submit_button("🔍 Recommend My Plant")

    # ——— Recommendation Column ———
    with result_col:
        if not submitted:
            st.info(
                "Fill out the form on the left and click **Recommend My Plant** to see your ideal plant! 💚"
            )
        else:
            result = recommend_plant(light_pref, exp_level, kids_pets, care_time)
            if not result:
                st.warning("🚨 No matching plant found — try different preferences!")
            else:
                # unpack
                name = result["common"].split(",")[0]
                category = result.get("category", "N/A")
                origin = result.get("origin", "N/A")
                light_req = result.get("ideallight", "N/A")
                watering = result.get("watering", "N/A")
                # new temperature unpack (Celsius)
                tmin = result.get("tempmin.celsius", "N/A")
                tmax = result.get("tempmax.celsius", "N/A")
                temp_display = f"{tmin}°C – {tmax}°C"

                # build & display card
                card_html = f"""
<div style="
    background-color: #ffffff;
    border-left: 4px solid #2e7d32;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    font-family: Arial, sans-serif;
    color: #333333;
    max-width: 320px;
    margin: 0 auto;
">
  <h3 style="margin:0 0 8px; font-size:22px; color:#2e7d32; text-align:center;">
    🌱 {name}
  </h3>
  <p style="margin:0 0 16px; font-size:15px; text-align:center;">
    We found a plant that fits your space perfectly!
  </p>
  <div style="display:grid; grid-template-columns:1fr; gap:8px; font-size:14px;">
    <div>🌼 <strong>Category:</strong> {category}</div>
    <div>🌍 <strong>Origin:</strong> {origin}</div>
    <div>☀️ <strong>Light:</strong> {light_req}</div>
    <div>🌡️ <strong>Temperature:</strong> {temp_display}</div>
    <div>💧 <strong>Water:</strong> {watering}</div>
  </div>
  <p style="
      text-align:center;
      margin-top:16px;
      font-size:15px;
      font-weight:500;
      color:#2e7d32;
  ">
    🪴 Enjoy nurturing your new green companion!
  </p>
</div>
"""
                st.markdown(card_html, unsafe_allow_html=True)
