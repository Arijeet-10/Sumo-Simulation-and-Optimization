# AI-Driven Urban Traffic Management System

An intelligent traffic simulation and management system leveraging **Eclipse SUMO** and **Machine Learning** to optimize traffic flow in a simulated environment of Kolkata. The project demonstrates how dynamic AI control can drastically alleviate traffic gridlock during standard conditions and unexpected chaoses (such as sudden roadblocks or emergency vehicle dispatches).

## 📊 Overview

Traditional static traffic lights often fail to adapt to real-time road conditions. This project presents a dynamic, data-driven approach:
1. **Simulation**: Generates realistic baseline traffic data in Kolkata using Eclipse SUMO.
2. **Machine Learning**: Trains a Random Forest classifier on speed, vehicle count, and CO2 emission data to predict and identify congestion states.
3. **Chaos Management**: Injects random, disruptive events (stalled vehicles, speeding ambulances) into the simulation and uses the trained AI model to adjust traffic light phases dynamically to dissolve traffic jams and prioritize emergency vehicles.
4. **Data Visualization**: Compares the baseline (static) traffic flow with the ML-controlled flow, demonstrating enhanced speeds and reduced overall vehicles on the map.

## 🚀 Features

- **Baseline Intelligent Rerouting**: Dynamic vehicle rerouting based on travel time.
- **Congestion Prediction Model**: A lightweight Random Forest model trained on generated simulation data.
- **Real-Time Traffic Light Adjustment**: AI intervenes by extending green light durations when congestion is predicted.
- **Chaos Scenarios**: Built-in edge cases to stress-test the AI, including:
  - **Roadblocks**: A vehicle randomly breaking down for an extended period, creating an artificial chokepoint.
  - **Emergency Dispatch**: An ambulance with VIP routing requiring immediate clearance.
- **Data Analytics**: Comprehensive visual reports comparing speeds, vehicle count, and emissions.

## 📁 Repository Structure

- `simulation.py`: Runs the initial simulation to collect baseline traffic metrics and saves them to `traffic_data.csv`.
- `train_model.py`: Reads the collected dataset to train and serialize the Machine Learning model (`traffic_model.pkl`).
- `Simulation3_Chaos.py`: The advanced simulation script that loads the ML model, injects chaotic elements, and applies dynamic traffic control.
- `visualize_results.py`: A visualization suite using `seaborn` and `matplotlib` to compare the performance baseline against the AI-controlled outcomes.
- `kolkata.*`: The SUMO network, routing, and configuration files mapping the real-world topology of Kolkata.
- `build.bat`: A batch script to convert OpenStreetMap (OSM) data into a SUMO network file and generate random traffic routes.
- `requirements.txt`: Python dependencies required to run the project.

## 🛠️ Installation & Setup

1. **Install Python 3.8+**
2. **Install Eclipse SUMO**: Ensure `sumo` and `sumo-gui` are installed and available in your system's PATH. (Download: [Eclipse SUMO](https://eclipse.dev/sumo/))
3. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd path/to/project
   ```
4. **Install Python Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚗 Usage Workflow

To reproduce the full pipeline, execute the scripts in the following order:

0. **Network Preparation (First Time Only)**
   If you need to generate or regenerate the SUMO network and routes from raw `.osm` data:
   ```cmd
   build.bat
   ```
   *This executes SUMO's `netconvert` and `randomTrips.py` tools to create `kolkata.net.xml` and `kolkata.rou.xml`.*

1. **Generate Baseline Data**
   ```bash
   python simulation.py
   ```
   *This starts SUMO and logs standard traffic metrics to `traffic_data.csv`.*

2. **Train the AI Model**
   ```bash
   python train_model.py
   ```
   *This trains the Random Forest classifier and outputs `traffic_model.pkl`.*

3. **Run the AI-Controlled Chaos Simulation**
   *(Note: Ensure you log the output of this script to `ml_traffic_data.csv` if modifying, or run as is to view real-time SUMO adjustments.)*
   ```bash
   python Simulation3_Chaos.py
   ```
   *Watch as the AI detects roadblocks, clears a path for ambulances, and manages the localized congestion.*

4. **Visualize the Results**
   ```bash
   python visualize_results.py
   ```
   *Generates comparative graphs between the baseline run and the AI-controlled run.*

## 📈 Results

The visualization output (`Traffic_AI_Results.png`) typically highlights:
- A significant reduction in the **total number of vehicles** gridlocked on the map over time.
- A smoother, higher **average vehicle speed** across the network when the AI handles chaotic events dynamically.

---
*Built with ❤️ utilizing Eclipse SUMO and Python Machine Learning.*
