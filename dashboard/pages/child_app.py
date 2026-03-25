import streamlit as st
from model.text_analyzer import analyze_message
from database.db import init_db, save_message

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="SafetyNet – Child App",
    layout="centered"
)

# ----------------------------
# Title
# ----------------------------
st.title("Child App (Test Simulator)")
st.caption("Simulates a child sending messages. The SafetyNet system analyses risk levels.")

# ----------------------------
# Initialize database
# ----------------------------
init_db()

# ----------------------------
# Message input
# ----------------------------
msg = st.text_area(
    "Type a message (Arabic or English):",
    height=120,
    placeholder="Write a message..."
)

# ----------------------------
# Buttons
# ----------------------------
col1, col2 = st.columns(2)
send = col1.button("Send")
clear = col2.button("Clear")

if clear:
    st.rerun()

# ----------------------------
# Message processing
# ----------------------------
if send:
    text = msg.strip()

    if not text:
        st.warning("Please type a message first.")
    else:
        # Analyze message using NLP + keyword override
        result = analyze_message(text)

        # Save result to database
        save_message(result)
        st.caption(f"Saved risk: {result.get('risk')}")

        # ----------------------------
        # Professional Risk Display
        # ----------------------------
        risk = result.get("risk")

        if risk == "HIGH":
            st.error("🔴 HIGH RISK detected")
        elif risk == "MEDIUM":
            st.warning("🟠 MEDIUM RISK detected")
        else:
            st.success("🟢 LOW RISK detected")

        # ----------------------------
        # Show analysis mode
        # ----------------------------
        st.caption(f"Analysis mode: {result.get('mode')}")

        # ----------------------------
        # Developer / Viva Details
        # ----------------------------
        with st.expander("Technical details"):
            st.json(result)
