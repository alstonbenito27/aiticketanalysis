import streamlit as st
import boto3
import base64
import hmac
import hashlib

# AWS Cognito Configuration
APP_CLIENT_ID = "2dnursfj9sl3peqc8ue2oo79fs"
CLIENT_SECRET = "ohqesopnbefu0a3luaf5h97fivcni2mv0jpr6ufu09d9v4l4ku1"
USER_POOL_ID = "us-east-1_r1bFSUTBu"
REGION_NAME = "us-east-1"

# Initialize session state variables if not already set
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "group" not in st.session_state:
    st.session_state["group"] = ""

# Function to calculate Cognito secret hash
def calculate_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

# Get user groups from Cognito
def get_user_groups(username):
    client = boto3.client("cognito-idp", region_name=REGION_NAME)
    response = client.admin_list_groups_for_user(Username=username, UserPoolId=USER_POOL_ID)
    return [group["GroupName"] for group in response.get("Groups", [])]

# Custom CSS
st.markdown("""
<style>
    .login-title { text-align: center; font-size: 2em; font-weight: bold; color: #333; margin-bottom: 20px; }
    .form-container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
    .login-btn { background-color: #4CAF50; color: white; font-size: 1.2em; padding: 10px 30px; border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='login-title'>Login</div>", unsafe_allow_html=True)

if not st.session_state["logged_in"]:
    with st.container():
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)

        username = st.text_input("Username", value=st.session_state["username"], key="username_input")
        password = st.text_input("Password", type="password", key="password_input")

        if st.button("Login", key="login_button"):
            if username and password:
                try:
                    client = boto3.client("cognito-idp", region_name=REGION_NAME)
                    secret_hash = calculate_secret_hash(username, APP_CLIENT_ID, CLIENT_SECRET)
                    
                    response = client.initiate_auth(
                        AuthFlow="USER_PASSWORD_AUTH",
                        AuthParameters={"USERNAME": username, "PASSWORD": password, "SECRET_HASH": secret_hash},
                        ClientId=APP_CLIENT_ID,
                    )

                    groups = get_user_groups(username)

                    if not groups:
                        st.error("🚫 Access Denied: No group assigned.")
                    else:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username  
                        st.session_state["group"] = groups[0]

                        st.success("✅ Login successful!")

                        # Redirect based on group
                        if "Admin" in groups:
                            st.switch_page("pages/admin_dashboard.py")
                        else:
                            st.switch_page("pages/user_dashboard.py")

                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")
            else:
                st.error("⚠️ Please enter both username and password.")

        st.markdown("</div>", unsafe_allow_html=True)

        # Password reset and registration links
else:
    if "Admin" in st.session_state["group"]:
        st.switch_page("pages/admin_dashboard.py")
    else:
        st.switch_page("pages/user_dashboard.py")

# Logout button
if st.session_state["logged_in"]:
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["group"] = ""
        st.switch_page("auth/login.py")