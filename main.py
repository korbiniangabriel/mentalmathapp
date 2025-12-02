"""
Mental Math Training Application
Main entry point for Streamlit app
"""
import streamlit as st
from src.database.db_manager import DatabaseManager
from src.ui.styles import get_custom_css
from src.ui.pages.home_dashboard import show_home_dashboard
from src.ui.pages.mode_selection import show_mode_selection
from src.ui.pages.practice_session import show_practice_session
from src.ui.pages.results import show_results
from src.ui.pages.analytics_dashboard import show_analytics_dashboard


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    if 'active_session' not in st.session_state:
        st.session_state.active_session = None
    
    if 'session_summary' not in st.session_state:
        st.session_state.session_summary = None


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Mental Math Trainer",
        page_icon="🧮",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Get database manager
    db_manager = st.session_state.db_manager
    
    # Route to appropriate page
    page = st.session_state.page
    
    if page == 'home':
        show_home_dashboard(db_manager)
    
    elif page == 'mode_selection':
        show_mode_selection()
    
    elif page == 'practice_session':
        show_practice_session(db_manager)
    
    elif page == 'results':
        show_results(db_manager)
    
    elif page == 'analytics':
        show_analytics_dashboard(db_manager)
    
    else:
        st.error(f"Unknown page: {page}")
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()


if __name__ == "__main__":
    main()
