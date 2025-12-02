"""Mode selection page."""
import streamlit as st
from src.models.session import SessionConfig


def show_mode_selection():
    """Display mode selection page."""
    st.title("⚙️ Configure Practice Session")
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Session Type
    with col1:
        st.subheader("📋 Session Type")
        
        mode_type = st.radio(
            "Choose mode:",
            ["Sprint", "Marathon", "Targeted"],
            help="Sprint: Time-limited challenge\nMarathon: Question count challenge\nTargeted: Focus on weak areas"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if mode_type == "Sprint":
            duration = st.selectbox(
                "Duration:",
                [60, 120, 300],
                format_func=lambda x: f"{x//60} minute{'s' if x > 60 else ''}"
            )
            duration_seconds = duration
            question_count = None
        elif mode_type == "Marathon":
            count = st.selectbox(
                "Questions:",
                [25, 50, 100]
            )
            duration_seconds = None
            question_count = count
        else:  # Targeted
            count = st.selectbox(
                "Questions:",
                [15, 25, 50],
                index=1
            )
            duration_seconds = None
            question_count = count
    
    # Column 2: Category
    with col2:
        st.subheader("🎯 Category")
        
        categories = {
            "Mixed": "mixed",
            "Arithmetic": "arithmetic",
            "Percentages": "percentage",
            "Fractions": "fractions",
            "Ratios": "ratios",
            "Compound": "compound",
            "Estimation": "estimation"
        }
        
        category_display = st.radio(
            "Choose category:",
            list(categories.keys()),
            help="Mixed: All question types\nArithmetic: +, -, ×, ÷\nPercentages: % calculations\n"
                 "Fractions: Fraction conversions\nRatios: Ratio problems\n"
                 "Compound: Multi-step problems\nEstimation: Quick approximations"
        )
        
        category = categories[category_display]
        
        # Override category for targeted mode
        if mode_type == "Targeted":
            category = "targeted"
            st.info("📌 Targeted mode will focus on your weak areas")
    
    # Column 3: Difficulty
    with col3:
        st.subheader("💪 Difficulty")
        
        difficulties = {
            "Easy": "easy",
            "Medium": "medium",
            "Hard": "hard",
            "Adaptive": "adaptive"
        }
        
        difficulty_display = st.radio(
            "Choose difficulty:",
            list(difficulties.keys()),
            index=1,
            help="Easy: Simple problems\nMedium: Moderate challenge\n"
                 "Hard: Complex problems\nAdaptive: Adjusts based on performance"
        )
        
        difficulty = difficulties[difficulty_display]
    
    st.markdown("---")
    
    # Summary Preview
    st.subheader("📝 Session Summary")
    
    mode_str = mode_type
    if mode_type == "Sprint":
        mode_str += f" ({duration//60} min)"
    elif mode_type == "Marathon":
        mode_str += f" ({question_count} questions)"
    else:
        mode_str += f" ({question_count} questions)"
    
    category_str = category_display if mode_type != "Targeted" else "Weak Areas"
    
    st.info(f"""
    **Mode:** {mode_str}  
    **Category:** {category_str}  
    **Difficulty:** {difficulty_display}
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ BEGIN SESSION", use_container_width=True, type="primary"):
            # Create session config
            config = {
                'mode_type': mode_type.lower(),
                'category': category,
                'difficulty': difficulty,
                'duration_seconds': duration_seconds,
                'question_count': question_count
            }
            
            st.session_state.session_config = config
            st.session_state.page = "practice_session"
            st.rerun()
