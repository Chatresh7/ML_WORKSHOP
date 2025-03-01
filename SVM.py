import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR

# Fetch COVID-19 Data
url = "https://disease.sh/v3/covid-19/countries/usa"
data = requests.get(url).json()

# Process Data
covid_data = {
    "cases": data["cases"],
    "todayCases": data["todayCases"],
    "deaths": data["deaths"],
    "todayDeaths": data["todayDeaths"],
    "recovered": data["recovered"],
    "active": data["active"],
    "critical": data["critical"],
    "casesPerMillion": data["casesPerOneMillion"],
    "deathsPerMillion": data["deathsPerOneMillion"],
}
df = pd.DataFrame([covid_data])

# Generate Random Historical Data
np.random.seed(42)
historical_cases = np.random.randint(30000, 70000, size=30)
historical_deaths = np.random.randint(500, 2000, size=30)
df_historical = pd.DataFrame({"cases": historical_cases, "deaths": historical_deaths})
df_historical["day"] = range(1, 31)

# Prepare Data for Models
X = df_historical[["day"]]
y = df_historical["cases"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Models
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

svm_model = SVR(kernel='rbf')
svm_model.fit(X_train, y_train)

logistic_model = LogisticRegression()
logistic_model.fit(X_train, y_train > 50000)  # Binary classification: cases > 50K

# Streamlit UI
st.title("COVID-19 Cases Prediction - USA")
st.write("Predicting COVID-19 cases using Linear Regression, SVM, and Logistic Regression.")

# Show Bar Graph of Current Data
st.subheader("Current COVID-19 Data in USA")
fig, ax = plt.subplots()
ax.bar(["Total Cases", "Active Cases", "Recovered", "Deaths"], 
       [data["cases"], data["active"], data["recovered"], data["deaths"],], 
       color=['blue', 'orange', 'green', 'red'])
ax.set_ylabel("Count")
ax.set_title("COVID-19 Data Overview")
st.pyplot(fig)

# User Input
day_input = st.number_input("Enter day number (e.g., 31 for prediction)", min_value=1, max_value=100)

if st.button("Predict"):
    linear_pred = linear_model.predict([[day_input]])[0]
    svm_pred = svm_model.predict([[day_input]])[0]
    logistic_pred = logistic_model.predict([[day_input]])[0]
    logistic_label = "High" if logistic_pred == 1 else "Low"

    st.subheader("Predictions")
    st.write(f"Linear Regression Prediction: {int(linear_pred)} cases")
    st.write(f"SVM Prediction: {int(svm_pred)} cases")
    st.write(f"Logistic Regression Prediction: {logistic_label} risk")

    # Visualization
    plt.figure(figsize=(8,5))
    plt.plot(df_historical["day"], df_historical["cases"], label="Actual Cases", marker='o')
    plt.axvline(x=day_input, color='red', linestyle='--', label=f"Prediction for Day {day_input}")
    plt.legend()
    plt.xlabel("Day")
    plt.ylabel("Cases")
    plt.title("COVID-19 Case Trends")
    st.pyplot(plt)

    # Bar Graph for Predictions
    st.subheader("Prediction Comparison")
    fig2, ax2 = plt.subplots()
    ax2.bar(["Linear Regression", "SVM", "Logistic Regression"], 
            [linear_pred, svm_pred, int(logistic_pred * 50000)], 
            color=['blue', 'green', 'red'])
    ax2.set_ylabel("Predicted Cases")
    ax2.set_title("Prediction Comparison")
    st.pyplot(fig2)
