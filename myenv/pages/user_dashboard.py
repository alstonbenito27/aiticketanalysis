import streamlit as st
import boto3
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    tab1, tab2 = st.tabs(["Reports", "Future Trends Analysis"])
    
    with tab1:
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
    
    with tab2:
        st.subheader("📊 Future Trends Analysis Report")
        st.write("### Key Predictions")
        st.write("1. The most commonly predicted ticket type for the future is **'1'**, indicating a rise in related issues.")
        st.write("2. The highest priority issues are expected to be **'3'**, meaning more critical tickets may need urgent attention.")
        st.write("3. The most common severity level for tickets is **'2'**.")
        
        # IT Owner Ticket Distribution
        st.write("#### IT Owner Ticket Load Distribution")
        it_owners = {3: 2084, 39: 2080, 48: 2072, 35: 2058, 24: 2045, 5: 2040, 4: 2040, 19: 2040, 31: 2038, 10: 2032, 15: 2028, 32: 2019, 27: 2019, 1: 2017, 30: 2016, 9: 2016, 26: 2013, 33: 2011, 41: 2011, 8: 2010, 2: 2009, 17: 2008, 22: 2008, 42: 2007, 44: 2002, 6: 1999, 11: 1998, 7: 1997, 28: 1996, 50: 1996, 14: 1992, 46: 1990, 16: 1987, 29: 1985, 34: 1982, 37: 1982, 47: 1982, 38: 1978, 45: 1975, 20: 1975, 23: 1969, 25: 1963, 40: 1960, 12: 1953, 36: 1952, 43: 1951, 21: 1938, 49: 1937, 18: 1937, 13: 1903}
        df_it = pd.DataFrame(it_owners.items(), columns=["IT Owner", "Ticket Load"])
        st.bar_chart(df_it.set_index("IT Owner"))
        
        # Ticket Type Distribution
        st.write("#### Predicted Ticket Type Distribution")
        ticket_distribution = {1: 75.074, 0: 24.926}
        df_tickets = pd.DataFrame(ticket_distribution.items(), columns=["Ticket Type", "Percentage"])
        st.bar_chart(df_tickets.set_index("Ticket Type"))
        
        # Priority Distribution
        st.write("#### Predicted Priority Distribution")
        priority_distribution = {3: 36.498, 0: 30.127, 1: 17.117, 2: 16.258}
        df_priority = pd.DataFrame(priority_distribution.items(), columns=["Priority Level", "Percentage"])
        st.bar_chart(df_priority.set_index("Priority Level"))
        
        # Severity Distribution
        st.write("#### Predicted Severity Distribution")
        severity_distribution = {2: 90.912, 3: 4.974, 1: 2.317, 4: 1.43, 0: 0.367}
        df_severity = pd.DataFrame(severity_distribution.items(), columns=["Severity Level", "Percentage"])
        st.bar_chart(df_severity.set_index("Severity Level"))
        
        st.write("### Model Performance Overview (Expressed as Text Only)")
        st.write("- Ticket Type Prediction Accuracy: **72.79%**")
        st.write("- Priority Prediction Accuracy: **39.32%**")
        st.write("- Random Forest R² Score: **65.41%**")
        
    # Logout Button
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["group"] = ""
        st.switch_page("pages/login.py")

if __name__ == "__main__":
    show_dashboard()