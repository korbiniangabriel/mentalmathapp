"""Mode selection page."""
import streamlit as st


def show_mode_selection():
    """Display mode selection page."""
    st.title("⚙️ Configure")
    
    if st.button("← Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # Section 1: Session Type
    st.subheader("📋 Mode")
    
    mode_type = st.radio(
        "Choose mode:",
        ["Sprint", "Marathon", "Targeted"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if mode_type == "Sprint":
        duration = st.select_slider(
            "Duration:",
            options=[60, 120, 300],
            value=120,
            format_func=lambda x: f"{x//60}min"
        )
        duration_seconds = duration
        question_count = None
    elif mode_type == "Marathon":
        count = st.select_slider(
            "Questions:",
            options=[25, 50, 100],
            value=50
        )
        duration_seconds = None
        question_count = count
    else:  # Targeted
        count = st.select_slider(
            "Questions:",
            options=[15, 25, 50],
            value=25
        )
        duration_seconds = None
        question_count = count
    
    st.markdown("---")
    
    # Section 2: Category
    st.subheader("🎯 Category")
    
    categories = {
        "Mixed": "mixed",
        "Arithmetic": "arithmetic",
        "Percentage": "percentage",
        "Fractions": "fractions",
        "Ratios": "ratios",
        "Compound": "compound",
        "Estimation": "estimation"
    }
    
    if mode_type == "Targeted":
        st.info("📌 Targeted mode focuses on weak areas")
        category = "targeted"
    else:
        category_display = st.radio(
            "Category:",
            list(categories.keys()),
            horizontal=True,
            label_visibility="collapsed"
        )
        category = categories[category_display]
    
    st.markdown("---")
    
    # Section 3: Difficulty
    st.subheader("💪 Difficulty")
    
    difficulties = {
        "Easy": "easy",
        "Medium": "medium",
        "Hard": "hard",
        "Adaptive": "adaptive"
    }
    
    difficulty_display = st.radio(
        "Difficulty:",
        list(difficulties.keys()),
        index=1,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    difficulty = difficulties[difficulty_display]
    
    st.markdown("---")
    
    # Summary
    st.subheader("📝 Summary")
    
    mode_str = mode_type
    if mode_type == "Sprint":
        mode_str += f" ({duration//60}min)"
    else:
        mode_str += f" ({question_count}q)"
    
    category_str = "Weak Areas" if mode_type == "Targeted" else category_display
    
    st.write(f"**{mode_str}** • {category_str} • {difficulty_display}")
    
    st.markdown("---")
    
    # Start button
    if st.button("▶️ BEGIN", use_container_width=True, type="primary"):
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
