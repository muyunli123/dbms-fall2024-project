import streamlit as st

# --- PAGE SETUP ---
start_rent = st.Page(
    page = "views/start_rent.py",
    title = "Rent Cars",
    icon = ":material/emoji_transportation:",
    default = True,
)

log_in = st.Page(
    page = "views/log_in.py",
    title = "Log In",
    icon = ":material/account_circle:",
)

# --- NAVIGATION SETUP ---
pg = st.navigation(pages = [start_rent, log_in])


# --- SHARED ON ALL PAGES ---
st.logo("assets/logo.png")

# --- RUN NAVIGATION ---
pg.run()