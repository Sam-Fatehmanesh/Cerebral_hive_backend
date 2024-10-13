import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import List, Dict

def scrape_stackoverflow(tags: List[str], pages: int = 50) -> List[Dict]:
    base_url = "https://stackoverflow.com/questions/tagged/{}?tab=votes&page={}&pagesize=50"
    data = []

    for tag in tags:
        print(f"Scraping tag: {tag}")
        for page in range(1, pages + 1):
            url = base_url.format('+'.join(tag.split()), page)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            questions = soup.find_all('div', class_='question-summary')
            
            for question in questions:
                title = question.find('a', class_='question-hyperlink').text
                votes = question.find('span', class_='vote-count-post').text
                link = 'https://stackoverflow.com' + question.find('a', class_='question-hyperlink')['href']
                
                # Fetch the question details and answers
                question_response = requests.get(link)
                question_soup = BeautifulSoup(question_response.text, 'html.parser')
                
                question_body = question_soup.find('div', class_='question').find('div', class_='s-prose').text.strip()
                
                answers = question_soup.find_all('div', class_='answer')
                if answers:
                    top_answer = answers[0].find('div', class_='s-prose').text.strip()
                    answer_votes = answers[0].find('div', class_='js-vote-count').text.strip()
                    
                    # Only save questions with answers that have 10 or more upvotes
                    if int(answer_votes) >= 10:
                        data.append({
                            'title': title,
                            'votes': votes,
                            'link': link,
                            'question': question_body,
                            'answer': top_answer,
                            'answer_votes': answer_votes,
                            'tag': tag
                        })
            
            print(f"Scraped page {page} for tag {tag}")
            time.sleep(5)  # Be respectful to Stack Overflow's servers
    
    return data

def save_to_csv(data: List[Dict], filename: str):
    if not data:
        print("No data to save.")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    niche_tags = [
        "distributed-computing",
        "quantum-computing",
        "fpga",
        "cuda",
        "blockchain",
        "computer-vision",
        "natural-language-processing",
        "reinforcement-learning",
        "cybersecurity",
        "embedded-systems"
    ]
    import ipdb; ipdb.set_trace()
    all_data = []
    for tag in niche_tags:
        tag_data = scrape_stackoverflow([tag], pages=10)  # Reduced to 10 pages per tag for demonstration
        all_data.extend(tag_data)
        print(f"Scraped {len(tag_data)} questions for tag {tag}")
    
    save_to_csv(all_data, 'niche_topics_data.csv')
    print(f"Scraped a total of {len(all_data)} questions and saved to niche_topics_data.csv")
