# 🧮 Mental Math Training App

A comprehensive mental math training application built with Streamlit. Perfect for trading firm interview preparation and general mental math improvement.

## ✨ Features

### Game Modes
- **Sprint Mode**: Time-limited challenge (1, 2, or 5 minutes)
- **Marathon Mode**: Question count challenge (25, 50, or 100 questions)
- **Targeted Practice**: Focus on weak areas with adaptive question selection

### Question Categories
- **Arithmetic**: Addition, subtraction, multiplication, division
- **Percentages**: Percentage calculations, percentage change, reverse percentages
- **Fractions**: Fraction-to-decimal conversions, decimal-to-fraction, fraction arithmetic
- **Ratios**: Simple ratios, three-way ratios, ratio word problems
- **Compound**: Multi-step problems with multiple operations
- **Estimation**: Quick approximations with acceptable ranges
- **Mixed**: All question types combined

### Gamification
- **Combo System**: Build combos with consecutive correct answers (up to 3x multiplier)
- **Speed Bonuses**: Extra points for quick answers (up to +100 points)
- **Achievement Badges**: 19+ badges to earn across different categories
- **Daily Streaks**: Track consecutive days of practice
- **Leaderboards**: Personal best scores and statistics

### Analytics
- Performance tracking by category and difficulty
- Trend analysis to visualize improvement over time
- Weak area identification
- Session insights with personalized feedback

## 🚀 Quick Start

### Option 1: Docker (Recommended)

Docker provides isolated deployment that doesn't interfere with other applications.

```bash
# Start the app
docker-compose up -d

# Access at http://localhost:8501

# Stop the app
docker-compose down
```

**Or use the convenience scripts:**
```bash
./docker-start.sh
./docker-stop.sh
```

**Benefits:**
- ✅ No Python installation required
- ✅ Isolated from other applications
- ✅ Consistent environment
- ✅ Persistent data storage

### Option 2: Python Installation

**Prerequisites:** Python 3.13 or higher

```bash
# Install dependencies
pip install -e .

# Run the application
streamlit run main.py

# Access at http://localhost:8501
```

## 📖 How to Use

1. **Home Dashboard**: View your statistics, current streak, and recent sessions
2. **Start Practice**: Click "START PRACTICE" or choose a quick mode
3. **Configure Session**: Select mode, category, and difficulty
4. **Practice**: Answer questions as quickly and accurately as possible
5. **View Results**: See your performance, earn badges, and get insights
6. **Analytics**: Explore detailed statistics and trends

### Tips
- **Practice Daily**: Build and maintain a streak for consistent improvement
- **Start with Medium Difficulty**: Let adaptive mode adjust for you
- **Aim for Speed**: Try to answer under 3 seconds for maximum bonuses
- **Track Progress**: Check analytics to identify trends

## 🎯 Scoring System

- **Base Points**: 100 points per correct answer
- **Combo Multiplier**: Up to 3.0x for 15+ consecutive correct answers
- **Speed Bonus**: Up to +100 points for answers under 2 seconds
- **Difficulty Multiplier**: 1.0x (Easy), 1.5x (Medium), 2.0x (Hard)

## 🗄️ Data Storage

All data is stored locally in SQLite (`data/mentalmath.db`):
- Session history
- Question results
- Badge progress
- Daily streaks

**Your data stays private on your machine** - no external API calls or cloud storage.

## 🐳 Docker Commands

### Basic Operations
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down
```

### Troubleshooting
```bash
# Check status
docker-compose ps

# Access container shell
docker-compose exec mentalmath bash

# Reset everything
docker-compose down -v
rm -rf data/*.db
docker-compose up -d
```

### Configuration

**Change Port**: Edit `docker-compose.yml`
```yaml
ports:
  - "8502:8501"  # Change host port
```

**Resource Limits**: Default is 1 CPU core and 512MB RAM. Adjust in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src
```

## 🛠️ Project Structure

```
mentalmath/
├── main.py                    # Application entry point
├── src/
│   ├── models/               # Data models
│   ├── database/             # Database management
│   ├── question_generator/   # Question generation by category
│   ├── game_logic/           # Session management and scoring
│   ├── analytics/            # Performance tracking
│   ├── gamification/         # Badges and streaks
│   └── ui/                   # Streamlit UI components
├── data/                     # SQLite database (auto-created)
└── tests/                    # Unit tests
```

## 🔧 Common Issues

### Port Already in Use (Python)
```bash
streamlit run main.py --server.port 8502
```

### Port Already in Use (Docker)
Edit port in `docker-compose.yml` or stop conflicting service:
```bash
lsof -i :8501  # Find what's using the port
```

### Database Issues
```bash
# Python
rm data/mentalmath.db
streamlit run main.py

# Docker
docker-compose down
rm data/*.db
docker-compose up -d
```

### Permission Issues (Docker)
```bash
chmod 755 data/
```

## 📝 License

This project is open source and available under the MIT License.

## 📧 Support

For questions or issues, please open an issue on GitHub.

---

**Happy practicing! 🧮✨**
