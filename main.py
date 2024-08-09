import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

CSV_FILE = "machine_logs.csv"
MACHINES = ["Machine 1", "Machine 2", "Machine 3", "Machine 4", "Machine 5", "Machine 6"]

# Simulated user database (in a real application, use a secure database)
USERS = {
    "operator1": "password1",
    "operator2": "password2",
    "supervisor": "super_password"
}

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["timestamp", "machine_name", "status", "failure_description", "operator"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def log_status(df, machine_name, status, failure_description="", operator=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame({
        "timestamp": [timestamp],
        "machine_name": [machine_name],
        "status": [status],
        "failure_description": [failure_description],
        "operator": [operator]
    })
    updated_df = pd.concat([df, new_log], ignore_index=True)
    save_data(updated_df)
    return updated_df

def get_last_machine_statuses(df):
    if df.empty:
        return {machine: False for machine in MACHINES}
    
    last_statuses = {}
    for machine in MACHINES:
        machine_df = df[df['machine_name'] == machine]
        if not machine_df.empty:
            last_status = machine_df.iloc[-1]['status']
            last_statuses[machine] = (last_status == 'On')
        else:
            last_statuses[machine] = False
    return last_statuses

def check_password(username, password):
    if username in USERS and USERS[username] == password:
        return True
    return False

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if check_password(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Invalid username or password")

def main():
    st.title("Machine Status Logger")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
        st.warning("Please log in to use the application.")
        return

    # Load existing data
    df = load_data()

    # Initialize session state for machine statuses
    if 'machine_statuses' not in st.session_state:
        st.session_state.machine_statuses = get_last_machine_statuses(df)

    # Create two columns
    col1, col2 = st.columns(2)

    # Machine status buttons
    with col1:
        st.subheader("Machine Statuses")
        for machine in MACHINES:
            if st.button(f"{machine}: {'On' if st.session_state.machine_statuses[machine] else 'Off'}"):
                new_status = not st.session_state.machine_statuses[machine]
                st.session_state.machine_statuses[machine] = new_status
                df = log_status(df, machine, "On" if new_status else "Off", operator=st.session_state.username)
                st.success(f"Logged {'On' if new_status else 'Off'} status for {machine}")

    # Failure logging
    with col2:
        st.subheader("Failure Logging")
        failure_machine = st.selectbox("Select Machine", MACHINES)
        failure_description = st.text_area("Failure Description")
        if st.button("Log Failure"):
            if failure_description:
                df = log_status(df, failure_machine, "Failure", failure_description, operator=st.session_state.username)
                st.success(f"Logged failure for {failure_machine}")
            else:
                st.warning("Please enter a failure description")

    # Display logs
    st.header("Machine Logs")
    st.dataframe(df)

    # Add download button for CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="machine_logs.csv",
        mime="text/csv",
    )

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()
