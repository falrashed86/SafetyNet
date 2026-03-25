import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from streamlit_autorefresh import st_autorefresh

from database.db import init_db, get_counts, get_recent_high

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="SafetyNet – Parent Dashboard", layout="wide")

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

# ----------------------------
# Styles
# ----------------------------
st.markdown(
    """
    <style>
    .block-container{
        padding-top: 1rem;
    }

    .sn-header{
        display:flex;
        align-items:center;
        gap:15px;
        background:linear-gradient(90deg,#e9f3ff,#f2ecff);
        padding:16px 18px;
        border-radius:14px;
        border:1px solid #e2e2e2;
        min-height: 90px;
    }

    .sn-title{
        font-size:24px;
        font-weight:700;
        line-height:1.2;
        margin-bottom:4px;
    }

    .sn-sub{
        font-size:14px;
        color:#666;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Header
# ----------------------------
c1, c2 = st.columns([1.2, 5.8], vertical_alignment="center")

with c1:
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH)
        st.image(logo, width=140)
    else:
        st.warning(f"Logo not found: {LOGO_PATH}")

with c2:
    st.markdown(
        """
        <div class="sn-header">
            <div>
                <div class="sn-title">SafetyNet – Parent Dashboard</div>
                <div class="sn-sub">AI-powered child safety monitoring system</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ----------------------------
# Auto refresh
# ----------------------------
st_autorefresh(interval=1500, key="sn_parent_refresh")

# ----------------------------
# Init DB
# ----------------------------
init_db()

# ----------------------------
# Reliable beep sound
# ----------------------------
def play_beep():
    components.html(
        """
        <script>
        const audio = new Audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg");
        audio.volume = 0.8;
        audio.play().catch(e => console.log("Audio blocked", e));
        </script>
        """,
        height=0,
    )

# ----------------------------
# Sound enable
# ----------------------------
if "sound_enabled" not in st.session_state:
    st.session_state["sound_enabled"] = False

s1, s2 = st.columns([1.2, 4.8], vertical_alignment="center")

with s1:
    if st.button("🔊 Enable sound"):
        st.session_state["sound_enabled"] = True
        st.success("Sound enabled")

with s2:
    st.caption("Click once to allow sound in the browser")

# ----------------------------
# Alert logic
# ----------------------------
total_now, high_now = get_counts()
now = time.time()

if "prev_high" not in st.session_state:
    st.session_state["prev_high"] = high_now

if "alert_until" not in st.session_state:
    st.session_state["alert_until"] = 0.0

if high_now > st.session_state["prev_high"]:
    st.session_state["prev_high"] = high_now
    st.session_state["alert_until"] = now + 8
    st.toast("New high-risk alert received", icon="⚠️")

    if st.session_state["sound_enabled"]:
        play_beep()

alert_box = st.empty()

if now < st.session_state["alert_until"]:
    with alert_box.container():
        st.error("⚠️ New HIGH-RISK alert detected")
        if st.button("Dismiss alert"):
            st.session_state["alert_until"] = 0.0
            st.rerun()

# ----------------------------
# Metrics
# ----------------------------
m1, m2 = st.columns(2)
m1.metric("Total messages analysed", total_now)
m2.metric("High-risk alerts", high_now)

st.divider()

# ----------------------------
# Alerts table
# ----------------------------
st.subheader("Recent high-risk alerts")

show_text = st.checkbox("Show message text (privacy off)", value=False)

rows = get_recent_high(limit=30)

table = []
for msg_id, mode, stars, confidence, risk, text in rows:
    table.append({
        "ID": msg_id,
        "Risk": risk,
        "Mode": mode,
        "Stars": stars,
        "Confidence": round(confidence, 3) if confidence is not None else None,
        "Message": text if show_text else "[Hidden for privacy]"
    })

st.dataframe(table, use_container_width=True)
st.caption("Message content hidden by default to protect child privacy.")
