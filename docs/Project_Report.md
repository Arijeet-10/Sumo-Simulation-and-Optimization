# Project Report: AI-Driven Urban Traffic Management System

**Date:** April 2026  
**Subject:** Traffic Simulation, Machine Learning, and Edge Case (Chaos) Management

---

## 1. Executive Summary
The rapid growth of urban environments has severely strained existing static traffic management infrastructure. The "AI-Driven Urban Traffic Management System" addresses this challenge by utilizing a simulation-first approach to model, analyze, and optimize traffic flow dynamically. By employing **Eclipse SUMO** to simulate traffic across Kolkata's road network, integrating a **Random Forest Machine Learning Model**, and a secondary **Deep Reinforcement Learning (DQN)** agent, this project successfully tests scenarios where intelligent localized traffic lights predict congestion, mitigate gridlocks dynamically, and optimize phase switching entirely autonomously via trial and error.

## 2. Objectives
- **Baseline Metric Generation:** Run a standard SUMO simulation representing typical urban traffic to establish performance baselines.
- **Congestion Prediction:** Train a robust Machine Learning algorithm on simulation logs (speed, CO2 emissions, vehicle count) to categorize congestion levels accurately.
- **Dynamic Mitigation Engine (Chaos Management):** Develop a custom control loop using SUMO's TraCI API that actively interfaces with the ML model to alter traffic light phases in real time during irregular occurrences, such as random roadblocks or high-priority ambulance routing.
- **Deep Reinforcement Learning (RL):** Implement a PyTorch-based Deep Q-Network capable of natively analyzing intersection queues and progressively learning the optimal traffic light phase switches over multiple simulated episodes.
- **Performance Evaluation:** Provide a comparative analytical visualization of standard dynamic rerouting vs. Machine Learning-driven dynamic signal control.

## 3. Methodology and Architecture

The architecture consists of four distinct phases functioning in a continuous pipeline:

### 3.1. Phase 1: Baseline Simulation (`01_baseline_simulation.py`)
This phase runs Kolkata's topology via standard SUMO configurations (`kolkata.sumocfg`, `kolkata.net.xml`, `kolkata.rou.xml`). It injects vehicles and logs granular data per simulation step:
- **Metrics Collected:** Step count, vehicle volume, average network speed, CO2 emissions.
- **Congestion Threshold:** The script tags a congestion flag (`1` or `0`) based on thresholds of speed (`< 4.0 m/s`) and volume (`> 50 vehicles`).
- **Output:** Saves logs in `traffic_data.csv`.

### 3.2. Phase 2: Model Training (`02_train_rf_model.py`)
The generated CSV serves as the dataset for an external predictive model.
- **Algorithm Used:** `RandomForestClassifier` from Scikit-Learn.
- **Features:** `speed`, `co2_emission`, `vehicle_count`.
- **Target:** `congestion` boolean.
- **Serialization:** Saves a trained model object to `traffic_model.pkl` to decouple heavy ML training from the real-time simulation loop.

### 3.3. Phase 3: Chaos and Control Simulation (`03_run_chaos_simulation.py`)
The crux of the system, this script initializes a higher-stress simulation environment to rigorously test the trained AI model.
- **Core Loop:** The script interfaces continuously with the running SUMO simulation utilizing `traci`.
- **Inference Integration:** Connects with the `traffic_model.pkl` model to predict map-wide congestion states per timeframe. If predicted, localized traffic lights receive a dynamic extended green-phase override to flush dense vehicle clusters.
- **Edge Components (Chaos):**
  - **The Roadblock:** At `Step 1000`, a random vehicle breaks down, halting for a predefined duration. It is visually painted orange, mimicking a severe infrastructural choke.
  - **The Ambulance (Emergency):** At `Step 2000`, an ambulance spawns, colored red. The simulation alters the vehicle class, forcing ambient traffic to yield, while the AI prioritizes signal clearing.

### 3.4. Phase 4: Analytical Visualization (`06_generate_visualizations.py`)
Provides quantifiable metrics comparing baseline system results against AI optimization.
- **Tooling:** Visuals constructed via `pandas`, `matplotlib`, and `seaborn`.
- **Evaluated Constraints:** Focuses fundamentally on Total Map Vehicle saturation and Average Speed.

### 3.5. Phase 5: Deep Reinforcement Learning (DQN) Approach
Moving beyond static ML prediction, this entirely separated module (`rl_agent_core.py`) introduces true autonomy to intersection control via PyTorch.
- **State Definition**: The agent receives live queue matrices indicating how many vehicles are halting across given axis lanes. 
- **Reward Function**: The agent measures the global negative sum of halting cars. Its optimization goal is to maximize this reward (bring halts as close to 0 as possible).
- **Learning Loop (`04_train_rl_agent.py`)**: The agent controls SUMO across 50 individual episodes (running headless), shifting its action profile from epsilon-based random exploration to learned neural exploitation.
- **Deployment (`05_test_rl_agent.py`)**: Utilizes the saved `.pth` checkpoint on a GUI-enabled simulation to observe the network's final logical phase switches.

## 4. Results and Outcomes

From empirical observations detailed in the comparative charts:
1. **Vehicle Retention:** The baseline simulation demonstrates rapid congestion build-up, trapping vehicles inside the simulation grid. The ML-controlled model actively flushes vehicles through intersections, showing heavily reduced overall vehicles lingering on the network.
2. **Average Speed Maintenance:** The ML-controlled method consistently upholds a higher average speed network-wide, indicating that the intelligent traffic light durations successfully compensate for sudden congestions caused by the induced "Chaos events".

## 5. Conclusion
Integrating an underlying ML model with real-time signal processing in a simulation environment yields a vastly superior traffic flow model compared to rigid timing approaches. The ability for the traffic grid to react to unforeseen "chaotic" impediments dynamically verifies the value of predictive models in future smart city infrastructural upgrades.

## 6. Future Enhancements
- Expand the ML model features to ingest individualized intersection density parameters instead of aggregate global averages.
- Support real-world sensor API streaming (e.g., live municipal camera grids) into the model.

---
**Prepared By:** AI Systems Simulation Team
