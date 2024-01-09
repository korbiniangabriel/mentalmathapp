import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Data Loader
class DataLoader:
    def load_data(self, filepath, difficulty=None):
        df = pd.read_csv(filepath)
        if difficulty is not None:
            df = df[df['difficulty'] == difficulty]
        return df


# Analysis Functions
def timeline_analysis(df):
    session_summary = df.groupby('session_id').agg({'question': 'count', 'correctness_percentage': 'mean'})
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Session ID')
    ax1.set_ylabel('Number of Questions', color='tab:blue')
    ax1.plot(session_summary.index, session_summary['question'], color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Correctness Percentage', color='tab:red')
    ax2.plot(session_summary.index, session_summary['correctness_percentage'], color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Timeline Analysis: Questions and Correctness Percentage by Session')
    plt.show()


def density_plot(df):
    # We'll create a density plot using numpy and matplotlib
    for diff in df['difficulty'].unique():
        subset = df[df['difficulty'] == diff]['time_per_answer']
        sns.kdeplot(subset, label=f'Difficulty {diff}')

    plt.xlabel('Time Per Answer')
    plt.ylabel('Density')
    plt.title('Density Plot: Time Per Answer for Each Difficulty Level')
    plt.legend()
    plt.show()


# Main function
def main(args):
    data_loader = DataLoader()
    df = data_loader.load_data(args.file, args.difficulty)

    if args.timeline:
        timeline_analysis(df)

    if args.density:
        density_plot(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Math Session Log Analyser')
    parser.add_argument('--file', type=str, help='Path to the math_session_log.csv file', default='math_session_log.csv')
    parser.add_argument('--difficulty', type=int, help='Filter by difficulty level')
    parser.add_argument('--timeline', action='store_true', help='Generate timeline plot')
    parser.add_argument('--density', action='store_true', help='Generate density plot')

    args = parser.parse_args()
    main(args)