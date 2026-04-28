"""Custom CSS styling for the app."""


def get_custom_css() -> str:
    """Return the full style sheet for the Streamlit app."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {
        --bg-0: #f2f6f8;
        --bg-1: #dce9ef;
        --paper: #ffffff;
        --ink-900: #11212c;
        --ink-700: #384a56;
        --ink-500: #6c7a86;
        --line: #d2dde4;
        --brand: #0f766e;
        --brand-strong: #115e59;
        --accent: #f59e0b;
        --accent-soft: #fef3c7;
        --success: #15803d;
        --danger: #b42318;
        --warning: #b45309;
        --shadow: 0 14px 30px rgba(16, 34, 45, 0.08);
        --radius-lg: 18px;
        --radius-md: 12px;
        --radius-sm: 10px;
    }

    /* Dark-mode tokens (defined only; not auto-applied). Toggle by setting
       data-theme="dark" on a parent element in a future batch. */
    [data-theme="dark"] {
        --bg-0: #0b1419;
        --bg-1: #122029;
        --paper: #142632;
        --ink-900: #eaf2f5;
        --ink-700: #b8c6cf;
        --ink-500: #8395a0;
        --line: #20323d;
        --brand: #14b8a6;
        --brand-strong: #0f766e;
        --accent: #fbbf24;
        --accent-soft: #3b2e0e;
        --success: #34d399;
        --danger: #f87171;
        --warning: #fbbf24;
        --shadow: 0 14px 30px rgba(0, 0, 0, 0.45);
    }

    * {
        -webkit-tap-highlight-color: transparent;
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: "Manrope", "Segoe UI", sans-serif;
        color: var(--ink-900);
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1100px 500px at 90% -10%, rgba(15, 118, 110, 0.16), transparent 60%),
            radial-gradient(800px 420px at 0% 20%, rgba(245, 158, 11, 0.13), transparent 58%),
            linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 38%, #f8fbfc 100%);
    }

    .main .block-container {
        max-width: 1120px;
        padding-top: 1.2rem;
        padding-bottom: 2.2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1, h2, h3 {
        color: var(--ink-900);
        letter-spacing: -0.02em;
    }

    h1 {
        font-weight: 800;
        font-size: clamp(1.65rem, 2.4vw, 2.3rem);
        margin-bottom: 0.45rem;
    }

    h2 {
        font-weight: 700;
        font-size: clamp(1.12rem, 1.5vw, 1.42rem);
        margin-bottom: 0.4rem;
    }

    h3 {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.25rem;
    }

    p, li {
        color: var(--ink-700);
        line-height: 1.45;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        padding: 1.35rem 1.4rem;
        border: 1px solid rgba(17, 33, 44, 0.09);
        border-radius: var(--radius-lg);
        background:
            linear-gradient(130deg, rgba(255, 255, 255, 0.98), rgba(240, 248, 247, 0.93));
        box-shadow: var(--shadow);
        margin-bottom: 0.85rem;
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -55px;
        top: -105px;
        border-radius: 100%;
        background: radial-gradient(circle at center, rgba(15, 118, 110, 0.26), rgba(15, 118, 110, 0));
    }

    .hero-title {
        position: relative;
        z-index: 2;
        color: var(--ink-900);
        font-size: clamp(1.2rem, 2vw, 1.65rem);
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        position: relative;
        z-index: 2;
        color: var(--ink-700);
        font-size: 0.94rem;
        max-width: 760px;
    }

    .hero-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.72rem;
        position: relative;
        z-index: 2;
    }

    .hero-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: rgba(15, 118, 110, 0.1);
        color: var(--brand-strong);
        border: 1px solid rgba(15, 118, 110, 0.22);
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 0.26rem 0.62rem;
    }

    .stat-card {
        background: linear-gradient(170deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 252, 0.95));
        border: 1px solid rgba(17, 33, 44, 0.08);
        border-radius: var(--radius-md);
        padding: 0.88rem 0.9rem;
        box-shadow: 0 6px 14px rgba(17, 33, 44, 0.06);
        min-height: 118px;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(17, 33, 44, 0.12);
    }

    .stat-card-icon {
        font-size: 1.05rem;
        margin-bottom: 0.24rem;
    }

    .stat-card-value {
        color: var(--ink-900);
        font-weight: 800;
        font-size: clamp(1rem, 1.6vw, 1.33rem);
        letter-spacing: -0.02em;
        line-height: 1.15;
    }

    .stat-card-label {
        color: var(--ink-700);
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.12rem;
    }

    .stat-card-support {
        margin-top: 0.35rem;
        color: var(--ink-500);
        font-size: 0.73rem;
        line-height: 1.3;
    }

    .coach-note {
        border-radius: var(--radius-md);
        border: 1px solid var(--line);
        padding: 0.82rem 0.9rem;
        margin-bottom: 0.6rem;
        background: rgba(255, 255, 255, 0.9);
    }

    .coach-note-title {
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }

    .coach-note-body {
        color: var(--ink-700);
        font-size: 0.9rem;
        line-height: 1.35;
    }

    .coach-note-positive {
        border-color: rgba(21, 128, 61, 0.25);
        background: rgba(233, 252, 243, 0.95);
    }

    .coach-note-positive .coach-note-title {
        color: var(--success);
    }

    .coach-note-warning {
        border-color: rgba(180, 83, 9, 0.34);
        background: rgba(255, 247, 220, 0.95);
    }

    .coach-note-warning .coach-note-title {
        color: var(--warning);
    }

    .coach-note-neutral {
        border-color: rgba(15, 118, 110, 0.24);
        background: rgba(237, 250, 248, 0.95);
    }

    .coach-note-neutral .coach-note-title {
        color: var(--brand-strong);
    }

    .combo-text {
        color: var(--ink-900);
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.24rem;
    }

    .combo-meter {
        height: 10px;
        background: rgba(17, 33, 44, 0.13);
        border-radius: 999px;
        overflow: hidden;
    }

    .combo-meter-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #f59e0b, #f97316);
        transition: width 240ms ease;
    }

    .question-display {
        border: 1px solid rgba(17, 33, 44, 0.1);
        background: linear-gradient(180deg, #ffffff, #f7fbfc);
        border-radius: var(--radius-lg);
        padding: 1.12rem 1.06rem;
        font-size: clamp(1.42rem, 2.6vw, 2rem);
        letter-spacing: -0.02em;
        font-weight: 800;
        color: var(--ink-900);
        text-align: center;
        box-shadow: var(--shadow);
    }

    .feedback-correct,
    .feedback-incorrect {
        border-radius: var(--radius-md);
        padding: 0.78rem 0.9rem;
        font-weight: 700;
        font-size: 0.92rem;
    }

    .feedback-correct {
        color: #0f3f21;
        background: linear-gradient(180deg, #defbe8, #cbf2da);
        border: 1px solid rgba(21, 128, 61, 0.3);
    }

    .feedback-incorrect {
        color: #5c1b17;
        background: linear-gradient(180deg, #fdeceb, #fbe1e0);
        border: 1px solid rgba(180, 35, 24, 0.28);
    }

    .feedback-answer {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.86rem;
    }

    .insight-card {
        border-radius: var(--radius-md);
        border-left: 4px solid;
        padding: 0.8rem 0.88rem;
        margin-bottom: 0.44rem;
        font-size: 0.9rem;
        line-height: 1.36;
        box-shadow: 0 4px 10px rgba(17, 33, 44, 0.06);
    }

    .insight-positive {
        border-left-color: var(--success);
        background: rgba(235, 252, 244, 0.94);
        color: #0f3f21;
    }

    .insight-neutral {
        border-left-color: var(--brand);
        background: rgba(236, 248, 248, 0.94);
        color: #153645;
    }

    .insight-negative {
        border-left-color: var(--danger);
        background: rgba(254, 239, 238, 0.95);
        color: #5a201b;
    }

    .badge {
        border-radius: var(--radius-md);
        border: 1px solid rgba(15, 118, 110, 0.22);
        background: linear-gradient(180deg, rgba(15, 118, 110, 0.14), rgba(15, 118, 110, 0.05));
        padding: 0.62rem 0.58rem;
        text-align: center;
        min-height: 116px;
    }

    .badge-locked {
        opacity: 0.48;
        filter: grayscale(0.38);
    }

    .badge-icon {
        font-size: 1.25rem;
        margin-bottom: 0.15rem;
    }

    .badge-name {
        color: var(--ink-900);
        font-size: 0.77rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .badge-description {
        color: var(--ink-500);
        font-size: 0.66rem;
        line-height: 1.2;
        margin-top: 0.16rem;
    }

    .streak-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.55rem;
        border-radius: var(--radius-sm);
        background: rgba(245, 158, 11, 0.13);
        border: 1px solid rgba(180, 83, 9, 0.2);
        width: fit-content;
    }

    .streak-icon {
        font-size: 1rem;
    }

    .streak-flame {
        animation: flame-flicker 1.2s ease-in-out infinite;
    }

    .streak-text {
        color: #8a3f0f;
        font-size: 0.86rem;
        font-weight: 800;
    }

    @keyframes flame-flicker {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.08); }
    }

    .timer {
        display: inline-block;
        width: 100%;
        text-align: center;
        border: 1px solid rgba(17, 33, 44, 0.12);
        border-radius: var(--radius-sm);
        background: rgba(255, 255, 255, 0.92);
        font-family: "JetBrains Mono", monospace;
        font-size: 0.96rem;
        font-weight: 700;
        padding: 0.34rem 0.52rem;
        color: var(--ink-900);
    }

    .timer-warning {
        color: var(--danger);
        border-color: rgba(180, 35, 24, 0.34);
        background: rgba(254, 237, 236, 0.96);
    }

    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.2rem;
        font-size: 0.8rem;
        color: var(--ink-700);
        font-weight: 700;
    }

    .progress-container {
        height: 10px;
        border-radius: 999px;
        background: rgba(17, 33, 44, 0.13);
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--brand), #14b8a6);
        transition: width 220ms ease;
    }

    .celebration {
        border-radius: var(--radius-lg);
        padding: 0.95rem 1rem;
        text-align: center;
        background: linear-gradient(130deg, rgba(15, 118, 110, 0.12), rgba(245, 158, 11, 0.12));
        border: 1px solid rgba(17, 33, 44, 0.08);
    }

    .celebration-title {
        color: var(--ink-900);
        font-size: clamp(1.16rem, 2vw, 1.5rem);
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .stButton button {
        border-radius: 12px;
        border: 1px solid rgba(17, 33, 44, 0.14);
        padding: 0.56rem 0.82rem;
        font-size: 0.94rem;
        font-weight: 700;
        transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 7px 16px rgba(17, 33, 44, 0.14);
        border-color: rgba(17, 33, 44, 0.24);
    }

    .stButton button[kind="primary"] {
        color: #ffffff;
        border: 1px solid rgba(15, 118, 110, 0.55);
        background: linear-gradient(140deg, var(--brand), var(--brand-strong));
    }

    .stButton button[kind="primary"]:hover {
        border-color: rgba(15, 118, 110, 0.8);
        box-shadow: 0 9px 20px rgba(15, 118, 110, 0.25);
    }

    .stTextInput > div > div,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div,
    [data-baseweb="select"] > div {
        border-radius: 11px;
        border: 1px solid rgba(17, 33, 44, 0.16);
        background: rgba(255, 255, 255, 0.94);
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.92rem !important;
    }

    .stSlider [role="slider"] {
        background: var(--brand);
        border: none;
    }

    [data-baseweb="tab-list"] {
        gap: 0.28rem;
    }

    [data-baseweb="tab"] {
        border-radius: 10px;
        border: 1px solid transparent;
        background: rgba(255, 255, 255, 0.74);
        font-weight: 700;
        font-size: 0.84rem;
        padding: 0.34rem 0.7rem;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        border-color: rgba(15, 118, 110, 0.36);
        background: rgba(15, 118, 110, 0.11);
        color: var(--brand-strong);
    }

    [data-testid="stExpander"] {
        border-radius: var(--radius-md);
        border: 1px solid rgba(17, 33, 44, 0.1);
        background: rgba(255, 255, 255, 0.9);
    }

    [data-testid="stExpander"] details summary {
        color: var(--ink-900);
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        border: 1px solid rgba(17, 33, 44, 0.1);
        border-radius: var(--radius-sm);
        background: rgba(255, 255, 255, 0.9);
        padding: 0.4rem 0.56rem;
    }

    [data-testid="stMetricLabel"] {
        color: var(--ink-500);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.65rem;
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink-900);
        font-size: 1.1rem;
        font-weight: 800;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(17, 33, 44, 0.12);
        border-radius: var(--radius-sm);
        overflow: hidden;
    }

    [data-testid="stDataFrameResizable"] {
        font-size: 0.82rem;
    }

    .stAlert {
        border-radius: var(--radius-sm);
        border: 1px solid rgba(17, 33, 44, 0.14);
    }

    .element-container {
        margin-bottom: 0.44rem;
    }

    hr {
        margin: 0.7rem 0;
        border: none;
        border-top: 1px solid rgba(17, 33, 44, 0.12);
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* ---------- Combo escalation animations ---------- */
    /* Stages: x3 = pulse, x5 = glow, x10 = ring rotation, x15 = sparkle ring */
    .combo-stage-1 .combo-meter-fill {
        animation: combo-pulse 1.4s ease-in-out infinite;
    }
    .combo-stage-2 .combo-meter-fill {
        animation: combo-pulse 1.1s ease-in-out infinite,
                   combo-glow 1.6s ease-in-out infinite;
    }
    .combo-stage-3 .combo-meter-fill {
        animation: combo-pulse 0.9s ease-in-out infinite,
                   combo-glow 1.3s ease-in-out infinite;
    }
    .combo-stage-3::before {
        content: "";
        position: absolute;
        inset: -6px;
        border-radius: 999px;
        border: 2px solid rgba(245, 158, 11, 0.55);
        animation: combo-ring-rotate 2.4s linear infinite;
        pointer-events: none;
    }
    .combo-stage-4 .combo-meter-fill {
        animation: combo-pulse 0.7s ease-in-out infinite,
                   combo-glow 1s ease-in-out infinite;
    }
    .combo-stage-4::before {
        content: "";
        position: absolute;
        inset: -6px;
        border-radius: 999px;
        border: 2px solid rgba(245, 158, 11, 0.7);
        animation: combo-ring-rotate 1.8s linear infinite;
        pointer-events: none;
    }
    .combo-stage-4::after {
        content: "✦ ✦ ✦";
        position: absolute;
        inset: -16px 0 auto 0;
        text-align: center;
        color: var(--accent);
        font-size: 0.7rem;
        letter-spacing: 0.45em;
        animation: combo-sparkle 1.2s ease-in-out infinite;
        pointer-events: none;
    }
    .combo-glow {
        position: relative;
    }

    @keyframes combo-pulse {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(1.18); }
    }
    @keyframes combo-glow {
        0%, 100% { box-shadow: 0 0 0 rgba(245, 158, 11, 0); }
        50% { box-shadow: 0 0 14px rgba(245, 158, 11, 0.65); }
    }
    @keyframes combo-ring-rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes combo-sparkle {
        0%, 100% { opacity: 0.35; transform: translateY(0); }
        50% { opacity: 1; transform: translateY(-2px); }
    }

    /* ---------- Count-up score chip ---------- */
    .score-chip {
        display: inline-flex;
        align-items: baseline;
        gap: 0.35rem;
        padding: 0.32rem 0.7rem;
        border-radius: 999px;
        background: linear-gradient(140deg, rgba(15, 118, 110, 0.14), rgba(245, 158, 11, 0.14));
        border: 1px solid rgba(15, 118, 110, 0.22);
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        color: var(--ink-900);
    }
    .score-chip-label {
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--ink-500);
    }
    .score-chip-value {
        display: inline-block;
        font-size: 1.04rem;
        animation: score-count-up 380ms ease-out;
    }
    @keyframes score-count-up {
        0% { transform: translateY(6px) scale(0.9); opacity: 0; }
        60% { transform: translateY(-1px) scale(1.06); opacity: 1; }
        100% { transform: translateY(0) scale(1); opacity: 1; }
    }

    /* ---------- Timer warn pulse for sprint countdowns < 10s ---------- */
    .timer--pulse-warn {
        color: var(--danger);
        border-color: rgba(180, 35, 24, 0.45);
        background: rgba(254, 237, 236, 0.96);
        animation: timer-pulse-warn 0.9s ease-in-out infinite;
    }
    @keyframes timer-pulse-warn {
        0%, 100% { box-shadow: 0 0 0 rgba(180, 35, 24, 0); transform: scale(1); }
        50% { box-shadow: 0 0 14px rgba(180, 35, 24, 0.55); transform: scale(1.03); }
    }

    /* ---------- Milestone hint chip ---------- */
    .milestone-hint {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.5rem 0.7rem;
        border-radius: 999px;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(180, 83, 9, 0.28);
        margin-bottom: 0.4rem;
    }
    .milestone-hint-icon { font-size: 1rem; }
    .milestone-hint-text {
        color: #6b3a05;
        font-size: 0.84rem;
        font-weight: 700;
    }
    .milestone-hint-progress {
        flex: 1;
        height: 6px;
        background: rgba(180, 83, 9, 0.18);
        border-radius: 999px;
        overflow: hidden;
    }
    .milestone-hint-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent), #f97316);
        border-radius: 999px;
    }

    /* ---------- Friendly empty state ---------- */
    .empty-state {
        border-radius: var(--radius-lg);
        border: 1px dashed rgba(15, 118, 110, 0.38);
        background:
            linear-gradient(135deg, rgba(15, 118, 110, 0.06), rgba(245, 158, 11, 0.08));
        padding: 1.4rem 1.3rem;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .empty-state-title {
        color: var(--ink-900);
        font-size: 1.18rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        margin-bottom: 0.3rem;
    }
    .empty-state-body {
        color: var(--ink-700);
        font-size: 0.94rem;
        line-height: 1.45;
        max-width: 520px;
        margin: 0 auto 0.4rem auto;
    }

    /* ---------- Big primary CTA card ---------- */
    .primary-cta {
        border-radius: var(--radius-lg);
        padding: 1.1rem 1.2rem;
        background: linear-gradient(135deg, var(--brand), var(--brand-strong));
        color: #ffffff;
        box-shadow: 0 18px 36px rgba(15, 118, 110, 0.28);
        margin-bottom: 0.6rem;
    }
    .primary-cta-eyebrow {
        font-size: 0.74rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        opacity: 0.82;
    }
    .primary-cta-title {
        font-size: clamp(1.2rem, 2.2vw, 1.6rem);
        font-weight: 800;
        margin-top: 0.2rem;
        letter-spacing: -0.01em;
    }
    .primary-cta-sub {
        font-size: 0.92rem;
        opacity: 0.92;
        margin-top: 0.25rem;
    }

    @media (max-width: 900px) {
        .main .block-container {
            padding-left: 0.78rem;
            padding-right: 0.78rem;
        }

        .hero-shell {
            padding: 1.08rem 1.02rem;
        }

        .stat-card {
            min-height: 108px;
            padding: 0.76rem 0.78rem;
        }

        .question-display {
            font-size: clamp(1.24rem, 5.8vw, 1.55rem);
            padding: 0.92rem 0.74rem;
        }
    }

    @media (max-width: 600px) {
        .main .block-container {
            padding-top: 0.88rem;
            padding-left: 0.62rem;
            padding-right: 0.62rem;
        }

        .hero-chip {
            font-size: 0.68rem;
            padding: 0.22rem 0.5rem;
        }

        [data-baseweb="tab"] {
            font-size: 0.76rem;
            padding: 0.3rem 0.56rem;
        }

        [data-testid="stHorizontalBlock"] {
            gap: 0.4rem;
        }
    }
    </style>
    """
