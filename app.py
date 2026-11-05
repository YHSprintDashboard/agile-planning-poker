import json
import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Agile Planning Poker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit default UI where possible
st.markdown("""
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none;
}

[data-testid="stDecoration"] {
    display: none;
}

[data-testid="stStatusWidget"] {
    display: none;
}

[data-testid="stDeployButton"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

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
DAY_ESTIMATES = [
    "0.5", "1", "2", "3", "4", "5", "6+"
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
    "🦄": "Sounds great, probably isn't",
    "🏃": "BRB",
    "🙉": "I wasn't listening",
    "🛡️": "This is the way"
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

if "selected_dev_vote" not in st.session_state:
    st.session_state.selected_dev_vote = None

if "selected_qa_vote" not in st.session_state:
    st.session_state.selected_qa_vote = None

# =========================
# LOGIN SCREEN
# =========================

st.title("🎯 YH Planning Poker")

st.caption(
    "⚡ A long time ago in a sprint far, far away...... The Legend 👑 forged this Planning Poker app to bring balance to Story Points."
)

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

    col1, col2, col3 = st.columns([2,1,4])

    with col1:
        room_name = st.text_input(
            "Room Name",
            placeholder="Sprint Planning"
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
                    "current_story": "",
                    "history": [],
                    "users": [],
                    "sp_votes": {},
                    "dev_votes": {},
                    "qa_votes": {},
                    "fun_cards": {},
                    "revealed": False
                }

                save_rooms(rooms)

                st.success(
                    f"Room Created: {room_code}"
                )

    rooms = load_rooms()

    if rooms:

        st.divider()

        st.header("👑 Admin Controls")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            selected_room = st.selectbox(
                "Active Room",
                list(rooms.keys())
            )
        
        with col2:
            current_story = st.text_input(
                "User Story",
                value=rooms[selected_room].get(
                    "current_story",
                    ""
                ),
                placeholder="US-1234"
            )
        
            if st.button(
                "💾 Set Story",
                use_container_width=True
            ):
                rooms[selected_room][
                    "current_story"
                ] = current_story
        
                save_rooms(rooms)
        
                st.rerun()
        
        with col3:
            st.write("")
            reveal_votes = st.button(
                "🎭 Reveal Votes",
                use_container_width=True
            )
        
        with col4:
            st.write("")
            undo_reveal = st.button(
                "↩️ Undo Reveal",
                use_container_width=True
            )
        
        with col5:
            st.write("")
            new_story = st.button(
                "🆕 New User Story",
                use_container_width=True
            )
        
        with col6:
            st.write("")
            refresh_status = st.button(
                "🔄 Refresh",
                use_container_width=True
            )
        
        if refresh_status:
            st.rerun()


        room = rooms[selected_room]

        st.markdown("### 👥 Team Voting Board")

        users = room["users"]
        
        if users:
        
            cols = st.columns(8)
        
            for idx, user in enumerate(users):
        
                with cols[idx % 8]:
        
                    voted = user in room["sp_votes"]

                    if room["revealed"] and voted:
                    
                        st.metric(
                            label=user,
                            value=room["sp_votes"][user]
                        )
        
                    elif voted:
        
                        st.metric(
                            label=user,
                            value="✅"
                        )
        
                    else:
        
                        st.metric(
                            label=user,
                            value="⏳"
                        )
        st.markdown("### 🎭 Discussion Signals")

        fun_card_rows = []

        for user, signal in room.get(
            "fun_cards",
            {}
        ).items():

            fun_card_rows.append(
                {
                    "Participant": user,
                    "Signal": signal
                }
            )

        if fun_card_rows:

            st.table(
                pd.DataFrame(fun_card_rows)
            )

        else:

            st.info(
                "No discussion signals raised."
            )        

        st.divider()

        if reveal_votes:

            room["revealed"] = True

            save_rooms(rooms)

            st.rerun()

        if undo_reveal:

            room["revealed"] = False
        
            save_rooms(rooms)
        
            st.rerun()

        if new_story:

            history_row = {
                "US Number": room.get(
                    "current_story",
                    ""
                ),
                "SP": st.session_state.get(
                    "final_sp",
                    ""
                ),
                "Dev Days": st.session_state.get(
                    "final_dev_days",
                    ""
                ),
                "QA Days": st.session_state.get(
                    "final_qa_days",
                    ""
                )
            }
        
            room["history"].append(
                history_row
            )
        
            room["sp_votes"] = {}
            room["dev_votes"] = {}
            room["qa_votes"] = {}
            room["fun_cards"] = {}
        
            room["revealed"] = False
        
            save_rooms(rooms)
        
            st.rerun()

        if room["revealed"]:

            st.markdown(
                "### 🗳 Revealed Votes"
            )

            revealed_rows = []

            for user in room["users"]:

                revealed_rows.append(
                    {
                        "Participant": user,
                        "SP": room["sp_votes"].get(user, ""),
                        "Dev Days": room["dev_votes"].get(user, ""),
                        "QA Days": room["qa_votes"].get(user, "")
                    }
                )

            if revealed_rows:

                revealed_df = pd.DataFrame(
                    revealed_rows
                )
                
                st.dataframe(
                    revealed_df,
                    hide_index=True,
                    use_container_width=False
                )

            
            sp_votes = []
            dev_votes = []
            qa_votes = []
            
            for vote in room["sp_votes"].values():
            
                try:
                    sp_votes.append(float(vote))
                except:
                    pass
            
            for vote in room["dev_votes"].values():
            
                try:
                    dev_votes.append(float(vote))
                except:
                    pass
            
            for vote in room["qa_votes"].values():
            
                try:
                    qa_votes.append(float(vote))
                except:
                    pass
            
            if sp_votes:
            
                average_sp = (
                    sum(sp_votes)
                    / len(sp_votes)
                )
            
                median_sp = (
                    sorted(
                        sp_votes
                    )[len(sp_votes)//2]
                )
            
                average_dev = (
                    sum(dev_votes)
                    / len(dev_votes)
                    if dev_votes else 0
                )
            
                average_qa = (
                    sum(qa_votes)
                    / len(qa_votes)
                    if qa_votes else 0
                )

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric(
                        "Average SP",
                        f"{average_sp:.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Median SP",
                        median_sp
                    )
                
                with col3:

                    st.session_state.final_sp = st.number_input(
                        "Final SP",
                        value=float(round(average_sp)),
                        step=1.0,
                        key="final_sp"
                    )
                
                with col4:

                    st.session_state.final_dev_days = st.number_input(
                        "Dev Days",
                        value=float(round(average_dev, 1)),
                        step=0.5,
                        key="final_dev_days"
                    )
                
                with col5:

                    st.session_state.final_qa_days = st.number_input(
                        "QA Days",
                        value=float(round(average_qa, 1)),
                        step=0.5,
                        key="final_qa_days"
                    )

                st.success(
                    f"✅ Final SP Selected: {st.session_state.final_sp}"
                )
    st.divider()

    st.markdown(
        "### 📋 Refinement History"
    )

    history = room.get(
        "history",
        []
    )

    if history:

        st.table(
            pd.DataFrame(history)
        )

    else:

        st.info(
            "No completed user stories yet."
        )            



# =========================
# PARTICIPANT
# =========================

else:
    # Keep participant screens synced with admin actions
    if st.session_state.get("room_code"):
        st_autorefresh(
            interval=2000,
            key=f"sync_{st.session_state.room_code}"
        )
    col1, col2 = st.columns([3,1])

    with col1:
        st.subheader(
            f"👤 {st.session_state.display_name}"
        )
    
    with col2:
        if st.session_state.room_code:
    
            rooms = load_rooms()
    
            current_room = rooms.get(
                st.session_state.room_code,
                {}
            )
    
            participant_count = len(
                current_room.get("users", [])
            )
    
            st.info(
                f"🏠 {st.session_state.room_code}"
            )
    
            st.caption(
                f"👥 {participant_count} participant(s)"
            )

    if not st.session_state.room_code:

        col1, col2, col3 = st.columns([2,1,4])
    
        with col1:
            room_code = st.text_input(
                "Room Code",
                placeholder="SPRINT PLANNING"
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
    
                st.rerun()
    
    else:
    
        st.success(
            f"✅ Connected to Room: {st.session_state.room_code}"
        )

# =========================
# VOTING SECTION
# =========================

if st.session_state.room_code:

    st.divider()

    st.subheader(
        f"🗳 Voting Room: {st.session_state.room_code}"
    )

    rooms = load_rooms()

    room = rooms.get(
        st.session_state.room_code,
        {}
    )

    if room.get("current_story"):

        st.success(
            f"📋 Current User Story: {room['current_story']}"
        )

    voting_locked = room.get(
        "revealed",
        False
    )

    if voting_locked:

        st.warning(
            "🔒 Voting is locked. Admin has revealed votes."
        )

    st.markdown("### Story Points")

    cols = st.columns(7)

    for i, point in enumerate(STORY_POINTS):

        with cols[i]:

            if st.button(
                point,
                key=f"sp_{point}",
                use_container_width=True,
                disabled=voting_locked
            ):

                st.session_state.selected_vote = point

                rooms = load_rooms()

                rooms[
                    st.session_state.room_code
                ]["sp_votes"][
                    st.session_state.display_name
                ] = point

                save_rooms(rooms)

    st.markdown("### 💻 Dev Completion (Days)")

    dev_cols = st.columns(7)
    
    for i, day in enumerate(DAY_ESTIMATES):
    
        with dev_cols[i]:
    
            if st.button(
                day,
                key=f"dev_{day}",
                use_container_width=True,
                disabled=voting_locked
            ):
    
                st.session_state.selected_dev_vote = day
    
                rooms = load_rooms()
    
                rooms[
                    st.session_state.room_code
                ]["dev_votes"][
                    st.session_state.display_name
                ] = day
    
                save_rooms(rooms)

    st.markdown("### 🧪 Testing Completion (Days)")

    qa_cols = st.columns(7)
    
    for i, day in enumerate(DAY_ESTIMATES):
    
        with qa_cols[i]:
    
            if st.button(
                day,
                key=f"qa_{day}",
                use_container_width=True,
                disabled=voting_locked
            ):
    
                st.session_state.selected_qa_vote = day
    
                rooms = load_rooms()
    
                rooms[
                    st.session_state.room_code
                ]["qa_votes"][
                    st.session_state.display_name
                ] = day
    
                save_rooms(rooms)
                
    st.markdown("### Fun Cards")

    fun_cols = st.columns(5)

    for i, (emoji, description) in enumerate(
        FUN_CARDS.items()
    ):

        with fun_cols[i % 5]:

            if st.button(
                f"{emoji}\n{description}",
                key=f"fun_{emoji}_{i}",
                use_container_width=True,
                disabled=voting_locked
            ):

                selected_value = (
                    f"{emoji} {description}"
                )

                st.session_state.selected_vote = (
                    selected_value
                )

                rooms = load_rooms()

                rooms[
                    st.session_state.room_code
                ]["fun_cards"][
                    st.session_state.display_name
                ] = selected_value

                save_rooms(rooms)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.selected_vote:
            st.metric(
                "Story Points",
                st.session_state.selected_vote
            )
    
    with col2:
        if st.session_state.selected_dev_vote:
            st.metric(
                "Dev Days",
                st.session_state.selected_dev_vote
            )
    
    with col3:
        if st.session_state.selected_qa_vote:
            st.metric(
                "QA Days",
                st.session_state.selected_qa_vote
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
