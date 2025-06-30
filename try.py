import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from streamlit_option_menu import option_menu
from streamlit_card import card
import json
import os # Import os for directory creation
import base64 # Import base64 for image embedding
# Removed: from streamlit_lottie import st_lottie # No longer needed if removing Lottie animations

# --- Debugging & Error Handling Setup ---
# Set a flag to enable/disable debug messages
DEBUG_MODE = True

def debug_print(message):
    if DEBUG_MODE:
        st.sidebar.info(f"DEBUG: {message}") # Print debug messages in sidebar for visibility

# --- Utility Function to get Base64 image ---
@st.cache_data
def get_image_base64(image_path):
    """Reads an image file and returns its Base64 encoded string."""
    debug_print(f"Attempting to load image as Base64 from: {image_path}")
    try:
        if not os.path.exists(image_path):
            st.error(f"Image file not found at: {image_path}")
            return None
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error encoding image '{image_path}' to Base64: {e}")
        return None

# --- Caching Functions for Performance ---

# Removed: @st.cache_data for load_lottie as it's no longer used
# def load_lottie(path):
#     """Loads a Lottie animation JSON file."""
#     debug_print(f"Attempting to load Lottie from: {path}")
#     try:
#         if not os.path.exists(path):
#             st.error(f"Lottie file not found at: {path}")
#             return None
#         with open(path, "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         st.error(f"Lottie animation file not found at: {path}")
#         return None
#     except json.JSONDecodeError:
#         st.error(f"Error decoding JSON from Lottie file: {path}. Please ensure it's valid JSON.")
#         return None
#     except Exception as e:
#         st.error(f"An unexpected error occurred while loading Lottie: {e}")
#         return None

@st.cache_data(ttl=600) # Cache logs for 10 minutes
def get_logs_cached(username):
    """Fetches user upload logs from the database with caching."""
    debug_print(f"Fetching logs for user: {username}")
    conn = get_connection()
    if conn is None:
        st.error("Could not establish database connection for fetching logs.")
        return []
    c = conn.cursor()
    try:
        c.execute("SELECT filename, upload_time FROM user_uploads WHERE username=%s ORDER BY upload_time DESC", (username,))
        rows = c.fetchall()
        return rows
    except mysql.connector.Error as err:
        st.error(f"Database error fetching logs: {err}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching logs: {e}")
        return []
    finally:
        c.close()
        conn.close()

# --- Custom CSS for Enhanced UI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

