import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Machine Log Entry")

# Sidebar for user login
st.sidebar.header("User Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button:
    st.sidebar.success(f"Logged in as {username}")

# Main section for logging machine data
st.header("Log Machine Data")

# Machine selection
machine_id = st.selectbox("Select Machine",
                          ["Machine 1", "Machine 2", "Machine 3"])

# Action selection
action = st.radio("Action", ["Start", "Stop"])

# Failure input
failure = st.text_area("Failure (if any)")

submit_button = st.button("Submit")

if submit_button:
    if username and password:
        # Capture the current time
        current_time = datetime.now()

        # Create a DataFrame to store the log data
        log_data = {
            "Machine ID": [machine_id],
            "Action": [action],
            "Time": [current_time],
            "Failure": [failure],
            "Logged By": [username],
            "Timestamp": [current_time]
        }
        df = pd.DataFrame(log_data)

        # Save the data to a CSV file (or any other storage)
        df.to_csv("machine_log.csv", mode='a', header=False, index=False)

        st.success("Data logged successfully!")
    else:
        st.error("Please log in to submit data.")

# Load the logged data
try:
    log_df = pd.read_csv("machine_log.csv",
                         names=[
                             "Machine ID", "Action", "Time", "Failure",
                             "Logged By", "Timestamp"
                         ])
    log_df["Time"] = pd.to_datetime(log_df["Time"])

    # Calculate hours worked
    def calculate_hours(df):
        df = df.sort_values(by="Time")
        df["Next Action"] = df["Action"].shift(-1)
        df["Next Time"] = df["Time"].shift(-1)
        df = df[(df["Action"] == "Start") & (df["Next Action"] == "Stop")]
        df["Duration"] = (df["Next Time"] -
                          df["Time"]).dt.total_seconds() / 3600
        return df

    hours_df = log_df.groupby("Machine ID").apply(calculate_hours).reset_index(
        drop=True)

    # Calculate total hours by day, week, and month
    hours_df["Date"] = hours_df["Time"].dt.date
    daily_hours = hours_df.groupby(["Machine ID",
                                    "Date"])["Duration"].sum().reset_index()
    weekly_hours = hours_df.groupby([
        "Machine ID", pd.Grouper(key="Time", freq="W-MON")
    ])["Duration"].sum().reset_index()
    monthly_hours = hours_df.groupby(
        ["Machine ID", pd.Grouper(key="Time",
                                  freq="M")])["Duration"].sum().reset_index()

    # Display the results
    st.header("Hours Worked by Machine")
    st.subheader("Daily Hours")
    st.dataframe(daily_hours)

    st.subheader("Weekly Hours")
    st.dataframe(weekly_hours)

    st.subheader("Monthly Hours")
    st.dataframe(monthly_hours)

except FileNotFoundError:
    st.warning("No log data found. Please log some data first.")
