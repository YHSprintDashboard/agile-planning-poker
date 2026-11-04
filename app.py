import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Agile Planning Poker",
    layout="wide"
)

# =========================
# FILE SETUP
# =========================

DATA_DIR = "data"
ROOMS_FILE = f"{DATA_DIR}/rooms.json"

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(ROOMS_FILE):
    with open(ROOMS_FILE, "w") as f:
        json.dump({}, f)

# =========================
# HELPERS
# =========================

def load_rooms():
    try:
        with open(ROOMS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_rooms(rooms):
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f, indent=4)


STORY_POINTS = [
    "1", "2", "3", "5", "8", "13", "21"
]

FUN_CARDS = {
    "☕": "Need a break",
    "🍺": "End of refinement",
    "👻": "No idea / needs more detail",
    "🧙": "Hidden complexity",
    "🧔": "I've seen this before",
    "🚀": "Easy win",
    "🔥": "High risk",
    "🤯": "Massive effort",
    "🐙": "Too many dependencies",
    "🦄": "Sounds great, probably isn't"
}

# =========================
# SESSION STATE
# =========================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

if "room_code" not in st.session_state:
    st.session_state.room_code = ""

if "selected_vote" not in st.session_state:
    st.session_state.selected_vote = None

# =========================
# LOGIN SCREEN
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

        st.write("Display Name")

        display_name = st.text_input(
            "",
            placeholder="Enter your name"
        )

        if st.button(
            "🚀 Join",
            use_container_width=True
        ):

            if not display_name.strip():
                st.error(
                    "Please enter a display name."
                )

            else:
                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.session_state.display_name = display_name.strip()

                st.rerun()

    else:

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            if not password:
                st.error(
                    "Please enter password."
                )

            elif password == st.secrets["ADMIN_PASSWORD"]:

                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.session_state.display_name = "Admin"

                st.rerun()

            else:
                st.error(
                    "Invalid password."
                )

    st.stop()

# =========================
# HEADER
# =========================

col1, col2 = st.columns([8, 1])

with col1:
    st.success(
        f"Logged in as: {st.session_state.display_name}"
    )

with col2:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

rooms = load_rooms()

# =========================
# ADMIN
# =========================

if st.session_state.is_admin:

    st.subheader("👑 Admin Dashboard")

    room_name = st.text_input(
        "Room Name",
        placeholder="Sprint 15 Planning"
    )

    if st.button(
        "➕ Create Room",
        use_container_width=True
    ):

        if not room_name.strip():
            st.error(
                "Please enter a room name."
            )

        else:

            room_code = (
                room_name
                .upper()
                .replace(" ", "")
            )

            if room_code in rooms:

                st.warning(
                    "Room already exists."
                )

            else:

                rooms[room_code] = {
                    "name": room_name,
                    "status": "Open",
                    "users": []
                }

                save_rooms(rooms)

                st.success(
                    f"Room Created: {room_code}"
                )

# =========================
# PARTICIPANT
# =========================

else:

    st.subheader("👤 Participant")

    room_code = st.text_input(
        "Room Code",
        placeholder="SPRINT15PLANNING"
    )

    if st.button(
        "🚪 Join Room",
        use_container_width=True
    ):

        room_code = room_code.upper().strip()

        if not room_code:

            st.error(
                "Please enter a room code."
            )

        elif room_code not in rooms:

            st.error(
                "Room does not exist."
            )

        else:

            user_name = st.session_state.display_name

            if user_name not in rooms[room_code]["users"]:

                rooms[room_code]["users"].append(
                    user_name
                )

                save_rooms(rooms)

            st.session_state.room_code = room_code

            st.success(
                f"Joined Room: {room_code}"
            )

    # =========================
    # VOTING SECTION
    # =========================

    if st.session_state.room_code:

        st.divider()

        st.subheader(
            f"🗳 Voting Room: {st.session_state.room_code}"
        )

        st.markdown("### Story Points")

        cols = st.columns(7)

        for i, point in enumerate(STORY_POINTS):

            with cols[i]:

                if st.button(
                    point,
                    key=f"sp_{point}",
                    use_container_width=True
                ):
                    st.session_state.selected_vote = point

        st.markdown("### Fun Cards")

        for emoji, description in FUN_CARDS.items():

            if st.button(
                f"{emoji} {description}",
                key=f"fun_{emoji}",
                use_container_width=True
            ):
                st.session_state.selected_vote = (
                    f"{emoji} {description}"
                )

        if st.session_state.selected_vote:

            st.success(
                f"✅ Your Vote: "
                f"{st.session_state.selected_vote}"
            )

# =========================
# ACTIVE ROOMS
# =========================

st.divider()
st.markdown("### 📋 Active Rooms")

rooms = load_rooms()


if rooms:

    room_rows = []

    for code, room in rooms.items():

        room_rows.append(
            {
                "Room Code": code,
                "Room Name": room["name"],
                "Status": room["status"],
                "Participants": len(
                    room["users"]
                )
            }
        )

    st.table(pd.DataFrame(room_rows))

else:
    st.info(
        "No rooms created yet."
    )
