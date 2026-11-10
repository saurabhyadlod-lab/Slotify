import json
import os
from datetime import datetime
import streamlit as st
from abc import ABC, abstractmethod

# -------------------- SETTINGS --------------------
st.set_page_config(
    page_title="SmartPark | Parking Management",
    page_icon="🅿️",
    layout="wide"
)

DATA_FILE = "parking_data.json"
TOTAL_SLOTS = 10
RATE_PER_HOUR = 20


# -------------------- DESIGN --------------------
st.markdown("""
<style>
    .stApp { background: #0b1110; color: #edf5ef; }
    [data-testid="stSidebar"] { background: #101a17; border-right: 1px solid #263a31; }
    h1, h2, h3 { color: #f1f7f2 !important; }
    p, label, span { color: #d4e1d8; }
    .hero {
        background: linear-gradient(120deg, #14251e, #102019);
        border: 1px solid #315542; border-radius: 18px;
        padding: 24px 28px; margin-bottom: 18px;
    }
    .hero-title { font-size: 30px; font-weight: 800; color: #f4fff6; }
    .hero-sub { color: #a9c2b1; font-size: 14px; margin-top: 5px; }
    .metric-card {
        background: #14201b; border: 1px solid #294536;
        border-radius: 15px; padding: 17px 18px; min-height: 108px;
    }
    .metric-label { color: #9bb5a4; font-size: 13px; }
    .metric-value { color: #f3fff5; font-size: 29px; font-weight: 800; margin-top: 5px; }
    .slot {
        border-radius: 13px; padding: 14px 8px; text-align: center;
        border: 1px solid; min-height: 95px; margin-bottom: 8px;
    }
    .free { background: #153b2b; border-color: #2b8054; }
    .busy { background: #3a2224; border-color: #925052; }
    .slot-name { font-size: 13px; font-weight: 800; color: #f4fff6; }
    .slot-status { font-size: 12px; margin-top: 7px; color: #c8d9ce; }
    .section-note { color: #9bb5a4; font-size: 13px; }
    div.stButton > button {
        background: #1c7048; color: white; border: 1px solid #399568;
        border-radius: 10px; font-weight: 700; min-height: 42px;
    }
    div.stButton > button:hover { background: #258858; color: white; border-color: #59b985; }
    div[data-testid="stForm"] {
        background: #111c17; border: 1px solid #294536;
        border-radius: 14px; padding: 18px;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background: #17251e; color: #f4fff6;
    }
    hr { border-color: #294536; }
    .foot { color: #779384; font-size: 12px; text-align: center; padding: 20px 0 5px; }
</style>
""", unsafe_allow_html=True)


# -------------------- OOP PARKING LOGIC --------------------
class ParkingPolicy(ABC):
    @abstractmethod
    def calculate_fee(self, hours):
        pass


class StandardParking(ParkingPolicy):
    def calculate_fee(self, hours):
        return round(hours * RATE_PER_HOUR, 2)


class Vehicle:
    def __init__(self, number):
        self.number = number.strip().upper()


class Car(Vehicle):
    def show(self):
        return self.number


