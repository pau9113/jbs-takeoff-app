import hmac
import streamlit as st

# Simple login gate (good enough for internal tool).
# Change these credentials later.
USERS = {
    "pau9113": "Mark76078!",   # username: password
    "estimator1": "Fence123!",
}

def login_gate():
    if "authed" not in st.session_state:
        st.session_state.authed = False

    if st.session_state.authed:
        return True

    st.title("JBS Fence Takeoff Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Log in"):
        if u in USERS and hmac.compare_digest(USERS[u], p):
            st.session_state.authed = True
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()

