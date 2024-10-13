import pandas as pd
import numpy as np
from kaggle.api.kaggle_api_extended import KaggleApi
import os
import zipfile
from tqdm import tqdm

def download_dataset():
    api = KaggleApi()
    api.authenticate()

    print("Downloading Stack Overflow Q&A dataset...")
    api.dataset_download_files('stackoverflow/stackoverflow-questions-2017-to-2023', path='.')

    print("Extracting dataset...")
    with zipfile.ZipFile('stackoverflow-questions-2017-to-2023.zip', 'r') as zip_ref:
        zip_ref.extractall('.')

def preprocess_dataset(input_file, output_file, max_samples=100000):
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file, usecols=['title', 'body', 'answer'], nrows=max_samples)

    print("Preprocessing data...")
    df['question'] = df['title'] + " " + df['body']
    df = df.drop(['title', 'body'], axis=1)

    # Remove HTML tags (simple approach, consider using BeautifulSoup for more robust cleaning)
    df['question'] = df['question'].str.replace('<[^<]+?>', '', regex=True)
    df['answer'] = df['answer'].str.replace('<[^<]+?>', '', regex=True)

    # Remove newlines and extra spaces
    df['question'] = df['question'].str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
    df['answer'] = df['answer'].str.replace('\n', ' ').str.replace('\r', ' ').str.strip()

    # Drop rows with missing values
    df = df.dropna()

    print(f"Saving processed data to {output_file}...")
    df.to_json(output_file, orient='records', lines=True)

    print(f"Processed {len(df)} samples and saved to {output_file}")

if __name__ == "__main__":
    input_file = 'stackoverflow_questions.csv'
    output_file = 'stackoverflow_qa_processed.jsonl'

    if not os.path.exists(input_file):
        download_dataset()

    preprocess_dataset(input_file, output_file)

    print("Dataset processing complete!")