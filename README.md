# Mental Math App
A python program to train mental math on the console and analyze ones progress over time.


## Introduction
The Mental Math Training Program is a Python-based application designed to improve mental arithmetic skills. It provides a range of mathematical problems with varying levels of difficulty and immediate feedback. The program logs session details for performance analysis.

**Note on mobile version:** You can run this code on _Pythonista3_.

## Features
- **Dynamic Question Generation:** Generates arithmetic problems based on specified difficulty levels.
- **Customizable Sessions:** Set session duration, difficulty level, and number range.
- **Immediate Feedback:** Offers instant feedback on each answer.
- **Performance Logging:** Logs details for each session for analysis.
- **Data Analysis Tools:** Analyze performance over time and answer speed.

## Installation
1. Ensure Python is installed on your system.
2. Clone or download this repository to your local machine.
3. Install required libraries using the following command:
   ```bash
   pip install pandas matplotlib
   ```
## Usage
### Starting a Session
1. Run play.py:
   ```bash
   python play.py
   ```
2. Follow on-screen instructions to set session preferences.
3. Answer questions as they appear. Type -- to skip a question.
4. After the session, a performance summary is displayed.

### Analyzing Past Sessions
1. Run analyse.py for session analysis:
   ```bash
   python analyse.py --timeline --density --difficulty 1 (difficulty filter optional) --file math_session_log.csv (filepath is optional)
   ```
2. Use arguments to filter by difficulty, generate timeline, or density plots.

## Tutorial
### Main Menu Options

- **Session Time**: Set duration in seconds (default: 60).
- **Difficulty Level**: Choose between 1 (Easy), 2 (Intermediate), 3 (Hard), or 0 (Random).
- **Punishment for Wrong Answers**: Penalty points for incorrect answers (default: -1).
- **Number Range**: Set minimum and maximum values for questions.
- **Immediate Feedback**: Choose to see feedback after each question (default: Yes).

### In-Session Interface
- Answer questions like `12 + 7 =` or `sqrt(16)`.
- Enter your answer and press Enter.
- Feedback will be shown if enabled.

### Analyzing Performance
- Use `analyse.py` to review performance.
- Generate plots for progress visualization and speed analysis.


## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome. Please read below for contribution guidelines.


---


# Contributing to Mental Math Training Program

Your contributions are appreciated! Making the process of contributing to this project easy and transparent is a priority, whether it involves:
- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process
The development is done using GitHub. This is where the code is hosted, issues and feature requests are tracked, and pull requests are reviewed.

## Github Flow
All code changes happen through Pull Requests. Pull requests are the best way to propose changes to the codebase. Here's how to do it:

1. Fork the repo and create your branch from `main`.
2. Add tests for any new code you've added, if applicable.
3. If you make changes to APIs, update the documentation accordingly.
4. Ensure any added tests pass.
5. Ensure your code adheres to the established coding standards.
6. Submit the pull request.

## Contributions and Licensing
Any contributions made will fall under the MIT Software License. This ensures that all submissions are understood to be under the same [MIT License](http://opensource.org/licenses/MIT) that covers the project. If you have any concerns, feel free to reach out to the maintainers.

## Reporting Bugs
Bugs are tracked using GitHub's [Issues](https://github.com/korbiniangabriel/mentalmathapp/issues). To report a bug, [open a new issue](https://github.com/korbiniangabriel/mentalmathapp/issues/new).

## Writing Bug Reports
**Effective Bug Reports** generally have:
- A concise summary and/or background
- Steps to reproduce
  - Be as specific as possible.
  - Include sample code if possible.
- Expected outcomes
- Actual outcomes
- Any additional notes or hypotheses regarding the issue

## Code Style
Please adhere to a consistent coding style:
* Indentation should be 2 spaces, not tabs.
* Consider running `autopep8` for automatic style adherence.

## License
By contributing, you agree that your contributions will be licensed under its GNU General Public License v3.0.


## Reference
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md)