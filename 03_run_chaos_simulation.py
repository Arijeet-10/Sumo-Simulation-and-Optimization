import traci
import numpy as np
import pandas as pd
import joblib
import os
import warnings
import random

warnings.filterwarnings("ignore", category=UserWarning)

# ==============================
# 1. LOAD ML MODEL
# ==============================
model = None
if os.path.exists("models/traffic_model.pkl"):
    model = joblib.load("models/traffic_model.pkl")
    print("🧠 ML Model Loaded Successfully!")
else:
    print("⚠️ Model not found! Please run train_model.py first.")
    exit()

# ==============================
# 2. START SUMO (Increased Teleport Time for Roadblock!)
# ==============================
# We increased time-to-teleport to 120s so SUMO doesn't delete our broken car too early!
sumo_cmd = ["sumo-gui", "-c", "sumo_network/kolkata.sumocfg", "--start", "--time-to-teleport", "120"]

try:
    traci.start(sumo_cmd)
    print("🚀 CHAOS Simulation started...")
except Exception as e:
    print("❌ Error starting SUMO:", e)
    exit()

# ==============================
# 3. AI TRAFFIC CONTROL
# ==============================
def predict_congestion(speed, co2, vehicle_count):
    if model is None: return 0
    df = pd.DataFrame([{"speed": speed, "co2_emission": co2, "vehicle_count": vehicle_count}])
    return model.predict(df)[0]

def control_traffic_lights(congestion_prediction):
    for tls in traci.trafficlight.getIDList():
        current_state = traci.trafficlight.getRedYellowGreenState(tls)
        if congestion_prediction == 1:
            if 'G' in current_state or 'g' in current_state:
                traci.trafficlight.setPhaseDuration(tls, 45) 

# ==============================
# 4. CHAOS VARIABLES
# ==============================
stalled_car_id = None
stall_timer = 0
ambulance_id = None

# ==============================
# 5. SIMULATION LOOP
# ==============================
step = 0

while step < 3600:
    traci.simulationStep()
    vehicle_ids = traci.vehicle.getIDList()

    # -----------------------------------------
    # 🌪️ CHAOS EVENT 1: THE ROADBLOCK
    # -----------------------------------------
    if step == 1000 and len(vehicle_ids) > 0:
        stalled_car_id = random.choice(vehicle_ids)
        stall_timer = 45 # Stall for 45 steps
        traci.vehicle.setColor(stalled_car_id, (255, 165, 0)) # Paint it Orange
        print(f"\n⚠️ [STEP 1000] CHAOS EVENT: Vehicle {stalled_car_id} broke down! Roadblock initiated.\n")

    # Keep the car stopped if the timer is active
    if stalled_car_id and stall_timer > 0:
        try:
            traci.vehicle.setSpeed(stalled_car_id, 0)
            stall_timer -= 1
            if stall_timer == 0:
                traci.vehicle.setSpeed(stalled_car_id, -1) # -1 returns control to SUMO
                traci.vehicle.setColor(stalled_car_id, (255, 255, 255)) # Paint it back to white
                print(f"\n✅ [STEP {step}] Roadblock cleared! Vehicle {stalled_car_id} is moving again.\n")
                stalled_car_id = None
        except traci.exceptions.TraCIException:
            stalled_car_id = None # Car exited map early

    # -----------------------------------------
    # 🚑 CHAOS EVENT 2: THE AMBULANCE
    # -----------------------------------------
    if step == 2000 and len(vehicle_ids) > 0:
        ambulance_id = random.choice(vehicle_ids)
        traci.vehicle.setColor(ambulance_id, (255, 0, 0)) # Paint it Bright Red
        traci.vehicle.setSpeedFactor(ambulance_id, 2.0) # Let it speed
        
        # Tell SUMO this is a VIP Emergency Vehicle so other cars yield to it!
        traci.vehicle.setVehicleClass(ambulance_id, "emergency")
        
        print(f"\n🚑 [STEP 2000] CHAOS EVENT: Ambulance {ambulance_id} dispatched! Sirens ON!\n")

    # We just need to track when it finishes its route
    if ambulance_id:
        try:
            # If this doesn't throw an error, the ambulance is still on the map
            traci.vehicle.getSpeed(ambulance_id) 
        except traci.exceptions.TraCIException:
            print(f"\n🏁 [STEP {step}] Ambulance {ambulance_id} reached the hospital! (Exited map)\n")
            ambulance_id = None

    # -----------------------------------------
    # STANDARD AI OPERATIONS
    # -----------------------------------------
    if step % 10 == 0:
        for vid in vehicle_ids:
            try: traci.vehicle.rerouteTraveltime(vid, True)
            except: pass

    if len(vehicle_ids) > 0:
        speeds = [traci.vehicle.getSpeed(vid) for vid in vehicle_ids]
        co2s = [traci.vehicle.getCO2Emission(vid) for vid in vehicle_ids]
        avg_speed, avg_co2 = np.mean(speeds), np.mean(co2s)
    else:
        avg_speed, avg_co2 = 0, 0

    # Let the ML model handle the rest of the city
    congestion = predict_congestion(avg_speed, avg_co2, len(vehicle_ids))
    control_traffic_lights(congestion)

    # Clean terminal printing
    if step % 250 == 0:
        print(f"Step: {step} | Vehicles: {len(vehicle_ids)} | Avg Speed: {avg_speed:.2f} m/s")

    step += 1

traci.close()
print("✅ Chaos Simulation ended")