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

    col1, col2 = st.columns([4,1])

    with col1:
        room_name = st.text_input(
            "Room Name",
            placeholder="Sprint 15 Planning"
        )
    
    with col2:
        st.write("")
        st.write("")
    
        create_room = st.button(
            "➕ Create",
            use_container_width=True
        )
    
    if create_room:

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
                    "users": [],
                    "votes": {},
                    "revealed": False
                }

                save_rooms(rooms)

                st.success(
                    f"Room Created: {room_code}"
                )

    rooms = load_rooms()

    if rooms:

        st.divider()

        with st.sidebar:

            st.header("👑 Admin Controls")
        
            selected_room = st.selectbox(
                "Active Room",
                list(rooms.keys())
            )
        
            reveal_votes = st.button(
                "🎭 Reveal Votes",
                use_container_width=True
            )
        
            if st.button(
                "🔄 Refresh Status",
                use_container_width=True
            ):
                st.rerun()

        room = rooms[selected_room]

        st.markdown("### 👥 Team Voting Board")

        users = room["users"]
        
        if users:
        
            card_html = ""
        
            for user in users:
        
                voted = user in room["votes"]
        
                if room["revealed"] and voted:
        
                    display_value = room["votes"][user]
        
                elif voted:
        
                    display_value = "✅"
        
                else:
        
                    display_value = "⏳"
        
                card_html += f"""
                <div style="
                    width:120px;
                    margin:10px;
                    display:inline-block;
                    text-align:center;
                    vertical-align:top;
                ">
                    <div style="
                        height:120px;
                        border:2px dashed #cccccc;
                        border-radius:10px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:28px;
                        font-weight:bold;
                    ">
                        {display_value}
                    </div>
        
                    <div style="
                        margin-top:8px;
                        font-size:14px;
                    ">
                        {user}
                    </div>
                </div>
                """
        
            st.markdown(
                card_html,
                unsafe_allow_html=True
            )
        
                    voted = user in room["votes"]
        
                    if room["revealed"] and voted:
        
                        vote = room["votes"][user]
        
                        st.markdown(
                            f"""
                            <div style="
                                border:2px solid #c9b07c;
                                border-radius:10px;
                                padding:25px;
                                text-align:center;
                                min-height:120px;
                            ">
                                <h2>{vote}</h2>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
                    else:
        
                        st.markdown(
                            """
                            <div style="
                                border:2px dashed #cccccc;
                                border-radius:10px;
                                padding:25px;
                                text-align:center;
                                min-height:120px;
                            ">
                                ?
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
                    st.caption(user)

        users = room["users"]
        
        if users:
        
            cols = st.columns(
                min(len(users), 6)
            )
        
            for idx, user in enumerate(users):
        
                with cols[idx % 6]:
        
                    voted = user in room["votes"]
        
                    if room["revealed"] and voted:
        
                        vote = room["votes"][user]
        
                        st.markdown(
                            f"""
                            ### {vote}
        
                            **{user}**
                            """
                        )
        
                    else:
        
                        if voted:
        
                            st.success("✅")
        
                        else:
        
                            st.warning("⏳")
        
                        st.caption(user)

        st.divider()

        if reveal_votes:

            room["revealed"] = True

            save_rooms(rooms)

            st.rerun()

        if room["revealed"]:

            st.markdown(
                "### 🗳 Revealed Votes"
            )

            revealed_rows = []

            for user, vote in room["votes"].items():

                revealed_rows.append(
                    {
                        "Participant": user,
                        "Vote": vote
                    }
                )

            if revealed_rows:

                st.table(
                    pd.DataFrame(
                        revealed_rows
                    )
                )

            numeric_votes = []

            for vote in room["votes"].values():

                if str(vote).isdigit():

                    numeric_votes.append(
                        int(vote)
                    )

            if numeric_votes:

                average_sp = (
                    sum(numeric_votes)
                    / len(numeric_votes)
                )

                median_sp = (
                    sorted(
                        numeric_votes
                    )[len(numeric_votes)//2]
                )

                st.markdown(
                    f"**Average SP:** {average_sp:.2f}"
                )

                st.markdown(
                    f"**Median SP:** {median_sp}"
                )

                col1, col2, col3 = st.columns([1,1,4])

                with col1:
                    st.metric(
                        "Average",
                        f"{average_sp:.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Median",
                        median_sp
                    )
                
                with col3:
                    final_sp = st.number_input(
                        "Final SP",
                        value=float(round(average_sp)),
                        step=1.0
                    )

                st.success(
                    f"✅ Final SP Selected: {final_sp}"
                )


# =========================
# PARTICIPANT
# =========================

else:

    col1, col2 = st.columns([3,1])

    with col1:
        st.subheader(
            f"👤 {st.session_state.display_name}"
        )
    
    with col2:
        if st.session_state.room_code:
            st.info(
                f"🏠 {st.session_state.room_code}"
            )

    col1, col2 = st.columns([4,1])

    with col1:
        room_code = st.text_input(
            "Room Code",
            placeholder="SPRINT15PLANNING"
        )
    
    with col2:
        st.write("")
        st.write("")
    
        join_clicked = st.button(
            "🚪 Join",
            use_container_width=True
        )
    
    if join_clicked:
    
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

                    rooms = load_rooms()
                    
                    rooms[
                        st.session_state.room_code
                    ]["votes"][
                        st.session_state.display_name
                    ] = point
                    
                    save_rooms(rooms)

       
        st.markdown("### Fun Cards")

        fun_cols = st.columns(5)
        
        for i, (emoji, description) in enumerate(FUN_CARDS.items()):
        
            with fun_cols[i % 5]:
        
                if st.button(
                    f"{emoji}\n{description}",
                    key=f"fun_{emoji}",
                    use_container_width=True
                ):
        
                    selected_value = f"{emoji} {description}"
        
                    st.session_state.selected_vote = selected_value
        
                    rooms = load_rooms()
        
                    rooms[
                        st.session_state.room_code
                    ]["votes"][
                        st.session_state.display_name
                    ] = selected_value
        
                    save_rooms(rooms)

        if st.session_state.selected_vote:

            st.metric(
                "Your Vote",
                st.session_state.selected_vote
            )

# =========================
# ACTIVE ROOMS
# =========================

with st.expander(
    "📋 Active Rooms",
    expanded=False
):

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

        st.table(
            pd.DataFrame(room_rows)
        )

    else:

        st.info(
            "No rooms created yet."
        )
