import streamlit as st
import boto3

# AWS S3 Configuration
REPORT_BUCKET = "dem-forecast-report"
FINAL_BUCKET = "dem-forecast-final"
LOGS_BUCKET = "ticket-final-reports"
AWS_REGION = "us-east-1"

# Initialize S3 Client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def list_s3_files(bucket_name):
    """Fetch files from an S3 bucket and organize by username"""
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = response.get("Contents", [])
    
    file_dict = {}
    for file in files:
        key = file["Key"]
        parts = key.split("/")
        if len(parts) > 1:
            username, filename = parts[0], "/".join(parts[1:])
            if username not in file_dict:
                file_dict[username] = []
            file_dict[username].append(filename)
    
    return file_dict

def move_file_to_final(username, filename, source_bucket):
    """Move a file to the final bucket"""
    if not username:
        return "Error: Username not provided"
    
    source_key = f"{username}/{filename}"
    dest_key = f"{username}/{filename}"
    
    try:
        # Move file to the final bucket
        s3_client.copy_object(Bucket=FINAL_BUCKET, CopySource={"Bucket": source_bucket, "Key": source_key}, Key=dest_key)
        s3_client.delete_object(Bucket=source_bucket, Key=source_key)
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"

def view_log_content(username, log_name):
    """Fetch and display log content from S3"""
    try:
        log_key = f"{username}/{log_name}"
        obj = s3_client.get_object(Bucket=LOGS_BUCKET, Key=log_key)
        log_content = obj["Body"].read().decode("utf-8")
        return log_content
    except Exception as e:
        return f"Error retrieving log: {str(e)}"

def show_admin_dashboard():
    if not st.session_state.get("logged_in", False):
        st.switch_page("pages/login.py")
        return

    st.title("Admin Dashboard")

    # === REPORTS SECTION ===
    st.subheader("📂 Generated Reports")
    reports_by_user = list_s3_files(REPORT_BUCKET)
    
    selected_reports = []
    
    if reports_by_user:
        for username, reports in reports_by_user.items():
            with st.expander(f"📁 {username} Reports"):
                user_selected = []
                for report in reports:
                    is_selected = st.checkbox(report, key=f"{username}_{report}")
                    if is_selected:
                        user_selected.append(report)
                selected_reports.append((username, user_selected))
        
        if st.button("✅ Send Selected Reports to Users"):
            success_count = 0
            for username, reports in selected_reports:
                for report_name in reports:
                    result = move_file_to_final(username, report_name, REPORT_BUCKET)
                    if "Success" in result:
                        success_count += 1
            
            st.success(f"{success_count} reports sent successfully!")
    else:
        st.info("No reports available.")

    # === LOGS SECTION ===
    st.subheader("📜 User Logs")
    logs_by_user = list_s3_files(LOGS_BUCKET)

    if logs_by_user:
        for username, logs in logs_by_user.items():
            with st.expander(f"📄 {username} Logs"):
                for log in logs:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.text(log)
                    
                    with col2:
                        if st.button("👀 View", key=f"view_{username}_{log}"):
                            log_content = view_log_content(username, log)
                            st.text_area("Log Content", log_content, height=200)
                        
                        file_key = f"{username}/{log}"
                        file_obj = s3_client.get_object(Bucket=LOGS_BUCKET, Key=file_key)
                        file_data = file_obj["Body"].read()
                        st.download_button("⬇ Download", file_data, log)
    else:
        st.info("No user logs available.")

    # Logout Button
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["group"] = ""
        st.switch_page("pages/login.py")

if __name__ == "__main__":
    show_admin_dashboard()