import os
import csv
import random
import time
from datetime import datetime
from math import sqrt
import uuid

class QuestionGenerator:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.difficult_questions = set()

    def generate_question(self, difficulty):
        if difficulty == 0:
            difficulty = random.choice([1, 2, 3])

        while True:
            if difficulty == 1:
                num1, num2 = random.randint(self.min_value, self.max_value), random.randint(self.min_value, self.max_value)
                op = random.choice(['+', '-', '*', '/'])
                question = f"{num1} {op} {num2}"
            elif difficulty == 2:
                num1, num2 = random.uniform(self.min_value, self.max_value), random.uniform(self.min_value, self.max_value)
                op = random.choice(['+', '-', '*', '/'])
                question = f"{num1:.2f} {op} {num2:.2f}"
            else:
                if random.choice([True, False]):
                    num = random.randint(self.min_value, self.max_value)
                    question = f"sqrt({num})"
                else:
                    num = random.randint(self.min_value, self.max_value)
                    question = f"{num}**2"

            if question not in self.difficult_questions:
                break

        try:
            answer = round(eval(question), 2)
        except ZeroDivisionError:
            return self.generate_question(difficulty)

        self.difficult_questions.add(question)
        return question, answer

class Timer:
    def __init__(self, duration):
        self.end_time = time.time() + duration

    def is_time_up(self):
        return time.time() > self.end_time

class Logger:
    def __init__(self, filename, session_id):
        self.filename = filename
        self.session_id = session_id
        self.fields = ['session_id', 'datetime', 'total_time', 'difficulty', 'question', 'user_answer', 'correct_answer', 'time_per_answer', 'right/wrong', 'score', 'total_score', 'correctness_percentage']
        self.write_header()

    def write_header(self):
        # Check if the file exists and is not empty
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fields)
                writer.writeheader()

    def log(self, data):
        data['session_id'] = self.session_id
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fields)
            writer.writerow(data)

def main(duration, difficulty, punishment, min_value, max_value, show_feedback, session_id):
    generator = QuestionGenerator(min_value, max_value)
    timer = Timer(duration)
    logger = Logger('math_session_log.csv', session_id)  # Pass session ID to Logger
    total_questions, correct_answers, total_score = 0, 0, 0

    while not timer.is_time_up():
        question, correct_answer = generator.generate_question(difficulty)
        start_time = time.time()
        user_answer = input(f"Question: {question} = ")

        if user_answer == '--':
            continue

        end_time = time.time()

        total_questions += 1
        try:
            correct = round(float(user_answer), 2) == correct_answer
        except ValueError:
            correct = False
        correct_answers += correct
        score = 1 if correct else punishment
        total_score += score

        if show_feedback:
            feedback = 'Correct!' if correct else 'Wrong!'
            print(feedback)

        log_data = {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_time': f'{duration // 60} min',
            'difficulty': difficulty,
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'time_per_answer': round(end_time - start_time, 2),
            'right/wrong': 'Right' if correct else 'Wrong',
            'score': score,
            'total_score': total_score,
            'correctness_percentage': round((correct_answers / total_questions) * 100, 2)
        }
        logger.log(log_data)

    print(f"Session ended. Total Score: {total_score}, Correctness: {round((correct_answers / total_questions) * 100, 2)}%")


def get_options():
    print("Welcome to the Mental Math Training Program!")
    print("Please enter the following options:")
    duration = int(input("Time for the session in seconds (default: 60): ") or 60)
    difficulty = int(input("Difficulty level (1, 2, 3, 0 for random; default: 1): ") or 1)
    punishment = int(input("Punishment for wrong answers (-1 or -2; default: -1): ") or -1)
    min_value = float(input("Minimum number for questions (default: 0): ") or 0)
    max_value = float(input("Maximum number for questions (default: 100): ") or 10)
    show_feedback_input = input("Show immediate feedback (y/n; default: y): ").lower() or 'y'
    show_feedback = show_feedback_input == 'y'
    return duration, difficulty, punishment, min_value, max_value, show_feedback

def start_countdown():
    print("\nStarting in...")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)
    print('------------------------')

def read_last_session_id(log_filename):
    try:
        with open(log_filename, 'r') as file:
            # Read all lines from the file
            lines = file.readlines()
            # Find the last line with a session ID
            for line in reversed(lines):
                if line.strip() and 'session_id' not in line:
                    # Extract the session ID from the last valid line
                    return int(line.split(',')[0])
    except FileNotFoundError:
        return 0  # Return 0 if the file does not exist
    except Exception as e:
        print(f"Error reading session ID from log: {e}")
        return 0

    return 0  # Return 0 if no valid session ID is found

def update_session_id(filename, session_id):
    with open(filename, 'w') as file:
        file.write(str(session_id))



if __name__ == "__main__":
    session_id_file = 'math_session_log.csv'
    last_session_id = read_last_session_id(session_id_file)

    options = get_options()

    while True:
        last_session_id += 1  # Increment the session ID for each new session

        start_countdown()
        main(*options, session_id=last_session_id)  # Pass the updated session ID to the main function

        play_again = input("Do you want to play again? (y/n): ").lower()
        if play_again != 'y':
            break  # Exit the loop if the user doesn't want to play again

        change_options = input("Do you want to change the options? (y/n): ").lower()
        if change_options == 'y':
            options = get_options()  # Get new options if the user wants to change them