import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load balanced data
balanced_data = pd.read_csv('bluetooth_data.txt', sep=',', header=0)
new_data = pd.read_csv('new_bluetooth_data.txt', sep=',', header=0)

# Split data into features and labels
X = balanced_data.drop(columns=['L'])
y = balanced_data['L']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Make predictions on new data
predictions = model.predict(new_data)

# Print predictions
for i, pred in enumerate(predictions):
    print(f"Sample {i + 1}: {pred}")
