import os
import subprocess
import sys
import sqlite3
import hashlib
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

# Function to install required packages
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

# Ensure required packages are installed
required_packages = ["plotly", "streamlit"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"⚠ {package} not found. Installing now...")
        install_package(package)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to add user
def add_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Function to check user credentials
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    record = cursor.fetchone()
    conn.close()
    if record and record[0] == hash_password(password):
        return True
    return False

# Initialize database
init_db()

# Login Page
st.title("🔐 Login Page")
menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.success(f"Welcome, {username}!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password")

elif choice == "Sign Up":
    st.subheader("Create New Account")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    if st.button("Sign Up"):
        if add_user(new_username, new_password):
            st.success("Account created successfully! You can now log in.")
        else:
            st.error("Username already exists. Choose a different one.")

# If user is logged in, show the stock market app
if st.session_state.get('logged_in'):
    st.sidebar.success(f"Logged in as {st.session_state['username']}")
    
    # Stock Market App starts here...
    st.title("📊 Stock Market App")
    
    API_KEY = "MVVQ3GM2LROFV9JI"
    
    companies = {
        "Apple (AAPL)": "AAPL",
        "Microsoft (MSFT)": "MSFT",
        "Google (GOOGL)": "GOOGL",
        "Amazon (AMZN)": "AMZN",
        "Tesla (TSLA)": "TSLA",
        "Meta (META)": "META",
        "Netflix (NFLX)": "NFLX",
        "Nvidia (NVDA)": "NVDA",
        "IBM (IBM)": "IBM",
        "Intel (INTC)": "INTC"
    }
    
    def get_stock_data(symbol):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
        response = requests.get(url)
        return response.json()
    
    selected_company = st.selectbox("📌 Select a Company", list(companies.keys()))
    
    if st.button("🔍 Fetch Stock Data"):
        stock_data = get_stock_data(companies[selected_company])
        
        if "Time Series (5min)" in stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index").astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]
            st.session_state.stock_data = df
        else:
            st.warning(f"⚠ Could not fetch data for {selected_company}.")
    
    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        current_price = df["Close"].iloc[-1]
        highest_price = df["High"].max()
        starting_price = df["Open"].iloc[0]
        
        st.subheader(f"📈 {selected_company} Stock Details")
        st.info(f"💰 Current Price: ${current_price:.2f}")
        st.success(f"📈 Highest Price: ${highest_price:.2f}")
        st.warning(f"🔽 Starting Price: ${starting_price:.2f}")
        
        fig = px.line(df, x=df.index, y="Close", title="📊 Intraday Stock Prices", 
                     labels={"Close": "Stock Price"}, template="plotly_dark")
        st.plotly_chart(fig)
        
        num_stocks = st.number_input("🛒 Enter number of stocks to buy", min_value=1, step=1)
        
        if st.button("📊 Fetch Profit/Loss"):
            total_cost = num_stocks * current_price
            st.info(f"💰 Total Investment: ${total_cost:.2f}")
