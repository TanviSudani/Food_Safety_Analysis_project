import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# Load the dataset
df = pd.read_csv("outbreaks.csv")
df.head()

"""### Data Cleaning & Preprocessing"""

# Check missing values
missing_values = df.isnull().sum()

# Fill missing values
df_cleaned = df.copy()

# Fill missing categorical columns with "Unknown"
categorical_cols = ['Location', 'Food', 'Ingredient', 'Species', 'Serotype/Genotype', 'Status']
df_cleaned[categorical_cols] = df_cleaned[categorical_cols].fillna('Unknown')

# Fill numeric columns with 0
df_cleaned[['Hospitalizations', 'Fatalities']] = df_cleaned[['Hospitalizations', 'Fatalities']].fillna(0)

# Convert categorical columns to category dtype
for col in categorical_cols + ['State', 'Month']:
    df_cleaned[col] = df_cleaned[col].astype('category')

# Create a binary target variable: Was anyone hospitalized?
df_cleaned['Hospitalized'] = df_cleaned['Hospitalizations'].apply(lambda x: 1 if x > 0 else 0)

# Preview cleaned data
df_cleaned.head()

"""### EDA"""

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# 1. Trend of total illnesses and hospitalizations per year
illness_trend = df_cleaned.groupby('Year')[['Illnesses', 'Hospitalizations']].sum().reset_index()

# 2. Top 10 food items associated with hospitalization
top_foods = df_cleaned[df_cleaned['Hospitalized'] == 1]['Food'].value_counts().head(10)
st.dataframe(top_foods)

# 3. Top 10 locations where hospitalizations occurred
top_locations = df_cleaned[df_cleaned['Hospitalized'] == 1]['Location'].value_counts().head(10)

# 4. Top 10 affected states (by illness count)
top_states = df_cleaned.groupby('State')['Illnesses'].sum().sort_values(ascending=False).head(10)
top_states

# Trend over years
plt.figure(figsize=(12, 6))

sns.lineplot(data=illness_trend, x='Year', y='Illnesses', label='Illnesses')
sns.lineplot(data=illness_trend, x='Year', y='Hospitalizations', label='Hospitalizations')
plt.title("Yearly Trend of Illnesses and Hospitalizations")
plt.legend()

plt.tight_layout()
plt.show()

# Top affected states
plt.figure(figsize=(12,6))

sns.barplot(x=top_states.values, y=top_states.index)
plt.title("Top 10 States by Illness Count")
plt.xlabel("Number of Illnesses")

plt.tight_layout()
plt.show()

"""### Model Training"""

# Copy cleaned dataset
df_model = df_cleaned.copy()

# Select features and target
features = ['Year', 'Month', 'State', 'Location', 'Food']
target = 'Hospitalized'

# Encode categorical features
le_dict = {}
for col in features:
    if df_model[col].dtype.name == 'category':
        le = LabelEncoder()
        df_model[col] = le.fit_transform(df_model[col])
        le_dict[col] = le

# Split data
X = df_model[features]
y = df_model[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

"""### Check feature importance"""

# Plot feature importance
feat_importances = pd.Series(model.feature_importances_, index=features)
feat_importances.sort_values().plot(kind='barh')
plt.title("Feature Importance - Random Forest")
plt.xlabel("Importance Score")
plt.show()

"""### Save the model"""

import pickle
pickle.dump(model, open('model.pkl', 'wb'))

"""### Deep Learning"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score

# Encode categorical features
df_dl = df_cleaned.copy()
features = ['Year', 'Month', 'State', 'Location', 'Food']
target = 'Hospitalized'

le_dict = {}
for col in features:
    if df_dl[col].dtype.name == 'category':
        le = LabelEncoder()
        df_dl[col] = le.fit_transform(df_dl[col])
        le_dict[col] = le

# Prepare input/output
X = df_dl[features]
y = df_dl[target]

# Normalize input features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# Build model
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)

# Evaluate
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

"""### Hyperparamater Tunning"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

# Instantiate model
rf = RandomForestClassifier(random_state=42)

# Randomized Search
rf_random = RandomizedSearchCV(estimator=rf, param_distributions=param_grid,
                               n_iter=20, cv=3, verbose=2, n_jobs=-1, random_state=42)

rf_random.fit(X_train, y_train)

# Best model evaluation
best_model = rf_random.best_estimator_
y_pred_tuned = best_model.predict(X_test)

print("Tuned Accuracy:", accuracy_score(y_test, y_pred_tuned))
print("\nTuned Classification Report:\n", classification_report(y_test, y_pred_tuned))

"""### Visualize Training Loss and Accuracy Curves"""

# Plot Accuracy
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy', marker='o')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy', marker='o')
plt.title('Model Accuracy Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

# Plot Loss
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss', marker='o')
plt.plot(history.history['val_loss'], label='Validation Loss', marker='o')
plt.title('Model Loss Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

"""### Prediction"""

# Predict probabilities
y_pred_prob = model.predict(X_test)

# Convert to binary labels (0 or 1)
y_pred = (y_pred_prob > 0.5).astype(int)

print("Test set Accuracy:", accuracy_score(y_test, y_pred))

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

print("Test set Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

decoded_df = pd.DataFrame(X_test, columns=['Year', 'Month', 'State', 'Location', 'Food'])

# Add Actual and Predicted columns
decoded_df['Actual'] = y_test.values
decoded_df['Predicted'] = y_pred.flatten()

# Final DataFrame
final_df = decoded_df.copy()

# View top results
final_df.head(10)          # Actual = 1, Predicted = 0 means a false negative,
                           # Actual = 0, Predicted = 1 means a false positive.

# View Only Incorrect Predictions
incorrect_preds = final_df[final_df['Actual'] != final_df['Predicted']]
incorrect_preds.head(10)

"""### Confusion Matrix Visualization"""

cm = confusion_matrix(y_test, y_pred)

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['No Hospitalization', 'Hospitalization'],
            yticklabels=['No Hospitalization', 'Hospitalization'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()
