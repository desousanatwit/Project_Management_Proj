import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
#
#   UI Layout 
#   todo: Add a side bar with buttons to navigate between differnet pages
#   todo: Pages will include: Home, Schedule, Add Shift, etc
#---------------
#st.markdown("<h1 style='text-align: center;'>Scheduling</h1>", unsafe_allow_html=True)
#st.markdown("---")
 
#left, right = st.columns(2)

#with left:
    #st.markdown("<h3>Menu</h3>", unsafe_allow_html=True)
#with right:
   # st.markdown("<h3>Home</h3>", unsafe_allow_html=True)
    


st.set_page_config(page_title="Scheduling App", page_icon="📅", layout="wide")

# --------------------------
# Session State Setup
# --------------------------
def init_state():
    if "employees" not in st.session_state:
        st.session_state.employees = [
            "Arianna",
            "Noah",
            "Vincent",
            "Adrien",
            "jordan"
        ]

    if "shifts" not in st.session_state:
        today = date.today()
        st.session_state.shifts = [
            {
                "id": 1,
                "employee": "Arianna",
                "shift_date": today,
                "start": "09:00 AM",
                "end": "05:00 PM",
                "role": "Front Desk",
                "status": "Scheduled"
            },
            {
                "id": 2,
                "employee": "Jordan",
                "shift_date": today + timedelta(days=1),
                "start": "10:00 AM",
                "end": "06:00 PM",
                "role": "Support",
                "status": "Scheduled"
            }
        ]

    if "next_shift_id" not in st.session_state:
        st.session_state.next_shift_id = 3

    if "time_log" not in st.session_state:
        st.session_state.time_log = []

    if "swap_requests" not in st.session_state:
        st.session_state.swap_requests = []

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"


init_state()


# --------------------------
# Helpers
# --------------------------
def format_time(t: time) -> str:
    return t.strftime("%I:%M %p")


def get_shifts_df():
    df = pd.DataFrame(st.session_state.shifts)
    if not df.empty:
        df = df.sort_values(by=["shift_date", "start", "employee"]).reset_index(drop=True)
    return df


def get_time_log_df():
    df = pd.DataFrame(st.session_state.time_log)
    if not df.empty:
        df = df.sort_values(by=["timestamp"], ascending=False).reset_index(drop=True)
    return df


def get_swap_df():
    df = pd.DataFrame(st.session_state.swap_requests)
    if not df.empty:
        df = df.sort_values(by=["request_id"], ascending=False).reset_index(drop=True)
    return df


def employee_is_clocked_in(employee_name: str) -> bool:
    logs = [x for x in st.session_state.time_log if x["employee"] == employee_name]
    if not logs:
        return False
    return logs[-1]["action"] == "Clock In"


def clock_in(employee_name: str):
    if employee_is_clocked_in(employee_name):
        st.warning(f"{employee_name} is already clocked in.")
        return

    st.session_state.time_log.append({
        "employee": employee_name,
        "action": "Clock In",
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    })
    st.success(f"{employee_name} clocked in successfully.")


def clock_out(employee_name: str):
    if not employee_is_clocked_in(employee_name):
        st.warning(f"{employee_name} is not currently clocked in.")
        return

    st.session_state.time_log.append({
        "employee": employee_name,
        "action": "Clock Out",
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    })
    st.success(f"{employee_name} clocked out successfully.")


def add_shift(employee, shift_date, start_time, end_time, role):
    st.session_state.shifts.append({
        "id": st.session_state.next_shift_id,
        "employee": employee,
        "shift_date": shift_date,
        "start": format_time(start_time),
        "end": format_time(end_time),
        "role": role,
        "status": "Scheduled"
    })
    st.session_state.next_shift_id += 1


def request_shift_swap(from_employee, shift_id, to_employee, note):
    shift = next((s for s in st.session_state.shifts if s["id"] == shift_id), None)
    if shift is None:
        st.error("Shift not found.")
        return

    if shift["employee"] != from_employee:
        st.error("That shift does not belong to the selected employee.")
        return

    request_id = len(st.session_state.swap_requests) + 1
    st.session_state.swap_requests.append({
        "request_id": request_id,
        "shift_id": shift_id,
        "from_employee": from_employee,
        "to_employee": to_employee,
        "shift_date": shift["shift_date"],
        "start": shift["start"],
        "end": shift["end"],
        "role": shift["role"],
        "note": note,
        "status": "Pending"
    })


def approve_swap(request_id):
    request = next((r for r in st.session_state.swap_requests if r["request_id"] == request_id), None)
    if request is None or request["status"] != "Pending":
        return

    shift = next((s for s in st.session_state.shifts if s["id"] == request["shift_id"]), None)
    if shift:
        shift["employee"] = request["to_employee"]

    request["status"] = "Approved"


def deny_swap(request_id):
    request = next((r for r in st.session_state.swap_requests if r["request_id"] == request_id), None)
    if request and request["status"] == "Pending":
        request["status"] = "Denied"


# --------------------------
# Sidebar Navigation
# --------------------------
with st.sidebar:
    st.title("📋 Scheduling App")
    st.markdown("Use the menu below to move through the app.")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = "Home"
    if st.button("📅 Schedule", use_container_width=True):
        st.session_state.current_page = "Schedule"
    if st.button("➕ Add Shift", use_container_width=True):
        st.session_state.current_page = "Add Shift"
    if st.button("⏱ Clock In / Out", use_container_width=True):
        st.session_state.current_page = "Clock"
    if st.button("🔄 Shift Swaps", use_container_width=True):
        st.session_state.current_page = "Swaps"

    st.markdown("---")
    st.subheader("Team Members")
    for emp in st.session_state.employees:
        st.write(f"• {emp}")


