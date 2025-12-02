"""Custom CSS styling for the app."""


def get_custom_css() -> str:
    """Get custom CSS for the application.
    
    Returns:
        CSS string
    """
    return """
    <style>
    /* Main color scheme - trading inspired */
    :root {
        --profit-green: #2ecc71;
        --loss-red: #e74c3c;
        --neutral-blue: #3498db;
        --dark-bg: #2c3e50;
        --light-bg: #ecf0f1;
    }
    
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Stat card styling */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .stat-card-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .stat-card-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Combo meter styling */
    .combo-meter {
        background: linear-gradient(90deg, #f39c12 0%, #e74c3c 100%);
        height: 30px;
        border-radius: 15px;
        position: relative;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .combo-meter-fill {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
        height: 100%;
        border-radius: 15px;
        transition: width 0.5s ease;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Question display styling */
    .question-display {
        background: white;
        border: 3px solid #3498db;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    /* Feedback styling */
    .feedback-correct {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        animation: slideIn 0.3s ease;
    }
    
    .feedback-incorrect {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        min-width: 120px;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .badge:hover {
        transform: scale(1.05);
    }
    
    .badge-locked {
        opacity: 0.5;
        filter: grayscale(100%);
    }
    
    .badge-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-name {
        font-weight: bold;
        color: white;
    }
    
    /* Insight card styling */
    .insight-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
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
    
    /* Streak flame animation */
    .streak-flame {
        display: inline-block;
        animation: flicker 1.5s infinite;
    }
    
    @keyframes flicker {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.9; }
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Progress bar styling */
    .progress-container {
        background: #ecf0f1;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
        height: 100%;
        transition: width 0.5s ease;
    }
    
    /* Timer styling */
    .timer {
        font-size: 2rem;
        font-weight: bold;
        color: #3498db;
        text-align: center;
        padding: 1rem;
        background: #ecf0f1;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .timer-warning {
        color: #e74c3c;
        animation: pulse 1s infinite;
    }
    
    /* Session complete celebration */
    .celebration {
        text-align: center;
        padding: 2rem;
        animation: bounce 1s ease;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #ecf0f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3498db;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2980b9;
    }
    </style>
    """
