import traci
import numpy as np
import pandas as pd
import joblib
import os
import warnings

ml_data_log = []

# Suppress warnings from pandas about feature names
warnings.filterwarnings("ignore", category=UserWarning)

# ==============================
# 1. LOAD ML MODEL
# ==============================
model = None
if os.path.exists("traffic_model.pkl"):
    model = joblib.load("traffic_model.pkl")
    print("🧠 ML Model Loaded Successfully!")
else:
    print("⚠️ Model not found! Please run train_model.py first.")
    exit()

# ==============================
# 2. START SUMO
# ==============================
# Added auto-start and teleporting for deadlocks
sumo_cmd = ["sumo-gui", "-c", "kolkata.sumocfg", "--start", "--time-to-teleport", "60"]

try:
    traci.start(sumo_cmd)
    print("🚀 ML-Powered Simulation started...")
except Exception as e:
    print("❌ Error starting SUMO:", e)
    exit()

# ==============================
# 3. PREDICTION FUNCTION
# ==============================
def predict_congestion(speed, co2, vehicle_count):
    if model is None:
        return 0

    # Ensure column names match EXACTLY what was trained in train_model.py
    df = pd.DataFrame([{
        "speed": speed,
        "co2_emission": co2,
        "vehicle_count": vehicle_count
    }])

    return model.predict(df)[0]

# ==============================
# 4. SMART TRAFFIC CONTROL
# ==============================
def control_traffic_lights(congestion_prediction):
    for tls in traci.trafficlight.getIDList():
        current_state = traci.trafficlight.getRedYellowGreenState(tls)
        
        # If the ML model says it's congested, ONLY extend lights that are currently GREEN
        if congestion_prediction == 1:
            if 'G' in current_state or 'g' in current_state:
                traci.trafficlight.setPhaseDuration(tls, 45) # Give them more time
        else:
            # If no congestion, let SUMO run its normal traffic light schedule
            pass 

# ==============================
# 5. SIMULATION LOOP
# ==============================
step = 0

while step < 3600:
    traci.simulationStep()

    # Dynamic Rerouting to avoid jams (every 10 steps)
    if step % 10 == 0:
        for vid in traci.vehicle.getIDList():
            try:
                traci.vehicle.rerouteTraveltime(vid, True)
            except traci.exceptions.TraCIException:
                pass

    # Gather Global Data for the ML Model
    vehicle_ids = traci.vehicle.getIDList()
    vehicle_count = len(vehicle_ids)

    if vehicle_count > 0:
        speeds = [traci.vehicle.getSpeed(vid) for vid in vehicle_ids]
        co2s = [traci.vehicle.getCO2Emission(vid) for vid in vehicle_ids]

        avg_speed = np.mean(speeds)
        avg_co2 = np.mean(co2s)
    else:
        avg_speed = 0
        avg_co2 = 0

    # Ask the ML model to predict congestion
    congestion = predict_congestion(avg_speed, avg_co2, vehicle_count)

    # Control traffic lights based on the AI's decision
    control_traffic_lights(congestion)
    ml_data_log.append({
        "step": step,
        "vehicle_count": vehicle_count,
        "speed": avg_speed,
        "co2_emission": avg_co2
    })

    # Print out what the AI is thinking every 100 steps
    if step % 100 == 0:
        status = "🔴 CONGESTED (AI Extending Greens)" if congestion == 1 else "🟢 FLOWING (Normal Lights)"
        print(f"Step: {step} | Vehicles: {vehicle_count} | Speed: {avg_speed:.2f} | AI Status: {status}")

    step += 1

df_ml = pd.DataFrame(ml_data_log)
df_ml.to_csv("ml_traffic_data.csv", index=False)
print("📁 AI run data saved to ml_traffic_data.csv")

# ==============================
# CLOSE
# ==============================
traci.close()
print("✅ ML Simulation ended")