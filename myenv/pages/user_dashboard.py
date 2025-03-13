import streamlit as st
import boto3
import os

# AWS S3 Bucket Configuration
FINAL_BUCKET_NAME = "ticket-triggered-reports"
UPLOAD_BUCKET_NAME = "ticket-upload-data"
AWS_REGION = "us-east-1"

# Initialize S3 Client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def show_dashboard():
    if not st.session_state.get("logged_in", False):
        st.switch_page("pages/login.py")
        return

    st.title("📊 User Dashboard")
    username = st.session_state.get("username", "User")
    st.write(f"👋 Welcome, **{username}**!")

    # Fetch reports from S3
    st.subheader("📂 Your Reports")
    try:
        response = s3_client.list_objects_v2(Bucket=FINAL_BUCKET_NAME, Prefix=f"{username}/")
        files = response.get("Contents", [])
        
        if files:
            for file in files:
                file_key = file["Key"]
                file_name = file_key.split("/")[-1]
                
                # Download file into memory
                file_obj = s3_client.get_object(Bucket=FINAL_BUCKET_NAME, Key=file_key)
                file_data = file_obj["Body"].read()
                
                # Download button without page refresh
                st.download_button(f"⬇ Download {file_name}", file_data, file_name)
        else:
            st.info("📭 No reports found.")
    except Exception as e:
        st.error(f"❌ Error fetching reports: {str(e)}")
    
    # Model Performance Insights
    st.subheader("📈 Model Performance Insights")
    st.write("Sample Accuracy: **85%**")  # Placeholder, replace with actual calculation
    st.write("Sample Fastest Moving SKU: **SKU123**")
    st.write("Sample Slowest Moving SKU: **SKU987**")
    st.write("Sample Low Availability Alert: **SKU555 (Only 5 left!)")

    # File Upload Section
    st.subheader("📤 Upload New File")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file:
        try:
            file_key = f"{username}/{uploaded_file.name}"

            response = s3_client.list_objects_v2(Bucket=UPLOAD_BUCKET_NAME, Prefix=file_key)
            if "Contents" in response:
                st.warning(f"A file with the name `{uploaded_file.name}` already exists.")
            else:
                with st.spinner("Uploading file..."):
                    s3_client.upload_fileobj(uploaded_file, UPLOAD_BUCKET_NAME, file_key)
                st.success(f"File uploaded successfully to: `{file_key}`")
        except Exception as e:
            st.error(f"Error uploading file: {e}")

    # Logout Button
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["group"] = ""
        st.switch_page("pages/login.py")

if __name__ == "__main__":
    show_dashboard()