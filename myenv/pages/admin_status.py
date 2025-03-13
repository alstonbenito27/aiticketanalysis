import streamlit as st
import boto3

# AWS S3 Configuration
S3_BUCKET_NAME = "ticket-userlogs"  # Your S3 bucket name
REGION_NAME = "us-east-1"  # AWS region

# Ensure session state is initialized
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "group" not in st.session_state:
    st.session_state["group"] = ""

# Function to fetch all files from S3 bucket
def fetch_all_files_from_s3():
    s3_client = boto3.client("s3", region_name=REGION_NAME)
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        files = response.get("Contents", [])

        if not files:
            return []

        return [file["Key"] for file in files]  # Return list of file names

    except Exception as e:
        st.error(f"❌ Error fetching files: {str(e)}")
        return []

# Function to fetch and display a selected file's content
def display_file_content(file_key):
    s3_client = boto3.client("s3", region_name=REGION_NAME)
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=file_key)
        file_data = obj["Body"].read().decode("utf-8")  # Read file content as text
        st.text_area(f"📂 {file_key}", file_data, height=250)
    except Exception as e:
        st.error(f"❌ Error reading file {file_key}: {str(e)}")

# Admin Status Page
def show_admin_status():
    if not st.session_state["logged_in"]:
        st.error("🚫 Access Denied. Please log in.")
        return

    st.title("📊 Admin Status Page")
    st.write("View all system logs stored in S3.")

    # Fetch list of log files
    files = fetch_all_files_from_s3()

    if files:
        st.subheader("📄 Available Log Files")
        for file_key in files:
            with st.expander(f"📁 {file_key}"):  # Expandable sections for each file
                display_file_content(file_key)
    else:
        st.warning("⚠️ No logs available.")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Admin Dashboard"):
            st.session_state["page"] = "admin_dashboard"
            st.rerun()
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()

# Run the page
if __name__ == "__main__":
    show_admin_status()