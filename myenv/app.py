import streamlit as st
import os

def main():
    st.set_page_config(page_title="AI Ticket Forecasting", page_icon="📊", layout="wide")

   
    custom_css = """
    <style>
        body {
            background-color: #f4f4f4;
            font-family: 'Arial', sans-serif;
        }
        .main-title {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .sub-text {
            text-align: center;
            font-size: 1.2em;
            color: #555;
            margin-bottom: 30px;
        }
        .login-btn {
            display: flex;
            justify-content: center;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-size: 1.2em;
            padding: 10px 30px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
   
    st.markdown("<div class='main-title'>AI Ticket Forecasting</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Welcome to the AI-powered ticket forecasting system.</div>", unsafe_allow_html=True)
   
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # Instead of using st.switch_page, use a regular link
        st.markdown("""
        <a href="/login" target="_self">
            <button style="
                background-color: #4CAF50;
                color: white;
                font-size: 1.2em;
                padding: 10px 30px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: 0.3s;
                width: 100%;
            ">
                Login to Continue
            </button>
        </a>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Make sure the pages directory exists
    os.makedirs("pages", exist_ok=True)
    main()