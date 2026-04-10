import traci
import numpy as np
import torch
from rl_agent_core import TrafficAgent

# ==============================
# CONFIGURATION
# ==============================
# State: [Queue_North, Queue_South, Queue_East, Queue_West]
STATE_SIZE = 2 
# Actions: 0 = Stay, 1 = Switch Phase
ACTION_SIZE = 2 
EPISODES = 50 # How many times the AI "plays" the city
BATCH_SIZE = 32

# ==============================
# HELPER: GET INTERSECTION STATE
# ==============================
def get_state(tls_id):
    lanes = traci.trafficlight.getControlledLanes(tls_id)
    # Get unique lanes (sometimes SUMO lists the same lane twice for different directions)
    unique_lanes = list(dict.fromkeys(lanes)) 
    
    # Get halting cars for the number of lanes we defined in STATE_SIZE
    queues = [traci.lane.getLastStepHaltingNumber(l) for l in unique_lanes[:STATE_SIZE]]
    
    # Fill with zeros if for some reason we find fewer lanes than STATE_SIZE
    while len(queues) < STATE_SIZE:
        queues.append(0)
        
    state = np.array(queues)
    return state.reshape(1, STATE_SIZE)

# ==============================
# MAIN TRAINING LOOP
# ==============================
agent = TrafficAgent(STATE_SIZE, ACTION_SIZE)

for e in range(EPISODES):
    # Start SUMO in 'sumo' (cmd) mode for faster training, or 'sumo-gui' to watch
    sumo_cmd = ["sumo", "-c", "sumo_network/kolkata.sumocfg", "--start", "--quit-on-end"]
    traci.start(sumo_cmd)
    
    tls_id = traci.trafficlight.getIDList()[0] # Focus on one main intersection for training
    state = get_state(tls_id)
    total_reward = 0
    step = 0

    while step < 3600:
        traci.simulationStep()
        
        # 1. AI chooses an action
        action = agent.act(state)
        
        # 2. Apply the action
        if action == 1:
            # Switch to next phase
            current_phase = traci.trafficlight.getPhase(tls_id)
            traci.trafficlight.setPhase(tls_id, (current_phase + 1) % 4)
        
        # 3. Observe the result (The Reward)
        next_state = get_state(tls_id)
        # Reward = - (Total waiting cars). We want to MINIMIZE waiting, so we maximize negative reward.
        reward = -np.sum(next_state) 
        total_reward += reward
        
        # 4. Remember what happened
        done = (step == 3599)
        agent.remember(state, action, reward, next_state, done)
        
        state = next_state
        step += 1

        # 5. Train the brain on its memories
        if step % 10 == 0:
            agent.replay(BATCH_SIZE)

    print(f"Episode: {e+1}/{EPISODES} | Total Reward: {total_reward} | Epsilon: {agent.epsilon:.2f}")
    
    # Save the model every 10 episodes
    if (e + 1) % 10 == 0:
        torch.save(agent.model.state_dict(), f"models/dqn_traffic_model_{e+1}.pth")
        print("💾 Model Checkpoint Saved")

    traci.close()

print("✅ Training Complete!")