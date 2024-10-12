import json
import httpx
from tqdm import tqdm

#######################
###### ADD A THRESHOLD SUCH THAT TOO SIMILAR ANSWERS ARE NOT ADDED TO THE DB
#####################

def download_file(url, filename):
    with httpx.stream("GET", url) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        with open(filename, "wb") as file, tqdm(
            desc=filename,
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_bytes():
                size = file.write(chunk)
                progress_bar.update(size)

def process_codeqa_dataset(input_file, output_file, max_samples=10000):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    processed_data = []
    for item in data[:max_samples]:
        question = item['question']
        answer = item['answer']
        processed_data.append({
            'question': question,
            'answer': answer
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"Processed {len(processed_data)} samples and saved to {output_file}")

url = "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/Code-Question-Answering/dataset/traindata.json"
input_file = "codeqa_raw.json"
output_file = "codeqa_processed.json"

print("Downloading CodeQA dataset...")
download_file(url, input_file)

print("Processing CodeQA dataset...")
process_codeqa_dataset(input_file, output_file)

print("Dataset processing complete!")