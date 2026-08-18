import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
data = pd.read_csv("Crop_recommendation.csv")
print("Columns in dataset:", data.columns)

# Features and Target
X = data.drop("label", axis=1)
y = data["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Accuracy
acc = model.score(X_test, y_test)
print(f"✅ Model trained with accuracy: {acc*100:.2f}%")

# Save model
with open("crop_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as crop_model.pkl")
