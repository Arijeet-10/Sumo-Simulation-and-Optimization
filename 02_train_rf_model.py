import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# 1. Load the data you just generated
print("📥 Loading traffic_data.csv...")
df = pd.read_csv("data/traffic_data.csv")

# 2. Define our Features (X) and Target (y)
# We want the model to look at these three things...
X = df[["speed", "co2_emission", "vehicle_count"]]
# ...to predict this one thing.
y = df["congestion"]

# 3. Split the data (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Create and Train the Model
print("🧠 Training Random Forest Model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Test the Model's Accuracy
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"🎯 Model Accuracy: {accuracy * 100:.2f}%")

# 6. Save the Model for your simulation to use
joblib.dump(model, "models/traffic_model.pkl")
print("✅ Model saved successfully as 'traffic_model.pkl'")