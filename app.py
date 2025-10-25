import streamlit as st
import json
import os
import datetime
from hashlib import sha256

# ---------------- Data Files ----------------
PATIENT_FILE = "patients.json"
DOCTOR_FILE = "doctors.json"
USER_FILE = "users.json"

# ---------------- Load / Save JSON ----------------
def load_records(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_records(file, records):
    with open(file, "w") as f:
        json.dump(records, f, indent=4)

# ---------------- User Functions ----------------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):  # Ensure it's a dict
                return data
            else:
                return {}
    return {}

def save_users(users):
    save_records(USER_FILE, users)

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def verify_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def add_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

# ---------------- Initialize Data ----------------
patients = load_records(PATIENT_FILE)
doctors = load_records(DOCTOR_FILE)

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="Hospital Management System", page_icon="🏥", layout="wide")

# Common CSS
st.markdown("""
<style>
body { background: linear-gradient(to right, #e6f7ff, #f0faff); font-family: 'Segoe UI', sans-serif; }
h1 { text-align: center; color: #0073e6; font-size: 3rem; margin-bottom: 40px; }
.page-card { background: white; border-radius: 25px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
.stButton>button { background-color: #0073e6; color:white; padding:10px 20px; border-radius:10px; font-weight:bold; }
.stButton>button:hover { background-color:#005bb5; }
</style>
""", unsafe_allow_html=True)

# ---------------- Login / Sign Up ----------------
if not st.session_state.logged_in:
    st.markdown("<h1>🏥 Hospital Management System 🏥</h1>", unsafe_allow_html=True)
    auth_choice = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)

    if auth_choice == "Sign Up":
        st.subheader("Create a new account")
        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if new_user and new_pass:
                if add_user(new_user, new_pass):
                    st.success("✅ Account created! Please login now.")
                else:
                    st.warning("⚠ Username already exists.")
            else:
                st.warning("⚠ Fill all fields.")

    elif auth_choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome {username}!")
            else:
                st.error("❌ Invalid username or password")

# ---------------- Main App ----------------
if st.session_state.logged_in:
    st.sidebar.title(f"Welcome, {st.session_state.username} 🏥")
    menu = st.sidebar.radio("Navigation", ["Home", "Add Patient", "View Patients", "Add Doctor", "View Doctors", "Logout"])

    # ---------------- Home ----------------
    if menu == "Home":
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("Welcome to Hospital Management System")
        st.write("Add patients, doctors and manage hospital data easily!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Add Patient ----------------
    elif menu == "Add Patient":
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("Add New Patient")
        with st.form("patient_form"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            city = st.text_input("City")
            doctor = st.selectbox("Assign Doctor", [d['name'] for d in doctors] if doctors else ["No doctor available"])
            submitted = st.form_submit_button("Add Patient")

        if submitted:
            if name and city and doctor and doctor != "No doctor available":
                patient_id = len(patients) + 1
                data = {"id": patient_id, "name": name, "age": age, "gender": gender, "city": city, "doctor": doctor, "timestamp": str(datetime.datetime.now())}
                patients.append(data)
                save_records(PATIENT_FILE, patients)
                st.success(f"✅ Patient {name} added successfully with ID {patient_id}!")
            else:
                st.warning("⚠ Please fill all fields and select a doctor.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- View Patients ----------------
    elif menu == "View Patients":
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("All Patients")
        if not patients:
            st.info("No patient records found.")
        else:
            search_name = st.text_input("Search by Name")
            filtered_patients = [p for p in patients if search_name.lower() in p['name'].lower()]
            for p in filtered_patients:
                st.markdown(f"""
                    <div style='background:#e6f7ff;padding:15px;border-radius:15px;margin-bottom:10px;'>
                    <h4 style='margin:0;color:#0073e6;'>Patient #{p['id']} - {p['name']}</h4>
                    <p><strong>Age:</strong> {p['age']}, <strong>Gender:</strong> {p['gender']}</p>
                    <p><strong>City:</strong> {p['city']}, <strong>Doctor:</strong> {p['doctor']}</p>
                    <p style='font-size:0.8em;color:gray;'>Added on: {p['timestamp']}</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Add Doctor ----------------
    elif menu == "Add Doctor":
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("Add New Doctor")
        with st.form("doctor_form"):
            name = st.text_input("Doctor Name")
            specialization = st.text_input("Specialization")
            city = st.text_input("City")
            submitted = st.form_submit_button("Add Doctor")

        if submitted:
            if name and specialization and city:
                doctor_id = len(doctors) + 1
                data = {"id": doctor_id, "name": name, "specialization": specialization, "city": city, "timestamp": str(datetime.datetime.now())}
                doctors.append(data)
                save_records(DOCTOR_FILE, doctors)
                st.success(f"✅ Doctor {name} added successfully with ID {doctor_id}!")
            else:
                st.warning("⚠ Please fill all fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- View Doctors ----------------
    elif menu == "View Doctors":
        st.markdown('<div class="page-card">', unsafe_allow_html=True)
        st.subheader("All Doctors")
        if not doctors:
            st.info("No doctor records found.")
        else:
            search_name = st.text_input("Search by Name")
            filtered_doctors = [d for d in doctors if search_name.lower() in d['name'].lower()]
            for d in filtered_doctors:
                st.markdown(f"""
                    <div style='background:#f0faff;padding:15px;border-radius:15px;margin-bottom:10px;'>
                    <h4 style='margin:0;color:#0073e6;'>Doctor #{d['id']} - {d['name']}</h4>
                    <p><strong>Specialization:</strong> {d['specialization']}</p>
                    <p><strong>City:</strong> {d['city']}</p>
                    <p style='font-size:0.8em;color:gray;'>Added on: {d['timestamp']}</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Logout ----------------
    elif menu == "Logout":
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("✅ Logged out successfully! Please login again.")