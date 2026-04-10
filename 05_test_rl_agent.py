import traci
import torch
import numpy as np
from rl_agent_core import TrafficAgent

# ==============================
# CONFIGURATION
# ==============================
STATE_SIZE = 2 
ACTION_SIZE = 2 
MODEL_PATH = "models/dqn_traffic_model_50.pth"

# ==============================
# HELPER: GET STATE
# ==============================
def get_state(tls_id):
    lanes = traci.trafficlight.getControlledLanes(tls_id)
    unique_lanes = list(dict.fromkeys(lanes)) 
    queues = [traci.lane.getLastStepHaltingNumber(l) for l in unique_lanes[:STATE_SIZE]]
    while len(queues) < STATE_SIZE:
        queues.append(0)
    return np.array(queues).reshape(1, STATE_SIZE)

# ==============================
# TEST EXECUTION
# ==============================
# 1. Initialize Agent and LOAD the trained brain
agent = TrafficAgent(STATE_SIZE, ACTION_SIZE)
# Set epsilon to 0 so the AI doesn't guess anymore—it only uses its brain
agent.epsilon = 0.0 

try:
    agent.model.load_state_dict(torch.load(MODEL_PATH))
    agent.model.eval() # Set to evaluation mode
    print(f"🧠 Trained RL Model {MODEL_PATH} Loaded!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# 2. Start SUMO GUI
sumo_cmd = ["sumo-gui", "-c", "sumo_network/kolkata.sumocfg", "--start"]
traci.start(sumo_cmd)

tls_id = traci.trafficlight.getIDList()[0]
step = 0

print("🚀 Running RL-Controlled Simulation... Watch the GUI!")

while step < 3600:
    traci.simulationStep()
    
    # AI looks at the lanes
    state = get_state(tls_id)
    
    # AI decides what to do
    action = agent.act(state)
    
    if action == 1:
        current_phase = traci.trafficlight.getPhase(tls_id)
        # Switch to the next logical phase
        traci.trafficlight.setPhase(tls_id, (current_phase + 1) % 4)
        print(f"Step {step}: AI decided to SWITCH phases!")

    step += 1

traci.close()
print("✅ Test Complete")