class SmartPark:
    def __init__(self):
        self.slots = {f"P{i:02d}": None for i in range(1, TOTAL_SLOTS + 1)}
        self.history = []
        self.policy = StandardParking()
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                saved_slots = data.get("slots", {})
                for slot in self.slots:
                    self.slots[slot] = saved_slots.get(slot)
                self.history = data.get("history", [])
            except (json.JSONDecodeError, OSError, AttributeError):
                self.history = []

    def save_data(self):
        data = {"slots": self.slots, "history": self.history}
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def park_vehicle(self, number):
        number = number.strip().upper()
        if not number:
            return False, "Enter a vehicle registration number."
        if number in self.slots.values():
            return False, "This vehicle is already parked."
        for slot, vehicle in self.slots.items():
            if vehicle is None:
                car = Car(number)
                self.slots[slot] = car.show()
                self.history.append({
                    "vehicle": number,
                    "slot": slot,
                    "entry_time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "exit_time": None,
                    "hours": None,
                    "fee": None,
                    "status": "Parked"
                })
                self.save_data()
                return True, f"{number} assigned to {slot}."
        return False, "Parking is full. No slot is currently available."

    def remove_vehicle(self, number, hours):
        number = number.strip().upper()
        if hours <= 0:
            return False, "Parking duration must be greater than zero."
        for slot, vehicle in self.slots.items():
            if vehicle == number:
                fee = self.policy.calculate_fee(hours)
                self.slots[slot] = None
                for record in reversed(self.history):
                    if record["vehicle"] == number and record["status"] == "Parked":
                        record["exit_time"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
                        record["hours"] = hours
                        record["fee"] = fee
                        record["status"] = "Completed"
                        break
                self.save_data()
                return True, f"{number} checked out from {slot}. Total fee: ₹{fee:.2f}"
        return False, "Vehicle not found in the parking area."

    def get_summary(self):
        available = sum(vehicle is None for vehicle in self.slots.values())
        occupied = TOTAL_SLOTS - available
        completed = sum(r.get("status") == "Completed" for r in self.history)
        revenue = sum((r.get("fee") or 0) for r in self.history)
        return available, occupied, completed, revenue


# -------------------- LOAD APP DATA --------------------
if "parking" not in st.session_state:
    st.session_state.parking = SmartPark()

parking = st.session_state.parking
available, occupied, completed, revenue = parking.get_summary()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## 🅿️ SmartPark")
    st.caption("PARKING MANAGEMENT SYSTEM")
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Vehicle Entry / Exit", "Parking History"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("**Parking facility**")
    st.caption(f"{TOTAL_SLOTS} total spaces")
    st.caption(f"Rate: ₹{RATE_PER_HOUR} per hour")
    st.caption("Software simulation")
    st.divider()
    st.caption("SmartPark • Python project")


# -------------------- HEADER --------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">Smart parking. Made simple.</div>
    <div class="hero-sub">Monitor spaces, manage vehicle movement and keep parking records in one place.</div>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    st.subheader("Overview")
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "TOTAL SPACES", TOTAL_SLOTS),
        (c2, "AVAILABLE", available),
        (c3, "OCCUPIED", occupied),
        (c4, "TOTAL REVENUE", f"₹{revenue:.0f}")
    ]
    for col, label, value in cards:
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("")
    left, right = st.columns([1.7, 1])
    with left:
        st.subheader("Live parking layout")
        st.markdown('<div class="section-note">Green = available &nbsp; • &nbsp; Red = occupied</div>', unsafe_allow_html=True)
        slot_items = list(parking.slots.items())
        for start in range(0, len(slot_items), 5):
            row = st.columns(5)
            for col, (slot, vehicle) in zip(row, slot_items[start:start + 5]):
                is_free = vehicle is None
                status = "AVAILABLE" if is_free else "OCCUPIED"
                detail = "Ready to use" if is_free else vehicle
                css = "free" if is_free else "busy"
                with col:
                    st.markdown(
                        f'<div class="slot {css}"><div class="slot-name">▣ {slot}</div>'
                        f'<div class="slot-status">{status}<br>{detail}</div></div>',
                        unsafe_allow_html=True
                    )
    with right:
        st.subheader("Occupancy")
        occupancy_pct = int((occupied / TOTAL_SLOTS) * 100)
        st.metric("Spaces in use", f"{occupancy_pct}%")
        st.progress(occupancy_pct / 100)
        st.caption(f"{occupied} occupied out of {TOTAL_SLOTS} spaces")
        st.divider()
        st.metric("Completed sessions", completed)
        st.caption("Total collected from completed parking sessions")

    st.divider()
    st.subheader("Quick actions")
    q1, q2 = st.columns(2)
    with q1:
        if st.button("＋ Register a vehicle", use_container_width=True):
            st.session_state["go_to_entry"] = True
            st.rerun()
    with q2:
        if st.button("View parking history", use_container_width=True):
            st.session_state["go_to_history"] = True
            st.rerun()

    if st.session_state.pop("go_to_entry", False):
        st.info("Choose **Vehicle Entry / Exit** from the left navigation to register a vehicle.")
    if st.session_state.pop("go_to_history", False):
        st.info("Choose **Parking History** from the left navigation to see records.")

elif page == "Vehicle Entry / Exit":
    st.subheader("Vehicle management")
    entry_col, exit_col = st.columns(2)

    with entry_col:
        st.markdown("### 🚗 Vehicle entry")
        st.caption("Register a vehicle and assign the next free space.")
        with st.form("entry_form"):
            vehicle_number = st.text_input("Vehicle registration number", placeholder="e.g. MH12AB1234")
            entry_submit = st.form_submit_button("Assign parking slot", use_container_width=True)
        if entry_submit:
            success, message = parking.park_vehicle(vehicle_number)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with exit_col:
        st.markdown("### ↗ Vehicle exit")
        st.caption("Release the vehicle's space and calculate its fee.")
        active_vehicles = [v for v in parking.slots.values() if v is not None]
        with st.form("exit_form"):
            selected_vehicle = st.selectbox(
                "Select parked vehicle",
                options=active_vehicles,
                placeholder="No vehicles currently parked"
            )
            hours = st.number_input("Parking duration (hours)", min_value=0.0, value=1.0, step=0.5)
            st.caption(f"Rate: ₹{RATE_PER_HOUR} per hour")
            exit_submit = st.form_submit_button("Check out vehicle", use_container_width=True)
        if exit_submit:
            if selected_vehicle:
                success, message = parking.remove_vehicle(selected_vehicle, hours)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("There are no vehicles to check out.")

    st.divider()
    st.subheader("Currently parked vehicles")
    active_records = [r for r in parking.history if r.get("status") == "Parked"]
    if active_records:
        st.dataframe(
            [{"Vehicle": r["vehicle"], "Slot": r["slot"], "Entry time": r["entry_time"]}
             for r in active_records],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No vehicles are currently parked.")

elif page == "Parking History":
    st.subheader("Parking history")
    st.caption("A record of vehicle entries and completed parking sessions.")
    if parking.history:
        rows = []
        for record in reversed(parking.history):
            rows.append({
                "Vehicle": record.get("vehicle"),
                "Slot": record.get("slot"),
                "Entry": record.get("entry_time"),
                "Exit": record.get("exit_time") or "—",
                "Duration (hrs)": record.get("hours") if record.get("hours") is not None else "—",
                "Fee": f"₹{record['fee']:.2f}" if record.get("fee") is not None else "Pending",
                "Status": record.get("status")
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.download_button(
            "Download history as JSON",
            data=json.dumps(parking.history, indent=4),
            file_name="smartpark_history.json",
            mime="application/json"
        )
    else:
        st.info("No parking records yet. Register a vehicle to create the first record.")

st.markdown('<div class="foot">SMARTPARK • A Python-based parking management project • Simulation only</div>', unsafe_allow_html=True)
