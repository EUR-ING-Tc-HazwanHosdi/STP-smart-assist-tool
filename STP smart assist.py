import streamlit as st
import cv2
import numpy as np
from PIL import Image
import datetime

# ----------------------------
# IMAGE ANALYSIS FUNCTION
# ----------------------------
def extract_features(pil_image):
    image = np.array(pil_image)
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Foam detection (white areas)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 50, 255])
    foam_mask = cv2.inRange(hsv, lower_white, upper_white)
    foam_ratio = np.sum(foam_mask > 0) / foam_mask.size

    # Dark sludge detection
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    dark_ratio = np.sum(gray < 50) / gray.size

    # Clarity estimation
    clarity = np.var(gray) / 1000

    return {
        "foam": foam_ratio,
        "dark_sludge": dark_ratio,
        "clarity": clarity
    }

# ----------------------------
# DECISION ENGINE
# ----------------------------
def analyze_condition(features, odor_score):

    score = (
        features["foam"] * 0.5 +
        features["dark_sludge"] * 0.3 +
        odor_score * 0.2
    )

    if features["foam"] > 0.35:
        return {
            "issue": "Excess Foam",
            "cause": "Filamentous bacteria or surfactants",
            "action": "Reduce aeration, check F/M ratio, inspect influent source",
            "confidence": f"{round(score*100)}%"
        }

    elif features["dark_sludge"] > 0.4:
        return {
            "issue": "Septic Sludge",
            "cause": "Low dissolved oxygen (DO)",
            "action": "Increase aeration immediately and monitor DO levels",
            "confidence": f"{round(score*100)}%"
        }

    elif features["clarity"] > 0.6:
        return {
            "issue": "Good Condition",
            "cause": "System operating normally",
            "action": "Continue routine monitoring",
            "confidence": f"{round(score*100)}%"
        }

    else:
        return {
            "issue": "Uncertain Condition",
            "cause": "Mixed indicators detected",
            "action": "Perform manual inspection and lab testing (BOD/COD/MLSS)",
            "confidence": f"{round(score*100)}%"
        }

# ----------------------------
# STREAMLIT UI
# ----------------------------
st.set_page_config(page_title="STP Smart Assist", layout="centered")

st.title("STP Smart Assist")
st.caption("AI-assisted inspection tool for sewerage treatment plants")

st.warning(
    "This tool provides preliminary visual assessment only. "
    "Not a substitute for laboratory or certified measurements."
)

uploaded_file = st.file_uploader("Upload STP Image", type=["jpg", "png", "jpeg"])

odor = st.selectbox("Odor Condition", ["Normal", "Strong"])
manual_foam = st.selectbox("Foam Level (Optional Override)", ["Auto", "Low", "High"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    features = extract_features(image)

    # Manual override
    if manual_foam == "High":
        features["foam"] = 0.8
    elif manual_foam == "Low":
        features["foam"] = 0.1

    odor_score = 0.7 if odor == "Strong" else 0.2

    result = analyze_condition(features, odor_score)

    st.subheader("Analysis Result")
    st.write("🛑 Issue:", result["issue"])
    st.write("📌 Cause:", result["cause"])
    st.write("✅ Recommended Action:", result["action"])
    st.write("📊 Confidence:", result["confidence"])

    st.caption(f"Analysis Time: {datetime.datetime.now()}")