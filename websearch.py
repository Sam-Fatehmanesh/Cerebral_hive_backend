import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"An error occurred while fetching the URL: {str(e)}"


def scrape_google_results(query, num_results=16):
    try:
        # Construct the Google search URL
        search_url = f"https://www.google.com/search?{urlencode({'q': query})}"
        
        # Send a GET request to the search URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search result links
        search_results = soup.find_all('div', class_='yuRUbf')
        
        # Extract URLs from the search results
        urls = []
        for result in search_results[:num_results]:
            link = result.find('a')
            if link and 'href' in link.attrs:
                urls.append(link['href'])
        
        # Construct the output string
        output = f"Top {num_results} results for '{query}':\n\n"
        for i, url in enumerate(urls, 1):
            output += f"{i}. {url}\n"
        
        return output
    except Exception as e:
        return f"An error occurred during the web scraping: {str(e)}"