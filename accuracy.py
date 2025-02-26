import pandas as pd  
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
dataset = pd.read_csv("/Users/achirashah/Desktop/logic_depth_dataset.csv")

# Ensure only numeric features are used (remove 'File' column)
X = dataset.drop(columns=["File", "Signal", "Logic Depth"], errors='ignore')
y = dataset["Logic Depth"]

# Convert all features to float (ensure numeric format)
X = X.astype(float)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Model
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print(f"Model MAE: {mae}")

# Additional evaluation metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model Performance Metrics:")
print(f" - Mean Absolute Error (MAE): {mae}")
print(f" - Mean Squared Error (MSE): {mse}")
print(f" - R² Score: {r2}")