/* General body and main content styling */
html, body, [data-testid="stAppViewContainer"] {
    /* Professional and cool, subtle live gradient background */
    background: linear-gradient(135deg, #0A192F 0%, #172A45 50%, #0A192F 100%); /* Deep Navy to Dark Blue */
    background-size: 400% 400%;
    animation: gradientShift 20s ease infinite; /* Slower, smoother animation */
    font-family: 'Inter', sans-serif; /* Using Inter font */
    color: #E6F1FF; /* Light blue-white text for dark background */
    overflow-x: hidden; /* Prevent horizontal scroll */
}

/* Subtle animated grid/data flow overlay */
html::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: linear-gradient(0deg, rgba(255,255,255,0.02) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 50px 50px; /* Adjust grid size */
    opacity: 0.1; /* Very subtle */
    z-index: -1;
    animation: gridMovement 60s linear infinite; /* Slow grid movement */
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes gridMovement {
    0% { background-position: 0 0; }
    100% { background-position: 50px 50px; } /* Move by one grid cell */
}


.main {
    background-color: rgba(10, 25, 47, 0.7); /* More opaque, dark navy overlay */
    backdrop-filter: blur(8px); /* Stronger blur effect */
    border-radius: 18px; /* Slightly less rounded */
    padding: 30px; /* More padding */
    margin: 25px; /* More margin */
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5); /* Deeper shadow */
    border: 1px solid rgba(255, 255, 255, 0.1); /* Subtle border */
}

/* Ensure the main content block takes full width within the wide layout */
.block-container {
    padding-top: 2.5rem; /* More padding at the top of the content */
    padding-bottom: 2.5rem; /* More padding at the bottom */
    padding-left: 6%; /* Adjust left/right padding for content margin */
    padding-right: 6%;
}

/* Header logo and title styling for the main content area */
.header-logo {
    display: flex;
    align-items: center;
    justify-content: center; /* Center the header logo and text */
    gap: 25px; /* Increased gap */
    margin-bottom: 50px; /* More space below header */
    padding: 40px 0; /* More padding for header area */
    border-bottom: 2px solid rgba(255, 255, 255, 0.15); /* Lighter, more subtle separator */
}
.header-logo img {
    height: 90px; /* Larger logo */
    filter: drop-shadow(0 0 15px rgba(0, 200, 255, 0.6)); /* Subtle blue glow effect on logo */
}
.header-logo h1 {
    color: #64FFDA; /* Bright accent color for the title */
    margin: 0; /* Remove default margin from h1 */
    font-size: 3.5rem; /* Even larger title font */
    font-weight: 800; /* Bolder font */
    text-shadow: 0 0 15px rgba(100, 255, 218, 0.4); /* Text shadow for glow */
}

/* Streamlit card styling */
.st-emotion-cache-1r6dm1x { /* Target for streamlit_card, may change with versions */
    border-radius: 15px; /* Slightly less rounded */
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); /* Stronger shadow for depth */
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out; /* Smooth hover effect */
    background: rgba(255, 255, 255, 0.08); /* More transparent background for cards */
    backdrop-filter: blur(10px); /* Stronger blur effect for cards */
    border: 1px solid rgba(255, 255, 255, 0.15); /* Subtle white border */
    color: #E6F1FF; /* Light blue-white text for cards */
    padding: 25px; /* More padding */
}
.st-emotion-cache-1r6dm1x:hover {
    transform: translateY(-12px); /* Lift card more on hover */
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6); /* Enhanced shadow on hover */
}
.st-emotion-cache-1r6dm1x p { /* Text inside cards */
    color: #E6F1FF;
}

/* Improve button styling */
.stButton>button {
    background: linear-gradient(45deg, #64FFDA, #00C6FF); /* Teal to Cyan gradient button */
    color: #0A192F; /* Dark text for bright button */
    border-radius: 12px; /* More rounded buttons */
    border: none;
    padding: 16px 35px; /* More padding */
    cursor: pointer;
    font-weight: 700; /* Bolder font */
    font-size: 1.15rem; /* Slightly larger font */
    transition: background 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
    box-shadow: 0 8px 20px rgba(100, 255, 218, 0.4); /* Teal shadow */
    text-transform: uppercase; /* Uppercase text */
    letter-spacing: 1.5px; /* More letter spacing */
}
.stButton>button:hover {
    background: linear-gradient(45deg, #00C6FF, #64FFDA); /* Reverse gradient on hover */
    transform: translateY(-4px); /* Slight lift on hover */
    box-shadow: 0 12px 25px rgba(100, 255, 218, 0.6);
}

/* Input field styling */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stFileUploader>div>div>button {
    border-radius: 10px; /* Rounded inputs */
    border: 1px solid rgba(100, 255, 218, 0.4); /* Subtle teal border */
    padding: 16px; /* More padding */
    background-color: rgba(255, 255, 255, 0.08); /* Transparent background */
    color: #E6F1FF; /* Light blue-white text */
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3); /* Deeper inner shadow */
    transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
}
.stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder {
    color: rgba(230, 241, 255, 0.5); /* Lighter placeholder text */
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: #64FFDA; /* Teal border on focus */
    box-shadow: 0 0 0 0.4rem rgba(100, 255, 218, 0.3); /* Stronger focus glow */
    background-color: rgba(255, 255, 255, 0.12); /* Slightly less transparent on focus */
    outline: none;
}

/* Info and Success messages */
.stAlert {
    border-radius: 12px;
    padding: 1.5rem 2rem; /* More padding */
    font-size: 1.15rem;
    background-color: rgba(0, 0, 0, 0.5); /* Darker, semi-transparent background */
    color: #E6F1FF; /* White text */
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}
.stAlert > div[data-testid="stMarkdownContainer"] p { /* Target text inside alerts */
    color: #E6F1FF !important;
}

/* Sidebar styling - Only for the logo and debug messages now */
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #0A192F, #000000); /* Darker gradient for sidebar */
    color: #E6F1FF;
    box-shadow: 5px 0 20px rgba(0, 0, 0, 0.6);
}
.css-1lcbmhc.e1fqkh3o0 { /* Target for sidebar content wrapper */
    background-color: transparent; /* Let the gradient show through */
}
.css-1lcbmhc.e1fqkh3o0 .css-1qxtjkw.e1fqkh3o1 { /* Target for sidebar elements */
    color: #E6F1FF;
}

