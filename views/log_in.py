import streamlit as st

st.title("Log in to your account")

ssn = st.text_input('SSN')
st.button('Log In')