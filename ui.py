import streamlit as st
from PIL import Image
import requests
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(
    page_title="Smart Post Scheduler",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
    <style>
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 0.6em 1.2em;
            border-radius: 12px;
        }
        .stSelectbox, .stTextInput, .stDateInput, .stTimeInput {
            background-color: #f8f9fb !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title & Intro ---
st.title("📸 Smart Social Media Post Scheduler")
st.markdown("Upload an image and get the **best time and day** to post it for maximum engagement 🚀")

# --- Upload Section ---
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_image = st.file_uploader("Upload your image", type=["jpg", "jpeg", "png"])
with col2:
    platform = st.selectbox("Select Platform", ["LinkedIn", "Instagram", "Twitter"])
    company_name = st.text_input("Company Name", placeholder="e.g., Amazon")

# --- Date & Time Selection ---
st.markdown("---")
st.subheader("📆 Schedule Starting Date & Time")

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("Start From Date", value=datetime.today())
with col_time:
    selected_time = st.time_input("Start From Time", value=datetime.now().time())

start_datetime = datetime.combine(selected_date, selected_time)

st.markdown("---")

# --- Main Logic ---
if uploaded_image:
    st.image(uploaded_image, use_column_width=True, caption="Uploaded image preview")

    if st.button("🚀 Check virality and Score"):
        with st.spinner("Generating caption and analyzing..."):
            try:
                # --- API 1: Caption Generation ---
                files = {"image": uploaded_image}
                form_data = {"company_name": company_name.strip()}

                caption_response = requests.post(
                    "http://localhost:8000/generate-caption/",
                    files=files,
                    data=form_data
                )
                caption_response.raise_for_status()
                caption_result = caption_response.json().get("result", {})

                caption_text = caption_result.get("caption_and_hashtag", "No caption returned.")
                virality_reasons = caption_result.get("virality", "No virality explanation provided.")
                caption_score = caption_result.get("score", "N/A")

                # --- API 2: Time Prediction ---
                best_time = None
                best_day = None
                best_hour = None
                best_score = float("-inf")
                best_metrics = {}

                for day_offset in range(7):
                    for hour in range(9, 21, 2):  # 9 AM to 9 PM every 2 hrs
                        test_dt = start_datetime.replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=day_offset)
                        date_str = test_dt.strftime("%Y-%m-%d %H:%M:%S")

                        payload = {
                            "date_str": date_str,
                            "company_name": company_name.strip()
                        }

                        metric_response = requests.post("http://localhost:8200/predict_metrics/", json=payload)
                        metric_response.raise_for_status()
                        metric_data = metric_response.json()

                        score = sum(v for v in metric_data.values() if isinstance(v, (int, float)))

                        if score > best_score:
                            best_score = score
                            best_time = date_str
                            best_hour = test_dt.strftime("%I:%M %p")
                            best_day = test_dt.strftime("%A")
                            best_metrics = metric_data

                # --- Output Results ---
                #st.success(f"📆 Check virality and Score**{platform}**: **{best_day} at {best_hour}**")

                st.markdown("### ✨ Generated Caption & Hashtags")
                st.markdown(f"**💡 Score:** {caption_score}")
                st.info(caption_text)

                st.markdown("### 📈 Virality Analysis")
                st.warning(virality_reasons)

                st.markdown("### 📊 Predicted Engagement Metrics")
                st.table(best_metrics)

            except Exception as e:
                st.error("❌ Something went wrong. Try again.")
                st.code(str(e))
else:
    st.warning("📥 Please upload an image to continue.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size: 14px;'>Made with ❤️ by <b>SPBND</b> ✅</div>",
    unsafe_allow_html=True,
)