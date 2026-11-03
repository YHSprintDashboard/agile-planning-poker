import json
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
ROOMS_FILE = "data/rooms.json"

if st.session_state.is_admin:

    st.subheader("👑 Admin Dashboard")

    room_name = st.text_input(
        "Room Name"
    )

    if st.button("Create Room"):

    room_code = (
        room_name.upper()
        .replace(" ", "")
    )

    try:

        with open(
            ROOMS_FILE,
            "r"
        ) as f:

            rooms = json.load(f)

    except:

        rooms = {}

    rooms[room_code] = {
        "name": room_name,
        "status": "Open",
        "users": []
    }

    with open(
        ROOMS_FILE,
        "w"
    ) as f:

        json.dump(
            rooms,
            f,
            indent=4
        )

    st.success(
        f"Room Created: {room_code}"
    )

else:

    st.subheader("👤 Participant")

    room_code = st.text_input(
        "Room Code"
    )

    st.button("Join Room")

st.markdown("### Active Rooms")

try:

    with open(
        ROOMS_FILE,
        "r"
    ) as f:

        rooms = json.load(f)

except:

    rooms = {}

if rooms:

    room_rows = []

    for code, room in rooms.items():

        room_rows.append(
            {
                "Room Code": code,
                "Room Name": room["name"],
                "Status": room["status"]
            }
        )

    st.dataframe(
        pd.DataFrame(room_rows),
        use_container_width=True
    )

else:

    st.info(
        "No rooms created"
    )

