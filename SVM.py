import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

url = "https://disease.sh/v3/covid-19/countries/usa"
r = requests.get(url)
data = r.json()

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

np.random.seed(42)
historical_cases = np.random.randint(30000, 70000, size=30)  
historical_deaths = np.random.randint(500, 2000, size=30)
df_historical = pd.DataFrame({"cases": historical_cases, "deaths": historical_deaths})
df_historical["day"] = range(1, 31)

X = df_historical[["day"]]
y = df_historical["cases"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

svm_model = SVR(kernel='rbf')
svm_model.fit(X_train, y_train)

next_day = np.array([[31]])
predicted_cases_svm = svm_model.predict(next_day)

df_historical["high_case"] = (df_historical["cases"] > 50000).astype(int)
y_class = df_historical["high_case"]
X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

log_reg = LogisticRegression()
log_reg.fit(X_train_scaled, y_train)
pred_class = log_reg.predict(scaler.transform(next_day))

st.title("COVID-19 Cases Prediction in USA")
st.write("Predicting COVID-19 cases for the next day using SVM and Logistic Regression.")

day_input = st.number_input("Enter day number (e.g., 31 for prediction)", min_value=1, max_value=100)

if st.button("Predict"):
    prediction_svm = svm_model.predict([[day_input]])
    prediction_class = log_reg.predict(scaler.transform([[day_input]]))
    
    st.write(f"Predicted cases for day {day_input} using SVM: {int(prediction_svm[0])}")
    st.write(f"Prediction if cases exceed 50,000 (1 = Yes, 0 = No): {int(prediction_class[0])}")
