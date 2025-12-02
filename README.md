# 🧮 Mental Math Training App

A comprehensive mental math training application built with Streamlit, designed for practicing quick calculations - perfect for trading firm interview preparation and general mental math improvement.

## ✨ Features

### 🎮 Multiple Game Modes
- **Sprint Mode**: Time-limited challenge (1, 2, or 5 minutes)
- **Marathon Mode**: Question count challenge (25, 50, or 100 questions)
- **Targeted Practice**: Focus on your weak areas with adaptive question selection

### 📚 Question Categories
- **Arithmetic**: Addition, subtraction, multiplication, division
- **Percentages**: Percentage calculations, percentage change, reverse percentages
- **Fractions**: Fraction-to-decimal conversions, decimal-to-fraction, fraction arithmetic
- **Ratios**: Simple ratios, three-way ratios, ratio word problems
- **Compound**: Multi-step problems with multiple operations
- **Estimation**: Quick approximations with acceptable ranges
- **Mixed**: All question types combined

### 💪 Difficulty Levels
- **Easy**: Simple problems to build confidence
- **Medium**: Moderate challenge for steady improvement
- **Hard**: Complex problems for advanced training
- **Adaptive**: Automatically adjusts based on your performance

### 🏆 Gamification
- **Combo System**: Build combos with consecutive correct answers for score multipliers
- **Speed Bonuses**: Extra points for quick answers
- **Achievement Badges**: 19+ badges to earn across different categories
- **Daily Streaks**: Track consecutive days of practice
- **Leaderboards**: Personal best scores and statistics

### 📊 Analytics & Insights
- **Performance Tracking**: Detailed statistics by category and difficulty
- **Trend Analysis**: Visualize accuracy and speed improvements over time
- **Weak Area Identification**: Automatically identify areas needing improvement
- **Session Insights**: Get personalized feedback after each session
- **Time-of-Day Analysis**: See when you perform best

## 🚀 Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd mentalmath
```

2. Install dependencies:
```bash
pip install -e .
```

Or install dependencies directly:
```bash
pip install streamlit pandas plotly pydantic python-dateutil pytest
```

3. Run the application:
```bash
streamlit run main.py
```

The app will open in your default web browser at `http://localhost:8501`

## 📖 Usage

### Getting Started

1. **Home Dashboard**: View your overall statistics, current streak, and recent sessions
2. **Start Practice**: Click "START PRACTICE" or choose a quick mode
3. **Configure Session**: Select mode type, category, and difficulty
4. **Practice**: Answer questions as quickly and accurately as possible
5. **View Results**: See your performance, earn badges, and get insights
6. **Analytics**: Explore detailed statistics and trends

### Tips for Best Results

- **Practice Daily**: Build and maintain a streak for consistent improvement
- **Start with Medium Difficulty**: Let adaptive mode adjust for you
- **Focus on Weak Areas**: Use targeted practice to improve specific skills
- **Aim for Speed**: Try to answer under 3 seconds for maximum bonuses
- **Track Progress**: Regularly check analytics to identify trends

## 🎯 Scoring System

- **Base Points**: 100 points per correct answer
- **Combo Multiplier**: 
  - 3+ correct: 1.5x
  - 5+ correct: 2.0x
  - 10+ correct: 2.5x
  - 15+ correct: 3.0x (max)
- **Speed Bonus**:
  - Under 2s: +100 points
  - Under 3s: +50 points
  - Under 5s: +25 points
- **Difficulty Multiplier**:
  - Easy: 1.0x
  - Medium: 1.5x
  - Hard: 2.0x

## 🏅 Badges

### Milestone Badges
- **First Steps**: Complete your first session
- **Century Club**: Answer 100 total questions
- **Veteran**: Answer 1000 total questions
- **Marathon Finisher**: Complete first marathon mode

### Performance Badges
- **Perfectionist**: 100% accuracy in a session (min 10 questions)
- **Speed Demon**: 10 answers under 3 seconds in one session
- **Lightning Round**: Average under 3s in a session
- **No Miss**: 50 consecutive correct answers

### Streak Badges
- **Consistent**: 3-day streak
- **Week Warrior**: 7-day streak
- **Month Master**: 30-day streak

### Category Mastery Badges
- **Arithmetic Ace**: 95% accuracy over 50 arithmetic questions
- **Percentage Pro**: 95% accuracy over 50 percentage questions
- **Fraction Master**: 95% accuracy over 50 fraction questions
- And more...

## 🗄️ Data Storage

All data is stored locally in a SQLite database (`data/mentalmath.db`):
- Session history
- Question results
- Badge progress
- Daily streaks
- User preferences

No external API calls or cloud storage - your data stays private on your machine.

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

Test coverage includes:
- Question generation for all categories
- Answer validation logic
- Scoring calculations
- Difficulty adjustment
- Analytics functions

## 🛠️ Development

### Project Structure

```
mentalmath/
├── main.py                    # Streamlit entry point
├── src/
│   ├── models/               # Data models (Question, Session, etc.)
│   ├── database/             # Database management
│   ├── question_generator/   # Question generation by category
│   ├── game_logic/           # Session management, scoring, validation
│   ├── analytics/            # Performance tracking and insights
│   ├── gamification/         # Badges and streaks
│   └── ui/                   # Streamlit UI components and pages
├── data/                     # SQLite database (created at runtime)
├── tests/                    # Unit tests
└── assets/                   # Badge icons and images
```

### Key Technologies

- **Streamlit**: Web interface and user interaction
- **SQLite**: Local database for data persistence
- **Pandas**: Data manipulation and analytics
- **Plotly**: Interactive charts and visualizations
- **Pydantic**: Data validation
- **pytest**: Testing framework

## 🎨 Customization

The app uses a trading-inspired color scheme:
- 🟢 Green for correct answers and gains
- 🔴 Red for incorrect answers and losses
- 🔵 Blue for neutral information

Custom CSS styling is defined in `src/ui/styles.py` and can be modified for different themes.

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 🙏 Acknowledgments

Built for traders and mental math enthusiasts who want to sharpen their quantitative skills.

## 📧 Contact

For questions, suggestions, or feedback, please open an issue on GitHub.

---

**Happy practicing! 🧮✨**
