"""Custom CSS styling for the app - Mobile First Design."""


def get_custom_css() -> str:
    """Get custom CSS for the application.
    
    Returns:
        CSS string - Mobile first approach
    """
    return """
    <style>
    /* ========================================
       MOBILE FIRST CSS - Base styles for mobile
       ======================================== */
    
    /* Mobile viewport optimization */
    * {
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
    }
    
    html {
        -webkit-text-size-adjust: 100%;
        text-size-adjust: 100%;
    }
    
    /* Main color scheme */
    :root {
        --profit-green: #2ecc71;
        --loss-red: #e74c3c;
        --neutral-blue: #3498db;
        --dark-bg: #2c3e50;
        --light-bg: #ecf0f1;
    }
    
    /* Main container - tight padding on mobile */
    .main {
        padding: 0.25rem;
    }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* ========================================
       MOBILE LAYOUT FIXES
       - Streamlit columns can get too narrow on phones,
         causing ugly wrapping and left-stacked "boxes".
       - Stack 3+ column rows vertically on small screens.
       ======================================== */

    @media (max-width: 520px) {
        /* Stack 3+ column rows (but keep 2-column button rows side-by-side) */
        [data-testid="stHorizontalBlock"]:has(> div:nth-child(3)) {
            flex-direction: column !important;
            align-items: stretch !important;
        }

        /* Make each column full width */
        [data-testid="stHorizontalBlock"]:has(> div:nth-child(3)) > div,
        [data-testid="stHorizontalBlock"]:has(> div:nth-child(3)) [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(> div:nth-child(3)) [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 0 !important;
        }

        /* Reduce the "gutter" between stacked columns */
        [data-testid="stHorizontalBlock"]:has(> div:nth-child(3)) > div {
            margin-bottom: 0.35rem !important;
        }
    }
    
    /* ========================================
       STAT CARDS - Compact for mobile
       ======================================== */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.4rem 0.3rem;
        border-radius: 6px;
        color: white;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 0.25rem;
    }
    
    .stat-card-icon {
        font-size: 0.9rem;
        line-height: 1;
    }
    
    .stat-card-value {
        font-size: 0.95rem;
        font-weight: bold;
        margin: 0.1rem 0;
        line-height: 1.2;
    }
    
    .stat-card-label {
        font-size: 0.6rem;
        opacity: 0.9;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.2;
    }
    
    /* ========================================
       COMBO METER - Compact
       ======================================== */
    .combo-meter {
        background: linear-gradient(90deg, #f39c12 0%, #e74c3c 100%);
        height: 14px;
        border-radius: 7px;
        position: relative;
        overflow: hidden;
        margin: 0.3rem 0;
    }
    
    .combo-meter-fill {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
        height: 100%;
        border-radius: 7px;
        transition: width 0.5s ease;
    }
    
    .combo-text {
        font-size: 0.85rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    /* ========================================
       QUESTION DISPLAY - Readable on mobile
       ======================================== */
    .question-display {
        background: white;
        border: 2px solid #3498db;
        border-radius: 8px;
        padding: 0.75rem;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        margin: 0.5rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        word-break: normal;
        overflow-wrap: anywhere;
        position: relative;
    }
    
    /* ========================================
       FEEDBACK - Compact
       ======================================== */
    .feedback-correct {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 6px;
        text-align: center;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    .feedback-incorrect {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 6px;
        text-align: center;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    /* ========================================
       BADGES - Small on mobile
       ======================================== */
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        padding: 0.35rem;
        border-radius: 6px;
        text-align: center;
        min-width: 55px;
        margin: 0.15rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .badge-locked {
        opacity: 0.5;
        filter: grayscale(100%);
    }
    
    .badge-icon {
        font-size: 1rem;
        margin-bottom: 0.1rem;
    }
    
    .badge-name {
        font-weight: bold;
        color: white;
        font-size: 0.6rem;
        line-height: 1.2;
    }
    
    .badge-description {
        font-size: 0.5rem;
        color: rgba(255,255,255,0.8);
        line-height: 1.1;
    }
    
    /* ========================================
       INSIGHT CARDS - Compact
       ======================================== */
    .insight-card {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        border-left: 3px solid;
        font-size: 0.8rem;
        line-height: 1.3;
    }
    
    .insight-positive {
        background: #d5f4e6;
        border-color: #2ecc71;
    }
    
    .insight-neutral {
        background: #d6eaf8;
        border-color: #3498db;
    }
    
    .insight-negative {
        background: #fadbd8;
        border-color: #e74c3c;
    }
    
    /* ========================================
       STREAK FLAME
       ======================================== */
    .streak-flame {
        display: inline-block;
        animation: flicker 1.5s infinite;
    }
    
    .streak-container {
        text-align: center;
        padding: 0.3rem;
    }
    
    .streak-icon {
        font-size: 1.2rem;
    }
    
    .streak-text {
        font-size: 0.85rem;
        font-weight: bold;
        margin-top: 0.15rem;
    }
    
    @keyframes flicker {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.9; }
    }
    
    /* ========================================
       TIMER - Compact
       ======================================== */
    .timer {
        font-size: 1rem;
        font-weight: bold;
        color: #3498db;
        text-align: center;
        padding: 0.3rem;
        background: #ecf0f1;
        border-radius: 6px;
        margin: 0.25rem 0;
    }
    
    .timer-warning {
        color: #e74c3c;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* ========================================
       PROGRESS BAR - Compact
       ======================================== */
    .progress-container {
        background: #ecf0f1;
        border-radius: 6px;
        height: 10px;
        overflow: hidden;
        margin: 0.25rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
        height: 100%;
        transition: width 0.5s ease;
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.15rem;
        font-size: 0.75rem;
    }
    
    /* ========================================
       CELEBRATION
       ======================================== */
    .celebration {
        text-align: center;
        padding: 0.5rem;
    }
    
    .celebration-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0;
    }
    
    /* ========================================
       BUTTONS - Mobile optimized
       ======================================== */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        padding: 0.6rem 0.8rem;
        font-size: 16px;
        font-weight: bold;
        border: none;
        transition: all 0.2s ease;
        min-height: 44px;
        touch-action: manipulation;
        white-space: normal;
        line-height: 1.15;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    .stButton {
        margin-bottom: 0.2rem;
    }
    
    /* ========================================
       TYPOGRAPHY - Small base for mobile
       ======================================== */
    h1 {
        font-size: 1.2rem !important;
        margin-bottom: 0.3rem !important;
        margin-top: 0 !important;
    }
    
    h2 {
        font-size: 0.95rem !important;
        margin-bottom: 0.25rem !important;
        margin-top: 0.5rem !important;
    }
    
    h3 {
        font-size: 0.85rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0.4rem !important;
    }
    
    .stMarkdown p {
        font-size: 0.8rem;
        margin-bottom: 0.25rem;
    }
    
    /* ========================================
       FORM ELEMENTS - Mobile optimized
       ======================================== */
    .stTextInput input {
        font-size: 16px !important;
        padding: 0.5rem;
        -webkit-appearance: none;
        border-radius: 6px;
    }

    /* Hide number input spinners (desktop browsers) */
    .stTextInput input[type="number"]::-webkit-outer-spin-button,
    .stTextInput input[type="number"]::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    .stTextInput input[type="number"] {
        -moz-appearance: textfield;
        appearance: textfield;
    }
    
    /* Prevent zoom on focus for mobile */
    input, select, textarea, button {
        font-size: 16px !important;
    }
    
    .stRadio label {
        font-size: 14px;
        min-height: 44px;
        display: flex;
        align-items: center;
    }
    
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stSelectbox label {
        font-size: 14px;
    }
    
    .stSelectbox select {
        font-size: 16px !important;
        padding: 0.5rem;
    }
    
    /* Form submit buttons need proper touch targets */
    [data-testid="stFormSubmitButton"] button {
        min-height: 50px !important;
        font-size: 16px !important;
    }
    
    /* ========================================
       METRICS - Compact
       ======================================== */
    [data-testid="stMetricValue"] {
        font-size: 0.9rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.65rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.6rem !important;
    }
    
    /* ========================================
       DATAFRAME - Compact
       ======================================== */
    [data-testid="stDataFrame"] {
        font-size: 0.7rem;
    }
    
    /* ========================================
       MISC ELEMENTS
       ======================================== */
    hr {
        margin: 0.3rem 0;
    }
    
    .stCaption {
        font-size: 0.7rem;
        color: rgba(0,0,0,0.6);
    }
    
    .stAlert {
        font-size: 0.8rem;
        padding: 0.4rem;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-size: 0.8rem !important;
    }
    
    /* Tabs */
    [data-baseweb="tab"] {
        font-size: 0.75rem !important;
        padding: 0.3rem 0.5rem !important;
    }
    
    /* Reduce element spacing */
    .element-container {
        margin-bottom: 0.3rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #ecf0f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3498db;
        border-radius: 3px;
    }
    
    /* ========================================
       TABLET BREAKPOINT (min-width: 480px)
       ======================================== */
    @media (min-width: 480px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        
        .stat-card {
            padding: 0.5rem 0.4rem;
        }
        
        .stat-card-value {
            font-size: 1.05rem;
        }
        
        .stat-card-label {
            font-size: 0.65rem;
        }
        
        .stat-card-icon {
            font-size: 1rem;
        }
        
        .question-display {
            font-size: 1.4rem;
            padding: 1rem;
        }
        
        .badge {
            padding: 0.45rem;
            min-width: 65px;
        }
        
        .badge-icon {
            font-size: 1.2rem;
        }
        
        .badge-name {
            font-size: 0.65rem;
        }
        
        h1 {
            font-size: 1.35rem !important;
        }
        
        h2 {
            font-size: 1.05rem !important;
        }
        
        h3 {
            font-size: 0.9rem !important;
        }
        
        .stMarkdown p {
            font-size: 0.85rem;
        }
        
        .timer {
            font-size: 1.1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
        }
    }
    
    /* ========================================
       DESKTOP BREAKPOINT (min-width: 768px)
       ======================================== */
    @media (min-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .stat-card {
            padding: 0.6rem 0.5rem;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .stat-card-value {
            font-size: 1.2rem;
            margin: 0.2rem 0;
        }
        
        .stat-card-label {
            font-size: 0.7rem;
        }
        
        .stat-card-icon {
            font-size: 1.1rem;
        }
        
        .question-display {
            font-size: 1.5rem;
            padding: 1.25rem;
            margin: 0.75rem 0;
            position: sticky;
            top: 0.25rem;
            z-index: 100;
        }
        
        .feedback-correct, .feedback-incorrect {
            font-size: 1rem;
            padding: 0.6rem;
        }
        
        .combo-meter {
            height: 18px;
        }
        
        .combo-text {
            font-size: 1rem;
        }
        
        .badge {
            padding: 0.6rem;
            min-width: 80px;
            margin: 0.2rem;
        }
        
        .badge:hover {
            transform: scale(1.05);
        }
        
        .badge-icon {
            font-size: 1.5rem;
        }
        
        .badge-name {
            font-size: 0.75rem;
        }
        
        .badge-description {
            font-size: 0.6rem;
        }
        
        .insight-card {
            padding: 0.6rem;
            font-size: 0.85rem;
        }
        
        .streak-icon {
            font-size: 1.4rem;
        }
        
        .streak-text {
            font-size: 0.95rem;
        }
        
        .timer {
            font-size: 1.25rem;
            padding: 0.4rem;
        }
        
        .progress-container {
            height: 14px;
        }
        
        .progress-label {
            font-size: 0.85rem;
        }
        
        .celebration-title {
            font-size: 1.4rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2 {
            font-size: 1.15rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
        
        .stMarkdown p {
            font-size: 0.9rem;
        }
        
        .stButton>button {
            padding: 0.5rem 1rem;
        }
        
        .stTextInput input {
            padding: 0.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        
        [data-testid="stDataFrame"] {
            font-size: 0.8rem;
        }
        
        hr {
            margin: 0.5rem 0;
        }
        
        .stCaption {
            font-size: 0.8rem;
        }
        
        .element-container {
            margin-bottom: 0.5rem;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
    }
    
    /* ========================================
       LARGE DESKTOP (min-width: 1024px)
       ======================================== */
    @media (min-width: 1024px) {
        .stat-card {
            padding: 0.75rem;
        }
        
        .stat-card-value {
            font-size: 1.4rem;
        }
        
        .stat-card-label {
            font-size: 0.75rem;
        }
        
        .question-display {
            font-size: 1.75rem;
            padding: 1.5rem;
        }
        
        .badge {
            min-width: 90px;
        }
        
        .badge-icon {
            font-size: 1.8rem;
        }
        
        .badge-name {
            font-size: 0.85rem;
        }
        
        h1 {
            font-size: 1.75rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
        }
    }
    </style>
    """
