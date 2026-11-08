import streamlit as st
import pandas as pd
import joblib
import json
import os
import shap
import matplotlib.pyplot as plt
import sys
sys.path.append(os.path.abspath("src"))
from sajagnet.risk_engine import calculate_risk, ASSET_REGISTRY
from sajagnet.incidents import build_incidents
from sajagnet.config import ASSUMED_TRIAGE_COST_PER_ALERT, ASSUMED_DOWNTIME_HOURS, ASSUMED_P_BREACH, RISK_WEIGHTS, MIN_CONFIDENCE_TO_BLOCK, MIN_CONFIDENCE_TO_INVESTIGATE

st.set_page_config(page_title="SajagNet: Network Threat Detection", layout="wide")

@st.cache_resource
def load_artifacts():
    model = joblib.load(os.path.join("models", "lgbm_model.pkl"))
    le = joblib.load(os.path.join("models", "label_encoder.pkl"))
    with open("models/feature_columns.json", "r") as f:
        feature_cols = json.load(f)
    try:
        with open(os.path.join("reports", "metrics.json"), "r") as f:
            metrics = json.load(f)
            fa_prim = metrics["LightGBM_No_Ports"]["false_alarms_per_100k"]
            fa_no = metrics["LightGBM_No_Ports_No_TCP"]["false_alarms_per_100k"]
    except Exception as e:
        st.error(f"Could not read reports/metrics.json: {e}")
        fa_prim, fa_no = float("nan"), float("nan")
    return model, le, feature_cols, fa_prim, fa_no

@st.cache_resource
def load_explainer(_model):
    return shap.TreeExplainer(_model)

def main():
    st.title("🛡️ SajagNet: Network Threat Detection")
    st.sidebar.header("Traffic Controls")
    if st.sidebar.button("Load Simulated Traffic Sample", type="primary"):
        st.session_state['simulating'] = True

    if st.session_state.get('simulating', False):
        model, le, feature_cols, fa_primary, fa_notcp = load_artifacts()
        explainer = load_explainer(model)
        stream_df = pd.read_csv(os.path.join("data", "sample_stream.csv"))
        X_predict = stream_df[feature_cols]
        raw_preds = model.predict(X_predict)
        predicted_classes = le.inverse_transform(raw_preds)
        confidence = model.predict_proba(X_predict).max(axis=1) if hasattr(model, "predict_proba") else [1.0] * len(raw_preds)
        
        tl_raw = stream_df['Label'].values
        true_labels = le.inverse_transform(tl_raw) if pd.api.types.is_numeric_dtype(tl_raw) else tl_raw
        
        display_df = pd.DataFrame({'Destination_Port': stream_df['Destination_Port'], 'True_Label': true_labels, 'Predicted_Class': predicted_classes, 'Model score': [f"{c*100:.4f}%" for c in confidence]})
        display_df['Correct?'] = display_df.apply(lambda r: '✓' if r['True_Label'] == r['Predicted_Class'] else 'X', axis=1)
        
        tab1, tab2 = st.tabs(["Simulated Stream & Explainability", "Business Risk & Incidents"])
        
        with tab1:
            st.subheader("SIMULATED Traffic Stream")
            st.dataframe(display_df, width="stretch")
            st.divider()
            st.subheader("Explain Prediction (SHAP)")
            sel_idx = st.selectbox("Select Flow Index", display_df.index)
            row_data = X_predict.iloc[[sel_idx]]
            pred_class_idx = int(raw_preds[sel_idx])
            shap_values = explainer.shap_values(row_data)
            shap_v = shap_values[pred_class_idx][0] if isinstance(shap_values, list) else (shap_values[0,:,pred_class_idx] if len(shap_values.shape)==3 else shap_values[0])
            contribs = pd.DataFrame({'feature': X_predict.columns, 'shap_val': shap_v})
            top8 = contribs.assign(abs=contribs['shap_val'].abs()).sort_values('abs', ascending=False).head(8).sort_values('shap_val')
            plt.style.use('dark_background'); fig, ax = plt.subplots(figsize=(8,4)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
            ax.barh(top8['feature'], top8['shap_val'], color=['#ff4b4b' if v>0 else '#0068c9' for v in top8['shap_val']])
            st.pyplot(fig)

        with tab2:
            st.subheader("Business Exposure & Incident Response")
            stream_df['Predicted_Class'] = predicted_classes
            stream_df['Confidence'] = confidence
            incidents_df = build_incidents(stream_df)
            
            if incidents_df.empty:
                st.success("No active threats detected.")
            else:
                incidents_df = incidents_df.sort_values(by="Exposure", ascending=False).reset_index(drop=True)
                total_exposure = incidents_df["Exposure"].sum()
                st.metric("Total estimated exposure for this 1,000-flow sample (illustrative)", f"${total_exposure:,.2f}")
                incidents_df['Exposure'] = incidents_df['Exposure'].apply(lambda x: f"${x:,.2f}")
                st.table(incidents_df)
                
            st.divider()
            st.subheader("Decision Explorer (Cost-Benefit Logic)")
            st.markdown("Adjust the model score to see how the engine dynamically shifts actions.")
            c1, c2, c3 = st.columns(3)
            with c1: tc = st.selectbox("Select Threat Class", ["DoS/DDoS", "PortScan", "Brute Force", "Web Attack"])
            with c2: tp = st.selectbox("Select Target Port", [80, 21, 22, 443])
            with c3: t_conf = st.slider("Model Score (Confidence)", 0.05, 1.00, 0.99, step=0.01)
            
            do = calculate_risk(tc, t_conf, tp)
            port_str = str(int(tp))
            ast = ASSET_REGISTRY.get(port_str, ASSET_REGISTRY["default"])
            b_cost = ast["assumed_cost_of_blocking_legit_traffic"]
            downtime_h = ASSUMED_DOWNTIME_HOURS.get(tc, 0.0)
            p_br = ASSUMED_P_BREACH.get(tc, 0.0)
            full_exp = (downtime_h * ast["assumed_hourly_downtime_cost"]) + (p_br * ast["assumed_breach_liability"])
            c_star = b_cost / (full_exp + b_cost) if (full_exp + b_cost) > 0 else 1.0
            
            st.info(f"**Risk Score:** {do['risk_score']}/100 | **Expected Exposure:** ${do['expected_financial_exposure_usd']:,.2f} | **Action:** {do['recommended_action']}")
            
            # The wording fix Claude demanded is right here:
            st.caption(f"Rule: Break-even score c* = {c_star:.2%}. Policy: Block if score >= 90% AND the cost rule holds; Investigate if score >= 50% AND the cost rule holds; otherwise Log & Alert.")
            
            st.divider()
            st.subheader("Primary model vs model without TCP-window features")
            c = ASSUMED_TRIAGE_COST_PER_ALERT
            st.table(pd.DataFrame({
                "Daily Benign Flows": ["100,000", "1,000,000", "10,000,000"],
                "Primary Alerts": [f"{fa_primary:,}", f"{fa_primary*10:,}", f"{fa_primary*100:,}"],
                "No-TCP Alerts": [f"{fa_notcp:,}", f"{fa_notcp*10:,}", f"{fa_notcp*100:,}"],
                f"Primary Cost (@${c:g})": [f"${fa_primary*c:,.0f}", f"${fa_primary*10*c:,.0f}", f"${fa_primary*100*c:,.0f}"],
                f"No-TCP Cost (@${c:g})": [f"${fa_notcp*c:,.0f}", f"${fa_notcp*10*c:,.0f}", f"${fa_notcp*100*c:,.0f}"]
            }))

if __name__ == "__main__":
    main()

