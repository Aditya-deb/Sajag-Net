import pandas as pd
from sajagnet.risk_engine import calculate_risk, ASSET_REGISTRY
from sajagnet.mitre_mapper import get_mitre_info

def build_incidents(stream_df):
    threats_df = stream_df[stream_df['Predicted_Class'] != 'Benign'].copy()
    if threats_df.empty:
        return pd.DataFrame()
        
    def map_grouping_asset(port):
        port_str = str(int(port))
        if port_str in ASSET_REGISTRY:
            return ASSET_REGISTRY[port_str]["server_type"]
        return "General Endpoint (various ports)"
        
    threats_df['Grouping_Asset'] = threats_df['Destination_Port'].apply(map_grouping_asset)
    
    incidents = []
    for threat_class in threats_df['Predicted_Class'].unique():
        class_df = threats_df[threats_df['Predicted_Class'] == threat_class]
        
        if threat_class == "PortScan":
            groups = [(threat_class, "General Endpoint (various ports)", class_df)]
        else:
            groups = [(threat_class, asset, group) for asset, group in class_df.groupby('Grouping_Asset')]
            
        for t_class, asset_name, group_df in groups:
            flow_count = len(group_df)
            highest_conf = group_df['Confidence'].max()
            example_port = group_df['Destination_Port'].iloc[0]
            
            engine_out = calculate_risk(t_class, highest_conf, example_port)
            intel = get_mitre_info(t_class)
            
            incidents.append({
                "Threat Class": t_class,
                "Target Asset": asset_name,
                "Flow Count": flow_count,
                "MITRE ID": intel["id"],
                "Risk Score": f"{engine_out['risk_score']}/100",
                "Exposure": engine_out['expected_financial_exposure_usd'],
                "Recommended Action": engine_out['recommended_action'],
                "Mitigation": intel["mitigation"]
            })
            
    return pd.DataFrame(incidents)
