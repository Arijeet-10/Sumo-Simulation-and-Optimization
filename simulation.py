import traci
import numpy as np
import pandas as pd

# ==============================
# START SUMO
# ==============================
# Added "--start" so the simulation begins automatically
sumo_cmd = ["sumo-gui", "-c", "kolkata.sumocfg", "--start"]

try:
    traci.start(sumo_cmd)
    print("🚀 Simulation started...")
except Exception as e:
    print("❌ Error starting SUMO:", e)
    exit()

# ==============================
# OPTIMIZED TRAFFIC CONTROL 🔥
# ==============================
def control_traffic_lights_optimized():
    for tls in traci.trafficlight.getIDList():
        # Get the actual string of lights (e.g., "GGggrrrr")
        current_state = traci.trafficlight.getRedYellowGreenState(tls)
        
        lanes = traci.trafficlight.getControlledLanes(tls)
        tls_vehicle_count = 0
        speeds = []
        
        for lane in lanes:
            tls_vehicle_count += traci.lane.getLastStepVehicleNumber(lane)
            speeds.append(traci.lane.getLastStepMeanSpeed(lane))
            
        avg_speed = np.mean(speeds) if speeds else 0
        
        # ONLY extend the phase if the light is currently GREEN ('G' or 'g')
        if 'G' in current_state or 'g' in current_state:
            if tls_vehicle_count > 10 and avg_speed < 3.0: 
                # Give them more time to clear the jam
                traci.trafficlight.setPhaseDuration(tls, 45)
            else:
                # Normal flow
                pass # Let SUMO handle the default duration
# ==============================
# DATA STORAGE
# ==============================
data_log = []

# ==============================
# SIMULATION LOOP
# ==============================
step = 0

while step < 3600:
    traci.simulationStep()

    # 1. Dynamic Rerouting (Check every 10 steps to save CPU)
    if step % 10 == 0:
        for vid in traci.vehicle.getIDList():
            try:
                traci.vehicle.rerouteTraveltime(vid, True)
            except traci.exceptions.TraCIException:
                pass # Ignore if vehicle has already reached its destination

    # 2. Apply Localized Traffic Control
    control_traffic_lights_optimized()

    # 3. Global Data Collection (For your CSV)
    vehicle_ids = traci.vehicle.getIDList()
    vehicle_count = len(vehicle_ids)

    if vehicle_count > 0:
        # List comprehensions are slightly faster than for-loops here!
        speeds = [traci.vehicle.getSpeed(vid) for vid in vehicle_ids]
        co2s = [traci.vehicle.getCO2Emission(vid) for vid in vehicle_ids]

        avg_speed = np.mean(speeds)
        avg_co2 = np.mean(co2s)
    else:
        avg_speed = 0
        avg_co2 = 0

    # Global congestion flag (just for your CSV logging purposes)
    if avg_speed < 4.0 and vehicle_count > 50:
        congestion = 1
    else:
        congestion = 0

    # ==============================
    # SAVE DATA
    # ==============================
    data_log.append({
        "step": step,
        "vehicle_count": vehicle_count,
        "speed": avg_speed,
        "co2_emission": avg_co2,
        "congestion": congestion
    })

    # ==============================
    # PRINT (Cleaned up)
    # ==============================
    # Print every 100 steps so the terminal doesn't lag the simulation
    if step % 100 == 0:
        print(f"Step: {step} | Vehicles: {vehicle_count} | Speed: {avg_speed:.2f} | CO2: {avg_co2:.2f} | Congestion: {congestion}")

    step += 1

# ==============================
# SAVE CSV
# ==============================
df = pd.DataFrame(data_log)
df.to_csv("traffic_data.csv", index=False)

print("📁 Data saved to traffic_data.csv")

# ==============================
# CLOSE
# ==============================
traci.close()
print("✅ Simulation ended")