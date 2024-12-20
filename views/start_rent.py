import streamlit as st
import requests
FLASK_API_BASE_URL = "http://127.0.0.1:5000"

st.title("Let's start renting a car!")

# input necessary information

car_brands = ['Toyota', 'Honda', 'Ford', 'BMW', 'Audi']
car_models = ['Corolla', 'Civic', 'Focus', 'X5', 'A4']
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami']

car_brand = st.selectbox("Select Car Brand", car_brands)
car_model = st.selectbox("Select Car Model", car_models)
seats = st.slider("Number of Seats", min_value=2, max_value=7, value=4)
location_city = st.selectbox("Select Pick-Up Location", cities)
pick_up_day = st.slider("Pick-Up Day of Week (0=Monday, 6=Sunday)", min_value=0, max_value=6, value=0)
pick_up_month = st.slider("Pick-Up Month (1=January, 12=December)", min_value=1, max_value=12, value=1)
drop_off_day = st.slider("Drop-Off Day of Week (0=Monday, 6=Sunday)", min_value=0, max_value=6, value=0)
drop_off_month = st.slider("Drop-Off Month (1=January, 12=December)", min_value=1, max_value=12, value=1)
credit_score = st.number_input("Enter Credit Score", min_value=300, max_value=850, value=700)

# Button to get the quote
if st.button("Get Rental Price Estimate"):
    # Payload for API call
    payload = {
        "Brand": car_brand,
        "Model": car_model,
        "Seats": seats,
        "Location_City": location_city,
        "Pick_Up_Day": pick_up_day,
        "Pick_Up_Month": pick_up_month,
        "Drop_Off_Day": drop_off_day,
        "Drop_Off_Month": drop_off_month,
        "Credit_Score": credit_score
    }
    # st.success(f"Estimated Rental Price: $275.23")
    # API call to the Flask route
    try:
        response = requests.post(f"{FLASK_API_BASE_URL}/predict-price", json=payload)
        if response.status_code == 200:
            estimated_price = response.json().get("estimated_price", "N/A")
            st.success(f"Estimated Rental Price: ${estimated_price}")
        else:
            error_message = response.json().get("error", "Unknown error occurred")
            st.error(f"Error: {error_message}")
    except Exception as e:
        st.error(f"An error occurred while fetching the rental price: {e}")
