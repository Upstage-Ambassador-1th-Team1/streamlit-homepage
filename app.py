"""
Main Streamlit application entry point
"""
import streamlit as st
import base64
import os

from styles import get_base_styles, get_sidebar_styles
from pages.chat_page import render_chat_page
from pages.search_page import render_search_page


def load_logo():
    """Load and encode the logo image."""
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def render_sidebar(logo_encoded: str, current_page: str):
    """Render the sidebar navigation."""
    with st.sidebar:
        if logo_encoded:
            st.markdown(
                f"""
                <a href>
                    <img src="data:image/png;base64,{logo_encoded}" width="200" style="margin-top:-40px; margin-bottom:60px;">
                </a>
                """,
                unsafe_allow_html=True
            )
        
        if st.button("채팅", key="home_btn", type="secondary", use_container_width=True):
            st.query_params = {"page": ["home"]}
            st.rerun()
            
        if st.button("공고 검색", key="search_btn", type="secondary", use_container_width=True):
            st.query_params = {"page": ["search"]}
            st.rerun()

        st.markdown(get_sidebar_styles(), unsafe_allow_html=True)


def main():
    """Main application entry point."""
    st.set_page_config(page_title="집착 - 공공임대 검색", layout="wide")
    
    # Get current page from URL params
    params = st.query_params
    page = params.get("page", ["home"])[0]
    
    # Load logo
    logo_encoded = load_logo()
    
    # Apply base styles
    st.markdown(get_base_styles(page), unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar(logo_encoded, page)
    
    # Main content area
    st.markdown('<div class="content">', unsafe_allow_html=True)
    
    if page == "home":
        render_chat_page()
    elif page == "search":
        render_search_page()
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

