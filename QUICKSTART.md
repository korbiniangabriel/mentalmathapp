# 🚀 Quick Start Guide

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -e .
```

This will install:
- streamlit
- pandas
- plotly
- pydantic
- python-dateutil
- pytest

### 2. Run the Application

```bash
streamlit run main.py
```

The app will automatically:
- Create the SQLite database in `data/mentalmath.db`
- Initialize all tables and default badges
- Open in your browser at `http://localhost:8501`

### 3. First Time Usage

**Step 1:** You'll see the home dashboard with all stats at zero

**Step 2:** Click "🎮 START PRACTICE" to begin

**Step 3:** Configure your first session:
- Mode: Try "Sprint" with 2 minutes
- Category: Start with "Mixed"
- Difficulty: Select "Medium"

**Step 4:** Answer questions as fast as you can!

**Step 5:** View your results and earned badges

## Quick Commands

### Run Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_question_generators.py -v
```

### Check Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Clean Database (Start Fresh)
```bash
rm data/mentalmath.db
```
The database will be recreated on next run.

## Example Session Flow

1. **Home Dashboard** → View stats and streak
2. **Mode Selection** → Configure session
3. **Practice Session** → Answer questions
4. **Results Page** → See performance and badges
5. **Analytics Dashboard** → View detailed statistics

## Quick Mode Options

From the home page, you can instantly start:

- **⚡ Sprint Mode**: 2-minute challenge with mixed questions
- **🏃 Marathon Mode**: 50 questions challenge
- **🎯 Targeted Practice**: Focus on your weak areas

## Tips for Best Experience

1. **Use full screen** for better visibility
2. **Type answers quickly** - no need to click submit, press Enter
3. **Build streaks** by practicing daily
4. **Check analytics** regularly to track improvement
5. **Start with Medium** and let adaptive mode adjust for you

## Keyboard Shortcuts

- **Enter**: Submit answer
- **ESC**: Not available (use ❌ button to quit)
- **Tab**: Navigate between UI elements

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
rm data/mentalmath.db
streamlit run main.py
```

### Import Errors
Make sure you're in the project directory:
```bash
cd /home/dev/projects/mentalmath
pip install -e .
```

### Port Already in Use
If port 8501 is busy:
```bash
streamlit run main.py --server.port 8502
```

## What's Included

✅ **36 Python files** implementing:
- 7 Question generators (Arithmetic, Percentages, Fractions, Ratios, Compound, Estimation)
- Complete database management with SQLite
- Session management and game logic
- Scoring system with combos and bonuses
- Analytics and insights generation
- Badge system with 19+ achievements
- Streak tracking
- 5 Streamlit UI pages
- Comprehensive test suite (26 tests)

✅ **Features**:
- Real-time performance tracking
- Adaptive difficulty adjustment
- Interactive charts with Plotly
- Badge and achievement system
- Daily streak tracking
- Detailed analytics dashboard
- Multiple game modes
- 7 question categories
- 4 difficulty levels

## Next Steps

1. **Practice Daily**: Build your streak
2. **Try Different Modes**: Explore all game modes
3. **Check Analytics**: See your improvement over time
4. **Earn Badges**: Complete achievements
5. **Target Weak Areas**: Use targeted practice

Enjoy training! 🧮✨