/* Specific styling for the login/signup container */
.login-container {
    max-width: 700px; /* Wider */
    margin: 100px auto; /* More margin */
    padding: 60px; /* More padding */
    background: rgba(10, 25, 47, 0.8); /* Opaque dark navy */
    backdrop-filter: blur(12px); /* Stronger blur effect */
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); /* Deeper shadow */
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.15); /* Subtle white border */
}
.login-container h2 {
    color: #64FFDA; /* Accent color text */
    font-size: 3.2rem; /* Larger font */
    margin-bottom: 30px;
    text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
}
.login-container p {
    color: #B0C4DE; /* Muted light blue text */
    font-size: 1.3rem;
    margin-bottom: 50px;
}
.login-container .stRadio > label {
    font-size: 1.25rem; /* Larger font */
    font-weight: 600;
    color: #E6F1FF; /* Light blue-white radio label */
}
.login-container .stRadio > label > div[data-testid="stFlex"] {
    justify-content: center; /* Center the radio buttons */
    gap: 40px; /* More space between radio buttons */
}
.login-container .stRadio > label > div[data-testid="stFlex"] > div {
    padding: 18px 40px; /* More padding */
    border-radius: 15px; /* More rounded */
    transition: background-color 0.3s, color 0.3s, box-shadow 0.3s;
    border: 2px solid #64FFDA; /* Teal border for radio buttons */
    color: #64FFDA; /* Teal text */
    background-color: rgba(100, 255, 218, 0.1); /* Transparent teal background */
    box-shadow: 0 6px 15px rgba(100, 255, 218, 0.2);
}
.login-container .stRadio > label > div[data-testid="stFlex"] > div:hover {
    background-color: rgba(100, 255, 218, 0.2);
    box-shadow: 0 8px 20px rgba(100, 255, 218, 0.3);
}
.login-container .stRadio > label > div[data-testid="stFlex"] > div[data-checked="true"] {
    background: linear-gradient(45deg, #64FFDA, #00C6FF); /* Teal to Cyan gradient for selected */
    color: #0A192F; /* Dark text for selected */
    box-shadow: 0 10px 25px rgba(100, 255, 218, 0.5);
    border-color: transparent; /* No border when selected with gradient */
}

/* Styling for the main app navigation menu */
.st-emotion-cache-1f8p7d2 { /* option_menu container */
    background-color: rgba(255, 255, 255, 0.1) !important; /* More transparent white */
    border-radius: 15px !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
    margin-bottom: 50px !important;
    border: 1px solid rgba(255, 255, 255, 0.15);
}
.st-emotion-cache-1f8p7d2 .st-emotion-cache-10qre6c { /* option_menu nav-link */
    color: #B0C4DE !important; /* Muted light blue text */
    font-weight: 600;
}
.st-emotion-cache-1f8p7d2 .st-emotion-cache-10qre6c:hover { /* option_menu nav-link hover */
    background-color: rgba(255, 255, 255, 0.08) !important; /* More subtle hover */
    border-radius: 10px;
}
.st-emotion-cache-1f8p7d2 .st-emotion-cache-10qre6c-selected { /* option_menu nav-link-selected */
    background: linear-gradient(45deg, #64FFDA, #00C6FF) !important; /* Teal to Cyan gradient for selected */
    color: #0A192F !important; /* Dark text for selected */
    border-radius: 10px;
    box-shadow: 0 6px 15px rgba(100, 255, 218, 0.4);
}
.st-emotion-cache-1f8p7d2 .st-emotion-cache-10qre6c-selected svg { /* Selected icon color */
    color: #0A192F !important;
}
</style>
""", unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(
    page_title="BizPulse Finance",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar collapsed by default
)

# --- Database Connection and Auth Functions ---
# IMPORTANT: Replace with your actual MySQL credentials
def get_connection():
    """Establishes and returns a MySQL database connection."""
    debug_print("Attempting to get database connection.")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="raman@1234",
            database="bizpulse_db"
        )
        debug_print("Database connection successful.")
        return conn
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}. Please ensure MySQL is running and credentials are correct.")
        debug_print(f"Database connection failed: {err}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during database connection: {e}")
        debug_print(f"Unexpected error during DB connection: {e}")
        return None

def create_user(u, p):
    """Creates a new user in the database."""
    debug_print(f"Attempting to create user: {u}")
    conn = get_connection()
    if conn is None: return False
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (u, p))
        conn.commit()
        debug_print(f"User {u} created successfully.")
        return True
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry error
            st.error("Username already exists. Please choose a different one.")
            debug_print(f"User creation failed: Username {u} already exists.")
        else:
            st.error(f"Error creating user: {err}")
            debug_print(f"User creation failed: {err}")
        conn.rollback()
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while creating user: {e}")
        debug_print(f"Unexpected error creating user: {e}")
        return False
    finally:
        c.close()
        conn.close()

def login_user(u, p):
    """Authenticates a user against the database."""
    debug_print(f"Attempting to login user: {u}")
    conn = get_connection()
    if conn is None: return None
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
        r = c.fetchone()
        if r:
            debug_print(f"User {u} logged in successfully.")
        else:
            debug_print(f"Login failed for user {u}: Invalid credentials.")
        return r
    except mysql.connector.Error as err:
        st.error(f"Error logging in: {err}")
        debug_print(f"Login failed due to DB error: {err}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during login: {e}")
        debug_print(f"Unexpected error during login: {e}")
        return None
    finally:
        c.close()
        conn.close()

def log_file(u, fn):
    """Logs an uploaded file's metadata to the database."""
    debug_print(f"Attempting to log file {fn} for user {u}")
    conn = get_connection()
    if conn is None: return False
    c = conn.cursor()
    try:
        c.execute("INSERT INTO user_uploads(username, filename, upload_time) VALUES(%s, %s, %s)", (u, fn, datetime.now()))
        conn.commit()
        debug_print(f"File {fn} logged successfully for user {u}.")
        return True
    except mysql.connector.Error as err:
        st.error(f"Error logging file: {err}")
        debug_print(f"File logging failed: {err}")
        conn.rollback()
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while logging file: {e}")
        debug_print(f"Unexpected error logging file: {e}")
        return False
    finally:
        c.close()
        conn.close()

# --- Initializing Session State ---
debug_print("Initializing session state variables.")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    debug_print("st.session_state.authenticated initialized to False.")
if "user" not in st.session_state:
    st.session_state.user = None
    debug_print("st.session_state.user initialized to None.")
if "current_page" not in st.session_state:
    st.session_state.current_page = "📊 Dashboard" # Default page after login
    debug_print("st.session_state.current_page initialized to '📊 Dashboard'.")
if "auth_choice" not in st.session_state: # New session state for login/signup radio
    st.session_state.auth_choice = "Login"

# --- Conditional Rendering of Pages ---

# Always render the sidebar for logo and debug messages
with st.sidebar:
    # Use st.image directly for sidebar logo as it handles paths better
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180) # Adjust width as needed
    else:
        st.error("Sidebar: Logo file 'logo.png' not found. Please ensure it's in the same directory.")
        debug_print("Sidebar: Logo file 'logo.png' not found.")
    st.markdown("---") # Separator

    # Debug messages will appear here
    if DEBUG_MODE:
        st.subheader("Debug Messages")


# If not authenticated, show the full-page login/signup
if not st.session_state.authenticated:
    debug_print("User not authenticated. Displaying full-page login/signup.")

    # Get Base64 encoded logo for embedding in HTML
    logo_base64 = get_image_base64("logo.png")
    logo_html_tag = ""
    if logo_base64:
        logo_html_tag = f"<img src='data:image/png;base64,{logo_base64}' alt='BizPulse Logo'>"
    else:
        # If Base64 conversion failed, display a text fallback or error
        logo_html_tag = "<div style='color: red; font-weight: bold;'>Logo Missing</div>"


    st.markdown(f"""
        <div class="login-container">
            <div class="header-logo">
                {logo_html_tag}
                <h1>BizPulse Analytics</h1>
            </div>
            <p style="font-size: 1.1rem; color: #555; margin-bottom: 30px;">
                Welcome! Please Login or Sign Up to continue.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Use columns for a cleaner layout of login/signup forms
    col1, col2, col3 = st.columns([1, 2, 1]) # Center the forms

    with col2: # Place forms in the middle column
        st.session_state.auth_choice = st.radio(
            "Select an option",
            ["Login", "Signup"],
            key="auth_radio_main",
            horizontal=True # Display radio buttons horizontally
        )
        st.markdown("---")

        if st.session_state.auth_choice == "Signup":
            st.markdown("### Create New Account")
            su = st.text_input("New Username", key="signup_username_main")
            sp = st.text_input("New Password", type="password", key="signup_password_main")
            if st.button("Create Account", key="create_account_btn_main"):
                if su and sp:
                    if create_user(su, sp):
                        st.success("✅ Account created! Please log in.")
                        # Clear inputs after successful signup
                        st.session_state.signup_username_main = ""
                        st.session_state.signup_password_main = ""
                        st.session_state.auth_choice = "Login" # Switch to login after signup
                        st.rerun() # Rerun to show login form
                else:
                    st.error("Username and password cannot be empty.")
        else: # Login
            st.markdown("### User Login")
            u = st.text_input("Username", key="login_username_main")
            p = st.text_input("Password", type="password", key="login_password_main")
            if st.button("Login", key="login_btn_main"):
                if u and p:
                    if login_user(u, p):
                        st.session_state.authenticated = True
                        st.session_state.user = u
                        st.session_state.current_page = "📊 Dashboard" # Navigate to dashboard on login
                        st.success(f"Welcome, {u}!")
                        st.rerun() # Rerun to update UI for authenticated user
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.error("Username and password cannot be empty.")
    # No st.stop() here, so the script continues if authenticated, otherwise it will display the login/signup forms.
else: # User is authenticated
    debug_print(f"User {st.session_state.user} is authenticated. Rendering main application.")

    # Main Header and Navigation for Authenticated Users
    # Get Base64 encoded logo for embedding in HTML
    logo_base64 = get_image_base64("logo.png")
    logo_html_tag = ""
    if logo_base64:
        logo_html_tag = f"<img src='data:image/png;base64,{logo_base64}' alt='BizPulse Logo'>"
    else:
        logo_html_tag = "<div style='color: red; font-weight: bold;'>Logo Missing</div>"


    st.markdown(f"""
        <div class='header-logo'>
            {logo_html_tag}
            <h1>BizPulse Analytics</h1>
        </div>
    """, unsafe_allow_html=True)

    # Main Navigation Menu (Horizontal)
    st.session_state.current_page = option_menu(
        menu_title=None, # No title for a cleaner horizontal menu
        options=["📊 Dashboard", "➕ Upload Data", "💡 Feedback", "🔐 Logout"],
        icons=["bar-chart", "cloud-upload", "chat", "door-closed"],
        menu_icon="cast",
        # Set default_index based on current_page to maintain selection
        default_index=["📊 Dashboard", "➕ Upload Data", "💡 Feedback", "🔐 Logout"].index(st.session_state.current_page),
        orientation="horizontal", # THIS MAKES IT HORIZONTAL
        styles={
            "container": {"padding": "0!important", "background-color": "rgba(255, 255, 255, 0.15)", "border-radius": "15px", "box-shadow": "0 5px 20px rgba(0,0,0,0.2)", "margin-bottom": "40px", "border": "1px solid rgba(255, 255, 255, 0.2)"},
            "icon": {"color": "#007bff", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "rgba(255, 255, 255, 0.1)", "padding": "10px 20px", "border-radius": "10px", "color": "#e0e0e0"},
            "nav-link-selected": {"background": "linear-gradient(45deg, #007bff, #00c6ff)", "color": "white", "font-weight": "bold", "border-radius": "10px", "box-shadow": "0 4px 10px rgba(0, 123, 255, 0.3)"},
        },
        key="main_app_menu" # Unique key for the main menu
    )

    # Handle logout directly from menu selection
    if st.session_state.current_page == "🔐 Logout":
        debug_print("Logout selected from main menu.")
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = "Login" # Reset to Login state
        st.info("You have been logged out.")
        st.rerun() # Rerun to show login page

    # --- Dashboard Page ---
    if st.session_state.current_page == "📊 Dashboard":
        debug_print("Displaying Dashboard page.")
        st.subheader("📌 Key Metrics")
        logs = get_logs_cached(st.session_state.user) # Use cached version

        total_uploads = len(logs)
        last_upload_info = "N/A"
        if logs:
            try:
                # Format datetime object nicely if it's a datetime object
                last_upload_info = f"{logs[0][0]} @ {logs[0][1].strftime('%Y-%m-%d %H:%M:%S')}"
            except AttributeError: # If it's already a string or other format
                last_upload_info = f"{logs[0][0]} @ {str(logs[0][1])}"
        
        cols = st.columns(3) # Use 3 columns for better layout
        with cols[0]:
            # Removed 'icon' argument as it's not supported by streamlit_card
            card(
                title="Total Uploads",
                text=str(total_uploads),
                styles={"card": {"background-color": "rgba(255, 255, 255, 0.1)", "border-radius": "15px", "padding": "20px", "box-shadow": "0 8px 16px rgba(0,0,0,0.2)", "color": "#ffffff", "backdrop-filter": "blur(5px)", "border": "1px solid rgba(255, 255, 255, 0.2)"}}
            )
        with cols[1]:
            # Removed 'icon' argument
            card(
                title="Last Upload",
                text=last_upload_info,
                styles={"card": {"background-color": "rgba(255, 255, 255, 0.1)", "border-radius": "15px", "padding": "20px", "box-shadow": "0 8px 16px rgba(0,0,0,0.2)", "color": "#ffffff", "backdrop-filter": "blur(5px)", "border": "1px solid rgba(255, 255, 255, 0.2)"}}
            )
        with cols[2]:
            # Removed 'icon' argument
            card(
                title="Current User",
                text=st.session_state.user if st.session_state.user else "Guest", # Handle case if user is None
                styles={"card": {"background-color": "rgba(255, 255, 255, 0.1)", "border-radius": "15px", "padding": "20px", "box-shadow": "0 8px 16px rgba(0,0,0,0.2)", "color": "#ffffff", "backdrop-filter": "blur(5px)", "border": "1px solid rgba(255, 255, 255, 0.2)"}}
            )

        st.markdown("---")
        st.subheader("Sales Data Visualizations")

        if logs:
            fn = logs[0][0]
            user_upload_dir = os.path.join("uploads", st.session_state.user)
            file_path = os.path.join(user_upload_dir, fn)

            if os.path.exists(file_path):
                try:
                    # Assuming visualizer.py exists and has show_visuals function
                    try:
                        from visualizer import show_visuals
                        df = pd.read_csv(file_path)
                        show_visuals(df) # Call the visualization function
                    except ImportError:
                        st.error("Cannot display visualizations: 'visualizer.py' or 'show_visuals' function not found.")
                        st.dataframe(pd.read_csv(file_path).head()) # Show raw data head as fallback
                    except Exception as e:
                        st.error(f"Error displaying visualizations from '{fn}': {e}. Please check your 'visualizer.py' code.")
                        st.dataframe(pd.read_csv(file_path).head()) # Show raw data head as fallback
                except Exception as e:
                    st.error(f"Error loading CSV file '{fn}': {e}. Please ensure the CSV file is correctly formatted.")
            else:
                st.warning(f"File '{fn}' not found in your uploads. It might have been moved or deleted. Please re-upload your sales CSV file to see analytics.")
        else:
            st.info("📤 Please upload your sales CSV file to see analytics.")

    # --- Upload Data Page ---
    elif st.session_state.current_page == "➕ Upload Data":
        debug_print("Displaying Upload Data page.")
        st.header("📁 Upload New Sales Data")
        st.info("Ensure your CSV includes: Order Date, Customer ID, Product, Category, Quantity, Unit Price.")
        f = st.file_uploader("Upload CSV", type=["csv"], key="csv_uploader")

        if f:
            uid = st.session_state.user
            fn = f.name

            # Create user-specific upload directory if it doesn't exist
            upload_dir = os.path.join("uploads", uid)
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, fn)

            # Check if file with same name already exists
            if os.path.exists(file_path):
                st.warning(f"File '{fn}' already exists. Uploading will overwrite it.")

            try:
                # Save the uploaded file
                with open(file_path, "wb") as out_file:
                    out_file.write(f.getbuffer())

                # Log file upload to database
                if log_file(uid, fn):
                    st.success("✅ File uploaded and saved!")
                    # Invalidate cache for logs so dashboard updates
                    get_logs_cached.clear()
                else:
                    st.error("Failed to log file upload to database.")

                st.subheader("Preview of Uploaded Data:")
                df = pd.read_csv(file_path) # Read again to display preview
                st.dataframe(df.head())
                st.balloons()
            except Exception as e:
                st.error(f"Error processing uploaded CSV: {e}")
                if os.path.exists(file_path):
                    os.remove(file_path) # Clean up partially uploaded/corrupted file
                st.info("Please ensure the uploaded file is a valid CSV.")

    # --- Feedback Page ---
    elif st.session_state.current_page == "💡 Feedback":
        debug_print("Displaying Feedback page.")
        st.header("💬 Send Us Feedback")
        st.write("We'd love to hear from you! Your feedback helps us improve.")
        with st.form("feedback_form", clear_on_submit=True): # clear_on_submit makes it interactive
            name = st.text_input("Your Name", key="feedback_name_input")
            msg = st.text_area("Your Message", key="feedback_message_area")
            # Removed 'key' argument from st.form_submit_button
            sub = st.form_submit_button("Submit Feedback")
            if sub:
                if name and msg:
                    # In a real application, you would save this feedback to a database or service.
                    # For this example, we just show a success message.
                    st.success("Thank you for your feedback! We appreciate it.")
                    debug_print("Feedback submitted.")
                else:
                    st.error("Please fill in both your name and message.")
                    debug_print("Feedback submission failed: Name or message empty.")

        # Removed Lottie animation code:
        # lottie_animation_data = load_lottie("analytics.json")
        # if lottie_animation_data:
        #     st_lottie(lottie_animation_data, height=250, key="feedback_lottie_anim")
        # else:
        #     st.warning("Lottie animation could not be loaded. Check 'analytics.json' file and its path.")
        #     debug_print("Lottie animation data is None.")
