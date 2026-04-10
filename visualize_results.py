import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# 1. LOAD THE DATA
# ==============================
print("📊 Loading datasets...")
try:
    df_base = pd.read_csv("traffic_data.csv")
    df_ml = pd.read_csv("ml_traffic_data.csv")
except FileNotFoundError:
    print("❌ Error: Could not find the CSV files. Make sure both simulations have been run!")
    exit()

# Apply a beautiful Seaborn style
sns.set_theme(style="darkgrid")

# ==============================
# 2. SET UP THE GRAPH (2 Rows, 1 Column)
# ==============================
fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
fig.suptitle('AI Traffic Management: Before vs. After', fontsize=18, fontweight='bold')

# ==============================
# 3. PLOT 1: VEHICLE COUNT
# ==============================
axes[0].plot(df_base['step'], df_base['vehicle_count'], label='Baseline (No AI)', color='red', linewidth=2)
axes[0].plot(df_ml['step'], df_ml['vehicle_count'], label='ML Controlled', color='mediumseagreen', linewidth=2.5)

axes[0].set_title('Total Vehicles on Map (Lower is Better - Less Gridlock)', fontsize=14)
axes[0].set_ylabel('Number of Vehicles', fontsize=12)
axes[0].legend(fontsize=12)
axes[0].fill_between(df_base['step'], df_base['vehicle_count'], df_ml['vehicle_count'], color='red', alpha=0.1)

# ==============================
# 4. PLOT 2: AVERAGE SPEED
# ==============================
axes[1].plot(df_base['step'], df_base['speed'], label='Baseline (No AI)', color='red', linewidth=2)
axes[1].plot(df_ml['step'], df_ml['speed'], label='ML Controlled', color='mediumseagreen', linewidth=2.5)

axes[1].set_title('Average Vehicle Speed (Higher is Better - Smooth Flow)', fontsize=14)
axes[1].set_xlabel('Simulation Step (Time)', fontsize=12)
axes[1].set_ylabel('Speed (m/s)', fontsize=12)
axes[1].legend(fontsize=12)

# ==============================
# 5. SAVE AND DISPLAY
# ==============================
plt.tight_layout()
plt.subplots_adjust(top=0.92) # Make room for the main title

# Save the image to your folder
plt.savefig("Traffic_AI_Results.png", dpi=300)
print("✅ Graph saved successfully as 'Traffic_AI_Results.png'")

# Open the graph on your screen
plt.show()