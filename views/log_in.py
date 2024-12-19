import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

FLASK_API_BASE_URL = "http://127.0.0.1:5000"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login(account_id):
    if account_id:
        st.session_state.logged_in = True
        st.session_state.account_id = account_id

def logout():
    st.session_state.logged_in = False
    st.session_state.account_id = None

def get_customer_name(account_id):
    """Retrieve customer name using the Flask API."""
    response = requests.get(f"{FLASK_API_BASE_URL}/accounts/{account_id}")
    if response.status_code == 200:
        return response.json().get("name", "Unknown")
    return "Unknown"

def get_reservations(account_id):
    """Fetch reservations for the given account ID using the Flask API."""
    response = requests.get(f"{FLASK_API_BASE_URL}/reservations/account/{account_id}")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame([])

def extend_reservation(reservation_id):
    """Extend the drop-off time of a reservation by 1 week."""
    response = requests.put(f"{FLASK_API_BASE_URL}/reservations/{reservation_id}/extend")
    return response.status_code == 200

def create_new_reservation(account_id, car_type_id, pick_up_time, pick_up_location_id, drop_off_time, drop_off_location_id):
    """Create a new reservation using the Flask API."""
    data = {
        "AccountId": account_id,
        "CarTypeId": car_type_id,
        "PickUpTime": pick_up_time.isoformat(),
        "DropOffTime": drop_off_time.isoformat(),
        "PickUpLocationId": pick_up_location_id,
        "DropOffLocationId": drop_off_location_id
    }
    response = requests.post(f"{FLASK_API_BASE_URL}/reservations", json=data)
    return response.status_code == 201

def get_car_types():
    """Fetch all car types using the Flask API."""
    response = requests.get(f"{FLASK_API_BASE_URL}/car-types")
    if response.status_code == 200:
        return response.json()
    return []

def get_car_type_by_id(type_id): 
    response = requests.get(f"{FLASK_API_BASE_URL}/car-types/{type_id}")
    if response.status_code == 200:
        return response.json().get("type", "Unknown")
    return "Unknown"

def get_locations():
    """Fetch all branch locations using the Flask API."""
    response = requests.get(f"{FLASK_API_BASE_URL}/locations")
    if response.status_code == 200:
        return response.json()
    return []

def get_location_by_id(location_id):
    response = requests.get(f"{FLASK_API_BASE_URL}/locations/{location_id}")
    if response.status_code == 200:
        return response.json().get("location", "Unknown Location")
    else:
        return "Unknown Location"


if not st.session_state.logged_in:
    st.title("Log in to your account")
    account_id = st.text_input("Enter your Account ID: ")
    if st.button("Login"):
        login(account_id)
        st.rerun() 
else:
    st.session_state.customer_name = get_customer_name(st.session_state.account_id)
    st.title(f"Welcome, {st.session_state.customer_name}!")
    st.subheader("Your Reservations")
    reservations_df = get_reservations(st.session_state.account_id)
    display_data = []
    for _, row in reservations_df.iterrows():
        display_data.append({
            "Reservation ID": row["Id"],
            "Car Type": get_car_type_by_id(row["CarTypeId"]),  # Fetch car type
            "Pick-Up Time": row["PickUpTime"],
            "Drop-Off Time": row["DropOffTime"],
            "Pick-Up Location": get_location_by_id(row["PickUpLocationId"]),  # Fetch pick-up location
            "Drop-Off Location": get_location_by_id(row["DropOffLocationId"]),  # Fetch drop-off location
        })

    display_df = pd.DataFrame(display_data)

    st.dataframe(display_df, use_container_width=True)

    for _, row in reservations_df.iterrows():
        extend_button = st.button(f"Extend Reservation", key=f"extend_{row['Id']}")
        if extend_button:
            if extend_reservation(row["Id"]):
                st.success(f"Reservation {row['Id']} extended successfully!")
                st.rerun()
            else:
                st.error(f"Failed to extend reservation {row['Id']}.")

    st.subheader("Create New Reservation")
    car_types = get_car_types()
    car_type_choices = {f"{ct['Brand']} {ct['Model']}": ct['TypeId'] for ct in car_types}
    selected_car_type = st.selectbox("Select Car Type", list(car_type_choices.keys()))

    locations = get_locations()
    location_choices = {loc['City']: loc['Id'] for loc in locations}
    selected_pick_up_location = st.selectbox("Pick-Up Location", list(location_choices.keys()))
    selected_drop_off_location = st.selectbox("Drop-Off Location", list(location_choices.keys()))

    pick_up_time = st.date_input("Pick-Up Time")
    drop_off_time = st.date_input("Drop-Off Time")

    create_button = st.button("Create Reservation")
    if create_button:
        st.write("Your reservation has been submitted. We will inform you when your application is approved")
        # if create_new_reservation(
        #     account_id=st.session_state.account_id,
        #     car_type_id=car_type_choices[selected_car_type],
        #     pick_up_time=datetime.combine(pick_up_time, datetime.min.time()),
        #     pick_up_location_id=location_choices[selected_pick_up_location],
        #     drop_off_time=datetime.combine(drop_off_time, datetime.min.time()),
        #     drop_off_location_id=location_choices[selected_drop_off_location]
        # ):
        #     st.success("Reservation created successfully!")
        #     st.experimental_rerun()
        # else:
        #     st.error("Failed to create reservation.")

    st.button("Logout", on_click=logout)  # Logout button
