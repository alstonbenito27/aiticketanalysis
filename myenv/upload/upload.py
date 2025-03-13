import streamlit as st
import boto3

BUCKET_NAME = "dem-forcast-test"

def upload_file():
    client = boto3.client("s3", region_name="us-east-1")

    # Redirect to login if the user is not authenticated
    if not st.session_state.get("logged_in", False):
        st.experimental_set_query_params(page="login")  # Redirect to login
        st.stop()

    st.title("Upload File")

    # Logout Button with Immediate Redirect
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_set_query_params(page="login")  # Redirect to login page
        st.rerun()  # Trigger a re-run to refresh the page

    # Back Button to Dashboard
    if st.button("Back to Dashboard"):
        st.experimental_set_query_params(page="dashboard")
        st.rerun()

    username = st.session_state.get("username", None)
    if not username:
        st.error("No username found. Please log in first.")
        return

    # File Upload Section
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file:
        try:
            # Upload file directly to uploads/username/
            file_key = f"{username}/{uploaded_file.name}"

            # Check if the file already exists in S3
            response = client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=file_key)
            if "Contents" in response:
                st.warning(f"A file with the name `{uploaded_file.name}` already exists. Please rename your file.")
                return

            # Upload the file with a loading spinner
            with st.spinner("Uploading file..."):
                client.upload_fileobj(uploaded_file, BUCKET_NAME, file_key)

            st.success(f"File uploaded successfully to: `{file_key}`")

        except Exception as e:
            st.error(f"Error uploading file: {e}")
