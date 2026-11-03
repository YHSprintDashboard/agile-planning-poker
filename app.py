import streamlit as st

st.set_page_config(
    page_title="Agile Planning Poker",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

# =========================
# LOGIN
# =========================

st.title("🎯 Agile Planning Poker")

if not st.session_state.authenticated:

    role = st.radio(
        "Select Role",
        [
            "👤 Participant",
            "👑 Admin"
        ]
    )

    if role == "👤 Participant":

        display_name = st.text_input(
            "Display Name"
        )

        if st.button("Join"):

            if display_name.strip():

                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.session_state.display_name = display_name

                st.rerun()

    else:

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        if st.button("Login"):

            if password == st.secrets["ADMIN_PASSWORD"]:

                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.session_state.display_name = "Admin"

                st.rerun()

            else:
                st.error("Invalid password")

    st.stop()

# =========================
# HOME
# =========================

st.success(
    f"Logged in as {st.session_state.display_name}"
)

if st.session_state.is_admin:

    st.subheader("👑 Admin")

    st.button("Create Room")

else:

    st.subheader("👤 Participant")

    room_code = st.text_input(
        "Room Code"
    )

    st.button("Join Room")