# --------------------------
# Pages
# --------------------------
def home_page():
    st.markdown("<h1 style='text-align: center;'>Scheduling</h1>", unsafe_allow_html=True)
    st.markdown("---")

    total_employees = len(st.session_state.employees)
    total_shifts = len(st.session_state.shifts)
    pending_swaps = len([r for r in st.session_state.swap_requests if r["status"] == "Pending"])
    clocked_in_count = sum(employee_is_clocked_in(emp) for emp in st.session_state.employees)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Employees", total_employees)
    col2.metric("Scheduled Shifts", total_shifts)
    col3.metric("Pending Swap Requests", pending_swaps)
    col4.metric("Clocked In Now", clocked_in_count)

    st.markdown("### Upcoming Shifts")
    df = get_shifts_df()
    if df.empty:
        st.info("No shifts scheduled yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### Recent Time Activity")
    log_df = get_time_log_df()
    if log_df.empty:
        st.info("No clock activity yet.")
    else:
        st.dataframe(log_df.head(5), use_container_width=True, hide_index=True)


def schedule_page():
    st.title("📅 Schedule")

    df = get_shifts_df()
    if df.empty:
        st.info("No shifts available.")
        return

    employees = ["All"] + st.session_state.employees
    selected_employee = st.selectbox("Filter by employee", employees)

    start_filter = st.date_input("Show shifts starting from", value=date.today())

    filtered_df = df.copy()
    filtered_df["shift_date"] = pd.to_datetime(filtered_df["shift_date"]).dt.date
    filtered_df = filtered_df[filtered_df["shift_date"] >= start_filter]

    if selected_employee != "All":
        filtered_df = filtered_df[filtered_df["employee"] == selected_employee]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.markdown("### Delete a Shift")
    shift_ids = [shift["id"] for shift in st.session_state.shifts]
    if shift_ids:
        delete_id = st.selectbox("Choose shift ID to delete", shift_ids)
        if st.button("Delete Shift"):
            st.session_state.shifts = [s for s in st.session_state.shifts if s["id"] != delete_id]
            st.success(f"Shift {delete_id} deleted.")
            st.rerun()


def add_shift_page():
    st.title("➕ Add Shift")

    with st.form("add_shift_form"):
        employee = st.selectbox("Employee", st.session_state.employees)
        shift_date = st.date_input("Shift Date", value=date.today())
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", value=time(9, 0))
        with col2:
            end_time = st.time_input("End Time", value=time(17, 0))
        role = st.text_input("Role / Position", placeholder="Example: Front Desk")

        submitted = st.form_submit_button("Add Shift")

        if submitted:
            if end_time <= start_time:
                st.error("End time must be after start time.")
            elif not role.strip():
                st.error("Please enter a role.")
            else:
                add_shift(employee, shift_date, start_time, end_time, role.strip())
                st.success("Shift added successfully.")
                st.rerun()


def clock_page():
    st.title("⏱ Clock In / Clock Out")

    employee = st.selectbox("Select Employee", st.session_state.employees)

    status = "Clocked In" if employee_is_clocked_in(employee) else "Clocked Out"
    st.info(f"Current status for {employee}: {status}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clock In", use_container_width=True):
            clock_in(employee)
            st.rerun()
    with col2:
        if st.button("Clock Out", use_container_width=True):
            clock_out(employee)
            st.rerun()

    st.markdown("### Time Log")
    log_df = get_time_log_df()
    if log_df.empty:
        st.info("No time logs yet.")
    else:
        st.dataframe(log_df, use_container_width=True, hide_index=True)


def swaps_page():
    st.title("🔄 Shift Swaps")

    st.markdown("### Request a Shift Swap")
    employee = st.selectbox("Your Name", st.session_state.employees, key="swap_employee")

    employee_shifts = [s for s in st.session_state.shifts if s["employee"] == employee]

    if employee_shifts:
        shift_options = {
            f'ID {s["id"]} | {s["shift_date"]} | {s["start"]}-{s["end"]} | {s["role"]}': s["id"]
            for s in employee_shifts
        }

        selected_label = st.selectbox("Choose Your Shift", list(shift_options.keys()))
        selected_shift_id = shift_options[selected_label]

        other_workers = [e for e in st.session_state.employees if e != employee]
        to_employee = st.selectbox("Request Swap With", other_workers)
        note = st.text_area("Optional Note", placeholder="Can you take this shift for me?")

        if st.button("Submit Swap Request"):
            request_shift_swap(employee, selected_shift_id, to_employee, note)
            st.success("Swap request submitted.")
            st.rerun()
    else:
        st.info("This employee has no shifts to swap.")

    st.markdown("---")
    st.markdown("### Manage Swap Requests")

    swaps = get_swap_df()
    if swaps.empty:
        st.info("No shift swap requests yet.")
        return

    st.dataframe(swaps, use_container_width=True, hide_index=True)

    pending_ids = [r["request_id"] for r in st.session_state.swap_requests if r["status"] == "Pending"]
    if pending_ids:
        request_id = st.selectbox("Select Pending Request ID", pending_ids)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve Request", use_container_width=True):
                approve_swap(request_id)
                st.success("Swap approved.")
                st.rerun()
        with col2:
            if st.button("Deny Request", use_container_width=True):
                deny_swap(request_id)
                st.warning("Swap denied.")
                st.rerun()


# --------------------------
# Router
# --------------------------
page = st.session_state.current_page

if page == "Home":
    home_page()
elif page == "Schedule":
    schedule_page()
elif page == "Add Shift":
    add_shift_page()
elif page == "Clock":
    clock_page()
elif page == "Swaps":
    swaps_page()