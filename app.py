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
    
    /* Hide the +/- buttons in st.number_input */
    div[data-testid="stNumberInputStepUp"], 
    div[data-testid="stNumberInputStepDown"],
    .stNumberInput button {
        display: none !important;
    }
    
    /* Additional targeting for different Streamlit versions */
    [data-testid="stSidebar"] .stNumberInput {
        margin-bottom: -15px;
    }
    [data-testid="stSidebar"] label {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #64748b !important;
    }
    
    /* Make tabs in sidebar more compact */
    [data-testid="stSidebar"] [data-testid="stTab"] {
        padding: 5px 10px;
    }
    
    /* Hide Developer Menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    
    st.markdown("### Client Details")
    with st.form("sidebar_form"):
        name = st.text_input("Client Name", placeholder="Enter name")
        
        tab1, tab2, tab3 = st.tabs(["Info", "Billing", "Payments"])
        
        with tab1:
            limit_bal = st.number_input("Credit Limit", min_value=0, value=None)
            sex = st.selectbox("Sex", options=[1, 2], format_func=lambda x: "Male" if x==1 else "Female")
            education = st.selectbox("Education", options=[1, 2, 3, 4], format_func=lambda x: ["Grad School", "University", "High School", "Others"][x-1])
            marriage = st.selectbox("Marriage", options=[1, 2, 3], format_func=lambda x: ["Married", "Single", "Others"][x-1])
            age = st.number_input("Age", min_value=0, max_value=100, value=None)

        with tab2:
            st.caption("Statement Amounts")
            for month, var_name in [("Sept", "b1"), ("Aug", "b2"), ("July", "b3"), ("June", "b4"), ("May", "b5"), ("April", "b6")]:
                col1, col2 = st.columns([1, 2])
                col1.markdown(f"<p style='margin-top:25px;'>{month}</p>", unsafe_allow_html=True)
                if var_name == "b1": b1 = col2.number_input(f"Bill {month}", value=None, label_visibility="collapsed")
                elif var_name == "b2": b2 = col2.number_input(f"Bill {month}", value=None, label_visibility="collapsed")
                elif var_name == "b3": b3 = col2.number_input(f"Bill {month}", value=None, label_visibility="collapsed")
                elif var_name == "b4": b4 = col2.number_input(f"Bill {month}", value=None, label_visibility="collapsed")
                elif var_name == "b5": b5 = col2.number_input(f"Bill {month}", value=None, label_visibility="collapsed")
                elif var_name == "b6": b6 = col2.number_input(f"Bill {month}", value=None, label_visibility="collapsed")

        with tab3:
            st.caption("Status & Payments")
            # Header row
            h1, h2, h3 = st.columns([1, 1.5, 1.5])
            h2.markdown("<p style='font-size:10px; font-weight:bold; margin-bottom:0;'>STATUS</p>", unsafe_allow_html=True)
            h3.markdown("<p style='font-size:10px; font-weight:bold; margin-bottom:0;'>PAID</p>", unsafe_allow_html=True)
            
            # Rows for each month
            data_rows = [
                ("Sept", "p0", "am1"), ("Aug", "p2", "am2"), ("July", "p3", "am3"),
                ("June", "p4", "am4"), ("May", "p5", "am5"), ("April", "p6", "am6")
            ]
            
            for month, status_var, amt_var in data_rows:
                c1, c2, c3 = st.columns([1, 1.5, 1.5])
                c1.markdown(f"<p style='margin-top:5px; font-size:0.9rem;'>{month}</p>", unsafe_allow_html=True)
                
                if status_var == "p0": p0 = c2.number_input(f"S{month}", value=None, label_visibility="collapsed")
                elif status_var == "p2": p2 = c2.number_input(f"S{month}", value=None, label_visibility="collapsed")
                elif status_var == "p3": p3 = c2.number_input(f"S{month}", value=None, label_visibility="collapsed")
                elif status_var == "p4": p4 = c2.number_input(f"S{month}", value=None, label_visibility="collapsed")
                elif status_var == "p5": p5 = c2.number_input(f"S{month}", value=None, label_visibility="collapsed")
                elif status_var == "p6": p6 = c2.number_input(f"S{month}", value=None, label_visibility="collapsed")
                
                if amt_var == "am1": am1 = c3.number_input(f"P{month}", value=None, label_visibility="collapsed")
                elif amt_var == "am2": am2 = c3.number_input(f"P{month}", value=None, label_visibility="collapsed")
                elif amt_var == "am3": am3 = c3.number_input(f"P{month}", value=None, label_visibility="collapsed")
                elif amt_var == "am4": am4 = c3.number_input(f"P{month}", value=None, label_visibility="collapsed")
                elif amt_var == "am5": am5 = c3.number_input(f"P{month}", value=None, label_visibility="collapsed")
                elif amt_var == "am6": am6 = c3.number_input(f"P{month}", value=None, label_visibility="collapsed")

        st.markdown("---")
        submit = st.form_submit_button("Predict Risk")
        
    if submit:
        if not name or name.strip() == "":
            st.error("Client Name is required!")
        else:
            # Handle possible None values (treat as 0)
            def nz(x): return x if x is not None else 0
            
            iv = [nz(limit_bal), sex, education, marriage, nz(age)]
            pv = [nz(p0), nz(p2), nz(p3), nz(p4), nz(p5), nz(p6)]
            bv = [nz(b1), nz(b2), nz(b3), nz(b4), nz(b5), nz(b6)]
            av = [nz(am1), nz(am2), nz(am3), nz(am4), nz(am5), nz(am6)]
            
            # Construct feature array
            features = np.array([iv + pv + bv + av])
            
            probability = model.predict_proba(features)[0][1]
            
            # Store in session state
            st.session_state.prediction = {
                "name": name,
                "prob": probability,
                "timestamp": datetime.now(),
                "bills": bv[::-1],
                "payments": av[::-1]
            }
            
            # Save to file (Split Date & Time for better Excel visibility)
            now = datetime.now()
            risk = "High" if probability >= FINAL_THRESHOLD else ("Medium" if probability >= 0.3 else "Low")
            df_new = pd.DataFrame([{
                "Date": now.strftime("%d-%m-%Y"),
                "Time": now.strftime("%H:%M"),
                "Name": name,
                "Probability": round(probability, 4),
                "Risk Level": risk
            }])
            
            if os.path.exists("prediction_log.csv"):
                df_existing = pd.read_csv("prediction_log.csv")
                # Normalize old columns to new split format
                if "Assessment Date" in df_existing.columns:
                    df_existing.rename(columns={"Assessment Date": "Date"}, inplace=True)
                
                # If Date contains time (legacy format), split it
                if "Time" not in df_existing.columns and "Date" in df_existing.columns:
                    # Attempt to split "YYYY-MM-DD HH:MM:SS"
                    try:
                        temp_dates = pd.to_datetime(df_existing["Date"], errors='coerce')
                        df_existing["Date"] = temp_dates.dt.strftime("%d-%m-%Y")
                        df_existing["Time"] = temp_dates.dt.strftime("%H:%M")
                    except:
                        df_existing["Time"] = "00:00"
                
                df_combined = pd.concat([df_new, df_existing], ignore_index=True)
                # Ensure cleaner column order
                cols = ["Date", "Time", "Name", "Probability", "Risk Level"]
                cols = [c for c in cols if c in df_combined.columns]
                df_combined[cols].to_csv("prediction_log.csv", index=False)
            else:
                df_new.to_csv("prediction_log.csv", index=False)

# ===============================
# MAIN AREA
# ===============================

# Display Prediction Results
if "prediction" in st.session_state:
    p = st.session_state.prediction
    prob = p["prob"]
    color = "red" if prob >= FINAL_THRESHOLD else ("orange" if prob >= 0.3 else "green")
    risk = "High" if prob >= FINAL_THRESHOLD else ("Medium" if prob >= 0.3 else "Low")
    
    st.success(f"Prediction for {p['name']} completed!")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Client", p['name'])
    c2.metric("Probability", f"{prob:.2%}")
    c3.metric("Assessment Date", p['timestamp'].strftime("%Y-%m-%d"), help=p['timestamp'].strftime("%H:%M:%S"))
    c4.markdown(f"### Risk: :{color}[{risk}]")
        
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
    
    #bar chart to show the risk level of the clients
    with chart_col1:
      st.subheader("Risk Distribution")
      risk_counts = data["Risk Level"].value_counts()
      st.bar_chart(risk_counts, color="#1e40af")
    
    #bar chart to show the key features used to predict deafulters and non-defaulters
    with chart_col2:
        st.subheader("Key Risk Drivers")
        try:
            importance = model.feature_importances_
            feature_names = [
                'Limit Bal', 'Sex', 'Edu', 'Marry', 'Age',
                'Status Sept', 'Status Aug', 'Status July', 'Status June', 'Status May', 'Status April',
                'Bill Sept', 'Bill Aug', 'Bill July', 'Bill June', 'Bill May', 'Bill April',
                'Paid Sept', 'Paid Aug', 'Paid July', 'Paid June', 'Paid May', 'Paid April'
            ]
            imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importance})
            imp_df = imp_df.sort_values("Importance", ascending=False).head(10)
            st.bar_chart(imp_df.set_index("Feature"), color="#ef4444")
        except AttributeError:
            st.info("Feature importance data not available for this model type.")

    st.markdown("---")
    
    # Data Table
    st.subheader("Recent Assessments")
    
    # Sort and Reorder for Download/Display
    # Handle legacy 'Date' (which might be datetime string) or 'Assessment Date'
    if "Assessment Date" in data.columns:
        data.rename(columns={"Assessment Date": "Date"}, inplace=True)
    
    data = data.sort_values("Date", ascending=False)
    
    # Ensure Date and Time are the FIRST columns
    all_cols = data.columns.tolist()
    pref_order = ["Date", "Time", "Name", "Probability", "Risk Level"]
    cols = [c for c in pref_order if c in all_cols] + [c for c in all_cols if c not in pref_order]
    data = data[cols]

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.TextColumn("Date", width="small"),
            "Time": st.column_config.TextColumn("Time", width="small"),
            "Name": st.column_config.TextColumn("Client", width="medium"),
            "Probability": st.column_config.NumberColumn("Probability", format="%.2f"),
            "Risk Level": st.column_config.TextColumn("Risk Level")
        }
    )

    # Download Option
    st.download_button(
        label="📥 Download Assessment Log (Excel/CSV)",
        data=data.to_csv(index=False),
        file_name=f"payment_risk_log_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    st.info("No predictions have been made yet. Start by adding client information in the sidebar.")

