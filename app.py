import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# ===============================
# CONFIGURATION
# ===============================

st.set_page_config(
    page_title="Payment Default Risk System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Header Styling */
    h1 {
        color: #1e3a8a;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Card-like containers for metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #1e40af;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1e40af;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #1e3a8a;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

FINAL_THRESHOLD = 0.4

# ===============================
# LOAD MODEL
# ===============================

@st.cache_resource
def load_model():
    return joblib.load("payment_default_model.pkl")

model = load_model()

# ===============================
# SIDEBAR NAVIGATION & FORM
# ===============================

with st.sidebar:
    st.title("💳 Payment Risk")
    st.markdown("---")
    
    # Use a checkbox or radio for a "toggle" feel
    show_form = st.checkbox("📋 Client Information", value=False, help="Click to enter client details")
    
    if show_form:
        st.markdown("### Client Details")
        with st.form("sidebar_form"):
            name = st.text_input("Client Name", placeholder="e.g. Jane Smith")
            
            with st.expander("Demographics & Credit"):
                limit_bal = st.number_input("Credit Limit", min_value=0.0, value=20000.0)
                sex = st.selectbox("Sex", options=[1, 2], format_func=lambda x: "Male" if x==1 else "Female")
                education = st.selectbox("Education", options=[1, 2, 3, 4], format_func=lambda x: ["Grad School", "University", "High School", "Others"][x-1])
                marriage = st.selectbox("Marriage", options=[1, 2, 3], format_func=lambda x: ["Married", "Single", "Others"][x-1])
                age = st.number_input("Age", min_value=18, max_value=100, value=30)

            with st.expander("Payment Status"):
                p0 = st.number_input("Status Sept (PAY_0)", value=0, step=1)
                p2 = st.number_input("Status Aug (PAY_2)", value=0, step=1)
                p3 = st.number_input("Status July (PAY_3)", value=0, step=1)
                p4 = st.number_input("Status June (PAY_4)", value=0, step=1)
                p5 = st.number_input("Status May (PAY_5)", value=0, step=1)
                p6 = st.number_input("Status April (PAY_6)", value=0, step=1)

            with st.expander("Bill & Payment Amounts"):
                st.caption("Bill Amounts (BILL_AMT)")
                b1 = st.number_input("Bill Sept", value=0.0)
                b2 = st.number_input("Bill Aug", value=0.0)
                b3 = st.number_input("Bill July", value=0.0)
                b4 = st.number_input("Bill June", value=0.0)
                b5 = st.number_input("Bill May", value=0.0)
                b6 = st.number_input("Bill April", value=0.0)
                
                st.caption("Previous Payments (PAY_AMT)")
                am1 = st.number_input("Paid Sept", value=0.0)
                am2 = st.number_input("Paid Aug", value=0.0)
                am3 = st.number_input("Paid July", value=0.0)
                am4 = st.number_input("Paid June", value=0.0)
                am5 = st.number_input("Paid May", value=0.0)
                am6 = st.number_input("Paid April", value=0.0)

            submit = st.form_submit_button("Predict Risk")
            
        if submit:
            # Construct feature array with all 23 features in correct order
            features = np.array([[
                limit_bal, sex, education, marriage, age,
                p0, p2, p3, p4, p5, p6,
                b1, b2, b3, b4, b5, b6,
                am1, am2, am3, am4, am5, am6
            ]])
            
            probability = model.predict_proba(features)[0][1]
            
            # Store in session state to display in main area
            st.session_state.prediction = {
                "name": name,
                "prob": probability,
                "timestamp": datetime.now()
            }
            
            # Save to file
            risk = "High" if probability >= FINAL_THRESHOLD else ("Medium" if probability >= 0.3 else "Low")
            df_new = pd.DataFrame([{
                "Name": name,
                "Probability": probability,
                "Risk Level": risk,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            if os.path.exists("prediction_log.csv"):
                df_new.to_csv("prediction_log.csv", mode="a", header=False, index=False)
            else:
                df_new.to_csv("prediction_log.csv", index=False)

# ===============================
# MAIN AREA
# ===============================

# Display Prediction Result if available
if "prediction" in st.session_state:
    p = st.session_state.prediction
    prob = p["prob"]
    color = "red" if prob >= FINAL_THRESHOLD else ("orange" if prob >= 0.3 else "green")
    risk = "High" if prob >= FINAL_THRESHOLD else ("Medium" if prob >= 0.3 else "Low")
    
    st.success(f"Prediction for {p['name']} completed!")
    c1, c2, c3 = st.columns(3)
    c1.metric("Client", p['name'])
    c2.metric("Probability", f"{prob:.2%}")
    c3.markdown(f"### Risk: :{color}[{risk}]")
    st.markdown("---")

st.title("Payment Default Risk Overview")
st.markdown("Real-time monitoring of client credit risks.")


if os.path.exists("prediction_log.csv"):
    data = pd.read_csv("prediction_log.csv")

    # Top level metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Clients", len(data))
    m2.metric("High Risk", len(data[data["Risk Level"] == "High"]), delta_color="inverse")
    m3.metric("Medium Risk", len(data[data["Risk Level"] == "Medium"]), delta_color="off")
    m4.metric("Low Risk", len(data[data["Risk Level"] == "Low"]))

    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Risk Distribution")
        risk_counts = data["Risk Level"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]
        fig = px.pie(
            risk_counts,
            values="Count",
            names="Risk Level",
            hole=.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("Default Probabilities")
        fig2 = px.histogram(
            data,
            x="Probability",
            nbins=20,
            color_discrete_sequence=['#1e40af']
        )
        fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
    # Data Table
    st.subheader("Recent Assessments")
    st.dataframe(
        data.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    # Download Option
    st.download_button(
        label="📥 Download Detailed Report",
        data=data.to_csv(index=False),
        file_name=f"risk_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    st.info("No predictions have been made yet. Start by adding client information in the sidebar.")

