import random
import time
import json
from datetime import datetime

FAKE_THREATS = {
    "SYN_FLOOD": "DDoS Attempt Detected",
    "SQL_META_CHAR": "Potential SQL Injection",
    "XSS_SCRIPT_TAG": "Cross-Site Scripting (XSS) Probe",
    "TOR_EXIT_NODE": "Suspicious Tor Traffic",
    "BEACONING": "Possible C2 Communication"
}

def generate_mock_traffic():
    print("[*] Listening to network traffic (Simulated)...")
    time.sleep(1)
    
    traffic_data = []
    for _ in range(random.randint(5, 15)):
        packet = {
            "src_ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "dst_port": random.choice([22, 80, 443, 8080, 3389, 445]),
            "payload_size": random.randint(100, 5000),
            "signature": random.choice(list(FAKE_THREATS.keys()) + ["NORMAL_TRAFFIC", "NORMAL_TRAFFIC", "NORMAL_TRAFFIC"])
        }
        traffic_data.append(packet)
    
    return traffic_data

def fake_ai_inference(packet):
    base_score = random.uniform(0, 100)
    
    if packet["signature"] != "NORMAL_TRAFFIC":
        base_score += 30
        
    return min(base_score, 99.9)

def analyze_traffic(traffic_data):
    print("\n[*] Running AI Inference Engine...")
    time.sleep(1.5)
    
    detected_anomalies = []
    
    for pkt in traffic_data:
        threat_score = fake_ai_inference(pkt)
        if threat_score > 75:
            anomaly = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": pkt["src_ip"],
                "port": pkt["dst_port"],
                "threat_score": round(threat_score, 2),
                "classification": FAKE_THREATS.get(pkt["signature"], "Unknown Anomaly")
            }
            detected_anomalies.append(anomaly)
            print(f"    🚨 [ALERT] High Threat Score from {anomaly['ip']} | Score: {anomaly['threat_score']} | {anomaly['classification']}")
        else:
            print(f"    [OK] Traffic from {pkt['src_ip']} seems benign. (Score: {round(threat_score, 2)})")
            
    return detected_anomalies

def update_threat_log(anomalies):
    with open("threat_intelligence.log", "a") as f:
        if not anomalies:
            f.write(f"{datetime.now()} | SYSTEM STATUS: NOMINAL. No threats detected.\n")
        else:
            for a in anomalies:
                f.write(f"{a['timestamp']} | ALERT | IP: {a['ip']} | Port: {a['port']} | Score: {a['threat_score']} | Desc: {a['classification']}\n")
    
    print("\n[*] Threat intelligence log updated successfully.")

if __name__ == "__main__":
    print("🧠 Initializing Fake AI Threat Detection Engine v2.0...")
    time.sleep(1)
    
    mock_data = generate_mock_traffic()
    anomalies = analyze_traffic(mock_data)
    
    update_threat_log(anomalies)
    print("[*] Simulation finished. Ready for Git Commit.")
